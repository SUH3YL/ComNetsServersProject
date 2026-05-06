from node import Node
from config import PORT_A, PORT_B

def main():
    # Sunucu B: Kendi portu PORT_B, hedef portu PORT_A
    node_b = Node("127.0.0.1", PORT_B, "127.0.0.1", PORT_A)
    
    try:
        # 1. Bağlantı Kur (Handshake Dinleyici)
        print("\n--- Baglanti Bekleniyor ---")
        node_b.establish_connection(is_initiator=False)
        
        # 2. Mesaj Bekle
        print("\n--- Veri Bekleniyor ---")
        p_type, seq, payload = node_b.listen_data()
        print(f"Sunucu B mesaj aldi: {payload.decode()}")
        
        # 3. Yanıt Gönder
        response = b"Selam Sunucu A, guvenli mesajini aldim!"
        node_b.send_data(response)
        
    except Exception as e:
        print(f"Hata olustu: {e}")
    finally:
        node_b.close()

if __name__ == "__main__":
    main()
