from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from db_handler.models import OrderStatus


class OrderInlineButton:
    def __init__(self, text: str, callback_data: str):
        self.text = text
        self.callback_data = callback_data

    def __call__(self, order_id: int):
        return InlineKeyboardButton(
            text=self.text,
            callback_data=f"{self.callback_data}_{order_id}",
        )


confirm_btn = OrderInlineButton(text="Confirm", callback_data="confirm_order")
cancel_btn = OrderInlineButton(text="Cancel", callback_data="cancel_order")
delete_btn = OrderInlineButton(text="Delete", callback_data="delete_order")

show_details_btn = OrderInlineButton(text="Show more", callback_data="show_details")


def create_pending_buttons(order_id: int):
    return [
        confirm_btn(order_id),
        cancel_btn(order_id),
    ]


def create_active_buttons(order_id: int):
    return [
        cancel_btn(order_id),
    ]


def create_completed_buttons(order_id: int):
    return [
        delete_btn(order_id),
    ]


def create_cancelled_buttons(order_id: int):
    return [
        confirm_btn(order_id),
        delete_btn(order_id),
    ]


def create_admin_order_buttons(order_id: int, status: OrderStatus):
    status_dict = {
        OrderStatus.PENDING: create_pending_buttons,
        OrderStatus.ACTIVE: create_active_buttons,
        OrderStatus.COMPLETED: create_completed_buttons,
        OrderStatus.CANCELLED: create_cancelled_buttons,
    }
    return status_dict.get(status)(order_id)


def make_admin_order_inline_kb(order_id: int, status: OrderStatus):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [show_details_btn(order_id)],
            create_admin_order_buttons(order_id, status),
        ],
    )


def make_user_order_inline_kb(order_id: int, status: OrderStatus):
    return InlineKeyboardMarkup(
        inline_keyboard=[[show_details_btn(order_id)]],
    )
