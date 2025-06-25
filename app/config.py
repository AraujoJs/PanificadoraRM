# coding: UTF-8
"""
Script: PanificadoraRM/config
Création: jojo, le 11/04/2025
"""
import os

uri = os.environ.get('DATABASE_URL', '')
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

SQLALCHEMY_DATABASE_URI = uri
SQLALCHEMY_TRACK_MODIFICATIONS = False
