# coding: UTF-8
import uuid
from sqlalchemy import UUID
from app.extensions import db


class Product(db.Model):
    __tablename__ = "products"

    product_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.Text, nullable=False)
    unit_of_measure = db.Column(db.Text, nullable=False, default="un")
    unit_price = db.Column(db.Numeric, nullable=True)
    stock = db.Column(db.Integer, nullable=False, default=0)
    supplier_id = db.Column(UUID(as_uuid=True), db.ForeignKey("suppliers.supplier_id"), nullable=True)

    supplier = db.relationship("Supplier", backref="products")
    stock_entry_items = db.relationship("StockEntryItem", lazy=True)
