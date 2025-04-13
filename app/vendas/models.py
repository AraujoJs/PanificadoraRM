# coding: UTF-8
"""
Script: Backend/models
Création: jojo, le 12/04/2025
"""
import uuid
from datetime import datetime

from sqlalchemy import UUID

from app import db


# Imports

class Sale(db.Model):
    __tablename__ = 'sales'

    sale_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sale_datetime = db.Column(db.DateTime, default=datetime.now())
    total = db.Column(db.Numeric, nullable=False)
    payment_method = db.Column(db.Text, nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.user_id'), nullable=False)

    sale_items = db.relationship('SaleItem', backref='sale', lazy=True)


class SaleItem(db.Model):
    __tablename__ = 'sale_items'

    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Numeric, nullable=False)

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.user_id'), nullable=False)
    sale_id = db.Column(UUID(as_uuid=True), db.ForeignKey('sales.sale_id'), nullable=False)
    product_id = db.Column(UUID(as_uuid=True), db.ForeignKey('products.product_id'), nullable=False)