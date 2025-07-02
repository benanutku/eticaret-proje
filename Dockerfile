# Temel Python imajı
FROM python:3.11-slim

# Çalışma dizini oluştur
WORKDIR /app

# Bağımlılıkları kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala
COPY . .

# Ortam değişkenleri
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Port
EXPOSE 5000

# Uygulamayı başlat (production için gunicorn önerilir)
CMD ["gunicorn", "-b", "0.0.0.0:5000", "run:app"] 