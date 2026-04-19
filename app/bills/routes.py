# coding: UTF-8
"""
Script: PanificadoraRM/bills/routes
API para Contas a Pagar
"""
import uuid
from datetime import date, datetime
from flask import Blueprint, jsonify, request
from app.extensions import db
from app.bills.models import Bill
from app.suppliers.models import Supplier
from utils.auth import token_required

contas_pagar = Blueprint('bills_bp', __name__)


@contas_pagar.route('/', methods=['GET', 'POST'])
@token_required
def bills(current_user):

    if request.method == 'POST':
        data = request.get_json(silent=True) or {}

        description = data.get('description', '').strip()
        amount      = data.get('amount')
        due_date_str = data.get('due_date')

        if not description:
            return jsonify({'message': 'Descrição é obrigatória.'}), 400
        if not amount or float(amount) <= 0:
            return jsonify({'message': 'Valor deve ser maior que zero.'}), 400
        if not due_date_str:
            return jsonify({'message': 'Data de vencimento é obrigatória.'}), 400

        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': 'Formato de data inválido. Use AAAA-MM-DD.'}), 400

        # Fornecedor opcional
        supplier_id = None
        sid = data.get('supplier_id')
        if sid:
            try:
                supplier_id = uuid.UUID(str(sid))
                if not Supplier.query.filter_by(supplier_id=supplier_id).first():
                    return jsonify({'message': 'Fornecedor não encontrado.'}), 404
            except ValueError:
                return jsonify({'message': 'supplier_id inválido.'}), 400

        # Compra vinculada opcional
        entry_id = None
        eid = data.get('stock_entry_id')
        if eid:
            try:
                entry_id = uuid.UUID(str(eid))
            except ValueError:
                pass

        try:
            bill = Bill(
                description=description,
                amount=float(amount),
                due_date=due_date,
                note=data.get('note', '').strip() or None,
                supplier_id=supplier_id,
                stock_entry_id=entry_id,
                user_id=current_user.user_id
            )
            db.session.add(bill)
            db.session.commit()
            return jsonify({'message': f'Conta "{description}" cadastrada!', 'bill': bill.to_dict()}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Erro: {str(e)}'}), 500

    # GET — filtro por status
    status_filter = request.args.get('status')  # pendente | vencido | pago
    all_bills = Bill.query.order_by(Bill.due_date.asc()).all()

    result = [b.to_dict() for b in all_bills]
    if status_filter in ('pendente', 'vencido', 'pago'):
        result = [b for b in result if b['status'] == status_filter]

    return jsonify(result)


@contas_pagar.route('/<string:bill_id>/pagar', methods=['POST'])
@token_required
def pay_bill(current_user, bill_id):
    """Marca uma conta como paga (hoje ou data informada)."""
    try:
        bid = uuid.UUID(bill_id)
    except ValueError:
        return jsonify({'message': 'ID inválido'}), 400

    bill = Bill.query.filter_by(bill_id=bid).first()
    if not bill:
        return jsonify({'message': 'Conta não encontrada'}), 404
    if bill.paid_date:
        return jsonify({'message': 'Conta já está marcada como paga.'}), 400

    data = request.get_json(silent=True) or {}
    paid_str = data.get('paid_date')

    try:
        paid = datetime.strptime(paid_str, '%Y-%m-%d').date() if paid_str else date.today()
    except ValueError:
        paid = date.today()

    try:
        bill.paid_date = paid
        db.session.commit()
        return jsonify({'message': f'Conta "{bill.description}" marcada como paga!', 'bill': bill.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro: {str(e)}'}), 500


@contas_pagar.route('/<string:bill_id>', methods=['PUT', 'DELETE'])
@token_required
def bill_detail(current_user, bill_id):
    try:
        bid = uuid.UUID(bill_id)
    except ValueError:
        return jsonify({'message': 'ID inválido'}), 400

    bill = Bill.query.filter_by(bill_id=bid).first()
    if not bill:
        return jsonify({'message': 'Conta não encontrada'}), 404

    if request.method == 'DELETE':
        try:
            db.session.delete(bill)
            db.session.commit()
            return jsonify({'message': 'Conta removida!'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Erro: {str(e)}'}), 500

    # PUT — editar
    data = request.get_json(silent=True) or {}
    if 'description' in data:
        bill.description = data['description'].strip()
    if 'amount' in data:
        bill.amount = float(data['amount'])
    if 'due_date' in data:
        try:
            bill.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': 'Formato de data inválido.'}), 400
    if 'note' in data:
        bill.note = data['note'] or None

    try:
        db.session.commit()
        return jsonify({'message': 'Conta atualizada!', 'bill': bill.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro: {str(e)}'}), 500
