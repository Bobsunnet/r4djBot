from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton


def make_main_kb():
    buttons = [
        [KeyboardButton(text="Catalogue"), KeyboardButton(text="Contacts")],
        [KeyboardButton(text="Cart")],
    ]

    main_keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Use menu..."
        )
    return main_keyboard


def create_spec_kb():
    buttons = [
        [KeyboardButton(text="Send Geo", request_location=True)],
        [KeyboardButton(text="Send Contacts", request_contact=True)],
    ]

    spec_keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Use menu..."
        )
    return spec_keyboard