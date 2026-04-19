# coding: UTF-8
"""
Script: PanificadoraRM/suppliers/models
"""
import uuid
from sqlalchemy import UUID
from app.extensions import db


class Supplier(db.Model):
    __tablename__ = 'suppliers'

    supplier_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.Text, nullable=False)
    contact = db.Column(db.Text, nullable=True)   # Nome do contato
    phone = db.Column(db.Text, nullable=True)
    email = db.Column(db.Text, nullable=True)

    stock_entries = db.relationship('StockEntry', backref='supplier', lazy=True)
