# coding: UTF-8
"""
Script: PanificadoraRM/init_db
Création: jojo, le 11/04/2025
"""
# Imports
import logging

from app import create_app

# Configurations globales
logging.getLogger().setLevel(logging.DEBUG)

from app.products.models import Product
from app.sales.models import Sale, SaleItem
from app import db
from app.auth.models import User
import uuid


# Programme principal
def main():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Tabelas criadas com sucesso!")

        # db.session.execute(db.text("DELETE FROM sale_items"))
        # db.session.execute(db.text("DELETE FROM sales"))
        # db.session.execute(db.text("DELETE FROM users"))
        # db.session.query(Product).delete()
        # db.session.commit()

        p1 = Product(name="Coxinha", unit_price=5.0, stock=10)
        p2 = Product(name="Pão Francês", unit_price=1.0, stock=100)
        p3 = Product(name="Bolo formigueiro", unit_price=15.0, stock=5)

        db.session.add_all([p1, p2, p3])
        db.session.commit()

        print("Itens adicionados!")

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

        u3 = User(
            user_id=uuid.UUID("bdf9b718-1f36-435a-b39c-895c72983e55"),
            name="Toto",
            email="toto@gmail.com",
            password="11111111",
            role="user")

        db.session.add_all([u1, u2, u3])
        db.session.commit()

        print("Usuarios adicionados!")

        print("User Maria vendas:")
        user_id = u2.user_id
        user = User.query.filter_by(user_id=user_id).first()
        if user:
            sale_id = uuid.uuid4()
            s1 = Sale(sale_id=sale_id, total=0.0, user_id=user.user_id)

            quantity = 5
            i1 = SaleItem(
                quantity=quantity,
                product_id=p1.product_id,
                subtotal=(p1.unit_price * quantity),
                user_id=user_id,
                sale_id=sale_id)
            s1.total += float(i1.subtotal)

            quantity = 2
            i2 = SaleItem(
                quantity=quantity,
                subtotal=(p3.unit_price * quantity),
                user_id=user_id,
                sale_id=sale_id,
                product_id=p3.product_id)

            s1.total += float(i2.subtotal)
            payment_method = "pix"
            s1.payment_method = payment_method
            db.session.add(s1)
            db.session.commit()
            print("Venda 1 adicionada!")
            db.session.add_all([i1, i2])
            db.session.commit()
            print("Itens da venda 1 adicionados!")


            sale_id2 = uuid.uuid4()
            s2 = Sale(sale_id=sale_id2, total=0.0, user_id=user.user_id)

            quantity = 20
            i3 = SaleItem(
                quantity=quantity,
                product_id=p2.product_id,
                subtotal=(p2.unit_price * quantity),
                user_id=user_id,
                sale_id=sale_id2)

            s2.total += float(i3.subtotal)

            quantity = 2
            i4 = SaleItem(
                quantity=quantity,
                subtotal=(p3.unit_price * quantity),
                user_id=user_id,
                sale_id=sale_id2,
                product_id=p3.product_id)

            s2.total += float(i4.subtotal)
            payment_method = "Debito"
            s2.payment_method = payment_method
            db.session.add(s2)
            db.session.commit()
            print("Venda 2 adicionada!")
            db.session.add_all([i1, i2])
            db.session.commit()
            print("Itens da venda 2 adicionados!")

        else:
            print("User invalido!")

        print("User Pedro vendas:")
        user_id = u3.user_id
        user = User.query.filter_by(user_id=user_id).first()

        if user:
            sale_id = uuid.uuid4()
            s1 = Sale(sale_id=sale_id, total=0.0, user_id=user.user_id)

            quantity = 2
            i1 = SaleItem(
                quantity=quantity,
                product_id=p2.product_id,
                subtotal=(p2.unit_price * quantity),
                user_id=user_id,
                sale_id=sale_id)
            s1.total += float(i1.subtotal)

            quantity = 1
            i2 = SaleItem(
                quantity=quantity,
                subtotal=(p3.unit_price * quantity),
                user_id=user_id,
                sale_id=sale_id,
                product_id=p3.product_id)

            s1.total += float(i2.subtotal)
            payment_method = "Dinheiro"
            s1.payment_method = payment_method
            db.session.add(s1)
            db.session.commit()

            print("Venda 1 adicionada!")
            db.session.add_all([i1, i2])
            db.session.commit()
            print("Itens da venda 1 adicionados!")


            sale_id2 = uuid.uuid4()
            s2 = Sale(sale_id=sale_id2, total=0.0, user_id=user.user_id)

            quantity = 20
            i3 = SaleItem(
                quantity=quantity,
                product_id=p2.product_id,
                subtotal=(p2.unit_price * quantity),
                user_id=user_id,
                sale_id=sale_id2)

            s2.total += float(i3.subtotal)
            payment_method = "Pix"
            s2.payment_method = payment_method
            db.session.add(s2)
            db.session.commit()
            print("Venda 2 adicionada!")
            db.session.add(i1)
            db.session.commit()
            print("Itens da venda 2 adicionados!")

        else:
            print("User invalido!")


if __name__ == '__main__':
    main()
# Fin
