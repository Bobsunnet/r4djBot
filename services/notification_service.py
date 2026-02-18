from aiogram import Bot

from config import settings
from db_handler.models import Order, User
from keyboards.inline import make_admin_order_inline_kb
from utils import messages as ms
from utils.order_msg_builder import OrderAdminMsgBuilder, OrderUserMsgBuilder


async def notify_admin_new_order(bot: Bot, order: Order, user: User, was_edited=False):
    order_text = OrderAdminMsgBuilder(
        order=order,
        user=user,
        items=order.items_details,
        was_edited=was_edited,
    ).build_full_message()

    await bot.send_message(
        chat_id=settings.telegram.manager_id,
        text=order_text,
        reply_markup=make_admin_order_inline_kb(order_id=order.id, status=order.status),
    )


def build_user_confirmation_message(order: Order, was_edited=False):
    message_body = OrderUserMsgBuilder(
        order=order,
        items=order.items_details,
    ).build_full_message()
    message_header = ms.order_edited_message if was_edited else ms.order_processing_message
    return message_header + ". Слідкуйте за зміною статусу замовлення\n\n" + message_body

    
