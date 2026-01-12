from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from db_handler.models.base import Base


class Item(Base):
    __tablename__ = "items"

    name: Mapped[str] = mapped_column(String(512))
    hash_code: Mapped[str] = mapped_column(String(10), unique=True)
    desc: Mapped[str] = mapped_column(String(1024), nullable=True)
    price: Mapped[int] = mapped_column()
    amount: Mapped[int] = mapped_column()
