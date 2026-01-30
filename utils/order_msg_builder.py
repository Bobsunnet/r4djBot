from db_handler.models import Order, OrderItemAssociation, User


class OrderBaseMsgBuilder:
    """Base class for building order messages with common formatting logic."""
    
    def __init__(self, order: Order, items: list[OrderItemAssociation]):
        self.order = order
        self.items = items

    def get_header_text(self) -> str:
        return f"Замовлення #{self.order.id}.\n"

    def _order_preview_message(self) -> str:
        order_text = (
            f"Статус: *{self.order.status.value}*\n"
            f"Початок оренди: {self.order.date_start}\n"
            f"Кінець оренди: {self.order.date_end}\n"
            f"Кількість днів роботи: {self.order.work_days}\n"
            f"Адреса та час доставки/самовивіз: {self.order.address}\n\n"
            f"Коментар: {self.order.description}\n\n"
        )
        return order_text

    def _order_full_message(self) -> str:
        """
        Builds the order message with user details and items.
        """
        order_text = self._order_preview_message()
        for entry in self.items:
            order_text += f"• {entry.item.name} × {entry.quantity} шт.\n"

        return order_text

    def build_full_message(self) -> str:
        text = f"{self.get_header_text()}\n"
        text += self._order_full_message()
        return text

    def build_preview_message(self) -> str:
        text = f"{self.get_header_text()}\n"
        text += self._order_preview_message()
        return text


class OrderUserMsgBuilder(OrderBaseMsgBuilder):
    """Message builder for user-facing order messages (no contact details)."""
    pass


class OrderAdminMsgBuilder(OrderBaseMsgBuilder):
    """Message builder for admin-facing order messages with user contact details."""
    
    def __init__(self, order: Order, items: list[OrderItemAssociation], user: User):
        super().__init__(order, items)
        self.user = user

    def get_header_text(self) -> str:
        return (
            f"Замовлення #{self.order.id} від {self.user.name} {self.user.surname} @{self.user.username or 'N/A'}\n"
            f"{self.user.phone_number or 'N/A'}\n"
        )
