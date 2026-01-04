def format_welcome_message(name: str) -> str:
    """
    Formats the welcome message for the user.
    """
    return f"Вітаємо, {name}. Оберіть одну з команд:"


def format_order_message(
    user_full_name: str,
    username: str,
    phone_number: str,
    start_date: str,
    end_date: str,
    count: int,
    address: str,
    items: list,
) -> str:
    """
    Formats the order message with user details and items.
    """
    order_text = f"Заказ від {user_full_name} @{username or 'N/A'}\n"
    order_text += f"{phone_number or 'N/A'}\n\n"
    order_text += f"Початок оренди: {start_date}\n"
    order_text += f"Кінець оренди: {end_date}\n"
    order_text += f"Кількість днів роботи: {count}\n"
    order_text += f"Адреса доставки/самовивіз: {address}\n\n"

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
