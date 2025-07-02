# eticaret-proje

Modern Flask tabanlı, Stripe ödeme entegrasyonlu, Docker destekli temel e-ticaret projesi.

## Özellikler
- Flask ile backend
- SQLAlchemy ile ürün modeli
- Stripe ile ödeme entegrasyonu
- Jinja2 ile basit frontend
- Docker ve docker-compose ile kolay kurulum
- Nginx ile statik dosya ve reverse proxy desteği

## Kurulum

### 1. Gerekli Değişkenler
- `STRIPE_PUBLIC_KEY` ve `STRIPE_SECRET_KEY` anahtarlarını alın (https://dashboard.stripe.com/)
- Gerekirse `.env` dosyası oluşturun veya docker-compose ile environment olarak girin.

### 2. Docker ile Çalıştırma
```sh
docker-compose up --build
```
- Uygulama: http://localhost:5000

### 3. Manuel (Geliştirici) Kurulum
```sh
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
export FLASK_APP=run.py
export FLASK_ENV=development
flask run
```

## Klasör Yapısı
```
app/
  __init__.py
  config.py
  models.py
  views.py
  util.py
  static/
    css/
    js/
    img/
  templates/
    index.html
    product_detail.html
    payment_success.html
    payment_cancelled.html
nginx/
  app.conf
Dockerfile
docker-compose.yml
requirements.txt
run.py
README.md
```

## Notlar
- Stripe test anahtarları ile test edebilirsiniz.
- Ürün eklemek için veritabanına manuel kayıt ekleyin veya Flask shell kullanın.
- Geliştirme için kodları dilediğiniz gibi genişletebilirsiniz. 