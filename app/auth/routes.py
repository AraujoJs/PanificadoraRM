# coding: UTF-8
"""
Script: PanificadoraRM/auth/routes
"""
import datetime
import re
import jwt
import pytz
import uuid

from flask import Blueprint, render_template, jsonify, request, redirect, url_for, session

from app.auth.models import User
from app.extensions import db, SECRET_KEY
from utils.auth import token_required

auth = Blueprint('auth', __name__, template_folder='templates')
usuario = Blueprint('usuario', __name__, template_folder='templates')


@auth.route('/entrar', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                token = jwt.encode({
                    'user_id': str(user.user_id),
                    'role': user.role,
                    'exp': int((datetime.datetime.now(pytz.utc) + datetime.timedelta(hours=8)).timestamp())
                }, SECRET_KEY, algorithm='HS256')
                session['user_id'] = user.user_id
                session['role'] = user.role
                return jsonify({'token': token}), 200
            return jsonify({'message': 'Usuário ou senha inválida.'}), 401
        except Exception as e:
            print('Erro no login:', e)
            return jsonify({'message': 'Erro interno'}), 500
    return render_template('login.html')


@auth.route('/registrar', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            data = request.get_json() or {}
            name = data.get('name', '').strip()
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            role = data.get('role', 'user')

            # Validações
            if not name or len(name) < 2:
                return jsonify({'message': 'Nome deve ter pelo menos 2 caracteres.'}), 400
            if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
                return jsonify({'message': 'E-mail inválido.'}), 400
            if len(password) < 8:
                return jsonify({'message': 'Senha deve ter pelo menos 8 caracteres.'}), 400
            if role not in ('admin', 'user'):
                role = 'user'

            if User.query.filter_by(email=email).first():
                return jsonify({'message': 'E-mail já cadastrado.'}), 409

            new_user = User(name=name, email=email, role=role)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            return jsonify({'message': f'Usuário {name} cadastrado com sucesso!'}), 201

        except Exception as e:
            db.session.rollback()
            print('Erro no registro:', e)
            return jsonify({'message': 'Erro interno ao cadastrar usuário.'}), 500

    return render_template('register.html')


@auth.route('/entrar/recuperar')
def login_indentify():
    return render_template('login_indentify.html')


@auth.route('/sair', methods=['GET', 'POST'])
@token_required
def logout(current_user):
    session.clear()
    if request.method == 'GET':
        return redirect(url_for('auth.login'))
    return jsonify({'message': f'Usuário {current_user.name} desconectado.'}), 200


@usuario.route('/')
@token_required
def users(current_user):
    if current_user.role == 'admin':
        users = User.query.all()
        return jsonify([{"user_id": str(u.user_id), "name": u.name, "email": u.email, "role": u.role} for u in users])
    user = User.query.filter_by(user_id=current_user.user_id).first()
    if not user:
        return jsonify({"error": "Usuário não encontrado."}), 404
    return jsonify({"user_id": str(user.user_id), "name": user.name, "email": user.email, "role": user.role})


def get_user_name_by_id(user_id):
    user = User.query.filter_by(user_id=uuid.UUID(str(user_id))).first()
    return user.name if user else 'Desconhecido'