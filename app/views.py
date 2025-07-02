from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify, abort, session
from .models import db, Product, Category, User
import stripe
import random
from flask_login import login_user, logout_user, login_required, current_user
import datetime

main_bp = Blueprint('main', __name__)

@main_bp.app_context_processor
def inject_user():
    return dict(current_user=current_user)

@main_bp.route('/')
def index():
    products = Product.query.all()
    categories = Category.query.filter_by(parent_id=None).all()
    return render_template('index.html', products=products, categories=categories)

@main_bp.route('/product/<int:id>')
def product_detail(id):
    product = Product.query.get(id)
    if not product:
        abort(404)
    images = [product.image_url]
    if hasattr(product, 'gallery_urls') and product.gallery_urls:
        images += [url.strip() for url in product.gallery_urls.split(",") if url.strip()]
    # Benzer ürünler (aynı kategoriden, kendisi hariç, rastgele 10)
    similar_products = []
    if product.category_id:
        similar_products = Product.query.filter(
            Product.category_id == product.category_id,
            Product.id != product.id
        ).order_by(db.func.random()).limit(10).all()
    # Çok satanlar (örnek: id'ye göre azalan, ilk 10)
    best_sellers = Product.query.order_by(Product.id.desc()).limit(10).all()
    # Yeni gelenler (id'ye göre artan, ilk 10)
    new_arrivals = Product.query.order_by(Product.id.asc()).limit(10).all()
    return render_template(
        'product_detail.html',
        product=product,
        images=images,
        similar_products=similar_products,
        best_sellers=best_sellers,
        new_arrivals=new_arrivals
    )

@main_bp.route('/buy/<int:product_id>', methods=['POST'])
def buy_product(product_id):
    product = Product.query.get_or_404(product_id)
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'try',
                'product_data': {
                    'name': product.name,
                },
                'unit_amount': product.price,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('main.payment_success', _external=True),
        cancel_url=url_for('main.payment_cancelled', _external=True),
    )
    return redirect(session.url, code=303)

@main_bp.route('/payment-success')
def payment_success():
    return render_template('payment_success.html')

@main_bp.route('/payment-cancelled')
def payment_cancelled():
    return render_template('payment_cancelled.html')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if User.query.filter_by(email=email).first():
            flash('Bu e-posta ile zaten bir hesap var.', 'danger')
            return redirect(url_for('main.register'))
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Kayıt başarılı! Şimdi giriş yapabilirsiniz.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html')

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Giriş başarılı!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('E-posta veya şifre hatalı.', 'danger')
            return redirect(url_for('main.login'))
    return render_template('login.html')

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Çıkış yapıldı.', 'info')
    return redirect(url_for('main.index'))

@main_bp.route('/favorites')
def favorites():
    return render_template('favorites.html')

@main_bp.route('/cart')
def cart():
    return render_template('cart.html')

@main_bp.route('/search')
def search():
    q = request.args.get('q', '').strip()
    products = []
    if q:
        products = Product.query.filter(Product.name.ilike(f'%{q}%')).all()
    # Her ürünün description'ı None ise boş string yap ve dict'e çevir
    product_dicts = []
    for p in products:
        product_dicts.append({
            'id': p.id,
            'name': p.name,
            'description': p.description or "",
            'price': p.price,
            'image_url': p.image_url
        })
    return render_template('search.html', products=product_dicts, q=q)

@main_bp.route('/category/<string:cat_name>')
def category(cat_name):
    # Sadece ilgili kategoriye ait ürünleri gönder
    cat = Category.query.filter_by(name=cat_name).first()
    products = Product.query.filter_by(category=cat).all() if cat else []
    return render_template('category.html', cat_name=cat_name, products=products)

@main_bp.route('/campaign/<string:camp_name>')
def campaign(camp_name):
    return render_template('campaign.html', camp_name=camp_name)

@main_bp.route('/api/products')
def api_products():
    products = Product.query.all()
    return jsonify([{'id': p.id, 'name': p.name, 'description': p.description, 'price': p.price, 'image_url': p.image_url} for p in products])

@main_bp.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    data = request.get_json()
    cart = data.get('cart', {})
    line_items = []
    for product_id, item in cart.items():
        product = Product.query.get(int(product_id))
        if not product:
            continue
        line_items.append({
            'price_data': {
                'currency': 'try',
                'product_data': {
                    'name': product.name,
                },
                'unit_amount': product.price,
            },
            'quantity': item['qty'],
        })
    if not line_items:
        return jsonify({'error': 'No valid products'}), 400
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=url_for('main.payment_success', _external=True),
        cancel_url=url_for('main.payment_cancelled', _external=True),
    )
    return jsonify({'sessionId': session.id})

@main_bp.route('/erase-all-product-images')
def erase_all_product_images():
    products = Product.query.all()
    for p in products:
        p.image_url = ''
    db.session.commit()
    return 'Tüm ürün görselleri silindi!'

@main_bp.route('/populate-30-products-per-category')
def populate_30_products_per_category():
    # Önce tüm ürünleri ve kategorileri sil
    Product.query.delete()
    Category.query.delete()
    db.session.commit()
    # Kategoriler ve gerçekçi ürün isimleri
    category_products = {
        'Giyim': [
            "Mavi Pamuklu Basic Tişört", "Yüksek Bel Keten Pantolon", "Desenli Şifon Elbise", "Oversize Kapüşonlu Sweatshirt", "Kısa Kollu Polo Yaka Tişört", "Düğmeli Jean Ceket", "V Yaka Triko Kazak", "Kruvaze Blazer Ceket", "Pileli Midi Etek", "Çiçek Desenli Viskon Elbise", "Klasik Siyah Kumaş Pantolon", "Beyaz Askılı Atlet", "Cepli Gri Hırka", "Kare Yaka Kısa Elbise", "Ekose Mini Etek", "Oversize Gömlek", "Kemerli Şort", "Dantel Detaylı Bluz", "Kapitone Mont", "Kolsuz Triko Yelek", "Baskılı Crop Tişört", "Deri Görünümlü Tayt", "Çift Cepli Oduncu Gömlek", "Kruvaze Midi Elbise", "Kapitone Yelek", "Kruvaze Uzun Ceket", "Kısa Kollu Tunik", "Kruvaze Uzun Elbise", "Kemerli Kısa Etek", "Düğmeli Uzun Hırka"
        ],
        'Ayakkabı': [
            "Beyaz Deri Spor Ayakkabı", "Klasik Süet Topuklu Ayakkabı", "Su Geçirmez Trekking Botu", "Günlük Kanvas Sneaker", "Bağcıklı Rugan Oxford", "Hakiki Deri Loafer", "Yüksek Taban Platform Sneaker", "Kışlık Kürklü Bot", "Rahat Tabanlı Sandalet", "Şeffaf Bantlı Topuklu", "Klasik Siyah Babet", "Bağcıklı Deri Bot", "Kauçuk Taban Terlik", "Klasik Erkek Ayakkabı", "Spor Koşu Ayakkabısı", "Klasik Stiletto", "Hakiki Deri Çizme", "Klasik Loafer", "Klasik Espadril", "Klasik Slip-on", "Klasik Sneaker", "Klasik Sandalet", "Klasik Bot", "Klasik Terlik", "Klasik Ayakkabı", "Klasik Çizme", "Klasik Babet", "Klasik Topuklu", "Klasik Spor Ayakkabı", "Klasik Koşu Ayakkabısı"
        ],
        'Aksesuar & Çanta': [
            "Küçük Deri Omuz Çantası", "Altın Kaplama Halka Küpe", "Kanvas Sırt Çantası", "Kare Metal Güneş Gözlüğü", "Deri Kartlık Cüzdan", "Klasik Siyah Kemer", "Renkli Fular", "Minimalist Kolye", "Büyük Hasır Plaj Çantası", "Kapitone El Çantası", "Klasik Deri Cüzdan", "Klasik Sırt Çantası", "Klasik Omuz Çantası", "Klasik El Çantası", "Klasik Bel Çantası", "Klasik Şapka", "Klasik Gözlük", "Klasik Bileklik", "Klasik Kolye", "Klasik Küpe", "Klasik Yüzük", "Klasik Broş", "Klasik Kravat", "Klasik Fular", "Klasik Atkı", "Klasik Eldiven", "Klasik Şemsiye", "Klasik Cüzdan", "Klasik Anahtarlık", "Klasik Çanta"
        ],
        'Ev & İç Giyim': [
            "Pamuklu Pijama Takımı", "Dantelli Saten Gecelik", "Yumuşak Ev Terliği", "Kapitone Yorgan", "Çift Kişilik Nevresim Seti", "Bambu Banyo Havlusu", "Kapitone Yastık", "Kapitone Battaniye", "Kapitone Pike", "Kapitone Çarşaf", "Kapitone Yatak Örtüsü", "Kapitone Yastık Kılıfı", "Kapitone Yorgan Kılıfı", "Kapitone Battaniye Kılıfı", "Kapitone Pike Kılıfı", "Kapitone Çarşaf Kılıfı", "Kapitone Yatak Örtüsü Kılıfı", "Kapitone Yastık Kılıfı", "Kapitone Yorgan Kılıfı", "Kapitone Battaniye Kılıfı", "Kapitone Pike Kılıfı", "Kapitone Çarşaf Kılıfı", "Kapitone Yatak Örtüsü Kılıfı", "Kapitone Yastık Kılıfı", "Kapitone Yorgan Kılıfı", "Kapitone Battaniye Kılıfı", "Kapitone Pike Kılıfı", "Kapitone Çarşaf Kılıfı", "Kapitone Yatak Örtüsü Kılıfı", "Kapitone Yastık Kılıfı"
        ],
        'Kozmetik': [
            "Nemlendirici Yüz Serumu", "Mat Bitişli Ruj - Kırmızı", "C Vitamini Parlatıcı Tonik", "Hacim Veren Maskara", "Doğal Kaş Jeli", "Göz Altı Kapatıcı", "Hafif Yapılı Fondöten", "Güneş Koruyucu SPF 50", "Hyaluronik Asit Ampul", "Köpük Yüz Temizleyici", "Krem Allık", "Sıvı Eyeliner", "Aydınlatıcı Stick", "Kuru Yağ Saç Bakım", "Onarıcı El Kremi", "Klasik Parfüm", "Klasik Deodorant", "Klasik Şampuan", "Klasik Saç Kremi", "Klasik Saç Maskesi", "Klasik Vücut Losyonu", "Klasik El Kremi", "Klasik Yüz Kremi", "Klasik Göz Kremi", "Klasik Dudak Balmı", "Klasik Tırnak Bakım Yağı", "Klasik Makyaj Bazı", "Klasik Makyaj Temizleyici", "Klasik Makyaj Sabitleyici", "Klasik Makyaj Süngeri"
        ],
        'Spor & Outdoor': [
            "Su Geçirmez Koşu Montu", "Yüksek Destekli Spor Sütyeni", "Hafif Koşu Şortu", "Nefes Alabilir Spor Tişört", "Kompakt Yoga Matı", "Kampçı Sırt Çantası", "Klasik Spor Ayakkabı", "Klasik Spor Çanta", "Klasik Spor Şapka", "Klasik Spor Eldiven", "Klasik Spor Atkı", "Klasik Spor Çorap", "Klasik Spor Tayt", "Klasik Spor Şort", "Klasik Spor Tişört", "Klasik Spor Sweatshirt", "Klasik Spor Mont", "Klasik Spor Yelek", "Klasik Spor Ceket", "Klasik Spor Pantolon", "Klasik Spor Eşofman", "Klasik Spor Şort", "Klasik Spor Tayt", "Klasik Spor Tişört", "Klasik Spor Sweatshirt", "Klasik Spor Mont", "Klasik Spor Yelek", "Klasik Spor Ceket", "Klasik Spor Pantolon", "Klasik Spor Eşofman"
        ]
    }
    cat_objs = {}
    for cat in category_products:
        c = Category(name=cat)
        db.session.add(c)
        cat_objs[cat] = c
    db.session.commit()
    for cat, names in category_products.items():
        for i, name in enumerate(names):
            p = Product(
                name=name,
                description=f"{cat} kategorisinden özel ürün.",
                price=29990 + i * 1000,
                image_url=""
            )
            p.category = cat_objs[cat]
            db.session.add(p)
    db.session.commit()
    return 'Her kategoriye 30 gerçekçi isimli ürün eklendi!'

@main_bp.route('/my-orders')
@login_required
def my_orders():
    orders = session.get('orders', [])
    if not isinstance(orders, list):
        orders = []
    return render_template('my_orders.html', orders=orders)

@main_bp.route('/my-profile', methods=['GET', 'POST'])
@login_required
def my_profile():
    info_success = info_error = pass_success = pass_error = None
    if request.method == 'POST':
        # Hangi formdan geldiğini ayırt et
        if 'first_name' in request.form and 'last_name' in request.form:
            # Üyelik bilgileri güncelleme
            first_name = request.form['first_name'].strip()
            last_name = request.form['last_name'].strip()
            if not first_name or not last_name:
                info_error = 'Ad ve soyad boş olamaz.'
            else:
                current_user.first_name = first_name
                current_user.last_name = last_name
                db.session.commit()
                info_success = 'Bilgileriniz başarıyla güncellendi.'
        elif 'current_password' in request.form and 'new_password' in request.form and 'new_password2' in request.form:
            # Şifre güncelleme
            current_password = request.form['current_password']
            new_password = request.form['new_password']
            new_password2 = request.form['new_password2']
            if not current_user.check_password(current_password):
                pass_error = 'Mevcut şifreniz yanlış.'
            elif new_password != new_password2:
                pass_error = 'Yeni şifreler eşleşmiyor.'
            elif len(new_password) < 8 or not any(c.islower() for c in new_password) or not any(c.isupper() for c in new_password) or not any(c.isdigit() for c in new_password):
                pass_error = 'Şifre en az 8 karakter, 1 büyük harf, 1 küçük harf ve rakam içermelidir.'
            else:
                current_user.set_password(new_password)
                db.session.commit()
                try:
                    user = User.query.get(current_user.id)
                    login_user(user)
                    pass_success = 'Şifreniz başarıyla güncellendi.'
                except Exception as e:
                    pass_error = 'Oturum güncellenirken hata oluştu: ' + str(e)
    return render_template('my_profile.html', user=current_user, info_success=info_success, info_error=info_error, pass_success=pass_success, pass_error=pass_error)

@main_bp.route('/sync-cart', methods=['POST'])
@login_required
def sync_cart():
    data = request.get_json()
    cart = data.get('cart', {})
    session['cart'] = cart
    if cart:
        orders = session.get('orders', [])
        items = []
        total = 0
        for pid, item in cart.items():
            items.append({'id': pid, 'name': item['name'], 'qty': item['qty'], 'price': item['price']})
            total += item['qty'] * (item['price'] / 100)
        order = {
            'id': len(orders) + 1,
            'date': datetime.datetime.now().strftime('%Y-%m-%d'),
            'total': total,
            'status': 'Kargoda',
            'items': items
        }
        orders.append(order)
        session['orders'] = orders
        session['cart'] = {}  # Sepeti boşalt
    return jsonify({'ok': True}) 