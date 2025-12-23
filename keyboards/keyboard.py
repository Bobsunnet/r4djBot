from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton


order_buttons = [
        [KeyboardButton(text="Catalogue")],
        [KeyboardButton(text="Contact Support")],
        [KeyboardButton(text="Cart")],
    ]

main_keyboard = ReplyKeyboardMarkup(
    keyboard=order_buttons,
    resize_keyboard=True
    )