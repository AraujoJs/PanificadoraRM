# coding: UTF-8
"""
Script: PanificadoraRM/init_db
Création: jojo, le 11/04/2025
"""
# Imports
import logging
from app import create_app
from app.extensions import db

# Configurations globales
logging.getLogger().setLevel(logging.DEBUG)



# Fonctions

# Programme principal
def main():
    app = create_app()
    with app.app_context():
        db.create_all()
        print("Tabelas criadas com sucesso!")


if __name__ == '__main__':
    main()
# Fin
