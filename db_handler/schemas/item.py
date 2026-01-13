from pydantic import BaseModel


class ItemBase(BaseModel):
    name: str
    hash_code: str
    desc: str
    amount: int
    price: int


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
