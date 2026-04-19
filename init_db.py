# coding: UTF-8
"""
Script: PanificadoraRM/init_db
Recria o banco de dados com dados de exemplo de uma padaria real.
"""
import logging
import uuid

from app import create_app
from app.products.models import Product
from app.suppliers.models import Supplier
from app.stock_entries.models import StockEntry, StockEntryItem
from app.bills.models import Bill
from app import db
from app.auth.models import User

logging.getLogger().setLevel(logging.DEBUG)


def main():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("[OK] Tabelas criadas!")

        # ── Fornecedores ──────────────────────────────────────────────────
        f1 = Supplier(
            name="Moinho Sao Paulo",
            contact="Paulo Moreira",
            phone="(11) 91111-2222",
            email="vendas@moinhsp.com"
        )
        f2 = Supplier(
            name="Atacadista Central",
            contact="Carla Alves",
            phone="(11) 93333-4444",
            email="pedidos@atacentral.com"
        )
        f3 = Supplier(
            name="Distribuidora Norte",
            contact="Ricardo Lima",
            phone="(11) 95555-6666",
            email="contato@distnorte.com"
        )
        db.session.add_all([f1, f2, f3])
        db.session.commit()
        print("[OK] Fornecedores criados!")

        # ── Materiais / Insumos da Padaria ───────────────────────────────
        # (name, unit_of_measure, stock_inicial, supplier)
        materiais = [
            ("Farinha de Trigo",   "kg",     0, f1.supplier_id),
            ("Acucar Refinado",    "kg",     0, f1.supplier_id),
            ("Fermento Biologico", "pacote", 0, f1.supplier_id),
            ("Sal Refinado",       "kg",     0, f1.supplier_id),
            ("Manteiga",           "kg",     0, f2.supplier_id),
            ("Ovos",               "duzia",  0, f2.supplier_id),
            ("Leite Integral",     "L",      0, f2.supplier_id),
            ("Chocolate em Po",    "kg",     0, f3.supplier_id),
            ("Oleo de Soja",       "L",      0, f3.supplier_id),
            ("Embalagens Saco",    "caixa",  0, f3.supplier_id),
        ]
        produtos = []
        for name, unit, stock, supp_id in materiais:
            p = Product(name=name, unit_of_measure=unit, stock=stock, supplier_id=supp_id)
            db.session.add(p)
            produtos.append(p)
        db.session.commit()
        print(f"[OK] {len(produtos)} materiais cadastrados!")

        # ── Usuarios ──────────────────────────────────────────────────────
        u1 = User(name="Joao", email="joao@panificadora.com", role="admin")
        u1.set_password("admin1234")

        u2 = User(name="Maria", email="maria@panificadora.com", role="user")
        u2.set_password("maria1234")

        db.session.add_all([u1, u2])
        db.session.commit()
        print("[OK] Usuarios criados!")


        # ── Entrada 1: Compra de farinhas e acucar no Moinho SP ───────────
        p_farinha  = produtos[0]  # Farinha de Trigo
        p_acucar   = produtos[1]  # Acucar
        p_sal      = produtos[3]  # Sal

        eid1 = uuid.uuid4()
        e1 = StockEntry(entry_id=eid1, supplier_id=f1.supplier_id,
                        user_id=u1.user_id, note="Compra mensal de base")
        ei1 = StockEntryItem(entry_id=eid1, product_id=p_farinha.product_id,  quantity=50, unit_cost=3.50,  subtotal=175.0)
        ei2 = StockEntryItem(entry_id=eid1, product_id=p_acucar.product_id,   quantity=20, unit_cost=4.20,  subtotal=84.0)
        ei3 = StockEntryItem(entry_id=eid1, product_id=p_sal.product_id,      quantity=5,  unit_cost=1.80,  subtotal=9.0)
        e1.total_cost = 175.0 + 84.0 + 9.0
        p_farinha.stock += 50
        p_acucar.stock  += 20
        p_sal.stock     += 5
        db.session.add_all([e1, ei1, ei2, ei3])
        db.session.commit()
        print("[OK] Entrada 1 registrada (Moinho Sao Paulo)!")

        # ── Entrada 2: Compra de ovos, manteiga e leite no Atacadista ─────
        p_manteiga = produtos[4]  # Manteiga
        p_ovos     = produtos[5]  # Ovos
        p_leite    = produtos[6]  # Leite

        eid2 = uuid.uuid4()
        e2 = StockEntry(entry_id=eid2, supplier_id=f2.supplier_id,
                        user_id=u1.user_id, note="Reposicao semanal - frios e ovos")
        ei4 = StockEntryItem(entry_id=eid2, product_id=p_manteiga.product_id, quantity=10, unit_cost=22.00, subtotal=220.0)
        ei5 = StockEntryItem(entry_id=eid2, product_id=p_ovos.product_id,     quantity=15, unit_cost=14.50, subtotal=217.5)
        ei6 = StockEntryItem(entry_id=eid2, product_id=p_leite.product_id,    quantity=20, unit_cost=5.00,  subtotal=100.0)
        e2.total_cost = 220.0 + 217.5 + 100.0
        p_manteiga.stock += 10
        p_ovos.stock     += 15
        p_leite.stock    += 20
        db.session.add_all([e2, ei4, ei5, ei6])
        db.session.commit()
        print("[OK] Entrada 2 registrada (Atacadista Central)!")

        # ── Entrada 3: Chocolate e oleo na Distribuidora Norte ─────────────
        p_choco = produtos[7]  # Chocolate
        p_oleo  = produtos[8]  # Oleo

        eid3 = uuid.uuid4()
        e3 = StockEntry(entry_id=eid3, supplier_id=f3.supplier_id,
                        user_id=u2.user_id, note="Compra especial - confeitaria")
        ei7 = StockEntryItem(entry_id=eid3, product_id=p_choco.product_id, quantity=5,  unit_cost=18.00, subtotal=90.0)
        ei8 = StockEntryItem(entry_id=eid3, product_id=p_oleo.product_id,  quantity=10, unit_cost=7.50,  subtotal=75.0)
        e3.total_cost = 90.0 + 75.0
        p_choco.stock += 5
        p_oleo.stock  += 10
        db.session.add_all([e3, ei7, ei8])
        db.session.commit()
        print("[OK] Entrada 3 registrada (Distribuidora Norte)!")

        total_gasto = e1.total_cost + e2.total_cost + e3.total_cost
        print(f"\n[OK] Total gasto em compras: R$ {total_gasto:.2f}")

        # ── Contas a Pagar ────────────────────────────────────────────────
        from datetime import date, timedelta
        hoje = date.today()
        b1 = Bill(
            description=f"Boleto Referente a Entrada 1 (Moinho SP)",
            amount=e1.total_cost,
            due_date=hoje - timedelta(days=2), # Vencida
            supplier_id=f1.supplier_id,
            stock_entry_id=eid1,
            user_id=u1.user_id,
            note="Boleto 30 dias"
        )
        b2 = Bill(
            description=f"Conta Luz da Padaria",
            amount=350.00,
            due_date=hoje + timedelta(days=5), # Pendente
            user_id=u1.user_id
        )
        b3 = Bill(
            description="Boleto Ref. Entrada 2 (Atacadista Central)",
            amount=e2.total_cost,
            due_date=hoje - timedelta(days=10),
            paid_date=hoje - timedelta(days=9), # Paga
            supplier_id=f2.supplier_id,
            stock_entry_id=eid2,
            user_id=u1.user_id
        )
        db.session.add_all([b1, b2, b3])
        db.session.commit()
        print("[OK] Contas a pagar adicionadas!")


        print("\n--- Credenciais de acesso ---")
        print("  Admin -> joao@panificadora.com / admin1234")
        print("  User  -> maria@panificadora.com / maria1234")


if __name__ == '__main__':
    main()
