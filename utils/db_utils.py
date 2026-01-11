from typing import Optional

from db_handler.db_class import db_handler
from exceptions import exceptions


def get_authorized_user(user_id: int) -> Optional[dict]:
    """
    Checks if the user is authorized (exists in the database).
    Returns the user data if authorized, otherwise None.
    """
    return db_handler.read_user_by_user_id(user_id)


def get_user_phone_number(user_id: int) -> str:
    user = get_authorized_user(user_id)
    if not user:
        raise exceptions.UserNotFound("User not found in database")

    return user["phone_number"]
