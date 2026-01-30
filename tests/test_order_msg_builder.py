from datetime import date
from unittest.mock import MagicMock

from utils.order_msg_builder import OrderAdminMsgBuilder, OrderUserMsgBuilder


def test_order_user_msg_builder_header():
    """Test that the user message builder generates the correct header."""
    # Arrange: Create a mock order
    order = MagicMock()
    order.id = 42
    
    items = []
    
    # Act: Create the builder and generate header
    builder = OrderUserMsgBuilder(order, items)
    header = builder.get_header_text()
    
    # Assert: Header should only contain order ID
    assert "Замовлення #42" in header
    assert "@" not in header  # No user details


def test_order_admin_msg_builder_header():
    """Test that the admin message builder includes user contact details."""
    # Arrange: Create mock order and user
    order = MagicMock()
    order.id = 42
    
    user = MagicMock()
    user.name = "Олександр"
    user.surname = "Петренко"
    user.username = "alex_p"
    user.phone_number = "+380961234567"
    
    items = []
    
    # Act: Create the admin builder
    builder = OrderAdminMsgBuilder(order, items, user)
    header = builder.get_header_text()
    
    # Assert: Header should contain user details
    assert "Замовлення #42" in header
    assert "Олександр Петренко" in header
    assert "@alex_p" in header
    assert "+380961234567" in header


def test_order_preview_message():
    """Test the preview message contains order basics but no items."""
    # Arrange: Create a realistic order mock
    order = MagicMock()
    order.id = 10
    order.status.value = "Підтверджено"
    order.date_start = date(2024, 2, 15)
    order.date_end = date(2024, 2, 17)
    order.work_days = 3
    order.address = "вул. Хрещатик, 1, Київ"
    order.description = "Потрібен додатковий мікрофон"
    
    items = []
    
    # Act
    builder = OrderUserMsgBuilder(order, items)
    preview = builder.build_preview_message()
    
    # Assert: Should contain order details
    assert "Замовлення #10" in preview
    assert "Підтверджено" in preview
    assert "2024-02-15" in preview
    assert "2024-02-17" in preview
    assert "3" in preview
    assert "вул. Хрещатик, 1, Київ" in preview
    assert "Потрібен додатковий мікрофон" in preview
    
    # Should NOT contain item details (preview mode)
    # We'll test items in the full message


def test_order_full_message_with_items():
    """Test the full message includes item list with quantities."""
    # Arrange: Create order and items
    order = MagicMock()
    order.id = 5
    order.status.value = "Нове"
    order.date_start = date(2024, 3, 1)
    order.date_end = date(2024, 3, 5)
    order.work_days = 5
    order.address = "Самовивіз"
    order.description = "Без коментарів"
    
    # Create mock items
    item1 = MagicMock()
    item1.item.name = "Мікшерний пульт Yamaha"
    item1.quantity = 2
    
    item2 = MagicMock()
    item2.item.name = "LED екран 3x2м"
    item2.quantity = 1
    
    items = [item1, item2]
    
    # Act
    builder = OrderUserMsgBuilder(order, items)
    full_message = builder.build_full_message()
    
    # Assert: Should contain items
    assert "Мікшерний пульт Yamaha × 2 шт." in full_message
    assert "LED екран 3x2м × 1 шт." in full_message
    assert "Замовлення #5" in full_message


def test_admin_vs_user_message_difference():
    """Verify that admin and user builders produce different headers but same body."""
    # Arrange: Same order for both
    order = MagicMock()
    order.id = 99
    order.status.value = "Завершено"
    order.date_start = date(2024, 1, 20)
    order.date_end = date(2024, 1, 22)
    order.work_days = 3
    order.address = "пр. Перемоги, 10"
    order.description = "VIP-подія"
    
    user = MagicMock()
    user.name = "Іван"
    user.surname = "Іваненко"
    user.username = "ivan123"
    user.phone_number = "+380501234567"
    
    items = []
    
    # Act
    user_builder = OrderUserMsgBuilder(order, items)
    admin_builder = OrderAdminMsgBuilder(order, items, user)
    
    user_msg = user_builder.build_preview_message()
    admin_msg = admin_builder.build_preview_message()
    
    # Assert: Admin message should contain contact info
    assert "Іван Іваненко" in admin_msg
    assert "@ivan123" in admin_msg
    assert "+380501234567" in admin_msg
    
    # User message should NOT contain contact info
    assert "Іван Іваненко" not in user_msg
    assert "@ivan123" not in user_msg
    
    # Both should contain the basic order info
    assert "Завершено" in user_msg
    assert "Завершено" in admin_msg
    assert "пр. Перемоги, 10" in user_msg
    assert "пр. Перемоги, 10" in admin_msg
