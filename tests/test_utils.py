from utils.utils import format_welcome_message


def test_format_welcome_message():
    """
    Test that the welcome message is formatted correctly with the given name.
    """
    name = "Олександр"
    expected = "Вітаємо, Олександр. Оберіть одну з команд:"
    result = format_welcome_message(name)
    assert result == expected
