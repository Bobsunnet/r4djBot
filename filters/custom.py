from aiogram.filters import BaseFilter
from aiogram.types import Message, TelegramObject

from utils.utils import is_manager


class TextOrCommand(BaseFilter):
    """
    Filter to check if the message text or command matches a specific string.

    The filter normalizes both the target text and the message content by 
    converting to lowercase, stripping whitespace and leading slashes, 
    and joining words with underscores.
    """
    def __init__(self, text: str):
        """
        Initialize the filter with the target text.
        
        :param text: The string to compare against.
        """
        self.text_joined = self._make_text_joined(text)
    
    def _make_text_joined(self, text: str) -> str:
        """
        Normalize the text by joining words with underscores.
        
        :param text: Input string.
        :return: Normalized string.
        """
        return "_".join(text.split())

    async def __call__(self, message: Message) -> bool:
        """
        Check if the message text or command matches the target normalized text.
        
        :param message: The message object.
        :return: True if matches, False otherwise.
        """
        if not message.text:
            return False
        
        message_text = self._make_text_joined(message.text.casefold().strip().lstrip("/"))
        return message_text == self.text_joined


class IsManager(BaseFilter):
    async def __call__(self, event: TelegramObject) -> bool:
        return is_manager(event.from_user.id)
