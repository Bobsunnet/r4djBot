import json
from urllib.parse import quote

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo

from config import settings
from db_handler.models import OrderItemAssociation

contacts_button = KeyboardButton(text="Contacts")
register_button = KeyboardButton(text="Register")


keyboard_cancel = [
    [KeyboardButton(text="Back")],
    [KeyboardButton(text="Cancel")],
]


def make_user_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Catalogue"), contacts_button],
            [KeyboardButton(text="Order"), KeyboardButton(text="My orders")],
        ],
        resize_keyboard=True,
    )


def make_wo_auth_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[register_button], [contacts_button]],
        resize_keyboard=True,
    )


def make_manager_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Active"), KeyboardButton(text="Pending")],
            [KeyboardButton(text="Completed"), KeyboardButton(text="Cancelled")],
        ],
        resize_keyboard=True,
    )


def make_share_contact_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Поділитися контактом", request_contact=True)],
            *keyboard_cancel,
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def make_confirmation_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Confirm"), KeyboardButton(text="Cancel")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def make_cancel_kb():
    return ReplyKeyboardMarkup(
        keyboard=keyboard_cancel,
        resize_keyboard=True,
    )


def make_web_app_kb(work_days: int, items: list[OrderItemAssociation] | None = None):
    url_with_work_days = f"{settings.web_app_url}?work_days={work_days}"
    if items:
        items_data = [{"hash_code": item.item.hash_code, "quantity": item.quantity} for item in items]
        url_with_work_days += f"&items={quote(json.dumps(items_data))}"
    app_button = KeyboardButton(
        text="Обрати з Каталогу", web_app=WebAppInfo(url=url_with_work_days)
    )
    return ReplyKeyboardMarkup(
        keyboard=[
            *keyboard_cancel,
            [app_button],
        ],
        resize_keyboard=True,
    )
