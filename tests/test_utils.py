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
