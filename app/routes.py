# coding: UTF-8
"""
Script: PanificadoraRM/routes
Création: jojo, le 11/04/2025
"""


# Imports
from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, g
from app.extensions import db
from app.models import Usuario

from werkzeug.security import check_password_hash, generate_password_hash


# @bp.route('/')
# def index():
#     usuarios = Usuario.query.all()  # Pega todos os usuários do banco
#     return render_template('index.html', usuarios=usuarios)  # Passa os dados para o template
#
# # Rota para criar um usuário via API
# @bp.route('/api/usuarios', methods=['POST'])
# def criar_usuario():
#     dados = request.get_json()
#     usuario = Usuario(nome=dados['nome'])
#     db.session.add(usuario)
#     db.session.commit()
#     return jsonify({"mensagem": "Usuário criado com sucesso"}), 201
#
# # Rota para listar todos os usuários via API
# @bp.route('/api/usuarios', methods=['GET'])
# def listar_usuarios():
#     usuarios = Usuario.query.all()
#     return jsonify([{"id": u.id, "nome": u.nome} for u in usuarios])
# # Fin
