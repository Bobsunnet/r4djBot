from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db_handler.models.base import Base

from .order_item_association import order_item_association_table

if TYPE_CHECKING:
    from .order import Order


class Item(Base):
    __tablename__ = "items"
    row_order: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(512))
    hash_code: Mapped[str] = mapped_column(String(10), primary_key=True)
    description: Mapped[str] = mapped_column(String(1024), nullable=True)
    price: Mapped[int] = mapped_column(Integer)
    amount: Mapped[int] = mapped_column(Integer)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )

    orders: Mapped[list["Order"]] = relationship(
        secondary=order_item_association_table,
        back_populates="items",
    )
