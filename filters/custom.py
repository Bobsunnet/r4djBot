from aiogram.types import Message


def custom_filter(message: Message, command: str):
    return message.text.casefold().strip().lstrip("/") == command
