# coding: UTF-8
"""
Script: PanificadoraRM/auth/models
"""
import uuid

from sqlalchemy import UUID
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db


class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    role = db.Column(db.Text, nullable=False)

    sales = db.relationship('Sale', backref='user', lazy=True)

    def set_password(self, raw_password):
        """Armazena a senha como hash seguro (bcrypt via werkzeug)."""
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        """Verifica a senha comparando com o hash armazenado."""
        return check_password_hash(self.password, raw_password)
