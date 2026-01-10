from utils import utils


def test_format_welcome_message():
    """
    Test that the welcome message is formatted correctly with the given name.
    """
    name = "Олександр"
    expected = (
        "Вітаємо, Олександр. Оберіть одну з команд /catalogue, /contacts, /order:"
    )
    result = utils.format_welcome_message(name)
    assert result == expected


def test_format_order_message():
    """
    Test that the order message is formatted correctly with items.
    """
    user_full_name = "Бобер Маслов"
    username = "bobermaslov"
    phone_number = "+380999999999"
    start_date = "01.01.24"
    end_date = "01.01.24"
    count = 1
    address = "Київ"
    items = [{"name": "Speaker", "quantity": 2}, {"name": "Mixer", "quantity": 1}]
    comment = "comment text"

    expected = (
        "Замовлення від Бобер Маслов @bobermaslov\n"
        "+380999999999\n\n"
        "Початок оренди: 01.01.24\n"
        "Кінець оренди: 01.01.24\n"
        "Кількість днів роботи: 1\n"
        "Адреса та час доставки/самовивіз: Київ\n\n"
        "Коментар: comment text\n\n"
        "• Speaker × 2 шт.\n"
        "• Mixer × 1 шт.\n"
    )

    result = utils.format_order_message(
        user_full_name,
        username,
        phone_number,
        start_date,
        end_date,
        count,
        address,
        comment,
        items,
    )
    assert result == expected


def test_extract_date():
    """
    Test that the extract_date function correctly extracts the start and end dates from a date string.
    """
    date_str = "01.01.24 - 01.01.24"
    expected = ("01.01.24", "01.01.24")
    result = utils.extract_date(date_str)
    assert result == expected


def test_validate_date():
    """
    Test that the validate_date function correctly validates a date string.
    """
    date_str = "01.01.24"
    expected = True
    result = utils.validate_date(date_str)
    assert result == expected
