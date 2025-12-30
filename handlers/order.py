from typing import Any

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

order_router = Router()


class OrderState(StatesGroup):
    first_position = State()
    second_position = State()


@order_router.message(Command("order"))
async def start_order(message: Message, state: FSMContext):
    await state.set_state(OrderState.first_position)
    await message.answer("Enter First position")


@order_router.message(OrderState.first_position)
async def process_first_order(message: Message, state: FSMContext):
    await state.update_data(first_position=message.text)
    await state.set_state(OrderState.second_position)
    await message.answer(
        f"ok, your first position is {message.text}.\n\n Enter Second position"
    )


@order_router.message(OrderState.second_position)
async def process_second_order(message: Message, state: FSMContext):
    data = await state.update_data(second_position=message.text)
    await state.clear()
    await message.answer(f"ok, your second position is {message.text}.\n\n processing")
    await show_summary(message, data)


async def show_summary(message: Message, data: dict[str, Any]):
    first = data.get("first_position")
    second = data.get("second_position")
    await message.answer(f"Your order: \n{first} \n{second}")
