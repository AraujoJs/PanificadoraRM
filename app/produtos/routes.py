# coding: UTF-8
"""
Script: Backend/rotues
Création: jojo, le 12/04/2025
"""
from crypt import methods

from flask import Blueprint

# Imports


# Configurations globales
produtos_bp = Blueprint('produtos_bp', __name__)

@produtos_bp.route('/', methods=('GET', ))
def listar_produtos():
    pass
#     usuarios = Usuario.query.all()
#     return jsonify([{"id": u.id, "nome": u.nome} for u in usuarios])


# Routes