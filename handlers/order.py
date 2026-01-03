import json
import logging

from aiogram import F, Router
from aiogram.types import Message

import config

order_router = Router()
logger = logging.getLogger(__name__)


@order_router.message(F.web_app_data)
async def handle_web_app_data(message: Message):
    """Process order data sent from the Web App."""
    try:
        # Parse the data from Web App
        data = json.loads(message.web_app_data.data)
        items = data.get("items", [])

        logger.info(f"ORDER FROM {message.from_user.id} received: {items}")

        if not items:
            await message.answer("Ваш кошик був порожнім. Немає замовлення.")
            return

        # Format order message
        order_text = f"Заказ від {message.from_user.full_name}\n\n"
        order_text += f"User ID: {message.from_user.id}\n"
        order_text += f"Username: @{message.from_user.username or 'N/A'}\n\n"
        order_text += "Items:\n"

        for item in items:
            quantity = item.get("quantity", 1)
            order_text += f"• {item['name']} × {quantity} шт.\n"

        # Send confirmation to user
        await message.answer(
            "✅ Замовлення прийнято!\n\nЗамовлення було надіслане менеджеру."
        )

        # Forward to manager
        try:
            if config.DEBUG:
                logger.info(f"Order text: {order_text}")
                # await message.bot.send_message(
                #     chat_id=config.MANAGER_ID, text=order_text
                # )
            else:
                await message.bot.send_message(
                    chat_id=config.MANAGER_ID, text=order_text
                )

            logger.info(f"Order from {message.from_user.id} sent to manager")
        except Exception as e:
            logger.error(f"Failed to send order to manager: {e}")
            await message.answer(
                "Замовлення прийнято, але не було надіслане менеджеру. "
                "Зверніться до менеджера."
            )

    except json.JSONDecodeError:
        await message.answer("Failed to process order data. Please try again.")
        logger.error(f"Invalid JSON from web app: {message.web_app_data.data}")
    except Exception as e:
        await message.answer("An error occurred while processing your order.")
        logger.error(f"Error handling web app data: {e}")
