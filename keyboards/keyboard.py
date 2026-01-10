from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo

from config import WEB_APP_URL

contacts_button = KeyboardButton(text="Contacts")
register_button = KeyboardButton(text="Register")


def make_auth_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Catalogue"), contacts_button],
            [KeyboardButton(text="Order")],
        ],
        resize_keyboard=True,
    )


def make_wo_auth_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[register_button], [contacts_button]],
        resize_keyboard=True,
    )


def make_share_contact_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Поділитися контактом", request_contact=True)],
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


def make_web_app_kb(work_days: int):
    url_with_work_days = f"{WEB_APP_URL}?work_days={work_days}"
    button = KeyboardButton(
        text="Обрати з Каталогу", web_app=WebAppInfo(url=url_with_work_days)
    )
    return ReplyKeyboardMarkup(
        keyboard=[
            [button],
        ],
        resize_keyboard=True,
    )
