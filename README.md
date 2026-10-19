# iOS AI Agent (iPhone Otonom Kontrol Ajanı)

Bu repo, iPhone'unuzu tıpkı bir insanın kullandığı gibi **otonom olarak ekrana bakıp tıklayarak, yazarak ve kaydırarak** kontrol eden yapay zeka ajanını içerir.

> **Önemli:** Ağır Xcode kurulumuna gerek yoktur. Eski/düşük donanımlı bir Mac ve Sideloadly yeterlidir.

---

## 🛠️ Adım Adım Kurulum Rehberi

### Adım 1: iPhone'da Geliştirici Modunu Aç
1. iPhone'da **Ayarlar > Gizlilik ve Güvenlik > Geliştirici Modu (Developer Mode)** bölümüne girin.
2. Geliştirici Modunu **Açık** yapın ve telefonu yeniden başlatın.

---

### Adım 2: WebDriverAgent (WDA) IPA'sını Telefona Yükle (Xcode'suz)
1. Mac'inize **Sideloadly** indirin (~50 MB): [https://sideloadly.io](https://sideloadly.io)
2. Hazır `WebDriverAgentRunner.ipa` dosyasını indirin:
   * [Appium WebDriverAgent Releases](https://github.com/appium/WebDriverAgent/releases) üzerinden son sürüm `.ipa` dosyasını alın.
3. iPhone'unuzu kabloyla Mac'e takın.
4. Sideloadly'yi açın:
   * İndirdiğiniz `.ipa` dosyasını pencereye sürükleyin.
   * Apple ID bilginizi girin (ücretsiz kişisel hesap yeterlidir).
   * **Start** butonuna basın. Uygulama birkaç dakika içinde iPhone'a yüklenir.
5. iPhone'da:
   * **Ayarlar > Genel > VPN ve Aygıt Yönetimi** kısmına girip Apple ID'nize tıklayarak **Güven** deyin.

---

### Adım 3: Telefonu Mac'e Bağla & Portu Aç
Telefondaki `WebDriverAgentRunner` simgesine dokunup açın (siyah veya boş bir ekran gelip arka planda çalışır).

USB üzerinden bağlantıyı Mac'e köprülemek için terminalde `tidevice` veya `iproxy` kullanabilirsiniz:
```bash
# tidevice kurun (Xcode gerektirmez)
pip install tidevice

# WDA portunu Mac'e bağlayın (arka planda çalışsın)
tidevice wdaproxy -B com.facebook.WebDriverAgentRunner.xctrunner -p 8100
```
*(Artık iPhone `http://localhost:8100` üzerinden kontrol edilebilir).*

---

### Adım 4: Repoyu Hazırla

1. Bağımlılıkları yükleyin:
   ```bash
   cd /Users/brkn/ios-ai-agent
   pip install -r requirements.txt
   ```

2. `.env` dosyasını oluşturun:
   ```bash
   cp .env.example .env
   ```
   `.env` dosyasını açıp API anahtarınızı girin:
   ```env
   AI_PROVIDER=gemini
   GEMINI_API_KEY=AIzaSy...
   ```

3. Bağlantıyı test edin:
   ```bash
   python3 main.py --test
   ```
   Ekranda `[✅] Bağlantı başarılı!` yazıyorsa sistem hazırdır.

---

## 🚀 Kullanım

Ajanı terminalden çalıştırmak için istediğiniz görevi yazın:

```bash
# Örnek 1: Mesaj gönderme
python3 main.py "WhatsApp'ı aç, Mehmet'e 'Saat 5'te oradayım' yaz ve gönder"

# Örnek 2: Ayar kontrolü
python3 main.py "Ayarlar uygulamasını aç ve Pil Sağlığını kontrol et"

# Örnek 3: Safari'de gezinme
python3 main.py "Safari'yi aç, google.com'a git ve hava durumunu ara"
```

---

## 🧩 Mimari

```
[ Kullanıcı Emri ]
       │
       ▼
[ IOSAgent (agent.py) ] ◄──────┐
       │ (Ekran Görüntüsü)     │
       ▼                       │
[ VisionBrain (brain.py) ]     │ (Görsel Döngü)
  (Gemini / OpenAI Vision)     │
       │ (Karar: Tap, Type)    │
       ▼                       │
[ WDADriver (wda_driver.py) ] ──┘
       │ (HTTP REST: /wda/tap)
       ▼
[ iPhone Ekranı (WDA) ] (Fiziksel Tıklama ve Yazma)
```
