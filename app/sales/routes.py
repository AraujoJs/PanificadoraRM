# coding: UTF-8
"""
Script: PanificadoraRM/sales/routes
"""
import uuid

import flask
from flask import session, jsonify, request

from app.extensions import db
from app.products.models import Product
from app.sales.models import Sale, SaleItem
from app.auth.routes import get_user_name_by_id
from utils.auth import token_required

vendas = flask.Blueprint('sales_bp', __name__)
item_venda = flask.Blueprint('sale_items_bp', __name__)


@item_venda.route('/<venda_id>')
@token_required
def sale_items(current_user, venda_id):
    items = SaleItem.query.filter_by(sale_id=venda_id).all()
    if not items:
        return jsonify({"message": f"A venda {venda_id} não possui itens."}), 200
    return jsonify([{
        "item_id": s.item_id,
        "quantity": s.quantity,
        "subtotal": float(s.subtotal),
        "sale_id": str(s.sale_id),
        "product_id": str(s.product_id)
    } for s in items])


@vendas.route('/', methods=['GET', 'POST'])
@token_required
def sales(current_user):
    if request.method == 'POST':
        data = request.get_json() or {}
        payment_method = data.get('payment_method')
        items_data = data.get('items', [])

        if not payment_method:
            return jsonify({'message': 'Método de pagamento é obrigatório.'}), 400
        if not items_data:
            return jsonify({'message': 'A venda deve ter pelo menos um item.'}), 400

        # Validar e buscar todos os produtos antes de persistir qualquer coisa
        resolved_items = []
        for entry in items_data:
            product_id_str = entry.get('product_id')
            quantity = entry.get('quantity', 0)

            if not product_id_str or quantity <= 0:
                return jsonify({'message': 'Cada item deve ter product_id e quantity válidos.'}), 400

            try:
                product_id = uuid.UUID(str(product_id_str))
            except ValueError:
                return jsonify({'message': f'product_id inválido: {product_id_str}'}), 400

            product = Product.query.filter_by(product_id=product_id).first()
            if not product:
                return jsonify({'message': f'Produto {product_id_str} não encontrado.'}), 404
            if product.stock < quantity:
                return jsonify({
                    'message': f'Estoque insuficiente para "{product.name}". '
                               f'Disponível: {product.stock}, solicitado: {quantity}.'
                }), 400

            resolved_items.append((product, quantity))


        # Tudo ok — criar a venda e os itens numa transação única
        try:
            sale_id = uuid.uuid4()
            total = sum(float(p.unit_price) * q for p, q in resolved_items)

            new_sale = Sale(
                sale_id=sale_id,
                total=total,
                payment_method=payment_method,
                user_id=current_user.user_id
            )
            db.session.add(new_sale)

            for product, quantity in resolved_items:
                subtotal = float(product.unit_price) * quantity
                item = SaleItem(
                    quantity=quantity,
                    subtotal=subtotal,
                    sale_id=sale_id,
                    product_id=product.product_id
                )
                db.session.add(item)
                product.stock -= quantity  # Decrementa estoque

            db.session.commit()
            return jsonify({
                'message': 'Venda registrada com sucesso!',
                'sale_id': str(sale_id),
                'total': total
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Erro ao registrar venda: {str(e)}'}), 500

    # GET
    if current_user.role == 'admin':
        all_sales = Sale.query.all()
    else:
        all_sales = Sale.query.filter_by(user_id=current_user.user_id).all()
    return get_sales_json(all_sales)


@vendas.route('/usuario/<usuario_id>')
@token_required
def sales_user(current_user, usuario_id):
    if current_user.role == 'admin':
        sales = Sale.query.filter_by(user_id=uuid.UUID(usuario_id)).all()
    else:
        sales = Sale.query.filter_by(user_id=current_user.user_id).all()

    if not sales:
        name = get_user_name_by_id(usuario_id) if current_user.role == 'admin' else current_user.name
        return jsonify({"message": f"Usuário {name} não possui vendas."}), 200

    return get_sales_json(sales)


def get_sales_json(sales):
    return flask.jsonify([{
        "sale_id": str(s.sale_id),
        "sale_datetime": s.sale_datetime.strftime('%d/%m/%Y %H:%M:%S') if s.sale_datetime else None,
        "total": float(s.total) if s.total else 0.0,
        "payment_method": s.payment_method,
        "user_id": str(s.user_id)
    } for s in sales])