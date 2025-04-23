# coding: UTF-8
"""
Script: Backend/routes
Création: jojo, le 12/04/2025
"""
import uuid

import flask
from flask import session, jsonify

from app.sales.models import Sale, SaleItem
from app.auth.routes import get_user_name_by_id
from utils.auth import token_required

sales_bp = flask.Blueprint('sales_bp', __name__)
sale_items_bp = flask.Blueprint('sale_items_bp', __name__)

@sale_items_bp.route('/<sale_id>')
@token_required
def sale_items(current_user, sale_id):
    sale_items = SaleItem.query.filter_by(sale_id=sale_id).all()
    if len(sale_items) == 0:
        return jsonify({"message": f"The sale {sale_id} has no items."}), 201
    return jsonify([{"item_id": s.item_id, "quantity": s.quantity, "subtotal": s.subtotal, "user_id": s.user_id,
                     "sale_id": s.sale_id, "product_id": s.product_id} for s in sale_items])


@sales_bp.route('/', methods=('GET', 'POST'))
@token_required
def sales(current_user):
    if flask.request.method == 'POST':
        pass
    if current_user.role == 'admin':
        sales = Sale.query.all()
        return get_sales_json(sales)
    else:
        session_user = session.get("user_id")
        if current_user.user_id == session_user:
            sales = Sale.query.filter_by(user_id=current_user.user_id).all()
            return get_sales_json(sales)
        return jsonify({'message': 'You need to login before.'}), 405

@sales_bp.route('/user/<user_id>')
@token_required
def sales_user(current_user, user_id):
    sales = []
    if current_user.role == "admin":
        sales = Sale.query.filter_by(user_id=uuid.UUID(user_id)).all()
        if len(sales) == 0:
            return jsonify({"message": f"This user {get_user_name_by_id(user_id)} has no sales yet."}), 201
    else:
        sales = Sale.query.filter_by(user_id=current_user.user_id)
        if sales is None:
            return jsonify({"message": f"This user {current_user.name} has no sales yet."}), 201

    return [{"sale_id": s.sale_id,
                 "sale_datetime": s.sale_datetime,
                 "total": s.total,
                 "payment_method": s.payment_method,
                 "user_id": s.user_id} for s in sales]

@sales_bp.route('/itens/<sale_id>')
def itens_sale(sale_id):
    itens = SaleItem.query.filter_by(item_id=uuid.UUID(sale_id))

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