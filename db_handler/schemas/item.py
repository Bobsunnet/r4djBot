from pydantic import BaseModel


class ItemBase(BaseModel):
    name: str
    hash_code: str
    desc: str
    amount: int
    price: int


class Item(ItemBase):
    row_order: int
