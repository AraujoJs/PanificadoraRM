# coding: UTF-8
"""
Script: PanificadoraRM/__init__
Création: jojo, le 11/04/2025
"""
from flask import Flask, session
from dotenv import load_dotenv
from app.extensions import db
import os

# Carrega variáveis do arquivo .env
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY
    app.config.from_pyfile(os.path.join(os.path.dirname(__file__), 'config.py'))
    db.init_app(app)

    from app.auth.routes import auth_bp
    from app.auth.routes import users_bp
    from app.products.routes import products_bp
    from app.sales.routes import sales_bp
    from app.sales.routes import sale_items_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(users_bp, url_prefix="/api/v1/users")

    app.register_blueprint(products_bp, url_prefix='/api/v1/products')
    app.register_blueprint(sales_bp, url_prefix='/api/v1/sales')
    app.register_blueprint(sale_items_bp, url_prefix='/api/v1/sale_items')

    return app