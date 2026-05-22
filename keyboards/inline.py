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


class OrderChangeStatusButton:
    def __init__(self, text: str, action: OrderAction):
        self.text = text
        self.action = action

    def __call__(self, order_id: int):
        btn = InlineKeyboardButton(
            text=self.text,
            callback_data=OrderCallbackData(
                order_id=order_id, action=self.action
            ).pack(),
        )
        return btn


class OrderDetailsButton:
    def __init__(self, text: str):
        self.text = text

    def __call__(self, order_id: int):
        btn = InlineKeyboardButton(
            text=self.text,
            callback_data=f"show_details_{order_id}",
        )
        return btn


confirm_btn = OrderChangeStatusButton(text="Confirm", action=OrderAction.CONFIRM)
cancel_btn = OrderChangeStatusButton(text="Cancel", action=OrderAction.CANCEL)
delete_btn = OrderChangeStatusButton(text="Delete", action=OrderAction.DELETE)
show_details_btn = OrderDetailsButton(text="Детальніше")


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
    """
    Inline keyboard for admin order(show_details, change_status, delete)
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [show_details_btn(order_id)],
            create_admin_order_buttons(order_id, status),
        ],
    )


def make_user_order_inline_kb(order_id: int, status: OrderStatus):
    """
    Inline keyboard for users order(show_details, edit_all, edit_items)
    """
    keyboard = [[show_details_btn(order_id)]]

    if status == OrderStatus.PENDING or status == OrderStatus.ACTIVE:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="Редагувати все",
                    callback_data=f"edit_order_all_{order_id}",
                )
            ]
        )
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="Редагувати обладнання",
                    callback_data=f"edit_order_items_{order_id}",
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def make_edit_choice_kb(order_id: int, status: OrderStatus):
    """
    Inline keyboard for users order (show_details, edit_choice)
    """
    keyboard = [[show_details_btn(order_id)]]

    if status == OrderStatus.PENDING or status == OrderStatus.ACTIVE:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="Редагувати",
                    callback_data=f"edit_choice_{order_id}",
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
