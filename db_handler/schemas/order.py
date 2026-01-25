from datetime import date

from pydantic import BaseModel

from db_handler.models.order import OrderStatus


class OrderBase(BaseModel):
    user_id: int  # tg user id
    date_start: date
    date_end: date
    work_days: int
    address: str
    description: str | None = None
    cost: int | None = None
    status: OrderStatus = OrderStatus.PENDING


class Order(OrderBase):
    id: int


class OrderCreate(OrderBase):
    pass
