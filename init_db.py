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


from app.produtos.models import Product
from app.vendas.models import Sale, SaleItem
from app.auth.models import User

# Programme principal
def main():
    app = create_app()
    with app.app_context():
        db.create_all()
        print("Tabelas criadas com sucesso!")

        db.session.query(Product).delete()

        p1 = Product(name="Coxinha", unit_price=5.0, stock=10)
        p2 = Product(name="Pão Francês", unit_price=1.0, stock=100)
        p3 = Product(name="Bolo formigueiro", unit_price=15.0, stock=5)

        db.session.add_all([p1, p2, p3])
        db.session.commit()
        print("Itens adicionados!")

if __name__ == '__main__':
    main()
# Fin
