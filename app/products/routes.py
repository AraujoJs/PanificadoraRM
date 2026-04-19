# coding: UTF-8
"""
Script: PanificadoraRM/products/routes
Gerencia os materiais/insumos da padaria
"""
from flask import Blueprint, jsonify, request
from app.extensions import db
from app.products.models import Product
from utils.auth import token_required

produtos = Blueprint('products_bp', __name__)

UNIDADES_VALIDAS = ['kg', 'g', 'L', 'mL', 'un', 'pacote', 'caixa', 'saco', 'duzia']


@produtos.route('/', methods=['GET', 'POST'])
@token_required
def products(current_user):
    if request.method == 'POST':
        if current_user.role != 'admin':
            return jsonify({'message': 'Acesso negado'}), 403

        data = request.get_json() or {}
        name = data.get('name', '').strip()
        unit_of_measure = data.get('unit_of_measure', 'un').strip()

        if not name:
            return jsonify({'message': 'Nome do material é obrigatório.'}), 400

        try:
            supplier_id = None
            if data.get('supplier_id'):
                import uuid as _uuid
                try:
                    supplier_id = _uuid.UUID(data['supplier_id'])
                except ValueError:
                    return jsonify({'message': 'ID de fornecedor inválido'}), 400

            new_product = Product(
                name=name,
                unit_of_measure=unit_of_measure,
                unit_price=data.get('unit_price') or None,
                stock=data.get('stock', 0),
                supplier_id=supplier_id
            )
            db.session.add(new_product)
            db.session.commit()
            return jsonify({'message': f'Material "{name}" cadastrado com sucesso!',
                            'product_id': str(new_product.product_id)}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Erro: {str(e)}'}), 500

    # GET
    all_products = Product.query.options(db.joinedload(Product.supplier)).order_by(Product.name).all()
    return jsonify([{
        'product_id': str(p.product_id),
        'name': p.name,
        'unit_of_measure': p.unit_of_measure,
        'unit_price': float(p.unit_price) if p.unit_price else None,
        'stock': p.stock,
        'supplier_id': str(p.supplier_id) if p.supplier_id else None,
        'supplier_name': p.supplier.name if p.supplier else None
    } for p in all_products])


@produtos.route('/<string:product_id>', methods=['PUT', 'DELETE'])
@token_required
def product_detail(current_user, product_id):
    if current_user.role != 'admin':
        return jsonify({'message': 'Acesso negado'}), 403

    import uuid as _uuid
    try:
        pid = _uuid.UUID(product_id)
    except ValueError:
        return jsonify({'message': 'ID inválido'}), 400

    product = Product.query.filter_by(product_id=pid).first()
    if not product:
        return jsonify({'message': 'Material não encontrado'}), 404

    if request.method == 'PUT':
        data = request.get_json() or {}
        if 'name' in data:
            product.name = data['name'].strip()
        if 'unit_of_measure' in data:
            product.unit_of_measure = data['unit_of_measure'].strip()
        if 'unit_price' in data:
            product.unit_price = data['unit_price']
        if 'stock' in data:
            product.stock = data['stock']
        if 'supplier_id' in data:
            if data['supplier_id']:
                try:
                    product.supplier_id = _uuid.UUID(data['supplier_id'])
                except ValueError:
                    return jsonify({'message': 'ID de fornecedor inválido'}), 400
            else:
                product.supplier_id = None
        try:
            db.session.commit()
            return jsonify({'message': f'Material "{product.name}" atualizado!'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Erro: {str(e)}'}), 500

    # DELETE
    try:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Material removido!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro: {str(e)}'}), 500