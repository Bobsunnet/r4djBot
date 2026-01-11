import re
from datetime import datetime


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


def format_welcome_message(name: str) -> str:
    """
    Formats the welcome message for the user.
    """
    return f"Вітаємо, {name}. Оберіть одну з команд /catalogue, /contacts, /order:"


def format_order_message(
    user_full_name: str,
    username: str,
    phone_number: str,
    start_date: str,
    end_date: str,
    count: int,
    address: str,
    comment: str,
    items: list,
) -> str:
    """
    Formats the order message with user details and items.
    """
    order_text = f"Замовлення від {user_full_name} @{username or 'N/A'}\n"
    order_text += f"{phone_number or 'N/A'}\n\n"
    order_text += f"Початок оренди: {start_date}\n"
    order_text += f"Кінець оренди: {end_date}\n"
    order_text += f"Кількість днів роботи: {count}\n"
    order_text += f"Адреса та час доставки/самовивіз: {address}\n\n"
    order_text += f"Коментар: {comment}\n\n"
    for item in items:
        quantity = item.get("quantity", 1)
        order_text += f"• {item['name']} × {quantity} шт.\n"

    return order_text


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


def validate_date(date_str: str) -> bool:
    """validate date string in format some general formats"""
    formats = ["%d.%m.%y", "%d.%m.%Y", "%d-%m-%y", "%d-%m-%Y"]

    for format in formats:
        try:
            datetime.strptime(date_str, format)
            return True
        except ValueError:
            pass
    return False
