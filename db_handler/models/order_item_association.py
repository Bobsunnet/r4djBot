from sqlalchemy import Column, ForeignKey, Integer, Table, UniqueConstraint

from .base import Base

order_item_association_table = Table(
    "order_item_association",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("order_id", ForeignKey("orders.id"), nullable=False),
    Column("item_hash_code", ForeignKey("items.hash_code"), nullable=False),
    Column("quantity", Integer, nullable=False),
    Column("unit_price", Integer, nullable=False),
    UniqueConstraint("order_id", "item_hash_code", name="idx_unique_order_item"),
)
