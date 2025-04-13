# coding: UTF-8
"""
Script: Backend/extensions
Création: jojo, le 12/04/2025
"""


# Imports
import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
SECRET_KEY = os.getenv('SECRET_KEY')