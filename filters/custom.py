from aiogram.filters import BaseFilter
from aiogram.types import Message, TelegramObject

from utils.utils import is_manager


class TextOrCommand(BaseFilter):
    def __init__(self, text: str):
        self.text = text

    async def __call__(self, message: Message) -> bool:
        if not message.text:
            return False
        return message.text.casefold().strip().lstrip("/") == self.text


class IsManager(BaseFilter):
    async def __call__(self, event: TelegramObject) -> bool:
        return is_manager(event.from_user.id)
