from pydantic import BaseModel


class UserBase(BaseModel):
    name: str
    surname: str
    user_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str


class User(UserBase):
    id: int


class UserCreate(UserBase):
    pass
