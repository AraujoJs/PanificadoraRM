# coding: UTF-8
"""
Script: Backend/routes
Création: jojo, le 12/04/2025
"""
# Imports
from flask import Blueprint, render_template, session, redirect, url_for, jsonify, current_app

from app.auth.models import User
from app.home.map import site_map
from app.products.models import Product
from app.sales.models import Sale, SaleItem
from utils.auth import token_required

inicio = Blueprint('home', __name__, template_folder='templates')


@inicio.route('/')
def index():
    return redirect(url_for('home.sales'))


@inicio.route('/vendas')
def sales():
    user = get_logged_in_user()
    if not user:
        return redirect(url_for('auth.login'))
    if user.role == 'admin':
        sales = Sale.query.all()
    else:
        sales = Sale.query.filter_by(user_id=user.user_id).all()
    for sale in sales:
        user = User.query.filter_by(user_id=sale.user_id).first()
        sale.user_name = user.name
    return render_template('sales.html', user=user, sales=sales)


@inicio.route('/produtos')
def products():
    user = get_logged_in_user()
    if not user:
        return redirect(url_for('auth.login'))

    products = Product.query.all()
    return render_template('product.html', products=products)


@inicio.route('/item-venda')
def sale_item():
    user = get_logged_in_user()
    if not user:
        return redirect(url_for('auth.login'))
    user = User.query.filter_by(user_id=user.user_id).first()
    if not user:
        session.clear()
        return redirect(url_for('auth_bp.login'))
    if user.role == 'admin':
        items = SaleItem.query.all()
        for item in items:
            item.user_name = User.query.filter_by(user_id=item.user_id).first().name
            item.product_name = Product.query.filter_by(product_id=item.product_id).first().name
    else:
        items = SaleItem.query.filter_by(user_id=user.user_id).all()
        user_name = User.query.filter_by(user_id=user.user_id).first().name
        for item in items:
            item.user_name = user_name
            item.product_name = Product.query.filter_by(product_id=item.product_id).first().name
    return render_template('sale_item.html', items=items)


@inicio.route('/usuarios')
def users():
    user = get_logged_in_user()
    if not user:
        return redirect(url_for('auth.login'))
    user = User.query.filter_by(user_id=user.user_id).first()
    if user.role == 'admin':
        users = User.query.all()
    else:
        users = User.query.filter_by(user_id=user.user_id).all()
    return render_template('users.html', users=users)


@inicio.route('/api')
@token_required
def api_home(current_user):
    return jsonify({
        'user_id': current_user.user_id,
        'email': current_user.email,
        'role': current_user.role
    })


@inicio.route('/rotas')
def rotas_index():
    links = site_map(current_app.url_map)
    return render_template('map.html', links=links)


@inicio.route('/relatorio')
def relatorio():
    return render_template('relatorios.html')


def get_logged_in_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    user = User.query.get(user_id)
    if not user:
        session.clear()
        return None
    return user