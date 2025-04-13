# coding: UTF-8
"""
Script: Backend/routes
Création: jojo, le 12/04/2025
"""
import datetime

# Imports
# Imports
import os

import jwt
from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, g, session
from app.extensions import db, SECRET_KEY
from app.auth.models import User
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
import pytz

from utils.auth import token_required

auth = Blueprint('auth', __name__, template_folder='templates')

@auth.route('/login', methods=('POST', 'GET'))
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            utc_now = datetime.datetime.now(pytz.utc)
            exp_time = utc_now + datetime.timedelta(hours=1)

            token = jwt.encode({
                'user_id': str(user.user_id),
                'role': user.role,
                'exp': int(exp_time.timestamp())
            }, SECRET_KEY, algorithm='HS256')

            session['user_id'] = user.user_id
            session['role'] = user.role
            return jsonify({'token': token}), 200

        return jsonify({'message': 'Credenciais inválidas.'}), 401
    elif request.method == 'GET':
        return render_template('auth/login.html')
    return jsonify({'message': 'Método não permitido.'}), 405



@auth.route('/register', methods=('GET', 'POST'))
def register():
    usuarios = User.query.all()
    pass



@auth.route('/logout')
@token_required
def logout(current_user):
    session.clear()
    return jsonify({"message": "Logout realizado com sucesso!"}), 200


@auth.route('/users')
def get_users():
    usuarios = User.query.all()
    return jsonify(
        [{"user_id": u.user_id, "name": u.name, "email": u.email, "password": u.password, "role": u.role}
         for u in usuarios])