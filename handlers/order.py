from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

order_router = Router()


class OrderState(StatesGroup):
    first_position = State()
    second_position = State()


# @order_router.message()
# async def order_one(message: Message, state: State):
#     await message.answer("Enter Fist position")
