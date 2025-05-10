# coding: UTF-8
"""
Script: Panificadora-RM/rotas
Création: jojo, le 07/05/2025
"""
# Imports
import locale

from app.interno.services import *

locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

from flask import Blueprint, redirect, url_for, render_template, request

interno = Blueprint('interno', __name__, template_folder='templates')


@interno.route('/')
def home():
    return redirect(url_for('interno.compras'))


@interno.route('/compras')
def compras():
    filtro = request.args.get("filtro")
    compras = get_todas_compras()
    context = {
        "tela": "compras",
        "itens": compras,
        "total": calcular_total(compras)
    }
    if filtro == "fornecedor":
        context["fornecedores"] = get_todos_fornecedores()
        context["fornecedor_selected"] = True
    elif filtro == "produto":
        context["produtos"] = get_todos_produtos()
        context["produto_selected"] = True
    elif filtro == "periodo":
        anos_disponiveis = get_anos_disponiveis(context["itens"])
        context["anos"] = anos_disponiveis
        context["ano_selected"] = True
        context["mes_selected"] = None
    return render_template("interno.html", **context)

@interno.route('/compras/add', methods=["GET", "POST"])
def compras_add():
    if request.method == "GET":
        return render_template('compras_add.html', mode="add")



@interno.route('/compras/fornecedor/<id>')
def compras_por_fornecedor(id):
    fornecedor = get_fornecedor(id)
    if fornecedor:
        compras = get_compras_fornecedor(fornecedor.id)
        context = {
            "tela": "compras",
            "itens": compras,
            "total": calcular_total(compras),
            "fornecedores": get_todos_fornecedores(),
            "fornecedor_selected": fornecedor
        }
        return render_template('interno.html', **context)
    return redirect(url_for("interno.compras"))


@interno.route('/compras/produto/<produto_id>')
def compras_por_produto(produto_id):
    produto = get_produto(produto_id)
    if produto:
        compras = get_compras_produto(produto_id)
        context = {
            "tela": "compras",
            "itens": compras,
            "total": calcular_total(compras),
            "produtos": get_todos_produtos(),
            "produto_selected": produto
        }
        return render_template('interno.html', **context)
    return redirect(url_for("interno.compras"))


@interno.route('/compras/periodo/<ano>')
def compras_periodo_ano(ano):
    if not ano_valido(ano):
        return redirect(url_for("interno.compras"))
    compras = get_compras_ano(ano)
    context = {
        "tela": "compras",
        "itens": compras,
        "total": calcular_total(compras),
        "anos": get_anos_disponiveis(compras),
        "ano_selected": int(ano),
        "meses": get_meses_disponiveis(ano)
    }
    return render_template('interno.html', **context)


@interno.route('/compras/periodo/<ano>/<mes>')
def compras_periodo_mes(ano, mes):
    if ano == "all":
        return redirect("interno.compras")
    if mes == "all":
        compras = get_compras_ano(ano)
        mes_selected = "all"
    else:
        if not ano_valido(ano) or not mes_valido(ano, mes):
            return redirect(url_for("interno.compras"))
        compras = get_compras_mes(ano, mes)
        mes_selected = int(mes)
    context = {
        "tela": "compras",
        "itens": compras,
        "total": calcular_total(compras),
        "anos": get_anos_disponiveis(compras),
        "meses": get_meses_disponiveis(ano),
        "ano_selected": int(ano),
        "mes_selected": mes_selected
    }
    return render_template('interno.html', **context)


@interno.route('/produtos')
def produtos():
    context = {
        "tela": "produtos",
        "itens": get_todos_produtos()
    }
    return render_template('interno.html', **context)


@interno.route('/fornecedores')
def fornecedores():
    context = {
        "tela": "fornecedores",
        "itens": get_todos_fornecedores()
    }
    return render_template('interno.html', **context)


@interno.route('/relatorio')
def relatorio():
    return render_template('relatorios_interno.html')
