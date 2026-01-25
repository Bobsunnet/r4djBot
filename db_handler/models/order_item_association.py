from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .item import Item
    from .order import Order


class OrderItemAssociation(Base):
    __tablename__ = "order_item_association"
    __table_args__ = (
        UniqueConstraint("order_id", "item_hash_code", name="idx_unique_order_item"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    item_hash_code: Mapped[str] = mapped_column(
        ForeignKey("items.hash_code"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default="1"
    )
    unit_price: Mapped[int] = mapped_column(Integer, nullable=False)

    item: Mapped["Item"] = relationship(back_populates="orders_details")
    order: Mapped["Order"] = relationship(back_populates="items_details")
