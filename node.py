import socket
from enum import Enum
from config import BUFFER_SIZE, PacketType
from protocol_utils import pack_packet, unpack_packet

class NodeState(Enum):
    CLOSED = 0
    LISTEN = 1
    SYN_SENT = 2
    SYN_RECEIVED = 3
    ESTABLISHED = 4

class Node:
    def __init__(self, my_ip, my_port, target_ip, target_port):
        self.my_address = (my_ip, my_port)
        self.target_address = (target_ip, target_port)
        self.state = NodeState.CLOSED
        self.seq_num = 0
        
        # UDP Soketi oluşturma
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.my_address)
        self.state = NodeState.LISTEN
        print(f"Node başlatıldı: {self.my_address} | Durum: {self.state.name}")

    def send_packet(self, p_type: PacketType, payload: bytes = b""):
        """
        Paketleme yaparak veriyi gönderir.
        """
        packet = pack_packet(p_type, self.seq_num, payload)
        self.sock.sendto(packet, self.target_address)
        print(f"[GÖNDER] {p_type.name} | Seq: {self.seq_num} | Payload: {len(payload)} byte")
        self.seq_num += 1

    def receive_packet(self):
        """
        Veriyi alır ve paketi açar.
        """
        data, addr = self.sock.recvfrom(BUFFER_SIZE)
        p_type, seq, payload = unpack_packet(data)
        print(f"[ALINDI] {p_type.name} | Seq: {seq} | Kaynak: {addr}")
        return p_type, seq, payload

    def establish_connection(self, is_initiator=False):
        """
        3-way Handshake sürecini yönetir.
        """
        if is_initiator:
            # 1. SYN Gönder
            self.send_packet(PacketType.SYN)
            self.state = NodeState.SYN_SENT
            
            # 2. SYN-ACK Bekle (Basitleştirilmiş: Sadece ACK olarak kabul ediyoruz veya 
            # özel bir SYN_ACK tipi yoksa DATA içinde kontrol edilebilir. 
            # Ama biz ACK kullanacağız.)
            p_type, seq, _ = self.receive_packet()
            if p_type == PacketType.ACK:
                # 3. ACK Gönder (Bağlantı kurulduğunu onayla)
                self.send_packet(PacketType.ACK)
                self.state = NodeState.ESTABLISHED
                print(f"Bağlantı Kuruldu (İstemci) | Durum: {self.state.name}")
        else:
            # 1. SYN Bekle
            p_type, seq, _ = self.receive_packet()
            if p_type == PacketType.SYN:
                self.state = NodeState.SYN_RECEIVED
                # 2. ACK Gönder (SYN-ACK niyetine)
                self.send_packet(PacketType.ACK)
                
                # 3. Son ACK'yı bekle
                p_type, seq, _ = self.receive_packet()
                if p_type == PacketType.ACK:
                    self.state = NodeState.ESTABLISHED
                    print(f"Bağlantı Kuruldu (Sunucu) | Durum: {self.state.name}")

    def send_data(self, data: bytes):
        """
        Sadece ESTABLISHED durumunda veri gönderimine izin verir.
        """
        if self.state != NodeState.ESTABLISHED:
            raise ConnectionError("Hata: Bağlantı kurulmadan veri gönderilemez!")
        self.send_packet(PacketType.DATA, data)

    def listen_data(self):
        """
        Sadece ESTABLISHED durumunda veri alımına izin verir.
        """
        if self.state != NodeState.ESTABLISHED:
            raise ConnectionError("Hata: Bağlantı kurulmadan veri dinlenemez!")
        return self.receive_packet()

    def close(self):
        self.state = NodeState.CLOSED
        self.sock.close()
        print(f"Bağlantı Kapatıldı. Durum: {self.state.name}")
