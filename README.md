# 🛒 eticaret-proje

Modern, kullanıcı dostu ve Docker destekli bir **Flask e-ticaret** uygulaması.  
Stripe ile güvenli ödeme, dinamik ürün filtreleme, modern arayüz ve kolay kurulum!

---

## 🚀 Özellikler

- **Flask** tabanlı hızlı backend
- **SQLAlchemy** ile ürün, kategori ve kullanıcı yönetimi
- **Stripe** ile gerçekçi ödeme entegrasyonu (test modunda)
- **Jinja2** ile modern ve responsive frontend
- **Kapsamlı ürün filtreleme** (beden, numara, marka, fiyat, sıralama)
- **Kullanıcı işlemleri:** Kayıt, giriş, profil, şifre güncelleme
- **Siparişlerim:** Başarılı ödeme sonrası sipariş geçmişi
- **Favoriler ve Sepet:** LocalStorage ile kalıcı favori ve sepet
- **Docker & docker-compose** ile tek komutla kurulum
- **Nginx** ile statik dosya ve reverse proxy desteği

---

## 🛠️ Kurulum

### 1. Stripe API Anahtarları
- [Stripe Dashboard](https://dashboard.stripe.com/) üzerinden **test** anahtarlarını alın.
- Anahtarları `.env` dosyasına veya `docker-compose.yml`'ye ekleyin:
  ```
  STRIPE_PUBLIC_KEY=pk_test_...
  STRIPE_SECRET_KEY=sk_test_...
  ```

### 2. Docker ile Çalıştırma (Önerilen)
```sh
docker-compose up --build
```
- Uygulama: [http://localhost:5000](http://localhost:5000)

### 3. Geliştirici Modu (Manuel)
```sh
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt

export FLASK_APP=run.py
export FLASK_ENV=development
flask run
```

---

## 📁 Klasör Yapısı
eticaret-proje/
│
├── app/
│ ├── init.py
│ ├── config.py
│ ├── models.py
│ ├── views.py
│ ├── util.py
│ ├── static/
│ └── templates/
├── migrations/
├── nginx/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── run.py
└── README.md

---

## 👤 Demo Kullanıcılar

- Kayıt olarak kendi hesabınızı oluşturabilirsiniz.
- Giriş yaptıktan sonra sipariş, favori, profil ve sepet işlemlerini deneyebilirsiniz.

---

## 💡 Notlar

- Stripe test anahtarları ile gerçek ödeme alınmaz, demo amaçlıdır.
- Ürünler ve kategoriler otomatik olarak eklenir, isterseniz Flask shell ile yeni ürün ekleyebilirsiniz.
- Siparişlerim ekranı, her başarılı ödeme sonrası güncellenir.
- Modern filtreleme ve sıralama ile kullanıcı deneyimi üst düzeydedir.

---

## 🧑‍💻 Geliştiriciye Notlar

- Kodlarınızı dilediğiniz gibi genişletebilir, yeni özellikler ekleyebilirsiniz.
- Herhangi bir hata veya öneri için issue açabilirsiniz.

---

**Başarıyla alışveriş yapın, modern e-ticaret deneyimini yaşayın!**  
⭐️ Projeyi beğendiyseniz GitHub’da yıldızlamayı unutmayın!