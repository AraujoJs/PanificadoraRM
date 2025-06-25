# coding: UTF-8
"""
Script: Panificadora-RM/ProdutosFornecedor
Création: jojo, le 07/05/2025
"""

from datetime import date
from email.policy import default

from app import db


class Fornecedor(db.Model):
    __tablename__ = 'fornecedores'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    contato = db.Column(db.String(100))
    categoria = db.Column(db.String(50)) # Ex: bebidas, embalagens, ingredientes
    ativo = db.Column(db.Boolean, default=True)

    produtos = db.relationship('FornecedorProdutos', backref='fornecedor', lazy=True)
    def __repr__(self):
        return f'<Fornecedor {self.nome}>'


class FornecedorProdutos(db.Model):
    __tablename__ = 'fornecedor_produtos'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    fornecedor_id = db.Column(db.Integer, db.ForeignKey('fornecedores.id'), nullable=False)

    ativo = db.Column(db.Boolean, default=True)

    compras = db.relationship('Compra', back_populates='produto', lazy=True)

    def __repr__(self):
        return f'<Produto {self.nome}>'


class Compra(db.Model):
    __tablename__ = 'compras'
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('fornecedor_produtos.id'), nullable=False)
    data_compra = db.Column(db.Date, default=date.today)
    validade = db.Column(db.Date, nullable=True)
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Float, nullable=False) # Quando compra, tem o preço unidade ou total?
    consumido = db.Column(db.Boolean, default=False)

    produto = db.relationship('FornecedorProdutos', back_populates='compras')


    def __repr__(self):
        return f'<Compra {self.produto.nome} - {self.quantidade} un>'

    @property
    def preco_total(self):
        return self.quantidade * self.preco_unitario

    @property
    def validade_em_texto(self):
        if self.validade:
            dias = (self.validade - date.today()).days
            if dias > 0:
                return f"Faltam {dias} dias"
            elif dias == 0:
                return "Vence hoje"
            else:
                return f"Vencido há {-dias} dias"
        return "Sem validade"

    @property
    def dias_para_vencimento(self):
        if self.validade:
            return (self.validade - date.today()).days
        return None