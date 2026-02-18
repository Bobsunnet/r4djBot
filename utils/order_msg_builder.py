from aiogram import html

from db_handler.models import Order, OrderItemAssociation, User
from utils import utils

titles = ['зміну', 'зміни', 'змін']


class OrderBaseMsgBuilder:
    """Base class for building order messages with common formatting logic."""
    
    def __init__(self, order: Order, items: list[OrderItemAssociation]):
        self.order = order
        self.items = items

    def _build_items_text(self) -> str:
        items_text = ""
        for entry in self.items:
            items_text += f"• {html.quote(entry.item.name)} × {entry.quantity} шт.\n"
        return items_text

    def get_header_text(self) -> str:
        return f"Замовлення <b>#{self.order.id}</b>.\n"

    def _order_preview_message(self) -> str:
        order_text = (
            f"Статус: <b>{utils.translate_status(self.order.status)}</b>\n"
            f"Початок оренди: {self.order.date_start}\n"
            f"Кінець оренди: {self.order.date_end}\n"
            f"Кількість днів роботи: {self.order.work_days}\n"
            f"Адреса та час доставки/самовивіз: {html.quote(self.order.address)}\n\n"
            f"Коментар: {html.quote(self.order.description)}\n\n"
        )
        return order_text

    def _count_items_cost(self) -> int:
        cost_per_day = sum(entry.unit_price * entry.quantity for entry in self.items)
        return cost_per_day * self.order.work_days

    def _build_total_cost_text(self) -> str:
        if not self.items:
            return ""

        order_text = "_" * 30 + "\n"
        day_text = utils.format_plural_form_text(self.order.work_days, titles)
        order_text += f"Загальна вартість оренди за {self.order.work_days} {day_text}: {self._count_items_cost()} грн"
        return order_text

    def _order_full_message(self, show_price: bool = False) -> str:
        """
        Builds the order message with user details and items.
        """        
        order_text = self._order_preview_message()
        order_text += self._build_items_text()
        if show_price:
            order_text += self._build_total_cost_text()

        return order_text

    def build_full_message(self, show_price: bool = False) -> str:
        text = f"{self.get_header_text()}\n"
        text += self._order_full_message(show_price)
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
    
    def __init__(self, order: Order, items: list[OrderItemAssociation], user: User, was_edited=False):
        super().__init__(order, items)
        self.user = user
        self.was_edited = was_edited

    def get_header_text(self) -> str:
        order_number = f"Замовлення <b>#{self.order.id}</b>"
        user_info = f"Від {self.user.name} {self.user.surname} @{self.user.username or 'N/A'}\n{self.user.phone_number or 'N/A'}\n"
        was_edit = "було змінено. " if self.was_edited else ""
        
        return f"{order_number} {was_edit} {user_info}"
