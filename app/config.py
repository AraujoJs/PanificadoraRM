# coding: UTF-8
"""
Script: PanificadoraRM/config
Création: jojo, le 11/04/2025
"""
import os

SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
SQLALCHEMY_TRACK_MODIFICATIONS = False
