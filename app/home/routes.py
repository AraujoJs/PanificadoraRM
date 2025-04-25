# coding: UTF-8
"""
Script: Backend/routes
Création: jojo, le 12/04/2025
"""

# Imports
from flask import Blueprint, render_template, session, redirect, url_for, jsonify
from app.auth.models import User
from app.products.models import Product
from app.sales.models import Sale, SaleItem
from app.sales.routes import sales
from utils.auth import token_required

home_bp = Blueprint('home', __name__, template_folder='templates')

@home_bp.route('/')
def index():
    return redirect(url_for('home.sales'))

@home_bp.route('/sales')
def sales():
    user_id = session.get('user_id')
    if not user_id:
        redirect(url_for('auth_bp.login'))
    user = User.query.get(user_id)
    if not user:
        session.clear()
        return redirect(url_for('auth_bp.login'))
    if user.role == 'admin':
        sales = Sale.query.all()
    else:
        sales = Sale.query.filter_by(user_id=user_id).all()
    for sale in sales:
        user = User.query.filter_by(user_id=sale.user_id).first()
        sale.user_name = user.name
    return render_template('sales.html', user=user, sales=sales)

@home_bp.route('/products')
def products():
    user_id = session.get('user_id')
    if not user_id:
        redirect(url_for('auth_bp.login'))
    user = User.query.get(user_id)
    if not user:
        session.clear()
        return redirect(url_for('auth_bp.login'))

    products = Product.query.all()
    return render_template('product.html', products = products)

@home_bp.route('/saleitem')
def sale_item():
    user_id = session.get('user_id')
    if not user_id:
        redirect(url_for('auth_bp.login'))
    user = User.query.get(user_id)
    if not user:
        session.clear()
        return redirect(url_for('auth_bp.login'))
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        session.clear()
        return redirect(url_for('auth_bp.login'))

    if user.role == 'admin':
        items = SaleItem.query.all()
        for item in items:
            item.user_name = User.query.filter_by(user_id=item.user_id).first().name
            item.product_name = Product.query.filter_by(product_id=item.product_id).first().name
    else:
        items = SaleItem.query.filter_by(user_id=user_id).all()
        user_name = User.query.filter_by(user_id=user_id).first().name
        for item in items:
            item.user_name = user_name
            item.product_name = Product.query.filter_by(product_id=item.product_id).first()

    return render_template('sale_item.html', items=items)

@home_bp.route('/users')
def users():
    user_id = session.get('user_id')
    if not user_id:
        redirect(url_for('auth_bp.login'))
    user = User.query.get(user_id)
    if not user:
        session.clear()
        return redirect(url_for('auth_bp.login'))

    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        session.clear()
        return redirect(url_for('auth_bp.login'))

    if user.role == 'admin':
        users = User.query.all()
    else:
        users = User.query.filter_by(user_id=user_id).all()

    return render_template('users.html', users=users)

@home_bp.route('/api/home')
@token_required
def api_home(current_user):
    return jsonify({
        'user_id': current_user.user_id,
        'email': current_user.email,
        'role': current_user.role
    })