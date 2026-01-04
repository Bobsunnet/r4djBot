from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo

WEB_APP_URL = "https://madelaine-precongestive-rossana.ngrok-free.dev"


contacts_button = KeyboardButton(text="Contacts/Help")
register_button = KeyboardButton(text="Register")


def make_auth_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Catalogue"), contacts_button],
            [KeyboardButton(text="Order", web_app=WebAppInfo(url=WEB_APP_URL))],
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
