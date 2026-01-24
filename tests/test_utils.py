from datetime import date

from db_handler.schemas.order import Order
from db_handler.schemas.user import User
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
    user = User(
        id=1,
        name="Бобер",
        surname="Маслов",
        username="bobermaslov",
        phone_number="+380999999999",
        user_id=123456789,
    )
    order = Order(
        id=1,
        user_id=1,
        date_start=utils.validate_date("01.01.24"),
        date_end=utils.validate_date("02.01.24"),
        work_days=1,
        address="Київ",
        description="comment text",
    )
    items = [{"name": "Speaker", "quantity": 2}, {"name": "Mixer", "quantity": 1}]

    expected = (
        "Замовлення від Бобер Маслов @bobermaslov\n"
        "Статус: pending\n"
        "+380999999999\n\n"
        "Початок оренди: 2024-01-01\n"
        "Кінець оренди: 2024-01-02\n"
        "Кількість днів роботи: 1\n"
        "Адреса та час доставки/самовивіз: Київ\n\n"
        "Коментар: comment text\n\n"
        "• Speaker × 2 шт.\n"
        "• Mixer × 1 шт.\n"
    )

    result = utils.format_order_message_for_admin(user, order, items)

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
    expected = date(2024, 1, 1)
    result = utils.validate_date(date_str)

    assert result == expected
