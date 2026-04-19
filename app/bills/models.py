# coding: UTF-8
"""
Script: PanificadoraRM/bills/models
Controle de Contas a Pagar da padaria.
"""
import uuid
from datetime import date
from sqlalchemy import UUID
from app import db


class Bill(db.Model):
    """Conta a pagar — boleto, fornecedor, serviço, etc."""
    __tablename__ = 'bills'

    bill_id      = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description  = db.Column(db.Text, nullable=False)
    amount       = db.Column(db.Numeric, nullable=False)
    due_date     = db.Column(db.Date, nullable=False)        # Vencimento
    paid_date    = db.Column(db.Date, nullable=True)         # Data do pagamento (None = não pago)
    note         = db.Column(db.Text, nullable=True)

    # Vínculos opcionais: com fornecedor e/ou compra
    supplier_id     = db.Column(UUID(as_uuid=True), db.ForeignKey('suppliers.supplier_id'), nullable=True)
    stock_entry_id  = db.Column(UUID(as_uuid=True), db.ForeignKey('stock_entries.entry_id'), nullable=True)
    user_id         = db.Column(UUID(as_uuid=True), db.ForeignKey('users.user_id'), nullable=False)

    supplier    = db.relationship('Supplier', lazy=True)
    stock_entry = db.relationship('StockEntry', lazy=True)

    @property
    def status(self):
        """Calcula o status dinamicamente: pago / vencido / pendente."""
        if self.paid_date:
            return 'pago'
        if self.due_date and self.due_date < date.today():
            return 'vencido'
        return 'pendente'

    def to_dict(self):
        return {
            'bill_id':         str(self.bill_id),
            'description':     self.description,
            'amount':          float(self.amount),
            'due_date':        self.due_date.strftime('%Y-%m-%d') if self.due_date else None,
            'due_date_br':     self.due_date.strftime('%d/%m/%Y') if self.due_date else None,
            'paid_date':       self.paid_date.strftime('%Y-%m-%d') if self.paid_date else None,
            'paid_date_br':    self.paid_date.strftime('%d/%m/%Y') if self.paid_date else None,
            'status':          self.status,
            'note':            self.note,
            'supplier_id':     str(self.supplier_id) if self.supplier_id else None,
            'supplier_name':   self.supplier.name if self.supplier else None,
            'stock_entry_id':  str(self.stock_entry_id) if self.stock_entry_id else None,
        }
