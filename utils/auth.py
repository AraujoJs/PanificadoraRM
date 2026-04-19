# coding: UTF-8
"""
Script: Backend/auth
Création: jojo, le 13/04/2025
"""
from functools import wraps
from flask import request, jsonify
import jwt, os
from app.extensions import SECRET_KEY
from app.auth.models import User

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            parts = request.headers['Authorization'].split(" ")
            if len(parts) == 2:
                token = parts[1]

        if not token:
            return jsonify({'message': 'Token é necessário'}), 403

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id_str = payload['user_id']
            # JWT armazena user_id como string; converter para UUID para o SQLAlchemy
            import uuid as _uuid
            user_id = _uuid.UUID(user_id_str)
            current_user = User.query.filter_by(user_id=user_id).first()
            if not current_user:
                return jsonify({'message': 'Usuário não encontrado'}), 404

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido.'}), 401
        except Exception as e:
            return jsonify({'message': f'Erro de autenticação: {str(e)}'}), 401

        return f(current_user, *args, **kwargs)
    return decorated_function