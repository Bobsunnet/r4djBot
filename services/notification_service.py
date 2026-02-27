from aiogram import Bot

from config import settings
from db_handler.models import Order, User
from keyboards.inline import make_admin_order_inline_kb
from utils.order_msg_builder import OrderPopupAdminMessage, OrderPopupUserMessage


class NotifiedManagers:
    def __init__(self, _ids: list[int] | set[int]):
        self._ids = set(_ids)

    def add_manager(self, manager_id: int):
        self._ids.add(manager_id)

    def remove_manager(self, manager_id: int):
        self._ids.discard(manager_id)

    def is_notified(self, manager_id: int) -> bool:
        return manager_id in self._ids

    def __iter__(self):
        return iter(self._ids)

    def __contains__(self, item):
        return item in self._ids

    def __len__(self):
        return len(self._ids)


managers_notification_ids = NotifiedManagers(settings.telegram.manager_ids)


async def notify_admin_new_order(bot: Bot, order: Order, user: User, was_edited=False):
    order_text = OrderPopupAdminMessage(
        order=order,
        user=user,
        items=order.items_details,
        was_edited=was_edited,
    ).build_full_message()

    for manager_id in managers_notification_ids:
        await bot.send_message(
            chat_id=manager_id,
            text=order_text,
            reply_markup=make_admin_order_inline_kb(order_id=order.id, status=order.status),
        )


def build_user_confirmation_message(order: Order, was_edited=False):
    return OrderPopupUserMessage(
        order=order,
        items=order.items_details,
        was_edited=was_edited,
    ).build_full_message()

    
