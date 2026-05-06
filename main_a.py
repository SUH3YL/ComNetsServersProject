from node import Node
from config import PORT_A, PORT_B

def main():
    # Sunucu A: Kendi portu PORT_A, hedef portu PORT_B
    node_a = Node("127.0.0.1", PORT_A, "127.0.0.1", PORT_B)
    
    try:
        # 1. Bağlantı Kur (Handshake Başlatıcı)
        print("\n--- Bağlantı Kuruluyor ---")
        node_a.establish_connection(is_initiator=True)
        
        # 2. Veri Gönder
        print("\n--- Veri Gönderimi ---")
        message = b"Merhaba Sunucu B, bu guvenli bir protokoldur."
        node_a.send_data(message)
        
        # 3. Yanıt Bekle
        p_type, seq, payload = node_a.listen_data()
        print(f"Sunucu A yanit aldi: {payload.decode()}")
        
    except Exception as e:
        print(f"Hata oluştu: {e}")
    finally:
        node_a.close()

if __name__ == "__main__":
    main()
