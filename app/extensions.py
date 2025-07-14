# coding: UTF-8
"""
Script: Backend/extensions
Création: jojo, le 12/04/2025
"""


# Imports
import os

from flask.cli import load_dotenv
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

db = SQLAlchemy()
SECRET_KEY = os.getenv('SECRET_KEY')