# 🌐 Özel Protokol Bağlantı ve Sorun Giderme Rehberi

Bu rehber, iki sunucu (Node A ve Node B) arasında güvenli ve görsel bir iletişim kurmanızı sağlayacaktır.

## **Bölüm 1: Adım Adım Bağlantı Kurulumu**

Sistemi çalıştırmak için iki ayrı terminal ve iki ayrı tarayıcı sekmesine ihtiyacınız var.

### **1. Uygulamayı Başlatın**
Terminalinize şu komutu yazın ve çalıştırın:
```powershell
python -m streamlit run ui_app.py
```
*Tarayıcınızda bir sayfa açılacaktır. Bu sayfanın linkini (örn: `http://localhost:8501`) kopyalayıp yan sekmede bir kez daha açın.*

### **2. Sunucu B'yi Hazırlayın (Dinleyici/Passive)**
İlk sekmenize gidin ve şu ayarları yapın:
- **Kendi Port:** `5000`
- **Hedef Port:** `5001`
- **Bağlantıyı Ben Başlatayım:** ❌ (İşaretlemeyin)
- **Buton:** `🔌 Bağlantıyı Başlat` butonuna basın.
- **Beklenen Sonuç:** Loglarda `Node başlatıldı: ('127.0.0.1', 5000) | Durum: LISTEN` yazısını görmelisiniz.

### **3. Sunucu A'yi Hazırlayın (Başlatıcı/Active)**
İkinci sekmenize gidin ve şu ayarları yapın:
- **Kendi Port:** `5001`
- **Hedef Port:** `5000`
- **Bağlantıyı Ben Başlatayım:** ✅ (İşaretleyin - Kırmızı tik olmalı)
- **Buton:** `🔌 Bağlantıyı Başlat` butonuna basın.

### **4. Bağlantı Onayı**
Her iki sekmenin log panelinde pembe renkli **"Bağlantı Kuruldu! Durum: ESTABLISHED"** yazısını gördüğünüzde işlem tamamdır! Artık mesaj yazıp gönderebilirsiniz.

---

## **Bölüm 2: Karşılaşılabilecek Hatalar ve Çözümleri**

### **Hata 1: "WinError 10048 - Adres zaten kullanımda"**
**Neden:** Port (5000 veya 5001) başka bir program veya önceki denemenizden kalan bir Python süreci tarafından işgal ediliyor.
**Çözüm:**
1.  Terminali kapatıp açın veya şu komutu çalıştırarak tüm Python süreçlerini sonlandırın:
    ```powershell
    taskkill /F /IM python.exe
    ```
2.  Hala düzelmezse port numaralarını `6000` ve `6001` olarak değiştirip deneyin.

### **Hata 2: "Önce bağlantı kurulmalı!" Uyarısı**
**Neden:** "Gönder" butonuna bastınız ama durum henüz `ESTABLISHED` değil (Handshake tamamlanmadı).
**Çözüm:**
1.  Her iki sekmede de `🛑 Bağlantıyı Kes` butonuna basın.
2.  Önce **Dinleyici (Tik işareti olmayan)** tarafı başlatın.
3.  Ardından **Başlatıcı (Tik işareti olan)** tarafı başlatın.
4.  Loglarda "Bağlantı Kuruldu" yazısını bekleyin.

### **Hata 3: Mesajlar Karşıya Gitmiyor / Loglar Akmıyor**
**Neden:** Portlar çapraz (mirror) eşleşmemiş olabilir.
**Çözüm:** Ayarları şu tabloya göre kontrol edin:
| Ayar | Sekme 1 | Sekme 2 |
| :--- | :--- | :--- |
| Kendi Port | 5000 | 5001 |
| Hedef Port | 5001 | 5000 |
| SYN Gönder | Kapalı (False) | Açık (True) |

### **Hata 4: "Streamlit not recognized" Hatası**
**Neden:** Streamlit sistem yoluna (PATH) eklenmemiş.
**Çözüm:** Komutu her zaman `python -m streamlit run ui_app.py` şeklinde Python modülü olarak çalıştırın.

---

## **Bölüm 3: İpuçları**
- **Hata Modu:** Bağlantı kurulduktan sonra "Hata Modu"nu açarsanız, sistemin bozuk paketleri nasıl reddedip tekrar istediğini (Retransmission) loglardan canlı izleyebilirsiniz.
- **Temiz Başlangıç:** Bir şeyler ters giderse her zaman sekmeleri yenileyin (F5) ve `taskkill` komutunu kullanın.
