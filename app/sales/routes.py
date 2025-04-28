# coding: UTF-8
"""
Script: Backend/routes
Création: jojo, le 12/04/2025
"""
import uuid
from datetime import datetime

import flask
from flask import session, jsonify, request

from app.auth.routes import get_user_name_by_id
from app.extensions import db
from app.products.models import Product
from app.sales.models import Sale, SaleItem
from utils.auth import token_required

vendas = flask.Blueprint('sales_bp', __name__)
item_venda = flask.Blueprint('sale_items_bp', __name__)


@item_venda.route('/<venda_id>')
@token_required
def sale_items(current_user, venda_id):
    sale_items = SaleItem.query.filter_by(sale_id=venda_id).all()
    if len(sale_items) == 0:
        return jsonify({"message": f"The sale {venda_id} has no items."}), 201
    return jsonify([{"item_id": s.item_id, "quantity": s.quantity, "subtotal": s.subtotal, "user_id": s.user_id,
                     "sale_id": s.sale_id, "product_id": s.product_id} for s in sale_items])


@vendas.route('/', methods=['GET'])
@token_required
def sales(current_user):
    if current_user.role == 'admin':
        sales = Sale.query.all()
        return get_sales_json(sales)
    else:
        session_user = session.get("user_id")
        if current_user.user_id == session_user:
            sales = Sale.query.filter_by(user_id=current_user.user_id).all()
            return get_sales_json(sales)
        return jsonify({'message': 'You need to login before.'}), 405


@vendas.route('/', methods=['POST'])
@token_required
def add_sale(current_user):
    data = request.get_json()
    sale_id = data.get('sale_id')
    payment_method = data.get('payment_method')
    user_id = data.get('user_id')

    itens = data.get('itens')

    sale_datetime = datetime.now()

    if Sale.query.filter_by(sale_id=sale_id).first():
        return jsonify({"message": "Venda já existe."}), 409

    sale = Sale(
        sale_id=sale_id,
        sale_datetime=sale_datetime,
        payment_method=payment_method,
        total=0.0,
        user_id=user_id
    )
    sale_itens = []

    for item in itens:
        product = Product.query.filter_by(product_id=item["product_id"]).first()

        if product.stock < item["quantity"]:
            return jsonify(
                {"message": "Stock insuficiente.", "product_id": product.product_id, "stock": product.stock}), 422

        item_quantity = item["quantity"]
        item_price = product.unit_price
        item_subtotal = float(item_quantity * item_price)

        product.stock -= item_quantity
        sale.total += item_subtotal

        sale_itens.append(
            SaleItem(
                quantity=item_quantity,
                subtotal=item_subtotal,
                user_id=user_id,
                sale_id=sale_id,
                product_id=product.product_id
            ))

    try:
        db.session.add(sale)
        db.session.add_all(sale_itens)
        db.session.commit()
        return '', 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Erro ao inserir venda: {str(e)}"}), 500


@vendas.route('/', methods=['DELETE'])
@token_required
def delete_sale(current_user):
    sale_id = request.get_json().get('sale_id')
    sale = Sale.query.filter_by(sale_id=sale_id).first()
    if not sale:
        return jsonify({"message": "Venda não existe."}), 404

    sale_itens = SaleItem.query.filter_by(sale_id=sale_id).all()

    try:

        for item in sale_itens:
            db.session.delete(item)
        db.session.delete(sale)
        db.session.commit()
        return '', 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Erro ao deletar venda: {str(e)}"}), 500


@vendas.route('/usuario/<usuario_id>')
@token_required
def sales_user(current_user, usuario_id):
    sales = []
    if current_user.role == "admin":
        sales = Sale.query.filter_by(user_id=uuid.UUID(usuario_id)).all()
        if len(sales) == 0:
            return jsonify({"message": f"This user {get_user_name_by_id(usuario_id)} has no sales yet."}), 201
    else:
        sales = Sale.query.filter_by(user_id=current_user.user_id)
        if sales is None:
            return jsonify({"message": f"This user {current_user.name} has no sales yet."}), 201

    return [{"sale_id": s.sale_id,
             "sale_datetime": s.sale_datetime,
             "total": s.total,
             "payment_method": s.payment_method,
             "user_id": s.user_id} for s in sales]


@vendas.route('/item-venda/<venda_id>')
def itens_sale(venda_id):
    itens = SaleItem.query.filter_by(item_id=uuid.UUID(venda_id))

    return get_itens_json(itens)


def get_itens_json(itens):
    return flask.jsonify(
        [{"item_id": si.item_id, "quantity": si.quantity, "subtotal": si.subtotal, "user_id": si.user_id,
          "sale_id": si.sale_id, "product_id": si.product_id}
         for si in itens])


def get_sales_json(sales):
    return flask.jsonify(
        [{"sale_id": s.sale_id, "sale_datetime": s.sale_datetime, "total": s.total, "payment_method": s.payment_method,
          "user_id": s.user_id}
         for s in sales])
