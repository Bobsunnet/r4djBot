from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo

WEB_APP_URL = "https://madelaine-precongestive-rossana.ngrok-free.dev"


def make_main_kb():
    buttons = [
        [KeyboardButton(text="Catalogue"), KeyboardButton(text="Contacts/Help")],
        [KeyboardButton(text="Order", web_app=WebAppInfo(url=WEB_APP_URL))],
    ]

    main_keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Use menu...",
    )
    return main_keyboard
