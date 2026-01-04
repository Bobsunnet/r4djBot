import json
import logging

from aiogram import F, Router
from aiogram.types import Message

import config
from db_handler.db_class import db_handler
from utils.utils import format_order_message

order_router = Router()
logger = logging.getLogger(__name__)


failed_to_send_order_message = "Не вдалося обробити ваше замовлення. Спробуйте ще раз, перезавнтаживши бота командою /start"


class UserNotFound(Exception):
    pass


def get_user_phone_number(user_id: int) -> str:
    user = db_handler.read_user_by_user_id(user_id)
    if not user:
        raise UserNotFound("User not found in database")

    return user["phone_number"]


@order_router.message(F.web_app_data)
async def handle_web_app_data(message: Message):
    """Process order data sent from the Web App."""
    try:
        data = json.loads(message.web_app_data.data)
        items = data.get("items", [])

        logger.info(f"ORDER FROM {message.from_user.id} received: {items}")

        if not items:
            await message.answer("Ваш кошик був порожнім. Немає замовлення.")
            return

        phone_number = get_user_phone_number(message.from_user.id)

        # Format order message
        order_text = format_order_message(
            user_full_name=message.from_user.full_name,
            username=message.from_user.username,
            phone_number=phone_number,
            items=items,
        )

        try:
            if config.DEBUG:
                logger.info(f"Order text:\n{order_text}")
            else:
                await message.bot.send_message(
                    chat_id=config.MANAGER_ID, text=order_text
                )
            await message.answer("✅ Замовлення прийнято!")
            if config.DEBUG:
                await message.answer(order_text)

            logger.info(f"Order from {message.from_user.id} sent to manager")
        except Exception as e:
            logger.error(f"Failed to send order to manager: {e}")
            await message.answer(
                "Замовлення прийнято, але не було надіслане менеджеру. "
                "Зверніться до менеджера."
            )

    except json.JSONDecodeError:
        await message.answer(failed_to_send_order_message)
        logger.error(f"Invalid JSON from web app: {message.web_app_data.data}")
    except Exception as e:
        await message.answer(failed_to_send_order_message)
        logger.error(f"Error handling web app data: {e}")
