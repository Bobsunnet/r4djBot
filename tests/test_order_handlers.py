import json
from unittest.mock import AsyncMock, patch, MagicMock
import pytest
from aiogram.fsm.context import FSMContext
from handlers.order import order_final, OrderStates, order_edit

@pytest.mark.asyncio
async def test_order_states_isolation():
    """Verify that OrderStates does not have the shared order_for_edit attribute anymore."""
    assert not hasattr(OrderStates, "order_for_edit")


@pytest.mark.asyncio
async def test_order_final_empty_items_no_crash():
    """Verify that submitting an empty order doesn't crash and clears state."""
    message = AsyncMock()
    message.web_app_data.data = json.dumps({"items": []})
    state = AsyncMock(spec=FSMContext)
    state.get_data.return_value = {}
    session = AsyncMock()
    
    # Should not raise UnboundLocalError
    await order_final(message, state, session)
    
    # Check that it answered with error message and cleared state
    message.answer.assert_called()
    args, kwargs = message.answer.call_args
    assert "Ви не вибрали жодної позиції обладнання" in args[0]
    state.clear.assert_called_once()


@pytest.mark.asyncio
async def test_order_edit_sets_state_properly():
    """Verify that order_edit stores order_id in state data, not globally."""
    callback_query = AsyncMock()
    callback_query.data = "edit_order_123"
    callback_query.from_user.id = 456
    state = AsyncMock(spec=FSMContext)
    session = AsyncMock()
    
    order_orm = MagicMock(id=123)
    
    with patch("handlers.order.crud.get_order_with_items", new_callable=AsyncMock) as mock_get_order, \
         patch("handlers.order.get_user_locale", new_callable=AsyncMock) as mock_locale:
        
        mock_get_order.return_value = order_orm
        mock_locale.return_value = "uk"
        
        await order_edit(callback_query, state, session)
        
        # Verify state.update_data was called with order_id_for_edit
        state.update_data.assert_any_call(order_id_for_edit=123)
        # Verify state.clear was called (added by user earlier)
        state.clear.assert_called_once()


@pytest.mark.asyncio
async def test_order_final_success_flow():
    """Verify the full flow of order_final when everything is correct."""
    message = AsyncMock()
    message.web_app_data.data = json.dumps({"items": [{"hash_code": "item1", "quantity": 2}]})
    message.from_user.id = 789
    
    state = AsyncMock(spec=FSMContext)
    state_data = {
        "order_id_for_edit": 101,
        "date_start": "2024-01-01",
        "date_end": "2024-01-05",
        "work_days": 4,
        "address": "Test addr",
        "comment": "Test comment"
    }
    state.get_data.return_value = state_data
    
    session = AsyncMock()
    
    user = MagicMock(user_id=789)
    order_for_edit = MagicMock(id=101)
    new_order = MagicMock(id=102)
    order_with_items = MagicMock(id=102)
    
    with patch("handlers.order.crud.get_user_by_tg_id", new_callable=AsyncMock) as mock_get_user, \
         patch("handlers.order.crud.get_order_with_items", new_callable=AsyncMock) as mock_get_order, \
         patch("handlers.order.process_order_submission", new_callable=AsyncMock) as mock_process, \
         patch("handlers.order.notify_admin_new_order", new_callable=AsyncMock) as mock_notify, \
         patch("handlers.order.build_user_confirmation_message") as mock_build_msg, \
         patch("handlers.order.make_user_kb") as mock_kb:
        
        mock_get_user.return_value = user
        # First call for order_for_edit, second for order_with_items
        mock_get_order.side_effect = [order_for_edit, order_with_items]
        mock_process.return_value = new_order
        mock_build_msg.return_value = "Order success message"
        
        await order_final(message, state, session)
        
        # Verify order submission was called with the FETCHED order_for_edit
        mock_process.assert_called_once()
        _, kwargs = mock_process.call_args
        assert kwargs["order_for_edit"] == order_for_edit
        
        # Verify user received the success message
        message.answer.assert_called_with("Order success message", reply_markup=mock_kb())
        # Verify state was cleared
        state.clear.assert_called_once()
