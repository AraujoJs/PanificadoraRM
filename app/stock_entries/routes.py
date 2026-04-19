# coding: UTF-8
"""
Script: PanificadoraRM/stock_entries/routes
"""
import uuid
from flask import Blueprint, jsonify, request
from app.extensions import db
from app.products.models import Product
from app.suppliers.models import Supplier
from app.stock_entries.models import StockEntry, StockEntryItem
from utils.auth import token_required

entradas = Blueprint('stock_entries_bp', __name__)


@entradas.route('/', methods=['GET', 'POST'])
@token_required
def stock_entries(current_user):
    if request.method == 'POST':
        if current_user.role != 'admin':
            return jsonify({'message': 'Acesso negado'}), 403

        data = request.get_json() or {}
        supplier_id_str = data.get('supplier_id')
        items_data = data.get('items', [])
        raw_note = data.get('note') or ''
        note = raw_note.strip() or None

        if not supplier_id_str:
            return jsonify({'message': 'Fornecedor é obrigatório.'}), 400
        if not items_data:
            return jsonify({'message': 'A entrada deve ter pelo menos um item.'}), 400

        try:
            supplier_id = uuid.UUID(str(supplier_id_str))
        except ValueError:
            return jsonify({'message': 'supplier_id inválido.'}), 400

        supplier = Supplier.query.filter_by(supplier_id=supplier_id).first()
        if not supplier:
            return jsonify({'message': 'Fornecedor não encontrado.'}), 404

        # Validar todos os produtos antes de persistir
        resolved_items = []
        for entry in items_data:
            product_id_str = entry.get('product_id')
            quantity = entry.get('quantity', 0)
            unit_cost = entry.get('unit_cost', 0)

            if not product_id_str or quantity <= 0 or unit_cost < 0:
                return jsonify({'message': 'Cada item precisa de product_id, quantity > 0 e unit_cost >= 0.'}), 400

            try:
                product_id = uuid.UUID(str(product_id_str))
            except ValueError:
                return jsonify({'message': f'product_id inválido: {product_id_str}'}), 400

            product = Product.query.filter_by(product_id=product_id).first()
            if not product:
                return jsonify({'message': f'Produto {product_id_str} não encontrado.'}), 404

            resolved_items.append((product, quantity, float(unit_cost)))

        # Tudo ok — criar entrada e itens numa transação única
        try:
            entry_id = uuid.uuid4()
            total_cost = sum(q * c for _, q, c in resolved_items)

            new_entry = StockEntry(
                entry_id=entry_id,
                supplier_id=supplier_id,
                user_id=current_user.user_id,
                total_cost=total_cost,
                note=note
            )
            db.session.add(new_entry)

            for product, quantity, unit_cost in resolved_items:
                subtotal = quantity * unit_cost
                item = StockEntryItem(
                    entry_id=entry_id,
                    product_id=product.product_id,
                    quantity=quantity,
                    unit_cost=unit_cost,
                    subtotal=subtotal
                )
                db.session.add(item)
                # ✅ Incrementa estoque do produto
                product.stock += quantity

            db.session.commit()
            return jsonify({
                'message': 'Entrada de estoque registrada com sucesso!',
                'entry_id': str(entry_id),
                'total_cost': total_cost
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Erro ao registrar entrada: {str(e)}'}), 500

    # GET — listar entradas
    if current_user.role == 'admin':
        all_entries = StockEntry.query.order_by(StockEntry.entry_date.desc()).all()
    else:
        all_entries = StockEntry.query.filter_by(user_id=current_user.user_id)\
                                      .order_by(StockEntry.entry_date.desc()).all()
    return jsonify([{
        'entry_id': str(e.entry_id),
        'entry_date': e.entry_date.strftime('%d/%m/%Y %H:%M') if e.entry_date else None,
        'supplier_name': e.supplier.name,
        'total_cost': float(e.total_cost),
        'note': e.note,
        'user_id': str(e.user_id)
    } for e in all_entries])
