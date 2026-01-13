from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from db_handler.models.base import Base


class User(Base):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(128))
    surname: Mapped[str] = mapped_column(String(128), nullable=True)
    user_id: Mapped[int] = mapped_column(unique=True)
    first_name: Mapped[str] = mapped_column(String(256), nullable=True)
    last_name: Mapped[str] = mapped_column(String(256), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(32), nullable=True)

    def __repr__(self):
        return f"User(id={self.id}, name={self.name}, surname={self.surname}, first_name={self.first_name}, user_id={self.user_id}, phone_number={self.phone_number})"
