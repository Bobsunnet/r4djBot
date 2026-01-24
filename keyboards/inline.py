from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def make_order_inline_kb(order_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Confirm", callback_data=f"confirm_order_{order_id}"
                ),
                InlineKeyboardButton(
                    text="Cancel", callback_data=f"cancel_order_{order_id}"
                ),
            ],
        ],
    )
