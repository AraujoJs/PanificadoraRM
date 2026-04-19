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

    # Filtros customizados
    app.jinja_env.filters['enumerate'] = enumerate
    
    def format_currency(value):
        if value is None:
            return "0,00"
        try:
            val = float(value)
            # Retorna no formato 1.234,56
            formatted = f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            return formatted
        except (ValueError, TypeError):
            return "0,00"
    app.jinja_env.filters['currency'] = format_currency

    from app.auth.routes import auth
    from app.auth.routes import usuario
    from app.products.routes import produtos
    from app.sales.routes import vendas
    from app.sales.routes import item_venda
    from app.home.routes import inicio
    from app.suppliers.routes import fornecedores
    from app.stock_entries.routes import entradas
    from app.bills.routes import contas_pagar

    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(usuario, url_prefix="/api/v1/usuarios")

    app.register_blueprint(produtos, url_prefix='/api/v1/produtos')
    app.register_blueprint(vendas, url_prefix='/api/v1/vendas')
    app.register_blueprint(item_venda, url_prefix='/api/v1/item-venda')
    app.register_blueprint(fornecedores, url_prefix='/api/v1/fornecedores')
    app.register_blueprint(entradas, url_prefix='/api/v1/entradas-estoque')
    app.register_blueprint(contas_pagar, url_prefix='/api/v1/contas-pagar')

    app.register_blueprint(inicio, url_prefix='/inicio')
    return app
