from pydantic import BaseModel


class UserBase(BaseModel):
    name: str
    surname: str
    user_id: int
    first_name: str | None
    last_name: str | None
    phone_number: str


class User(UserBase):
    id: int


class UserCreate(UserBase):
    pass
