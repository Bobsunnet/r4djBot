from utils.utils import format_order_message, format_welcome_message


def test_format_welcome_message():
    """
    Test that the welcome message is formatted correctly with the given name.
    """
    name = "Олександр"
    expected = "Вітаємо, Олександр. Оберіть одну з команд:"
    result = format_welcome_message(name)
    assert result == expected


def test_format_order_message():
    """
    Test that the order message is formatted correctly with items.
    """
    user_full_name = "Бобер Маслов"
    username = "bobermaslov"
    phone_number = "+380999999999"
    items = [{"name": "Speaker", "quantity": 2}, {"name": "Mixer", "quantity": 1}]

    expected = (
        "Заказ від Бобер Маслов @bobermaslov\n"
        "+380999999999\n\n"
        "• Speaker × 2 шт.\n"
        "• Mixer × 1 шт.\n"
    )

    result = format_order_message(user_full_name, username, phone_number, items)
    assert result == expected
