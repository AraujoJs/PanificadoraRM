# coding: UTF-8
"""
Script: Backend/routes
Création: jojo, le 12/04/2025
"""

# Imports
import datetime
import uuid

import jwt
import pytz
from flask import Blueprint, render_template, jsonify, request, redirect, url_for, session

from app.extensions import SECRET_KEY, db
from app.externo.auth.models import User
from utils.auth import token_required

auth = Blueprint('auth', __name__, template_folder='templates')
usuario = Blueprint('usuario', __name__, template_folder='templates')


@auth.route('/entrar', methods=['GET'])
def login():
    return render_template('login.html')


def get_token(user):
    token = jwt.encode({
        'user_id': str(user.user_id),  # <- já faz isso no token, ok!
        'role': user.role,
        'exp': int((datetime.datetime.now(pytz.utc) + datetime.timedelta(hours=2)).timestamp())
    }, SECRET_KEY, algorithm='HS256')

    # ⚠️ Aqui está o erro: UUID precisa virar string!
    session['user_id'] = str(user.user_id)
    session['role'] = user.role
    return token


@auth.route('/entrar', methods=['POST'])
def send_login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        user = User.query.filter_by(email=email).first()
        print('Email:', email, 'Password:', password, type(password))

        if user and user.check_password(password):
            token = get_token(user)
            return jsonify({'token': token}), 200
        return jsonify({'message': 'Usuário ou senha inválida.'}), 401
    except Exception as e:
        print('Erro no login:', e)
        return jsonify({'message': 'Erro interno'}), 500


@auth.route('/registrar', methods=['GET'])
def register():
    return render_template('register.html')


@auth.route('/registrar', methods=['POST'])
def send_register():
    try:
        data = request.get_json() or {}
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        if not all([name, email, password]):
            return jsonify({"message": "Os campos nome, email e senha são obrigatorios."}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            try:
                new_user = User(name=name, email=email, password=password, role="user")
                db.session.add(new_user)
                db.session.commit()
                token = get_token(new_user)

                return jsonify({'token': token}), 200
            except Exception as e:
                db.session.rollback()
                return jsonify({"message": f"Falha ao adicionar o usuario no banco de dados. Erro: {str(e)}"}), 500
    except Exception as e:
        print(f"Erro na busca de dados: {str(e)}")
        return jsonify({"message": "Erro interno."}), 500


@auth.route('/registrar', methods=['DELETE'])
@token_required
def delete_register(current_user):
    if current_user.role == 'admin':
        user_id = request.get_json().get('user_id')

        if not user_id:
            return jsonify({"message": "ID de usuário não fornecido."}), 400

        try:
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                return jsonify({"message": "Usuário não encontrado no banco de dados."}), 404

            db.session.delete(user)
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Falha ao remover o usuário no banco de dados. Erro: {str(e)}"}), 500
    else:
        return jsonify({'message': 'Ação não autorizada.'}), 403


@auth.route('/entrar/recuperar')
def login_indentify():
    return render_template('login_indentify.html')


@auth.route('/sair', methods=('GET', 'POST'))
@token_required
def logout(current_user):
    if request.method == 'GET':
        session.clear()
        return redirect(url_for('auth.login'))
    elif request.method == 'POST':
        session.clear()
        return jsonify({'message': f'user {current_user.user_id} disconnected.'}), 200


@usuario.route('/')
@token_required
def users(current_user):
    if current_user.role == 'admin':
        users = User.query.all()
        return jsonify([{"user_id": u.user_id, "name": u.name, "email": u.email, "role": u.role} for u in users])
    else:
        user = User.query.filter_by(user_id=current_user.user_id).first()
        if user is None:
            return jsonify({"error": "User not found."}), 404
        return jsonify({"user_id": user.user_id, "name": user.name, "email": user.email, "role": user.role})


def get_user_name_by_id(user_id):
    user = User.query.filter_by(user_id=uuid.UUID(user_id)).first()
    return user.name
