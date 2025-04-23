# coding: UTF-8
"""
Script: Backend/routes
Création: jojo, le 12/04/2025
"""
import datetime

# Imports
# Imports
import os
import uuid

import jwt
from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, g, session
from app.extensions import db, SECRET_KEY
from app.auth.models import User
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
import pytz

from utils.auth import token_required

auth_bp = Blueprint('auth_bp', __name__, template_folder='templates')
users_bp = Blueprint('user_bp', __name__, template_folder='templates')

@users_bp.route('/')
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

@auth_bp.route('/login', methods=('POST', 'GET'))
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            utc_now = datetime.datetime.now(pytz.utc)
            exp_time = utc_now + datetime.timedelta(hours=2)

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



@auth_bp.route('/register', methods=('GET', 'POST'))
def register():
    users = User.query.all()
    pass



@auth_bp.route('/logout')
@token_required
def logout(current_user):
    session.clear()
    return jsonify({"message": "Logout realizado com sucesso!"}), 200


@auth_bp.route('/users')
# @token_required
def users():
    usuarios = User.query.all()
    return jsonify(
        [{"user_id": u.user_id, "name": u.name, "email": u.email, "role": u.role}
         for u in usuarios])


def get_user_name_by_id(user_id):
    user = User.query.filter_by(user_id = uuid.UUID(user_id)).first()
    return user.name