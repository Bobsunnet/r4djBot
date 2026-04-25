from aiogram import html

from db_handler.models import Order, OrderItemAssociation, User
from utils import messages as ms
from utils import utils

titles = ['зміну', 'зміни', 'змін']


class OrderBaseMsgBuilder:
    """Base class for building order messages with common formatting logic."""
    
    def __init__(self, order: Order, items: list[OrderItemAssociation], was_edited: bool = False):
        self.order = order
        self.items = items
        self.was_edited = was_edited

    def _build_items_text(self) -> str:
        items_text = ""
        for entry in self.items:
            deleted_mark = ""
            if entry.item.is_deleted:
                deleted_mark = " <b>(позиція видалена)</b>"
            items_text += f"• {html.quote(entry.item.name)} × {entry.quantity} шт.{deleted_mark}\n"
        return items_text

    def get_general_header_text(self) -> str:
        return f"Замовлення <b>#{self.order.id}</b>\n"

    def _build_order_text(self) -> str:
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

    def _order_with_items_text(self, show_price: bool = False) -> str:
        """
        Builds the order message with user details and items.
        """        
        order_text = self._build_order_text()
        order_text += self._build_items_text()
        if show_price:
            order_text += self._build_total_cost_text()

        return order_text

    def build_preview_message(self)-> str:
        head = self._get_header_text()
        return head + self._build_order_text()

    def build_full_message(self)-> str:
        text = self.build_preview_message()
        text += self._build_items_text()
        return text
    
    def get_order_info_header(self):
        super().get_general_header_text()


class OrderUserMessageBuilder(OrderBaseMsgBuilder):
    pass


class OrderAdminMessageBuilder(OrderBaseMsgBuilder):
    def __init__(self, order: Order, items: list[OrderItemAssociation], user: User, was_edited: bool = False):
        super().__init__(order, items, was_edited)
        self.user = user


class OrderPopupAdminMessage(OrderAdminMessageBuilder):
    def _get_header_text(self) -> str:
        status_icon = ms.manager_edit_order_message if self.was_edited else ms.manager_new_order_message
        order_info = super().get_general_header_text().strip()
        user_info = f"Від {self.user.name} {self.user.surname} @{self.user.username or 'N/A'}\n{self.user.phone_number or 'N/A'}"

        return f"{status_icon} {order_info}\n{user_info}\n"


class OrderDetailsAdminMessage(OrderAdminMessageBuilder):
    def _get_header_text(self) -> str:
        order_info = super().get_general_header_text().strip()
        user_info = f"Від {self.user.name} {self.user.surname} @{self.user.username or 'N/A'}\n{self.user.phone_number or 'N/A'}"

        return f"{order_info}\n{user_info}\n"


class OrderPopupUserMessage(OrderUserMessageBuilder):
    def _get_header_text(self) -> str:
        header = ms.order_edited_message if self.was_edited else ms.order_processing_message
        return f"{header}. Cлідкуйте за зміною статусу замовлення\n\n{super().get_general_header_text()}"


class OrderDetailsUserMessage(OrderUserMessageBuilder):
    """Message builder for user-facing order messages (no contact details)."""
    
    def _get_header_text(self) -> str:
        return super().get_general_header_text()



    
