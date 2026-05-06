import socket
from enum import Enum
from config import BUFFER_SIZE, PacketType, TIMEOUT, MAX_RETRIES
from protocol_utils import pack_packet, unpack_packet

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
        
        # UDP Soketi oluşturma
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.my_address)
        self.sock.settimeout(TIMEOUT)
        self.state = NodeState.LISTEN
        print(f"Node başlatıldı: {self.my_address} | Durum: {self.state.name}")

    def send_packet(self, p_type: PacketType, payload: bytes = b"", seq: int = None):
        """
        Paketleme yaparak veriyi gönderir.
        """
        if seq is None:
            seq = self.seq_num
            self.seq_num += 1
            
        packet = pack_packet(p_type, seq, payload)
        self.sock.sendto(packet, self.target_address)
        print(f"[GÖNDER] {p_type.name} | Seq: {seq} | Payload: {len(payload)} byte")
        return seq

    def receive_packet(self):
        """
        Veriyi alır ve paketi açar.
        """
        try:
            data, addr = self.sock.recvfrom(BUFFER_SIZE)
            p_type, seq, payload = unpack_packet(data)
            print(f"[ALINDI] {p_type.name} | Seq: {seq} | Kaynak: {addr}")
            return p_type, seq, payload
        except socket.timeout:
            return None, None, None

    def establish_connection(self, is_initiator=False):
        """
        3-way Handshake sürecini yönetir.
        """
        # Timeout'u handshake için geçici olarak artırabiliriz veya aynı bırakabiliriz.
        if is_initiator:
            retries = 0
            while retries < MAX_RETRIES:
                self.send_packet(PacketType.SYN, seq=0)
                self.state = NodeState.SYN_SENT
                
                p_type, seq, _ = self.receive_packet()
                if p_type == PacketType.ACK:
                    self.send_packet(PacketType.ACK, seq=1)
                    self.state = NodeState.ESTABLISHED
                    self.seq_num = 2 # Handshake sonrası 2'den devam etsin
                    print(f"Bağlantı Kuruldu (İstemci) | Durum: {self.state.name}")
                    return
                
                retries += 1
                print(f"SYN-ACK gelmedi, tekrar deneniyor ({retries}/{MAX_RETRIES})...")
            
            self.state = NodeState.ERROR
            raise ConnectionError("Bağlantı kurulamadı: Handshake Timeout.")
        else:
            # Dinleyici tarafında sonsuz döngü (veya uzun bir timeout) ile SYN bekleyebiliriz.
            self.sock.settimeout(None) # SYN beklerken bloklansın
            p_type, seq, _ = self.receive_packet()
            self.sock.settimeout(TIMEOUT) # Geri yükle
            
            if p_type == PacketType.SYN:
                self.state = NodeState.SYN_RECEIVED
                self.send_packet(PacketType.ACK, seq=0)
                
                p_type, seq, _ = self.receive_packet()
                if p_type == PacketType.ACK:
                    self.state = NodeState.ESTABLISHED
                    self.seq_num = 1
                    print(f"Bağlantı Kuruldu (Sunucu) | Durum: {self.state.name}")

    def send_data(self, data: bytes):
        """
        Sadece ESTABLISHED durumunda veri gönderimine izin verir.
        Retransmission mekanizması içerir.
        """
        if self.state != NodeState.ESTABLISHED:
            raise ConnectionError("Hata: Bağlantı kurulmadan veri gönderilemez!")
        
        current_seq = self.seq_num
        self.seq_num += 1
        retries = 0
        
        while retries <= MAX_RETRIES:
            # Paketi gönder
            self.send_packet(PacketType.DATA, data, seq=current_seq)
            
            # ACK bekle
            p_type, seq, _ = self.receive_packet()
            
            if p_type == PacketType.ACK and seq == current_seq:
                print(f"[BAŞARILI] Paket {current_seq} onaylandı (ACK alındı).")
                return
            
            retries += 1
            if retries <= MAX_RETRIES:
                print(f"[RE-TRY] Paket {current_seq} için ACK gelmedi, tekrar gönderiliyor ({retries}/{MAX_RETRIES})...")
        
        self.state = NodeState.ERROR
        print(f"[HATA] Paket {current_seq} için {MAX_RETRIES} deneme başarısız oldu. Durum: ERROR")
        raise ConnectionError(f"Veri gönderimi başarısız: Maksimum deneme sayısına ulaşıldı.")

    def listen_data(self):
        """
        Veri alımı yapar ve ACK gönderir.
        """
        if self.state != NodeState.ESTABLISHED:
            raise ConnectionError("Hata: Bağlantı kurulmadan veri dinlenemez!")
        
        # Veri gelene kadar bekle (dinleyici tarafında timeout bazen istenmeyebilir)
        old_timeout = self.sock.gettimeout()
        self.sock.settimeout(None) 
        
        try:
            p_type, seq, payload = self.receive_packet()
            if p_type == PacketType.DATA:
                # Alınan veri için hemen ACK gönder
                self.send_packet(PacketType.ACK, seq=seq)
                return p_type, seq, payload
            return p_type, seq, payload
        finally:
            self.sock.settimeout(old_timeout)

    def close(self):
        self.state = NodeState.CLOSED
        self.sock.close()
        print(f"Bağlantı Kapatıldı. Durum: {self.state.name}")
