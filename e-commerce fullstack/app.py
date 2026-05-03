from flask import Flask
from flask_session import Session
from database.db import init_db
from routes.auth import auth_bp
from routes.products import products_bp
from routes.cart import cart_bp
from routes.orders import orders_bp
from routes.wishlist import wishlist_bp
from routes.admin import admin_bp
import os

def create_app():
    app = Flask(__name__)

    # Secret key for sessions
    app.secret_key = os.environ.get('SECRET_KEY', 'flipkart-clone-secret-key-2024')
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(wishlist_bp)
    app.register_blueprint(admin_bp)

    # Initialize DB tables on startup
    with app.app_context():
        init_db()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
