# coding: UTF-8
"""
Script: Panificadora-RM/rotas_compras
Création: jojo, le 07/05/2025
"""


# Imports
from flask import blueprints, Blueprint

from app.interno.models import Compra

compras = Blueprint('compras_bp', __name__)

@compras.route('/')
def get_compras():
    compras = Compra.query.all()
    return compras

