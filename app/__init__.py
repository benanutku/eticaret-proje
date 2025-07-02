from flask import Flask
from .config import Config
from .models import db
from flask_migrate import Migrate
from flask_login import LoginManager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate = Migrate(app, db)

    login_manager = LoginManager()
    login_manager.login_view = 'main.login'
    login_manager.init_app(app)

    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .views import main_bp
    app.register_blueprint(main_bp)

    import stripe
    stripe.api_key = app.config['STRIPE_SECRET_KEY']

    return app 