import enum

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from db_handler.models import OrderStatus


class OrderAction(enum.Enum):
    CONFIRM = "confirm"
    CANCEL = "cancel"
    DELETE = "delete"


class OrderCallbackData(CallbackData, prefix="order"):
    order_id: int
    action: OrderAction


class OrderInlineButton:
    def __init__(self, text: str, action: OrderAction):
        self.text = text
        self.action = action

    def __call__(self, order_id: int):
        btn = InlineKeyboardButton(
            text=self.text,
            callback_data=OrderCallbackData(order_id=order_id, action=self.action).pack(),
        )
        return btn


confirm_btn = OrderInlineButton(text="Confirm", action=OrderAction.CONFIRM)
cancel_btn = OrderInlineButton(text="Cancel", action=OrderAction.CANCEL)
delete_btn = OrderInlineButton(text="Delete", action=OrderAction.DELETE)


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
            [InlineKeyboardButton(
            text="Show more",
            callback_data=f"show_details_{order_id}",
        )],
            create_admin_order_buttons(order_id, status),
        ],
    )


def make_user_order_inline_kb(order_id: int, status: OrderStatus):
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(
            text="Show more",
            callback_data=f"show_details_{order_id}",
        )]],
    )
