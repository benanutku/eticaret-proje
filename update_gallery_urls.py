import sqlite3

# Veritabanı dosyasının yolu
db_path = "instance/db.sqlite3"

# Ürün adı ve gallery_urls eşleşmeleri
gallery_updates = {
    "Kruvaze Uzun Elbise": (
        "https://static.ticimax.cloud/cdn-cgi/image/width=1920,quality=95/3176/uploads/urunresimleri/buyuk/kruvaze-desenli-uzun-elbise-haki-2f54e2.jpg,"
        "https://static.ticimax.cloud/cdn-cgi/image/width=1920,quality=95/3176/uploads/urunresimleri/buyuk/kruvaze-desenli-uzun-elbise-haki-d-bf37.jpg"
    ),
    "Kemerli Kısa Etek": (
        "https://cdn.swist.com.tr/siyah-full-pileli-kemerli-astar-sortlu-kadin-mini-etek-etek-swist-41698-35-B.jpg,"
        "https://cdn.swist.com.tr/siyah-full-pileli-kemerli-astar-sortlu-kadin-mini-etek-etek-swist-41697-35-B.jpg"
    ),
}

conn = sqlite3.connect(db_path)
cur = conn.cursor()

for product_name, gallery_urls in gallery_updates.items():
    cur.execute("UPDATE product SET gallery_urls = ? WHERE name = ?", (gallery_urls, product_name))

conn.commit()
conn.close()
print("Gallery URLs başarıyla güncellendi.")