from unittest.mock import AsyncMock, patch

import pytest

from handlers.user_private import orders_list


@pytest.mark.asyncio
async def test_orders_list_no_orders():
    """
    Test scenario: User calls /orders but has no orders in the database.
    Expectation: Bot responds with 'У вас ще немає замовлень'.
    """
    # 1. Arrange: Create mock objects
    # AsyncMock is used for methods that need to be awaited (like message.answer)
    message = AsyncMock()
    message.from_user.id = 12345
    session = AsyncMock()

    # 2. Act: Patch the CRUD function to return an empty list
    # We use 'patch' to temporarily replace the crud function in the context of the handler
    with patch("handlers.user_private.crud.get_orders_by_userid", new_callable=AsyncMock) as mock_get_orders:
        mock_get_orders.return_value = []  # No orders found

        # Call the handler
        await orders_list(message, session)

    # 3. Assert: Verify the behavior
    # Check if the CRUD function was called with the correct ID
    mock_get_orders.assert_called_once_with(session=session, user_id=12345)
    
    # Check if the bot sent the correct message
    message.answer.assert_called_once_with("У вас ще немає замовлень")

@pytest.mark.asyncio
async def test_orders_list_with_orders():
    """
    Test scenario: User calls /orders and has existing orders.
    Expectation: Bot shows the month selection calendar.
    """
    message = AsyncMock()
    message.from_user.id = 12345
    session = AsyncMock()

    with patch("handlers.user_private.crud.get_orders_by_userid", new_callable=AsyncMock) as mock_get_orders:
        # Return a list with one item to simulate "has orders"
        mock_get_orders.return_value = [{"id": 1}] 

        # We also need to mock get_user_locale because it's called in the handler
        with patch("handlers.user_private.get_user_locale", new_callable=AsyncMock) as mock_locale:
            mock_locale.return_value = "uk" # Example locale

            await orders_list(message, session)

    # Assert: We expect message.answer to be called with the calendar keyboard
    message.answer.assert_called_once()
    args, kwargs = message.answer.call_args
    assert "Оберіть місяць" in args[0]
    assert "reply_markup" in kwargs
