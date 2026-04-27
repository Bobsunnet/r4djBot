from datetime import date

from pydantic import BaseModel

from db_handler.models.order import OrderStatus


class OrderBase(BaseModel):
    user_id: int  # tg user id
    date_start: date
    date_end: date
    work_days: int
    address: str
    description: str = ""
    cost: int | None = None
    status: OrderStatus = OrderStatus.PENDING


class Order(OrderBase):
    id: int


class OrderCreate(OrderBase):
    pass

class OrderUpdate(Order):
    user_id: int | None
