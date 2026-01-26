from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from db_handler.models import OrderStatus


def create_pending_buttons(order_id: int):
    return [
        InlineKeyboardButton(text="Confirm", callback_data=f"confirm_order_{order_id}"),
        InlineKeyboardButton(text="Cancel", callback_data=f"cancel_order_{order_id}"),
    ]


def create_active_buttons(order_id: int):
    return [
        InlineKeyboardButton(text="Cancel", callback_data=f"cancel_order_{order_id}"),
    ]


def create_completed_buttons(order_id: int):
    return [
        InlineKeyboardButton(text="Delete", callback_data=f"delete_order_{order_id}"),
    ]


def create_cancelled_buttons(order_id: int):
    return [
        InlineKeyboardButton(text="Delete", callback_data=f"delete_order_{order_id}"),
    ]


def create_order_buttons(order_id: int, status: OrderStatus):
    status_dict = {
        OrderStatus.PENDING: create_pending_buttons,
        OrderStatus.ACTIVE: create_active_buttons,
        OrderStatus.COMPLETED: create_completed_buttons,
        OrderStatus.CANCELLED: create_cancelled_buttons,
    }
    return status_dict.get(status)(order_id)


def make_admin_order_inline_kb(order_id: int, status: OrderStatus):
    return InlineKeyboardMarkup(
        inline_keyboard=[create_order_buttons(order_id, status)],
    )
