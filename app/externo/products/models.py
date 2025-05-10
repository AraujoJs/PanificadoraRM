# coding: UTF-8
"""
Script: Backend/models
Création: jojo, le 12/04/2025
"""

# Imports
import uuid

from sqlalchemy import UUID

from app import db


class Product(db.Model):
    __tablename__ = 'products'

    product_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.Text, nullable=False)
    unit_price = db.Column(db.Numeric, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    sale_items = db.relationship('SaleItem', backref='product', lazy=True)
