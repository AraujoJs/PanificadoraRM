# coding: UTF-8
"""
Script: Backend/routes
Création: jojo, le 12/04/2025
"""
import uuid

import flask
from app.sales.models import Sale, SaleItem

sales_bp = flask.Blueprint('sales_bp', __name__)

@sales_bp.route('/', methods=('GET', 'POST'))
def sales():
    if flask.request.method == 'POST':
        pass

    sales = Sale.query.all()
    return flask.jsonify(
        [{"sale_id": s.sale_id, "sale_datetime": s.sale_datetime, "total": s.total, "payment_method": s.payment_method, "user_id": s.user_id}
         for s in sales])

@sales_bp.route('/<user_id>')
def sales_user(user_id):
    sales = SaleItem.query.filter_by(user_id=uuid.UUID(user_id))

    return flask.jsonify(
        [{"id": item.id,
          "quantity": item.quantity,
          "subtotal": item.subtotal,
          "user_id": item.user_id,
          "sale_id": item.sale_id,
          "product_id": item.product_id
          } for item in sales])
