# coding: UTF-8
"""
Script: PanificadoraRM/run
Création: jojo, le 11/04/2025
"""
# Imports
import logging
from app.app import app


# Configurations globales
logging.getLogger().setLevel(logging.DEBUG)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
# Fin
