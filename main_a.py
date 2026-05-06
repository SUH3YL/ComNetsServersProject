from node import Node
from config import PORT_A, PORT_B

def main():
    # Sunucu A: Kendi portu PORT_A, hedef portu PORT_B
    node_a = Node("127.0.0.1", PORT_A, "127.0.0.1", PORT_B)
    
    try:
        # Sunucu B'ye test mesajı gönder
        message = b"Merhaba Sunucu B, ben Sunucu A!"
        node_a.send_raw(message)
        
        # Yanıt bekle
        print("Yanıt bekleniyor...")
        data, addr = node_a.listen_raw()
        print(f"Sunucu A yanıt aldı: {data.decode()}")
        
    except KeyboardInterrupt:
        print("\nSunucu A durduruluyor...")
    finally:
        node_a.close()

if __name__ == "__main__":
    main()
