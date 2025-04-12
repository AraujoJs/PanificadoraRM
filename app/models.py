# coding: UTF-8
"""
Script: PanificadoraRM/models
Création: jojo, le 11/04/2025
"""
# Imports
from app.extensions import db

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
