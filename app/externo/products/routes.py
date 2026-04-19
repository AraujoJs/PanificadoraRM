# coding: UTF-8
"""
Script: Backend/rotues
Création: jojo, le 12/04/2025
"""

from flask import Blueprint, jsonify, request

from app.extensions import db
from app.externo.products.models import Product
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
        return jsonify({"message": "Nome, preço unitário e estoque são obrigatórios."}), 400

    try:
        new_product = Product(name=name, unit_price=unit_price, stock=stock)
        db.session.add(new_product)
        db.session.commit()
        return jsonify({"message": f"Produto {new_product.name} criado com sucesso!"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Ocorreu um erro: {str(e)}"}), 500


@produtos.route('/desativar', methods=['PATCH'])
@token_required
def deactivate_product(current_user):
    if current_user.role != "admin":
        return jsonify({"message": "Acesso negado."}), 403

    product_id = request.get_json().get("product_id")
    if not product_id:
        return jsonify({"message": "product_id é obrigatório."}), 400

    product = Product.query.filter_by(product_id=product_id).first()
    if not product:
        return jsonify({"message": f"Produto {product_id} não encontrado."}), 404

    product.is_active = False
    try:
        db.session.commit()
        return '', 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Ocorreu um erro: {str(e)}"}), 500



@produtos.route('/ativar', methods=['PATCH'])
@token_required
def activate_product(current_user):
    if current_user.role != "admin":
        return jsonify({"message": "Acesso negado."}), 403

    product_id = request.get_json().get("product_id")
    if not product_id:
        return jsonify({"message": "product_id é obrigatório."}), 400

    product = Product.query.filter_by(product_id=product_id).first()
    if not product:
        return jsonify({"message": f"Produto {product_id} não encontrado."}), 404

    product.is_active = True
    try:
        db.session.commit()
        return '', 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Ocorreu um erro: {str(e)}"}), 500

@produtos.route('/estoque', methods=['PATCH'])
@token_required
def add_stock(current_user):
    quantity = request.get_json().get("quantity")
    product_id = request.get_json().get("product_id")

    if quantity and product_id:
        product = Product.query.filter_by(product_id=product_id).first()
        product.stock = quantity
        try:
            db.session.commit()
            return '', 200
        except Exception as e:
            return jsonify({"message", f"Erro ao atualizar estoque: {str(e)}"}), 500
    else:
        return jsonify({"message": "Quantity e product_id são obrigatorios."})