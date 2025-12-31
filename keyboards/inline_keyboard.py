from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

# Web App URL - update this with your actual URL (ngrok or production)

WEB_APP_URL = "https://madelaine-precongestive-rossana.ngrok-free.dev"


def order_inline_kb():
    buttons = [
        [
            InlineKeyboardButton(
                text="🛒 Open Catalogue", web_app=WebAppInfo(url=WEB_APP_URL)
            )
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
