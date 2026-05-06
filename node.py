import socket
from config import BUFFER_SIZE

class Node:
    def __init__(self, my_ip, my_port, target_ip, target_port):
        self.my_address = (my_ip, my_port)
        self.target_address = (target_ip, target_port)
        
        # UDP Soketi oluşturma
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.my_address)
        print(f"Node başlatıldı: {self.my_address} dinleniyor...")

    def send_raw(self, data: bytes):
        """
        Hedef adrese ham veri gönderir.
        """
        print(f"Veri gönderiliyor -> {self.target_address}: {data}")
        self.sock.sendto(data, self.target_address)

    def listen_raw(self):
        """
        Gelen ham veriyi dinler.
        """
        data, addr = self.sock.recvfrom(BUFFER_SIZE)
        print(f"Veri alındı <- {addr}: {data}")
        return data, addr

    def close(self):
        self.sock.close()
