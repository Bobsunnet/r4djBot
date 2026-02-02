from aiogram.filters import BaseFilter
from aiogram.types import Message, TelegramObject

from utils.utils import is_manager


class TextOrCommand(BaseFilter):
    def __init__(self, text: str):
        self.text_joined = self._make_text_joined(text)
    
    def _make_text_joined(self, text: str):
        return "_".join(text.split())

    async def __call__(self, message: Message) -> bool:
        if not message.text:
            return False
        
        message_text = self._make_text_joined(message.text.casefold().strip().lstrip("/"))
        return message_text == self.text_joined


class IsManager(BaseFilter):
    async def __call__(self, event: TelegramObject) -> bool:
        return is_manager(event.from_user.id)
