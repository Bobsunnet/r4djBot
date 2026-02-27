from datetime import datetime
from typing import Optional

from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from db_handler import OrderStatus

from .common import GenericCalendar
from .schemas import (
    CalendarCallback,
    DialogCalAct,
    DialogCalendarCallback,
    ManagerCalendarCallback,
    highlight,
)


class DialogCalendar(GenericCalendar):

    ignore_callback = DialogCalendarCallback(act=DialogCalAct.ignore).pack()    # placeholder for no answer buttons

    def __init__(
        self,
        orders_count_dict: dict[tuple[int, int], int] = None,
        status: Optional[OrderStatus] = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.orders_count_dict = orders_count_dict
        self.status = status
        self.is_manager = bool(self.status)
        self.callback_builder = ManagerCalendarCallback if self.is_manager else DialogCalendarCallback    

    async def _get_month_kb(self, year: int):
        """Creates an inline keyboard with months for specified year"""
        if self.orders_count_dict is None:
            raise ValueError("[CALENDAR]: Argument 'orders_count_dict' is not set")
            
        kb = []
        # first row with year button
        years_row = []
        years_row.append(
            InlineKeyboardButton(
                text=self._labels.cancel_caption,
                callback_data=self.callback_builder(
                    act=DialogCalAct.cancel, year=year, month=1, day=1, status=self.status
                ).pack()
            )
        )
        years_row.append(InlineKeyboardButton(
            text="Back",
            callback_data=self.callback_builder(
                act=DialogCalAct.start, year=year, month=-1, day=-1, status=self.status
            ).pack()
        ))
        years_row.append(InlineKeyboardButton(text=" ", callback_data=self.ignore_callback))
        kb.append(years_row)

        def month_orders_count(month: int):
            month_str = self._labels.months[month - 1]
            if (year, month) in self.orders_count_dict:
                count = self.orders_count_dict[(year, month)]
                if count > 99:
                    count = "99+"
                month_str += f" ({count})"
            return month_str

        for i in range(1, 13, 3):
            month_row = []
            for month in range(i, i + 3):
                month_row.append(InlineKeyboardButton(
                    text=month_orders_count(month),
                    callback_data=self.callback_builder(
                        act=DialogCalAct.set_m, year=year, month=month, day=-1, status=self.status
                    ).pack()
                ))
            kb.append(month_row)

        return InlineKeyboardMarkup(row_width=3, inline_keyboard=kb)

    async def start_calendar(
        self,
        year: int = datetime.now().year,
    ) -> InlineKeyboardMarkup:
        today = datetime.now()
        now_year = today.year
        kb = []

        years_row = []
        for value in range(now_year - 1, now_year + 2):
            years_row.append(InlineKeyboardButton(
                text=str(value) if value != now_year else highlight(value),
                callback_data=self.callback_builder(
                    act=DialogCalAct.set_y, year=value, month=-1, day=-1, status=self.status
                ).pack()
            ))
        kb.append(years_row)
        nav_row = []
        nav_row.append(
            InlineKeyboardButton(
                text=self._labels.cancel_caption,
                callback_data=self.callback_builder(
                    act=DialogCalAct.cancel, year=year, month=1, day=1, status=self.status
                ).pack(),
            )
        )
        kb.append(nav_row)
        return InlineKeyboardMarkup(row_width=3, inline_keyboard=kb)

    async def process_selection(self, query: CallbackQuery, data: CalendarCallback) -> tuple:
        return_data = (False, None)
        if data.act == DialogCalAct.ignore:
            await query.answer(cache_time=60)
        if data.act == DialogCalAct.set_y:
            await query.message.edit_reply_markup(reply_markup=await self._get_month_kb(int(data.year)))
        # if data.act == DialogCalAct.prev_y:
        #     new_year = int(data.year) - 3
        #     await query.message.edit_reply_markup(reply_markup=await self.start_calendar(year=new_year))
        # if data.act == DialogCalAct.next_y:
        #     new_year = int(data.year) + 3
            # await query.message.edit_reply_markup(reply_markup=await self.start_calendar(year=new_year))
        if data.act == DialogCalAct.start:
            await query.message.edit_reply_markup(reply_markup=await self.start_calendar(int(data.year)))
        if data.act == DialogCalAct.set_m:
            return await self.process_month_select(data, query)
        if data.act == DialogCalAct.day:
            return await self.process_day_select(data, query)

        if data.act == DialogCalAct.cancel:
            await query.message.delete_reply_markup()
        return return_data
