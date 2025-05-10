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

SECRET_KEY = os.getenv("SECRET_KEY")

def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY
    app.config.from_pyfile(os.path.join(os.path.dirname(__file__), 'config.py'))
    db.init_app(app)

    from app.externo.auth.routes import auth
    from app.externo.auth.routes import usuario
    from app.externo.products.routes import produtos
    from app.externo.sales.routes import vendas
    from app.externo.sales.routes import item_venda
    from app.externo.home.routes import inicio



    from app.interno.rotas import interno


    # INTERNO
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(usuario, url_prefix="/api/v1/usuarios")

    app.register_blueprint(produtos, url_prefix='/api/v1/produtos')
    app.register_blueprint(vendas, url_prefix='/api/v1/vendas')
    app.register_blueprint(item_venda, url_prefix='/api/v1/item-venda')

    app.register_blueprint(inicio, url_prefix='/inicio')
    ###
    # Externo
    app.register_blueprint(interno, url_prefix='/interno')
    return app