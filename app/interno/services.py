# coding: UTF-8
"""
Script: Panificadora-RM/services
Création: jojo, le 10/05/2025
"""
import calendar
import logging
from datetime import datetime

from flask import flash
from sqlalchemy import extract

from app import db
from app.interno.models import Compra, Fornecedor, FornecedorProdutos

CATEGORIAS = [
    {"id": 1, "nome": "Insumos de Produção"},
    {"id": 2, "nome": "Bebidas"},
    {"id": 3, "nome": "Produtos para Revenda"},
    {"id": 4, "nome": "Materiais de Embalagem"},
    {"id": 5, "nome": "Produtos de Limpeza"},
    {"id": 6, "nome": "Descartáveis e Higiene"},
    {"id": 7, "nome": "Outros"}
]

TIPOS = [
    {"id": 1, "nome": "Ingrediente"},
    {"id": 2, "nome": "Bebida"},
    {"id": 3, "nome": "Produto de Limpeza"},
    {"id": 4, "nome": "Embalagem"},
    {"id": 5, "nome": "Descartável"},
    {"id": 6, "nome": "Produto para Revenda"},
    {"id": 7, "nome": "Utensílio"},
    {"id": 8, "nome": "Outros"}
]


def get_todas_compras():
    return Compra.query.all()


def get_todas_categorias():
    return CATEGORIAS


def get_categoria(id):
    for c in CATEGORIAS:
        if c['id'] == int(id):
            return c
    return "Outro"


def get_tipos_produtos():
    return TIPOS


def get_tipo_produto(tipo_id):
    for t in TIPOS:
        if t['id'] == int(tipo_id):
            return t
    return 'Outro'


def get_tipo_id(tipo_nome):
    for t in TIPOS:
        if t['nome'] == tipo_nome:
            return t
    return 'Outro'


def get_todos_fornecedores():
    return Fornecedor.query.all()


def get_todos_produtos():
    return FornecedorProdutos.query.all()


def get_compra(id):
    return Compra.query.filter_by(id=id).first()


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


def update_compra(compra_id, produto_id, data_compra, vencimento, quantidade, preco_total):
    compra = get_compra(compra_id)
    if compra:
        try:
            data_compra_formated = datetime.strptime(data_compra, '%Y-%m-%d').date()
            data_vencimento_formated = datetime.strptime(vencimento, '%Y-%m-%d').date()

            # Verifique se as datas foram formatadas corretamente
            print(f"Data de Compra formatada: {data_compra_formated}")
            print(f"Data de Vencimento formatada: {data_vencimento_formated}")

            compra.produto_id = produto_id
            compra.data_compra = data_compra_formated
            compra.validade = data_vencimento_formated
            compra.quantidade = quantidade
            compra.preco_unitario = float(preco_total) / float(quantidade)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao atualizar compra: {str(e)}")
            return False
    return False


def update_produto(produto_id, fornecedor_id, nome, tipo_id):
    produto: FornecedorProdutos = get_produto(produto_id)
    if produto:
        tipo = get_tipo_produto(tipo_id)
        try:
            produto.fornecedor_id = fornecedor_id
            produto.nome = nome
            produto.tipo = tipo['nome']
            db.session.commit()
            logging.info(f"Produto {produto_id} atualizado com sucesso!")
            return True
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao atualizar produto: {str(e)}")
            return False
    else:
        flash("Produto não encontrado.")
        return False


def calcular_total(compras):
    total = 0.0
    for c in compras:
        total += c.preco_total
    return total


def update_fornecedor(fornecedor_id, nome, contato, categoria):
    fornecedor: Fornecedor = get_fornecedor(fornecedor_id)
    if fornecedor:
        try:
            fornecedor.nome = nome
            fornecedor.contato = contato
            fornecedor.categoria = categoria['nome']
            db.session.commit()
            logging.info(f"Fornecedor {fornecedor.id} atualizado com sucesso!")
            return True
        except Exception as e:
            flash(f"Erro ao atualizar o fornecedor {fornecedor.id}: {str(e)}")
            return False
    flash("Fornecedor não encontrado.")
    return False


def get_atual_ano_mes(compras):
    anos = get_anos_disponiveis(compras)
    meses = get_meses_disponiveis(anos[0])
    return {"anos": anos[0], "mes": meses[-1][0]}


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


def get_anos_disponiveis(compras=None):
    if not compras:
        return datetime.today().year
    anos = [datetime.today().year]
    for c in compras:
        ano = c.data_compra.year
        if ano not in anos:
            anos.append(ano)
    return sorted(anos, reverse=True)


def get_meses_disponiveis(ano):
    if ano == 'all':
        return meses_ate(12)
    elif int(ano) == datetime.today().year:
        return meses_ate(datetime.today().month)
    elif int(ano) < datetime.today().year:
        return meses_ate(12)


def meses_ate(mes):
    return [(i, calendar.month_name[i]) for i in range(1, mes + 1)]


def delete_compra(compra_id):
    compra = get_compra(compra_id)
    if compra:
        try:
            db.session.delete(compra)
            db.session.commit()
            logging.log(1, f"Compra deletada com sucesso: {compra_id}")
            return True
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao deletar compra: {str(e)}")
            return False
    else:
        flash("Compra não encontrada.")
        return False


def adicionar_compra(produto_id, data_compra, data_vencimento, quantidade, preco_total):
    data_compra_formated = datetime.strptime(data_compra, '%Y-%m-%d').date()
    data_vencimento_formated = datetime.strptime(data_vencimento, '%Y-%m-%d').date()
    preco_unitario = float(preco_total) / float(quantidade)
    compra = Compra(
        produto_id=produto_id,
        data_compra=data_compra_formated,
        validade=data_vencimento_formated,
        quantidade=quantidade,
        preco_unitario=preco_unitario
    )
    try:
        db.session.add(compra)
        db.session.commit()
        logging.log(1, f"Compra adicionada no banco de dados:{compra.id}")
        return True
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao adicionar no banco de dados: {str(e)}")
    return False


def adicionar_produto(fornecedor, nome, tipo):
    produto = FornecedorProdutos(fornecedor_id=fornecedor.id, nome=nome, tipo=tipo['nome'])
    print(produto)
    try:
        db.session.add(produto)
        db.session.commit()
        logging.info("Fornecedor adicionado ao banco de dados.")
        return produto
    except Exception as e:
        flash(f"Erro ao adicionar fornecedor ao banco de dados: {str(e)}")
        return None


def desativar_produto(produto_id):
    produto = get_produto(produto_id)
    if produto:
        try:
            produto.ativo = False
            db.session.commit()
            logging.info(f"Produto desativado com sucesso! {produto.nome}")
            return True
        except Exception as e:
            flash(f"Erro ao desativar produto: {str(e)}")
            return False
    flash(f"produto_id invalido! Produto não encontrado.")
    return False


def desativar_fornecedor(fornecedor_id):
    fornecedor = get_fornecedor(fornecedor_id)
    if fornecedor:
        try:
            fornecedor.ativo = False
            db.session.commit()
            logging.info(f"Fornecedor desativado com sucesso! {fornecedor.nome}")
            return True
        except Exception as e:
            flash(f"Erro ao desativar fornecedor: {str(e)}")
            return False
    flash(f"fornecedor_id invalido! Fornecedor não encontrado.")
    return False


def adicionar_fornecedor(nome, contato, categoria):
    categoria = get_categoria(int(categoria))
    fornecedor = Fornecedor(nome=nome, contato=contato, categoria=categoria['nome'])
    try:
        db.session.add(fornecedor)
        db.session.commit()
        return fornecedor
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao inserir o fornecedor {fornecedor.id} no db: {str(e)}")
        return None
