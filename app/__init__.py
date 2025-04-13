# coding: UTF-8
"""
Script: PanificadoraRM/__init__
Création: jojo, le 11/04/2025
"""
from flask import Flask
from dotenv import load_dotenv
from app.extensions import db
import os

# Carrega variáveis do arquivo .env
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile(os.path.join(os.path.dirname(__file__), 'config.py'))

    db.init_app(app)

    from app.auth.routes import auth
    from app.produtos.routes import produtos_bp
    app.register_blueprint(auth)
    app.register_blueprint(produtos_bp, url_prefix='/api/v1/products')

    return app