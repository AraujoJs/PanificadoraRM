# coding: UTF-8
"""
Script: Backend/models
Création: jojo, le 12/04/2025
"""
import uuid

from sqlalchemy import UUID
from app.vendas.models import Sale, SaleItem
# Imports

from app.extensions import db

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    role = db.Column(db.Text, nullable=False)

    sales = db.relationship('Sale', backref='user', lazy=True)
    sale_items = db.relationship('SaleItem', backref='user', lazy=True)


    def check_password(self, user_password):
        return user_password == self.password