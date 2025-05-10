# coding: UTF-8
"""
Script: Panificadora-RM/services
Création: jojo, le 10/05/2025
"""
import calendar
from datetime import datetime

from flask import redirect, url_for
from sqlalchemy import extract

from app.interno.models import Compra, Fornecedor, FornecedorProdutos


def get_todas_compras():
    return Compra.query.all()


def get_todos_fornecedores():
    return Fornecedor.query.all()


def get_todos_produtos():
    return FornecedorProdutos.query.all()


def get_fornecedor(id):
    if id == "all":
        return None
    else:
        return Fornecedor.query.filter_by(id=id).first()


def get_produto(produto_id):
    if produto_id == "all":
        return None
    else:
        return FornecedorProdutos.query.filter_by(id=produto_id).first()


def get_compras_fornecedor(id):
    return Compra.query.join(FornecedorProdutos).filter(FornecedorProdutos.fornecedor_id == id).all()


def get_compras_produto(produto_id):
    return Compra.query.join(FornecedorProdutos).filter(FornecedorProdutos.id == produto_id).all()


def get_compras_ano(ano):
    return Compra.query.filter(extract('year', Compra.data_compra) == int(ano)).all()


def get_compras_mes(ano, mes):
    return Compra.query.filter(
        extract('year', Compra.data_compra) == int(ano),
        extract('month', Compra.data_compra) == int(mes)
    ).all()


def calcular_total(compras):
    total = 0.0
    for c in compras:
        total += c.preco_total
    return total


def ano_valido(ano):
    if ano == "all":
        return False
    return int(ano) <= datetime.today().year


def mes_valido(ano, mes):
    if ano == "all" or mes == "all":
        return False


    if int(ano) == datetime.today().year:
        return int(mes) <= datetime.today().month
    elif int(ano) < datetime.today().year:
        return int(mes) <= 12
    return False


def get_anos_disponiveis(compras):
    anos = [datetime.today().year]
    for c in compras:
        ano = c.data_compra.year
        if ano not in anos:
            anos.append(ano)
    return sorted(anos, reverse=True)


def get_meses_disponiveis(ano):
    if int(ano) == datetime.today().year:
        return meses_ate(datetime.today().month)
    elif int(ano) < datetime.today().year:
        return meses_ate(12)


def meses_ate(mes):
    return [(i, calendar.month_name[i]) for i in range(1, mes + 1)]
