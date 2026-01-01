from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardMarkup


def make_main_kb():
    buttons = [
        [KeyboardButton(text="Catalogue"), KeyboardButton(text="Contacts/Help")],
    ]

    main_keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Use menu...",
    )
    return main_keyboard
