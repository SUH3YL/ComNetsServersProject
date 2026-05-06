from node import Node, NodeState
from config import PORT_A, PORT_B, PacketType

def main():
    # Sunucu A: Kendi portu PORT_A, hedef portu PORT_B
    node_a = Node("127.0.0.1", PORT_A, "127.0.0.1", PORT_B)
    
    try:
        # 1. Bağlantı Kur (Handshake Başlatıcı)
        print("\n--- Baglanti Kuruluyor ---")
        node_a.establish_connection(is_initiator=True)
        
        # 2. Dinleme Thread'ini Başlat
        node_a.start_receive_thread()
        
        # 3. Chat Döngüsü
        print("\n--- Chat Baslatildi (Cikmak icin 'exit' yazin) ---")
        while node_a.state == NodeState.ESTABLISHED:
            msg = input("Siz: ")
            if msg.lower() == 'exit':
                node_a.send_packet(PacketType.FIN)
                break
            if msg:
                node_a.send_data(msg.encode())
        
    except Exception as e:
        print(f"Hata olustu: {e}")
    finally:
        node_a.close()

if __name__ == "__main__":
    main()
