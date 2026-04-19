# coding: UTF-8
"""
Script: PanificadoraRM/home/routes
"""
from flask import Blueprint, render_template, session, redirect, url_for, jsonify, current_app, request
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from datetime import datetime
from calendar import monthrange

from app.auth.models import User
from app.home.map import site_map
from app.products.models import Product
from app.suppliers.models import Supplier
from app.stock_entries.models import StockEntry, StockEntryItem
from app.bills.models import Bill
from app.extensions import db
from utils.auth import token_required

inicio = Blueprint('home', __name__, template_folder='templates')


@inicio.route('/')
def index():
    return redirect(url_for('home.dashboard'))


# ─────────────────────────────────────────────
# DASHBOARD  — visão geral de compras
# ─────────────────────────────────────────────
@inicio.route('/dashboard')
def dashboard():
    user = get_logged_in_user()
    if not user:
        return redirect(url_for('auth.login'))

    total_compras = StockEntry.query.count()
    total_gasto = db.session.query(func.sum(StockEntry.total_cost)).scalar() or 0
    total_materiais = Product.query.count()
    total_fornecedores = Supplier.query.count()

    # Resumo de contas a pagar
    from datetime import date as _date
    todas_contas = Bill.query.all()
    contas_pendentes = [b for b in todas_contas if b.status == 'pendente']
    contas_vencidas  = [b for b in todas_contas if b.status == 'vencido']
    contas_pagas     = [b for b in todas_contas if b.status == 'pago']
    total_pendente = sum(float(b.amount) for b in contas_pendentes)
    total_vencido  = sum(float(b.amount) for b in contas_vencidas)
    total_contas_pagas = sum(float(b.amount) for b in contas_pagas)

    # Últimas 5 compras
    ultimas_compras = StockEntry.query.options(
        joinedload(StockEntry.supplier)
    ).order_by(StockEntry.entry_date.desc()).limit(5).all()

    # Materiais com estoque baixo (≤ 5)
    estoque_baixo = Product.query.filter(Product.stock <= 5).order_by(Product.stock).all()

    return render_template('dashboard.html',
                           user=user,
                           total_compras=total_compras,
                           total_gasto=float(total_gasto),
                           total_materiais=total_materiais,
                           total_fornecedores=total_fornecedores,
                           ultimas_compras=ultimas_compras,
                           estoque_baixo=estoque_baixo,
                           contas_pendentes=contas_pendentes,
                           contas_vencidas=contas_vencidas,
                           total_pendente=total_pendente,
                           total_vencido=total_vencido,
                           total_contas_pagas=total_contas_pagas)


# ─────────────────────────────────────────────
# MATERIAIS / INSUMOS
# ─────────────────────────────────────────────
@inicio.route('/produtos')
def products():
    user = get_logged_in_user()
    if not user:
        return redirect(url_for('auth.login'))
    products = Product.query.options(db.joinedload(Product.supplier)).order_by(Product.name).all()
    suppliers = Supplier.query.order_by(Supplier.name).all()
    return render_template('product.html', user=user, products=products, suppliers=suppliers)


# ─────────────────────────────────────────────
# FORNECEDORES
# ─────────────────────────────────────────────
@inicio.route('/contas-pagar')
def contas_a_pagar():
    user = get_logged_in_user()
    if not user:
        return redirect(url_for('auth.login'))
    from datetime import date as _date
    todas_contas = Bill.query.options(
        db.joinedload(Bill.supplier)
    ).order_by(Bill.due_date.asc()).all()
    suppliers = Supplier.query.order_by(Supplier.name).all()
    hoje = _date.today()
    return render_template('contas_pagar.html',
                           user=user,
                           contas=todas_contas,
                           suppliers=suppliers,
                           hoje=hoje)


@inicio.route('/fornecedores')
def suppliers():
    user = get_logged_in_user()
    if not user:
        return redirect(url_for('auth.login'))
    all_suppliers = Supplier.query.order_by(Supplier.name).all()
    return render_template('suppliers.html', user=user, suppliers=all_suppliers)


# ─────────────────────────────────────────────
# COMPRAS / ENTRADAS DE ESTOQUE
# ─────────────────────────────────────────────
@inicio.route('/entradas-estoque')
def stock_entries():
    user = get_logged_in_user()
    if not user:
        return redirect(url_for('auth.login'))

    entries = StockEntry.query.options(
        joinedload(StockEntry.supplier),
        joinedload(StockEntry.items).joinedload(StockEntryItem.product)
    ).order_by(StockEntry.entry_date.desc()).all()

    return render_template('stock_entries.html', user=user, entries=entries)


@inicio.route('/nova-entrada')
def nova_entrada():
    user = get_logged_in_user()
    if not user:
        return redirect(url_for('auth.login'))
    if user.role != 'admin':
        return redirect(url_for('home.stock_entries'))
    products = Product.query.order_by(Product.name).all()
    suppliers = Supplier.query.order_by(Supplier.name).all()
    return render_template('nova_entrada.html', user=user, products=products, suppliers=suppliers)


# ─────────────────────────────────────────────
# RELATÓRIOS DE GASTOS
# ─────────────────────────────────────────────
@inicio.route('/relatorio')
def relatorio():
    user = get_logged_in_user()
    if not user:
        return redirect(url_for('auth.login'))

    mes_filtro = request.args.get('mes')  # formato YYYY-MM
    start_date = None
    end_date = None

    if mes_filtro:
        try:
            dt = datetime.strptime(mes_filtro, '%Y-%m')
            start_date = dt.replace(day=1)
            _, last_day = monthrange(dt.year, dt.month)
            end_date = dt.replace(day=last_day, hour=23, minute=59, second=59)
        except ValueError:
            mes_filtro = None

    stock_q = StockEntry.query.options(joinedload(StockEntry.supplier), joinedload(StockEntry.items).joinedload(StockEntryItem.product))
    bills_q = Bill.query.filter(Bill.paid_date.isnot(None)).options(joinedload(Bill.supplier))

    if start_date and end_date:
        stock_q = stock_q.filter(StockEntry.entry_date >= start_date, StockEntry.entry_date <= end_date)
        bills_q = bills_q.filter(Bill.paid_date >= start_date, Bill.paid_date <= end_date)

    todas_entradas = stock_q.all()
    todas_contas = bills_q.order_by(Bill.paid_date.desc()).all()

    # 1. Agregar despesas por fornecedor em Python
    fornecedor_dados = {}
    total_geral_compras = 0.0
    total_geral_contas_pagas = 0.0

    for e in todas_entradas:
        total_geral_compras += float(e.total_cost)
        if e.supplier:
            sid = e.supplier.supplier_id
            name = e.supplier.name
            if sid not in fornecedor_dados:
                fornecedor_dados[sid] = {'name': name, 'qtd_compras': 0, 'total_gasto': 0.0}
            fornecedor_dados[sid]['qtd_compras'] += 1
            fornecedor_dados[sid]['total_gasto'] += float(e.total_cost)

    for b in todas_contas:
        total_geral_contas_pagas += float(b.amount)
        if b.supplier:
            sid = b.supplier.supplier_id
            name = b.supplier.name
            if sid not in fornecedor_dados:
                fornecedor_dados[sid] = {'name': name, 'qtd_compras': 0, 'total_gasto': 0.0}
            fornecedor_dados[sid]['total_gasto'] += float(b.amount)
        else:
            sid = 'sem_fornecedor'
            if sid not in fornecedor_dados:
                fornecedor_dados[sid] = {'name': 'Diversos / Outros (Contas)', 'qtd_compras': 0, 'total_gasto': 0.0}
            fornecedor_dados[sid]['total_gasto'] += float(b.amount)

    gasto_por_fornecedor = sorted(fornecedor_dados.values(), key=lambda x: x['total_gasto'], reverse=True)
    despesa_total_super = total_geral_compras + total_geral_contas_pagas

    # 2. Material mais comprado (maior quantidade total)
    top_materiais = []
    if todas_entradas:
        mat_dict = {}
        for e in todas_entradas:
            for item in e.items:
                pid = item.product_id
                if pid not in mat_dict:
                    mat_dict[pid] = {'name': item.product.name, 'unit_of_measure': item.product.unit_of_measure, 'total_qty': 0, 'total_gasto': 0.0}
                mat_dict[pid]['total_qty'] += item.quantity
                mat_dict[pid]['total_gasto'] += float(item.subtotal)
        top_materiais = sorted(mat_dict.values(), key=lambda x: x['total_gasto'], reverse=True)[:8]

    # 3. Histórico mensal de gastos - Compatibilidade nativa com Postgres
    todas_entradas_historico = StockEntry.query.order_by(StockEntry.entry_date.desc()).all()
    hist_dict = {}
    for e in todas_entradas_historico:
        if e.entry_date:
            m = e.entry_date.strftime('%Y-%m')
            hist_dict[m] = hist_dict.get(m, 0.0) + float(e.total_cost)
    historico_mensal = [{'mes': m, 'total': v} for m, v in list(hist_dict.items())[:6]]
    historico_mensal.reverse()

    return render_template('relatorios.html',
                           user=user,
                           mes_filtro=mes_filtro or '',
                           gasto_por_fornecedor=gasto_por_fornecedor,
                           top_materiais=top_materiais,
                           total_geral=total_geral_compras,
                           total_compras=len(todas_entradas),
                           historico_mensal=historico_mensal,
                           contas_pagas=todas_contas[:10],
                           total_geral_contas_pagas=total_geral_contas_pagas,
                           despesa_total_super=despesa_total_super)


# ─────────────────────────────────────────────
# USUÁRIOS (admin)
# ─────────────────────────────────────────────
@inicio.route('/usuarios')
def users():
    user = get_logged_in_user()
    if not user:
        return redirect(url_for('auth.login'))
    if user.role == 'admin':
        users = User.query.all()
    else:
        users = [user]
    return render_template('users.html', user=user, users=users)


@inicio.route('/rotas')
def rotas_index():
    links = site_map(current_app.url_map)
    return render_template('map.html', links=links)


# ─────────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────────
def get_logged_in_user():
    import uuid as _uuid
    user_id = session.get('user_id')
    if not user_id:
        return None
    try:
        uid = _uuid.UUID(str(user_id))
        user = User.query.filter_by(user_id=uid).first()
    except (ValueError, AttributeError):
        session.clear()
        return None
    if not user:
        session.clear()
        return None
    return user