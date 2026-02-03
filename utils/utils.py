import re
from collections import Counter
from datetime import date, datetime

from config import settings
from db_handler.models import Order, OrderStatus


def translate_status(status: OrderStatus) -> str:
    return {
        OrderStatus.PENDING: "Очікує",
        OrderStatus.ACTIVE: "Активне",
        OrderStatus.COMPLETED: "Завершено",
        OrderStatus.CANCELLED: "Скасовано",
    }[status]


def format_plural_form_text(work_days: int, titles: list[str]) -> str:
    """
    Returns the correct plural form of a word based on the number of work days.
    """
    if 11 <= work_days % 100 <= 19:
        return titles[2]

    last_digit = work_days % 10
    if last_digit == 1:
        return titles[0]
    if 2 <= last_digit <= 4:
        return titles[1]
    return titles[2]


def validate_name(name: str) -> bool:
    """
    Validates if the name/surname contains only letters, spaces, or hyphens.
    Length should be between 2 and 50 characters.
    """
    if not (2 <= len(name) <= 50):
        return False
    # Allows Cyrillic, Latin, spaces, and hyphens
    pattern = r"^[a-zA-Zа-яА-ЯёЁіІїЇєЄґҐ’'`\s-]+$"
    return bool(re.match(pattern, name))


def extract_date(date_str: str) -> tuple[str, str]:
    """
    Extracts the start and end dates from a date string in the format dd.mm.yy - dd.mm.yy.
    """
    start_date, end_date = date_str.split("-")
    return start_date.strip(), end_date.strip()


def work_days_validation(work_days: str) -> int:
    try:
        work_days = int(work_days)
        if work_days < 1:
            return 0

    except ValueError:
        return 0

    return work_days


def is_valid_number(phone_number: str) -> bool:
    return (
        phone_number.startswith("+380")
        and len(phone_number) == 13
        and phone_number[1:].isdigit()
    )


def validate_date(date_str: str) -> date| None:
    """validate date string in format some general formats"""
    formats = ["%d.%m.%Y", "%d.%m.%y", "%d-%m-%y", "%d-%m-%Y"]

    for format in formats:
        try:
            return datetime.strptime(date_str, format).date()
        except ValueError:
            pass

    return None


def create_orders_count_dict(orders: list[Order]) -> dict[tuple[int, int], int]:
    orders_count_dict = Counter([
        (order.date_start.year, order.date_start.month) for order in orders
    ])
    return orders_count_dict


def is_manager(user_id: int) -> bool:
    return user_id == settings.telegram.manager_id