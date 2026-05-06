from node import Node, NodeState
from config import PORT_A, PORT_B, PacketType

def main():
    # Sunucu B: Kendi portu PORT_B, hedef portu PORT_A
    node_b = Node("127.0.0.1", PORT_B, "127.0.0.1", PORT_A)
    
    try:
        # 1. Bağlantı Kur (Handshake Dinleyici)
        print("\n--- Baglanti Bekleniyor ---")
        node_b.establish_connection(is_initiator=False)
        
        # 2. Dinleme Thread'ini Başlat
        node_b.start_receive_thread()
        
        # 3. Chat Döngüsü
        print("\n--- Chat Baslatildi (Cikmak icin 'exit' yazin) ---")
        while node_b.state == NodeState.ESTABLISHED:
            msg = input("Siz: ")
            if msg.lower() == 'exit':
                node_b.send_packet(PacketType.FIN)
                break
            if msg:
                node_b.send_data(msg.encode())
        
    except Exception as e:
        print(f"Hata olustu: {e}")
    finally:
        node_b.close()

if __name__ == "__main__":
    main()
