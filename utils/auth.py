# coding: UTF-8
"""
Script: Backend/auth
Création: jojo, le 13/04/2025
"""
from functools import wraps

import jwt
from flask import request, jsonify, redirect, url_for

from app.auth.models import User
from app.extensions import SECRET_KEY


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]  # Pega o token após o "Bearer"

        if not token:
            return jsonify({'message': 'Token é necessário'}), 403

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']
            current_user = User.query.filter_by(user_id=user_id).first()
            if not current_user:
                return jsonify({'message': 'Usuário não encontrado'}), 404

        except jwt.ExpiredSignatureError:
            return redirect(url_for("auth.login"))
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token invalido.'}), 401

        return f(current_user, *args, **kwargs)

    return decorated_function
