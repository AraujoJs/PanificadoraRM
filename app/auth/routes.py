# coding: UTF-8
"""
Script: Backend/routes
Création: jojo, le 12/04/2025
"""


# Imports
# Imports
from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, g, session
from app.extensions import db
from app.models import Usuario

from werkzeug.security import check_password_hash, generate_password_hash


auth = Blueprint('auth', __name__, url_prefix='/auth', template_folder='templates')

@auth.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        dados = request.get_json()
        username = dados['username']
        password = dados['password']
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES(?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for('auth.login'))

        flash(error)
    return render_template('auth/register.html')

@auth.route('/login', methods=('POST', 'GET'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
# Configurations globales


# Fonctions


# Programme principal
def main():
    pass


if __name__ == '__main__':
    main()
# Fin
