from typing import List

from aiogram import Router
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from db_handler import crud
from db_handler.models import User
from filters import TextOrCommand

user_data_router = Router()

users_per_page = 2


class EmptyCallbackData(CallbackData, prefix='empty'):
    pass


class UserPaginationCallback(CallbackData, prefix='user_pagination'):
    page: int
    pages_count: int


def format_users_text(users: List[User]):
    if not users:
        return "The end of list"
    long_text = ""
    for user in users:
        text = f"Name: {user.name} {user.surname} @{user.username or 'N/A'}\n"
        text += f"Phone: {user.phone_number}\n"
        text += f"Orders count: {len(user.orders)}\n"
        long_text += text
        long_text += "____________________\n"
    return long_text


@user_data_router.message(TextOrCommand("users"))
async def show_users(message: Message, session: AsyncSession):
    users = await crud.get_users(session)
    pages_count = len(users) // users_per_page + 1
    builder = InlineKeyboardBuilder()
    # builder.add(InlineKeyboardButton(text="Previous", callback_data=EmptyCallbackData().pack()))
    builder.add(
        InlineKeyboardButton(
            text="Next",
            callback_data=UserPaginationCallback(page=1, pages_count=pages_count).pack(),
        )
    )
    await message.answer("Users list...", reply_markup=builder.as_markup())


@user_data_router.callback_query(UserPaginationCallback.filter())
async def show_users_page(callback_query: CallbackQuery, callback_data: UserPaginationCallback, session: AsyncSession):
    users = await crud.get_users(
        session,
        limit=users_per_page,
        offset=callback_data.page * users_per_page - users_per_page,
    )
    long_text = format_users_text(users)
    builder = InlineKeyboardBuilder()
    if callback_data.page > 1:
        builder.add(
            InlineKeyboardButton(
                text="Previous",
                callback_data=UserPaginationCallback(
                    page=callback_data.page - 1,
                    pages_count=callback_data.pages_count,
                ).pack(),
            )
        )
    if callback_data.page < callback_data.pages_count:
        builder.add(
            InlineKeyboardButton(
                text="Next",
                callback_data=UserPaginationCallback(
                    page=callback_data.page + 1,
                    pages_count=callback_data.pages_count,
                ).pack(),
            )
        )
    await callback_query.message.edit_text(long_text, reply_markup=builder.as_markup())


@user_data_router.callback_query(EmptyCallbackData.filter())
async def handle_empty_pagination(callback_query: CallbackQuery, callback_data: EmptyCallbackData, session: AsyncSession):
    await callback_query.answer()