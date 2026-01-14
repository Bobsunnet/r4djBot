from datetime import datetime

from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column

from db_handler.models.base import Base


class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(nullable=True)
    name: Mapped[str] = mapped_column(String(512))
    hash_code: Mapped[str] = mapped_column(String(10), primary_key=True)
    description: Mapped[str] = mapped_column(String(1024), nullable=True)
    price: Mapped[int] = mapped_column()
    amount: Mapped[int] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
