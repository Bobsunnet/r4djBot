from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from db_handler.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    surname: Mapped[str] = mapped_column(String(128), nullable=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str] = mapped_column(String(256), nullable=True)
    first_name: Mapped[str] = mapped_column(String(256), nullable=True)
    last_name: Mapped[str] = mapped_column(String(256), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(32), nullable=True)

    def __repr__(self):
        return f"User(id={self.id}, name={self.name}, surname={self.surname}, first_name={self.first_name}, \
        user_id={self.user_id}, username={self.username}, phone_number={self.phone_number})"
