from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from playerokapi.enums import ItemDealDirections, ItemDealStatuses

from .. import callback_datas as calls


def deals_filter_kb(filter, last_page=0):
    di1 = "・" if filter["direction"] == ItemDealDirections.IN else ""
    di2 = "・" if filter["direction"] == ItemDealDirections.OUT else ""
    di3 = "・" if filter["direction"] == None else ""

    st1 = "・" if ItemDealStatuses.PAID in filter["statuses"] else ""
    st2 = "・" if ItemDealStatuses.SENT in filter["statuses"] else ""
    st3 = "・" if ItemDealStatuses.CONFIRMED in filter["statuses"] else ""
    st4 = "・" if ItemDealStatuses.ROLLED_BACK in filter["statuses"] else ""
    st5 = "・" if filter["statuses"] == [] else ""

    rows = [
        [InlineKeyboardButton(text="━━━  НАПРАВЛЕНИЕ  ━━━", callback_data="null_answer")],
        [
        InlineKeyboardButton(text=f"{di1} Покупки {di1}", callback_data=calls.ChangeDealsFilter(di=1).pack()), 
        InlineKeyboardButton(text=f"{di2} Продажи {di2}", callback_data=calls.ChangeDealsFilter(di=2).pack()),
        ],
        [InlineKeyboardButton(text=f"{di3} Все {di3}", callback_data=calls.ChangeDealsFilter(di=3).pack())],
        [InlineKeyboardButton(text="━━━  СТАТУС  ━━━", callback_data="null_answer")],
        [
        InlineKeyboardButton(text=f"{st1} Оплачено {st1}", callback_data=calls.ChangeDealsFilter(st=1).pack()), 
        InlineKeyboardButton(text=f"{st2} Подтверждено {st2}", callback_data=calls.ChangeDealsFilter(st=2).pack()),
        ],
        [
        InlineKeyboardButton(text=f"{st3} Выполнено {st3}", callback_data=calls.ChangeDealsFilter(st=3).pack()),
        InlineKeyboardButton(text=f"{st4} Возврат {st4}", callback_data=calls.ChangeDealsFilter(st=4).pack()), 
        ],
        [InlineKeyboardButton(text=f"{st5} Все {st5}", callback_data=calls.ChangeDealsFilter(st=5).pack()),],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.DealsPagination(page=last_page).pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb