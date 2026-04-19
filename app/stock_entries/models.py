# coding: UTF-8
"""
Script: PanificadoraRM/stock_entries/models
"""
import uuid
from datetime import datetime
from sqlalchemy import UUID
from app.extensions import db


class StockEntry(db.Model):
    """Representa uma compra/entrada de estoque (de um fornecedor)."""
    __tablename__ = 'stock_entries'

    entry_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entry_date = db.Column(db.DateTime, default=datetime.now)
    total_cost = db.Column(db.Numeric, nullable=False, default=0)
    note = db.Column(db.Text, nullable=True)

    supplier_id = db.Column(UUID(as_uuid=True), db.ForeignKey('suppliers.supplier_id'), nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.user_id'), nullable=False)

    items = db.relationship('StockEntryItem', backref='entry', lazy=True)


class StockEntryItem(db.Model):
    """Item de uma entrada de estoque: produto, quantidade e custo unitário."""
    __tablename__ = 'stock_entry_items'

    item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quantity = db.Column(db.Integer, nullable=False)
    unit_cost = db.Column(db.Numeric, nullable=False)
    subtotal = db.Column(db.Numeric, nullable=False)

    entry_id = db.Column(UUID(as_uuid=True), db.ForeignKey('stock_entries.entry_id'), nullable=False)
    product_id = db.Column(UUID(as_uuid=True), db.ForeignKey('products.product_id'), nullable=False)

    product = db.relationship('Product', lazy=True, overlaps='stock_entry_items')
