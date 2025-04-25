from flask import url_for, redirect

from app import create_app


# Cria e roda a aplicação Flask
app = create_app()
app.config['SESSION_PERMANENT'] = False

@app.route('/')
def index():
    return redirect(url_for('auth_bp.login'))


if __name__ == "__main__":
    app.run(debug=True)


