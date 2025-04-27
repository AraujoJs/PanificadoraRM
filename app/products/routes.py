# coding: UTF-8
"""
Script: Backend/rotues
Création: jojo, le 12/04/2025
"""

from flask import Blueprint, jsonify, request

from app.extensions import db
from app.products.models import Product
from utils.auth import token_required

# Imports


# Configurations globales
produtos = Blueprint('products_bp', __name__)


@produtos.route('/', methods=['GET'])
@token_required
def products(current_user):
    all_products = Product.query.all()
    products_list = [
        {
            "product_id": p.product_id,
            "name": p.name,
            "unit_price": p.unit_price,
            "stock": p.stock
        } for p in all_products
    ]
    return jsonify(products_list)


@produtos.route('/', methods=['POST'])
@token_required
def add_product(current_user):
    if current_user.role != 'admin':
        return jsonify({'message': 'Acesso negado'}), 403

    data = request.get_json() or {}
    name = data.get('name')
    unit_price = data.get('unit_price')
    stock = data.get('stock')

    if not all([name, unit_price, stock]):
        return jsonify({'message': 'Nome, preço unitário e estoque são obrigatórios.'}), 400

    try:
        new_product = Product(name=name, unit_price=unit_price, stock=stock)
        db.session.add(new_product)
        db.session.commit()
        return jsonify({'message': f'Produto {new_product.name} criado com sucesso!'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Ocorreu um erro: {str(e)}'}), 500


