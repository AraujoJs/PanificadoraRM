# coding: UTF-8
"""
Script: PanificadoraRM/init_db
Création: jojo, le 11/04/2025
"""
# Imports
import logging
import uuid

from werkzeug.routing import UUIDConverter

from app import create_app
from app.extensions import db

# Configurations globales
logging.getLogger().setLevel(logging.DEBUG)


from app.products.models import Product
from app.sales.models import Sale, SaleItem
from app.auth.models import User
from app import db
from app.auth.models import User
import uuid


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

        db.session.execute(db.text("DELETE FROM sale_items"))
        db.session.execute(db.text("DELETE FROM sales"))
        db.session.execute(db.text("DELETE FROM users"))
        db.session.commit()

        u1 = User(
            user_id=uuid.UUID("768e0770-37d7-4485-8ef0-724a593db3d3"),
            name="João",
            email="joão@gmail.com",
            password="12345678",
            role="admin"
        )
        u2 = User(
            user_id=uuid.UUID("bdf9b718-1f36-435a-b39c-895c72987e32"),
            name="Maria",
            email="maria@gmail.com",
            password="87654321",
            role="user")

        db.session.add_all([u1, u2])
        db.session.commit()

        print("Usuarios adicionados!")

        db.session.query(Sale).delete()
        user_id = uuid.UUID("bdf9b718-1f36-435a-b39c-895c72987e32")
        user = User.query.filter_by(user_id=user_id).first()
        if user:
            sale_id = uuid.uuid4()

            s1 = Sale(sale_id=sale_id, total=35.0, payment_method="pix", user_id=user.user_id)
            db.session.add_all([s1])
            db.session.commit()
            print("Venda adicionada!")


            product = Product.query.filter_by(name="Coxinha").first()
            product_2 = Product.query.filter_by(name="Bolo formigueiro").first()

            i1 = SaleItem(quantity=5, subtotal=5.0, user_id=user_id, sale_id=sale_id, product_id=product.product_id)
            i2 = SaleItem(quantity=6, subtotal=6.0, user_id=user_id, sale_id=sale_id, product_id=product_2.product_id)

            db.session.add_all([i1, i2])
            db.session.commit()
            print("itens vendidos adicionados!")


        else:
            print("User invalido!")



if __name__ == '__main__':
    main()
# Fin
