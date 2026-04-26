# coding: UTF-8
from datetime import date
from functools import wraps
from flask import Blueprint, render_template, session, redirect, url_for, request
from sqlalchemy import func, extract, text
from app.extensions import db
from app.auth.models import User
from app.products.models import Product
from app.suppliers.models import Supplier
from app.stock_entries.models import StockEntry, StockEntryItem
from app.bills.models import Bill
from app.sales.models import Sale

inicio = Blueprint("home", __name__, template_folder="templates")


def session_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def get_current_user():
    import uuid
    uid = session.get("user_id")
    if uid:
        return User.query.filter_by(user_id=uuid.UUID(str(uid))).first()
    return None


@inicio.route("/")
@session_required
def dashboard():
    user = get_current_user()
    total_compras = StockEntry.query.count()
    total_gasto = db.session.query(func.sum(StockEntry.total_cost)).scalar() or 0
    total_materiais = Product.query.count()
    total_fornecedores = Supplier.query.count()
    contas_pagas = Bill.query.filter(Bill.paid_date.isnot(None)).all()
    total_contas_pagas = sum(float(b.amount) for b in contas_pagas)
    hoje = date.today()
    contas_vencidas = Bill.query.filter(Bill.paid_date.is_(None), Bill.due_date < hoje).all()
    contas_pendentes = Bill.query.filter(Bill.paid_date.is_(None), Bill.due_date >= hoje).all()
    total_vencido = sum(float(b.amount) for b in contas_vencidas)
    total_pendente = sum(float(b.amount) for b in contas_pendentes)
    ultimas_compras = StockEntry.query.order_by(StockEntry.entry_date.desc()).limit(5).all()
    estoque_baixo = Product.query.filter(Product.stock <= 5, Product.is_active == True).order_by(Product.stock).all()
    return render_template("dashboard.html",
        user=user, total_compras=total_compras, total_gasto=total_gasto,
        total_contas_pagas=total_contas_pagas, total_materiais=total_materiais,
        total_fornecedores=total_fornecedores, contas_vencidas=contas_vencidas,
        contas_pendentes=contas_pendentes, total_vencido=total_vencido,
        total_pendente=total_pendente, ultimas_compras=ultimas_compras,
        estoque_baixo=estoque_baixo,
    )


@inicio.route("/produtos")
@session_required
def products():
    user = get_current_user()
    all_products = Product.query.order_by(Product.name).all()
    return render_template("product.html", products=all_products, logged_user=user, user=user)


@inicio.route("/usuarios")
@session_required
def users():
    user = get_current_user()
    all_users = User.query.order_by(User.name).all()
    return render_template("users.html", users=all_users, logged_user=user, user=user)


@inicio.route("/vendas")
@session_required
def vendas():
    user = get_current_user()
    all_sales = Sale.query.order_by(Sale.sale_datetime.desc()).all()
    return render_template("sales.html", sales=all_sales, user=user)


@inicio.route("/fornecedores")
@session_required
def suppliers():
    user = get_current_user()
    all_suppliers = Supplier.query.order_by(Supplier.name).all()
    return render_template("suppliers.html", suppliers=all_suppliers, user=user)


@inicio.route("/entradas-estoque")
@session_required
def stock_entries():
    user = get_current_user()
    entries = StockEntry.query.order_by(StockEntry.entry_date.desc()).all()
    return render_template("stock_entries.html", entries=entries, user=user)


@inicio.route("/nova-entrada")
@session_required
def nova_entrada():
    user = get_current_user()
    all_suppliers = Supplier.query.order_by(Supplier.name).all()
    all_products = Product.query.filter_by(is_active=True).order_by(Product.name).all()
    return render_template("nova_entrada.html", suppliers=all_suppliers, products=all_products, user=user)


@inicio.route("/contas-pagar")
@session_required
def contas_a_pagar():
    user = get_current_user()
    all_suppliers = Supplier.query.order_by(Supplier.name).all()
    contas = Bill.query.order_by(Bill.due_date.desc()).all()
    return render_template("contas_pagar.html", contas=contas, suppliers=all_suppliers,
                           user=user, hoje=date.today().strftime("%Y-%m-%d"), request=request)


@inicio.route("/relatorios")
@session_required
def relatorio():
    user = get_current_user()
    mes_filtro = request.args.get("mes", "")

    entry_q = StockEntry.query
    bill_q = Bill.query.filter(Bill.paid_date.isnot(None))

    if mes_filtro:
        try:
            ano, mes = int(mes_filtro[:4]), int(mes_filtro[5:7])
            entry_q = entry_q.filter(
                extract("year", StockEntry.entry_date) == ano,
                extract("month", StockEntry.entry_date) == mes,
            )
            bill_q = bill_q.filter(
                extract("year", Bill.paid_date) == ano,
                extract("month", Bill.paid_date) == mes,
            )
        except Exception:
            pass

    entries = entry_q.all()
    contas_pagas_list = bill_q.order_by(Bill.paid_date.desc()).limit(10).all()

    total_geral = sum(float(e.total_cost) for e in entries)
    total_geral_contas_pagas = sum(float(b.amount) for b in bill_q.all())
    despesa_total_super = total_geral + total_geral_contas_pagas
    total_compras = len(entries)

    fornecedor_map = {}
    for e in entries:
        sid = str(e.supplier_id)
        if sid not in fornecedor_map:
            fornecedor_map[sid] = {"name": e.supplier.name, "qtd_compras": 0, "total_gasto": 0}
        fornecedor_map[sid]["qtd_compras"] += 1
        fornecedor_map[sid]["total_gasto"] += float(e.total_cost)
    gasto_por_fornecedor = sorted(fornecedor_map.values(), key=lambda x: x["total_gasto"], reverse=True)

    material_map = {}
    for e in entries:
        for item in e.items:
            pid = str(item.product_id)
            if pid not in material_map:
                material_map[pid] = {
                    "name": item.product.name,
                    "unit_of_measure": item.product.unit_of_measure,
                    "total_qty": 0,
                    "total_gasto": 0,
                }
            material_map[pid]["total_qty"] += item.quantity
            material_map[pid]["total_gasto"] += float(item.subtotal)
    top_materiais = sorted(material_map.values(), key=lambda x: x["total_gasto"], reverse=True)

    historico_mensal = []
    if not mes_filtro:
        rows = db.session.execute(text(
            "SELECT TO_CHAR(entry_date, 'YYYY-MM') as mes, SUM(total_cost) as total "
            "FROM stock_entries GROUP BY mes ORDER BY mes DESC LIMIT 12"
        )).fetchall()
        historico_mensal = [{"mes": r[0], "total": float(r[1])} for r in rows]

    return render_template("relatorios.html",
        user=user, mes_filtro=mes_filtro,
        despesa_total_super=despesa_total_super,
        total_geral=total_geral, total_compras=total_compras,
        total_geral_contas_pagas=total_geral_contas_pagas,
        gasto_por_fornecedor=gasto_por_fornecedor,
        top_materiais=top_materiais,
        historico_mensal=historico_mensal,
        contas_pagas=contas_pagas_list,
    )
