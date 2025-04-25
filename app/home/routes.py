# coding: UTF-8
"""
Script: Backend/routes
Création: jojo, le 12/04/2025
"""

# Imports
from flask import Blueprint, render_template, session
from app.auth.models import User

home_bp = Blueprint('home', __name__, template_folder='templates')


@home_bp.route('/')
def home():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    return render_template('home.html', user=user)
