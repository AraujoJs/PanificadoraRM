# coding: UTF-8
"""
Script: PanificadoraRM/init_db
Création: jojo, le 11/04/2025
"""
import datetime
# Imports
import logging

from app import create_app
from app.interno.models import Fornecedor, FornecedorProdutos, Compra

# Configurations globales
logging.getLogger().setLevel(logging.DEBUG)

from app import db
from app.externo.auth.models import User
import uuid


# Programme principal
def main():
    app = create_app()
    with app.app_context():
        db.create_all()

        u1 = User(
            user_id=uuid.UUID("768e0770-37d7-4485-8ef0-724a593db3d3"),
            name="João",
            email="joao@gmail.com",
            password="12345678",
            role="admin"
        )
    #     u2 = User(
    #         user_id=uuid.UUID("bdf9b718-1f36-435a-b39c-895c72987e32"),
    #         name="Maria",
    #         email="maria@gmail.com",
    #         password="87654321",
    #         role="user")
    #
    #     u3 = User(
    #         user_id=uuid.UUID("bdf9b718-1f36-435a-b39c-895c72983e55"),
    #         name="Toto",
    #         email="toto@gmail.com",
    #         password="11111111",
    #         role="user")
    #
        db.session.add(u1)
        db.session.commit()
    #
    #     print("Usuarios adicionados!")
    #
    #     print("Tabelas criadas com sucesso!")
    #
    #     # 1. Adicionar fornecedores
    #     fornecedores_data = [
    #         {"nome": "Coca-Cola Empresa", "contato": "(83)9999-9999", "categoria": "Alimentos"},
    #         {"nome": "Zé da farinha", "contato": "(83)8888-8888", "categoria": "Alimentos"},
    #         {"nome": "Granja zé Ramalho", "contato": "(83)7777-7777", "categoria": "Alimentos"},
    #     ]
    #
    #     fornecedores = []
    #     for f in fornecedores_data:
    #         fornecedor = Fornecedor(**f)
    #         fornecedores.append(fornecedor)
    #
    #     db.session.add_all(fornecedores)
    #     db.session.commit()
    #     print("Fornecedores adicionados.")
    #
    #     # 2. Adicionar produtos
    #     produtos_data = [
    #         {"nome": "Coca-Cola", "tipo": "Bebida", "fornecedor": fornecedores[0]},
    #         {"nome": "Schweppes", "tipo": "Bebida", "fornecedor": fornecedores[0]},
    #         {"nome": "Fanta", "tipo": "Bebida", "fornecedor": fornecedores[0]},
    #         {"nome": "Farinha", "tipo": "Ingrediente", "fornecedor": fornecedores[1]},
    #         {"nome": "Fermento para pão", "tipo": "Ingrediente", "fornecedor": fornecedores[1]},
    #         {"nome": "Frango", "tipo": "Ingrediente", "fornecedor": fornecedores[2]},
    #         {"nome": "Ovo", "tipo": "Ingrediente", "fornecedor": fornecedores[2]},
    #     ]
    #
    #     produtos = []
    #     for p in produtos_data:
    #         produto = FornecedorProdutos(nome=p["nome"], tipo=p["tipo"], fornecedor_id=p["fornecedor"].id)
    #         produtos.append(produto)
    #
    #     db.session.add_all(produtos)
    #     db.session.commit()
    #     print("Produtos adicionados.")
    #
    #     # 3. Adicionar compras
    #     data_hoje = datetime.date.today()
    #     compras_data = [
    #         {"produto": produtos[0], "quantidade": 5, "preco_unitario": 25.00, "validade_dias": 90},  # Coca-Cola
    #         {"produto": produtos[1], "quantidade": 4, "preco_unitario": 23.00, "validade_dias": 90},  # Schweppes
    #         {"produto": produtos[2], "quantidade": 3, "preco_unitario": 24.00, "validade_dias": 90},  # Fanta
    #         {"produto": produtos[3], "quantidade": 5, "preco_unitario": 23.00, "validade_dias": 180},  # Farinha
    #         {"produto": produtos[4], "quantidade": 4, "preco_unitario": 12.50, "validade_dias": 90},  # Fermento
    #         {"produto": produtos[5], "quantidade": 6, "preco_unitario": 20.00, "validade_dias": 15},  # Frango
    #         {"produto": produtos[6], "quantidade": 30, "preco_unitario": 0.80, "validade_dias": 20},  # Ovo
    #     ]
    #
    #     compras = []
    #     for c in compras_data:
    #         compra = Compra(
    #             produto_id=c["produto"].id,
    #             data_compra=data_hoje,
    #             validade=data_hoje + datetime.timedelta(days=c["validade_dias"]),
    #             quantidade=c["quantidade"],
    #             preco_unitario=c["preco_unitario"]
    #         )
    #         compras.append(compra)
    #
    #     db.session.add_all(compras)
    #     db.session.commit()
    #     print("Compras adicionadas com sucesso.")


if __name__ == '__main__':
    main()
# Fin
