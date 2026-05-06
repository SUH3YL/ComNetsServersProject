# Custom Network Protocol Project

Bu proje, Python kullanarak UDP üzerinden iki sunucu arasında güvenilir bir iletişim sağlayan özel bir uygulama katmanı protokolü uygulamasıdır.

## Özellikler

- **Özel Paketleme:** `struct` kütüphanesi ile ikili (binary) paket yapısı.
- **Hata Kontrolü:** `zlib.crc32` ile Checksum doğrulaması.
- **Güvenilir Bağlantı:** 3-way handshake (SYN, SYN-ACK, ACK) mekanizması.
- **Paket Kaybı Telafisi:** Timeout ve Retransmission (Stop-and-Wait ARQ).
- **Hata Simülasyonu:** Debug modu ile rastgele paket bozma (Bit-flip).
- **Full-Duplex İletişim:** `threading` ile anlık mesajlaşma (Chat).
- **Renkli Loglama:** `colorama` ile terminalde görsel takip.

## Kurulum

1. Depoyu klonlayın.
2. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install colorama
   ```

## Çalıştırma

Proje iki sunucunun (A ve B) karşılıklı çalışmasını gerektirir.

1. **Sunucu B'yi Başlatın (Dinleyici):**
   ```bash
   python main_b.py
   ```

2. **Sunucu A'yı Başlatın (Başlatıcı):**
   ```bash
   python main_a.py
   ```

## Yapılandırma

`config.py` dosyası üzerinden şu ayarları değiştirebilirsiniz:
- `DEBUG_MODE`: Hata simülasyonunu açar/kapatır.
- `CORRUPTION_CHANCE`: Paketlerin bozulma ihtimalini belirler.
- `TIMEOUT`: Yanıt bekleme süresi.
- `MAX_RETRIES`: Maksimum tekrar deneme sayısı.

## Paket Yapısı

| Alan | Boyut | Tip |
| :--- | :--- | :--- |
| Packet Type | 1 Byte | Integer |
| Sequence Number | 4 Byte | Integer |
| Checksum | 4 Byte | Integer |
| Payload Length | 2 Byte | Integer |
| Payload | Dinamik | Bytes |
