from node import Node
from config import PORT_A, PORT_B

def main():
    # Sunucu B: Kendi portu PORT_B, hedef portu PORT_A
    node_b = Node("127.0.0.1", PORT_B, "127.0.0.1", PORT_A)
    
    try:
        print("Sunucu B dinlemede...")
        # Sunucu A'dan mesaj bekle
        data, addr = node_b.listen_raw()
        print(f"Sunucu B mesaj aldı: {data.decode()}")
        
        # Yanıt gönder
        response = b"Selam Sunucu A, mesajini aldim!"
        node_b.send_raw(response)
        
    except KeyboardInterrupt:
        print("\nSunucu B durduruluyor...")
    finally:
        node_b.close()

if __name__ == "__main__":
    main()
