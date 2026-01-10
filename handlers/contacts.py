from aiogram import Router
from aiogram.types import Message

from filters import TextOrCommand

contacts_router = Router()

contacts_reply_msg = """
Менеджер 👉 t.me/rent4djmanager

📍 Графік роботи складу:
11:00–18:00 щоденно.
Перед виїздом, будь ласка, повідомляйте за 1 годину.
- видача/повернення/доставка в неробочий час, оплачується додатково.

📍 Геолокація складу:
https://maps.app.goo.gl/Qxrg4aTEkYYxN4Ti8

❗️ При зворотній відправці обладнання курʼєром прохання вказувати виключно цю геолокацію.
"""


@contacts_router.message(TextOrCommand("contacts"))
async def cmd_contacts(message: Message):
    await message.answer(contacts_reply_msg)
