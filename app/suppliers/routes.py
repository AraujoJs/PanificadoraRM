# coding: UTF-8
"""
Script: PanificadoraRM/suppliers/routes
"""
import uuid
from flask import Blueprint, jsonify, request
from app.extensions import db
from app.suppliers.models import Supplier
from utils.auth import token_required

fornecedores = Blueprint('suppliers_bp', __name__)


@fornecedores.route('/', methods=['GET', 'POST'])
@token_required
def suppliers(current_user):
    if request.method == 'POST':
        if current_user.role != 'admin':
            return jsonify({'message': 'Acesso negado'}), 403

        data = request.get_json() or {}
        name = data.get('name', '').strip()
        if not name:
            return jsonify({'message': 'Nome do fornecedor é obrigatório.'}), 400

        try:
            supplier = Supplier(
                name=name,
                contact=data.get('contact', '').strip() or None,
                phone=data.get('phone', '').strip() or None,
                email=data.get('email', '').strip() or None,
            )
            db.session.add(supplier)
            db.session.commit()
            return jsonify({'message': f'Fornecedor "{name}" cadastrado!', 'supplier_id': str(supplier.supplier_id)}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Erro: {str(e)}'}), 500

    # GET
    all_suppliers = Supplier.query.order_by(Supplier.name).all()
    return jsonify([{
        'supplier_id': str(s.supplier_id),
        'name': s.name,
        'contact': s.contact,
        'phone': s.phone,
        'email': s.email
    } for s in all_suppliers])


@fornecedores.route('/<string:supplier_id>', methods=['PUT', 'DELETE'])
@token_required
def supplier_detail(current_user, supplier_id):
    if current_user.role != 'admin':
        return jsonify({'message': 'Acesso negado'}), 403

    try:
        sid = uuid.UUID(supplier_id)
    except ValueError:
        return jsonify({'message': 'ID inválido'}), 400

    supplier = Supplier.query.filter_by(supplier_id=sid).first()
    if not supplier:
        return jsonify({'message': 'Fornecedor não encontrado'}), 404

    if request.method == 'PUT':
        data = request.get_json() or {}
        if 'name' in data:
            supplier.name = data['name'].strip()
        if 'contact' in data:
            supplier.contact = data['contact']
        if 'phone' in data:
            supplier.phone = data['phone']
        if 'email' in data:
            supplier.email = data['email']
        try:
            db.session.commit()
            return jsonify({'message': f'Fornecedor "{supplier.name}" atualizado!'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Erro: {str(e)}'}), 500

    # DELETE
    try:
        db.session.delete(supplier)
        db.session.commit()
        return jsonify({'message': 'Fornecedor removido!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro: {str(e)}'}), 500
