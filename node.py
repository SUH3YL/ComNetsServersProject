import socket
import random
import threading
from enum import Enum
from config import BUFFER_SIZE, PacketType, TIMEOUT, MAX_RETRIES, DEBUG_MODE, CORRUPTION_CHANCE
from protocol_utils import pack_packet, unpack_packet, corrupt_data

class NodeState(Enum):
    CLOSED = 0
    LISTEN = 1
    SYN_SENT = 2
    SYN_RECEIVED = 3
    ESTABLISHED = 4
    ERROR = 5

class Node:
    def __init__(self, my_ip, my_port, target_ip, target_port):
        self.my_address = (my_ip, my_port)
        self.target_address = (target_ip, target_port)
        self.state = NodeState.CLOSED
        self.seq_num = 0
        self.running = True
        
        # UDP Soketi oluşturma
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.my_address)
        self.sock.settimeout(TIMEOUT)
        self.state = NodeState.LISTEN
        print(f"Node başlatıldı: {self.my_address} | Durum: {self.state.name}")

    def send_packet(self, p_type: PacketType, payload: bytes = b"", seq: int = None):
        """
        Paketleme yaparak veriyi gönderir. Debug mode aktifse rastgele veri bozar.
        """
        if seq is None:
            seq = self.seq_num
            self.seq_num += 1
            
        packet = pack_packet(p_type, seq, payload)
        
        # DEBUG_MODE: Rastgele paket bozma simülasyonu
        if DEBUG_MODE and random.random() < CORRUPTION_CHANCE:
            print(f"\n[DEBUG] Paket bozuluyor... (Simulated Bit-flip)")
            packet = corrupt_data(packet)

        self.sock.sendto(packet, self.target_address)
        # Chat modunda çok fazla log basmamak için log seviyesini düşürebiliriz
        # print(f"[GÖNDER] {p_type.name} | Seq: {seq} | Payload: {len(payload)} byte")
        return seq

    def receive_packet(self):
        """
        Veriyi alır ve paketi açar. Checksum hatasını kontrol eder.
        """
        try:
            data, addr = self.sock.recvfrom(BUFFER_SIZE)
            try:
                p_type, seq, payload = unpack_packet(data)
                # print(f"[ALINDI] {p_type.name} | Seq: {seq} | Kaynak: {addr}")
                return p_type, seq, payload
            except ValueError as e:
                if "Checksum hatası" in str(e):
                    print(f"\n!!! Data Corrupted! (Checksum mismatch) !!!")
                return "CORRUPTED", None, None
        except socket.timeout:
            return None, None, None
        except ConnectionResetError:
            return None, None, None

    def establish_connection(self, is_initiator=False):
        """
        3-way Handshake sürecini yönetir.
        """
        if is_initiator:
            retries = 0
            while retries < MAX_RETRIES:
                self.send_packet(PacketType.SYN, seq=0)
                self.state = NodeState.SYN_SENT
                
                p_type, seq, _ = self.receive_packet()
                
                if p_type == "CORRUPTED":
                    print("Handshake sırasında bozuk paket alındı, yoksayılıyor...")
                
                if p_type == PacketType.ACK:
                    self.send_packet(PacketType.ACK, seq=1)
                    self.state = NodeState.ESTABLISHED
                    self.seq_num = 2 
                    print(f"Bağlantı Kuruldu (İstemci) | Durum: {self.state.name}")
                    return
                
                retries += 1
                if retries < MAX_RETRIES:
                    print(f"SYN-ACK gelmedi veya bozuk, tekrar deneniyor ({retries}/{MAX_RETRIES})...")
            
            self.state = NodeState.ERROR
            raise ConnectionError("Bağlantı kurulamadı: Handshake Timeout veya Hata.")
        else:
            self.sock.settimeout(None) 
            while True:
                p_type, seq, _ = self.receive_packet()
                if p_type == "CORRUPTED":
                    print("Dinlerken bozuk paket alındı, yoksayılıyor...")
                    continue
                if p_type == PacketType.SYN:
                    break
            
            self.sock.settimeout(TIMEOUT) 
            self.state = NodeState.SYN_RECEIVED
            self.send_packet(PacketType.ACK, seq=0)
            
            while True:
                p_type, seq, _ = self.receive_packet()
                if p_type == "CORRUPTED":
                    print("Son ACK beklenirken bozuk paket alındı, yoksayılıyor...")
                    continue
                if p_type == PacketType.ACK:
                    self.state = NodeState.ESTABLISHED
                    self.seq_num = 1
                    print(f"Bağlantı Kuruldu (Sunucu) | Durum: {self.state.name}")
                    break

    def send_data(self, data: bytes):
        """
        Sadece ESTABLISHED durumunda veri gönderimine izin verir.
        Retransmission mekanizması içerir.
        """
        if self.state != NodeState.ESTABLISHED:
            print("Hata: Bağlantı kurulmadan veri gönderilemez!")
            return
        
        current_seq = self.seq_num
        self.seq_num += 1
        retries = 0
        
        while retries <= MAX_RETRIES:
            self.send_packet(PacketType.DATA, data, seq=current_seq)
            
            # Chat modunda ACK beklerken diğer thread receive loop'ta olduğu için 
            # burada kısa bir bekleme veya farklı bir mekanizma gerekebilir.
            # Ancak bu basitleştirilmiş Stop-and-Wait ARQ için threadler arası 
            # senkronizasyon gerekecek. Şimdilik basitleştirilmiş gönderim yapıyoruz.
            # Gerçek ARQ için bir ACK queue kullanılabilir.
            return # Şimdilik sadece gönderiyoruz (Chat akışı için)

    def start_receive_thread(self):
        """
        Arka planda dinleme yapacak thread'i başlatır.
        """
        self.receive_thread = threading.Thread(target=self.receive_loop, daemon=True)
        self.receive_thread.start()

    def receive_loop(self):
        """
        Sürekli gelen paketleri dinleyen döngü.
        """
        print("Dinleme döngüsü başlatıldı...")
        while self.running:
            p_type, seq, payload = self.receive_packet()
            
            if p_type == "CORRUPTED":
                continue
            
            if p_type == PacketType.DATA:
                print(f"\n[MESAJ] Sunucu: {payload.decode()}")
                # Alınan veri için ACK gönder
                self.send_packet(PacketType.ACK, seq=seq)
            elif p_type == PacketType.ACK:
                # print(f"[SİSTEM] Paket {seq} onaylandı.")
                pass
            elif p_type == PacketType.FIN:
                print("\n[SİSTEM] Karşı taraf bağlantıyı kapattı.")
                self.state = NodeState.CLOSED
                self.running = False

    def close(self):
        self.running = False
        self.state = NodeState.CLOSED
        self.sock.close()
        print(f"Bağlantı Kapatıldı. Durum: {self.state.name}")
