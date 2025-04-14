# coding: UTF-8
"""
Script: Backend/rotues
Création: jojo, le 12/04/2025
"""
from crypt import methods
from tkinter.font import names

from flask import Blueprint, jsonify, request
from flask.globals import request_ctx
from app.extensions import db
from app.products.models import Product
from utils.auth import token_required
# Imports


# Configurations globales
products_bp = Blueprint('products_bp', __name__)

@products_bp.route('/', methods=('GET', 'POST'))
@token_required
def products(current_user):
    if request.method == 'POST':
        if current_user.role != 'admin':
            return jsonify({'message': 'Acesso negado'}), 403

        try:
            data = request.get_json()
            name = data.get('name')
            unit_price = data.get('unit_price')
            stock = data.get('stock')

            if not name or not unit_price or not stock:
                return jsonify({'message': 'Nome, preço unidade e estoque são necessarios.'}), 400

            new_product = Product(name = name, unit_price = unit_price, stock = stock)
            db.session.add(new_product)
            db.session.commit()

            return jsonify({'message': f'Produto {new_product.name} criado com sucesso!'}), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Ocorreu um erro: {str(e)}'}), 500

    elif request.method == 'GET':
        products = Product.query.all()
        return jsonify(
            [{"product_id": p.product_id, "name": p.name, "unit_price": p.unit_price, "stock": p.stock} for p in
             products])
    return jsonify({'message': 'Metodo não permitido'}), 405





# Routes