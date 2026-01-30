from datetime import date

from utils import utils


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


def test_validate_name():
    """Test name validation with different patterns (Cyrillic, Latin, invalid chars)."""
    assert utils.validate_name("Олександр") is True
    assert utils.validate_name("Jean-Pierre") is True
    assert utils.validate_name("O'Connor") is True
    assert utils.validate_name("A") is False  # Too short
    assert utils.validate_name("ThisNameIsWayTooLongToBeValidAndShouldReturnFalseAccordingToLogic") is False
    assert utils.validate_name("User123") is False  # Numbers not allowed


def test_work_days_validation():
    """Test integer validation for work days input."""
    assert utils.work_days_validation("5") == 5
    assert utils.work_days_validation("0") == 0
    assert utils.work_days_validation("-1") == 0
    assert utils.work_days_validation("abc") == 0


def test_is_valid_number():
    """Test UA phone number format validation."""
    assert utils.is_valid_number("+380961234567") is True
    assert utils.is_valid_number("380961234567") is False  # Missing +
    assert utils.is_valid_number("+38096123456") is False   # Too short
    assert utils.is_valid_number("+3809612345678") is False # Too long
    assert utils.is_valid_number("+480961234567") is False  # Wrong prefix


def test_create_orders_count_dict():
    """Test the conversion of an order list to a (year, month) counter."""
    from datetime import date as dt_date
    from unittest.mock import MagicMock
    
    # Create mock orders with date_start attributes
    order1 = MagicMock()
    order1.date_start = dt_date(2024, 1, 15)
    
    order2 = MagicMock()
    order2.date_start = dt_date(2024, 1, 20)
    
    order3 = MagicMock()
    order3.date_start = dt_date(2024, 2, 5)
    
    orders = [order1, order2, order3]
    
    result = utils.create_orders_count_dict(orders)
    
    # Expectation: Jan 2024 has 2 orders, Feb 2024 has 1
    assert result[(2024, 1)] == 2
    assert result[(2024, 2)] == 1
    assert len(result) == 2
