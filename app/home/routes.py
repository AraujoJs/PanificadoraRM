# coding: UTF-8
"""
Script: Backend/routes
Création: jojo, le 12/04/2025
"""

# Imports
from flask import Blueprint, render_template, session, redirect, url_for, jsonify
from app.auth.models import User
from utils.auth import token_required

home_bp = Blueprint('home', __name__, template_folder='templates')


@home_bp.route('/')
def home():
    user_id = session.get('user_id')
    if not user_id:
        redirect(url_for('auth_bp.login'))

    user = User.query.get(user_id)
    if not user:
        session.clear()
        return redirect(url_for('auth_bp.login'))

    return render_template('home.html', user=user)

@home_bp.route('/api/home')
@token_required
def api_home(current_user):
    return jsonify({
        'user_id': current_user.user_id,
        'email': current_user.email,
        'role': current_user.role
    })