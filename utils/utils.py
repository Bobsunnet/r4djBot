def format_welcome_message(name: str) -> str:
    """
    Formats the welcome message for the user.
    """
    return f"Вітаємо, {name}. Оберіть одну з команд:"


def format_order_message(
    user_full_name: str, username: str, phone_number: str, items: list
) -> str:
    """
    Formats the order message with user details and items.
    """
    order_text = f"Заказ від {user_full_name} @{username or 'N/A'}\n"
    order_text += f"{phone_number or 'N/A'}\n\n"

    for item in items:
        quantity = item.get("quantity", 1)
        order_text += f"• {item['name']} × {quantity} шт.\n"

    return order_text
