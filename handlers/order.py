import json
import logging
import os

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from keyboards.inline_keyboard import order_inline_kb

order_router = Router()
logger = logging.getLogger(__name__)

# Mock manager ID (replace with real ID later)
MANAGER_ID = os.getenv("MANAGER_ID")


@order_router.message(Command("make_order"))
async def make_order(message: Message):
    """Open the Web App for catalogue browsing."""

    await message.answer(
        "Click the button below to browse the catalogue and add items to your cart:",
        reply_markup=order_inline_kb(),
    )


@order_router.message(F.content_type == "web_app_data")
async def handle_web_app_data(message: Message):
    """Process order data sent from the Web App."""
    try:
        # Parse the data from Web App
        data = json.loads(message.web_app_data.data)
        items = data.get("items", [])

        if not items:
            await message.answer("Your cart was empty. No order created.")
            return

        # Format order message
        order_text = f"📦 New Order from {message.from_user.full_name}\n\n"
        order_text += f"User ID: {message.from_user.id}\n"
        order_text += f"Username: @{message.from_user.username or 'N/A'}\n\n"
        order_text += "Items:\n"

        for item in items:
            quantity = item.get("quantity", 1)
            order_text += f"• {item['name']} × {quantity}\n"

        # Send confirmation to user
        await message.answer(
            "✅ Order received!\n\nYour order has been sent to the manager."
        )

        # Forward to manager
        try:
            await message.bot.send_message(chat_id=MANAGER_ID, text=order_text)
            logger.info(f"Order from {message.from_user.id} sent to manager")
        except Exception as e:
            logger.error(f"Failed to send order to manager: {e}")
            await message.answer(
                "⚠️ Order received but could not be forwarded to manager. "
                "Please contact support."
            )

    except json.JSONDecodeError:
        await message.answer("Failed to process order data. Please try again.")
        logger.error(f"Invalid JSON from web app: {message.web_app_data.data}")
    except Exception as e:
        await message.answer("An error occurred while processing your order.")
        logger.error(f"Error handling web app data: {e}")
