from datetime import datetime, timedelta
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from playerokapi.enums import TransactionStatuses, TransactionOperations, TransactionProviderIds

from .. import callback_datas as calls


def transactions_filter_kb(filter, last_page=0):
    st1 = "・" if filter["status"] == TransactionStatuses.PENDING else ""
    st2 = "・" if filter["status"] == TransactionStatuses.PROCESSING else ""
    st3 = "・" if filter["status"] == TransactionStatuses.CONFIRMED else ""
    st4 = "・" if filter["status"] == TransactionStatuses.ROLLED_BACK else ""
    st5 = "・" if filter["status"] == TransactionStatuses.FAILED else ""
    st6 = "・" if filter["status"] == None else ""
    
    op1 = "・" if filter["operation"] == TransactionOperations.DEPOSIT else ""
    op2 = "・" if filter["operation"] == TransactionOperations.BUY else ""
    op3 = "・" if filter["operation"] == TransactionOperations.SELL else ""
    op4 = "・" if filter["operation"] == TransactionOperations.ITEM_PREMIUM_PRIORITY else ""
    op5 = "・" if filter["operation"] == TransactionOperations.WITHDRAW else ""
    op6 = "・" if filter["operation"] == TransactionOperations.MANUAL_BALANCE_INCREASE else ""
    op7 = "・" if filter["operation"] == TransactionOperations.MANUAL_BALANCE_DECREASE else ""
    op8 = "・" if filter["operation"] == TransactionOperations.REFERRAL_BONUS else ""
    op9 = "・" if filter["operation"] == TransactionOperations.STEAM_DEPOSIT else ""
    op10 = "・" if filter["operation"] == None else ""

    pr1 = "・" if filter["provider_id"] == TransactionProviderIds.LOCAL else ""
    pr2 = "・" if filter["provider_id"] == TransactionProviderIds.SBP else ""
    pr3 = "・" if filter["provider_id"] == TransactionProviderIds.BANK_CARD_RU else ""
    pr4 = "・" if filter["provider_id"] == TransactionProviderIds.BANK_CARD_BY else ""
    pr5 = "・" if filter["provider_id"] == TransactionProviderIds.BANK_CARD else ""
    pr6 = "・" if filter["provider_id"] == TransactionProviderIds.YMONEY else ""
    pr7 = "・" if filter["provider_id"] == TransactionProviderIds.USDT else ""
    pr8 = "・" if filter["provider_id"] == TransactionProviderIds.PENDING_INCOME else ""
    pr9 = "・" if filter["provider_id"] == None else ""
    
    min_sym = "・" if (filter["min_value"] or 0) > 0 else ""
    min_val = f"{filter['min_value']}₽" if (filter["min_value"] or 0) > 0 else "❌"
    max_sym = "・" if (filter["max_value"] or 0) > 0 else ""
    max_val = f"{filter['max_value']}₽" if (filter["max_value"] or 0) > 0 else "❌"
    val = "・" if not any((filter["min_value"], filter["max_value"])) else ""

    from_sym = "・" if filter["from_date"] != None else ""
    from_dt = f"{datetime.strftime(filter['from_date'], '%d.%m.%Y')}" if filter["from_date"] != None else "❌"
    to_sym = "・" if filter["to_date"] != None else ""
    to_dt = f"{datetime.strftime(filter['to_date'], '%d.%m.%Y')}" if filter["to_date"] != None else "❌"
    dt = "・" if not any((filter["from_date"], filter["to_date"])) else ""

    rows = [
        [InlineKeyboardButton(text="━━━  СТАТУС  ━━━", callback_data="null_answer")],
        [
        InlineKeyboardButton(text=f"{st1} В ожидании {st1}", callback_data=calls.ChangeTransactionsFilter(st=1).pack()), 
        InlineKeyboardButton(text=f"{st2} В заморозке {st2}", callback_data=calls.ChangeTransactionsFilter(st=2).pack()),
        ],
        [
        InlineKeyboardButton(text=f"{st3} Успешно {st3}", callback_data=calls.ChangeTransactionsFilter(st=3).pack()), 
        InlineKeyboardButton(text=f"{st4} Возврат {st4}", callback_data=calls.ChangeTransactionsFilter(st=4).pack()),
        ],
        [
        InlineKeyboardButton(text=f"{st5} Ошибка {st5}", callback_data=calls.ChangeTransactionsFilter(st=5).pack()), 
        InlineKeyboardButton(text=f"{st6} Все {st6}", callback_data=calls.ChangeTransactionsFilter(st=6).pack()),
        ],
        [InlineKeyboardButton(text="━━━  ОПЕРАЦИЯ  ━━━", callback_data="null_answer")],
        [
        InlineKeyboardButton(text=f"{op1} 💳 Пополнение {op1}", callback_data=calls.ChangeTransactionsFilter(op=1).pack()), 
        InlineKeyboardButton(text=f"{op2} 🛒 Покупка {op2}", callback_data=calls.ChangeTransactionsFilter(op=2).pack()),
        ],
        [
        InlineKeyboardButton(text=f"{op3} 🤑 Продажа {op3}", callback_data=calls.ChangeTransactionsFilter(op=3).pack()), 
        InlineKeyboardButton(text=f"{op4} 🚀 Премиум {op4}", callback_data=calls.ChangeTransactionsFilter(op=4).pack()),
        ],
        [
        InlineKeyboardButton(text=f"{op5} 💰 Выплата {op5}", callback_data=calls.ChangeTransactionsFilter(op=5).pack()), 
        InlineKeyboardButton(text=f"{op6} ➕ Начисление {op6}", callback_data=calls.ChangeTransactionsFilter(op=6).pack()),
        ],
        [
        InlineKeyboardButton(text=f"{op7} ➖ Списание {op7}", callback_data=calls.ChangeTransactionsFilter(op=7).pack()), 
        InlineKeyboardButton(text=f"{op8} 👤 Реферал {op8}", callback_data=calls.ChangeTransactionsFilter(op=8).pack()),
        ],
        [
        InlineKeyboardButton(text=f"{op9} 🎮 Steam пополнение {op9}", callback_data=calls.ChangeTransactionsFilter(op=9).pack()), 
        InlineKeyboardButton(text=f"{op10} Все {op10}", callback_data=calls.ChangeTransactionsFilter(op=10).pack()),
        ],
        [InlineKeyboardButton(text="━━━  СПОСОБ ОПЛАТЫ  ━━━", callback_data="null_answer")],
        [
        InlineKeyboardButton(text=f"{pr1} Баланс аккаунта {pr1}", callback_data=calls.ChangeTransactionsFilter(pr=1).pack()), 
        InlineKeyboardButton(text=f"{pr2} СБП {pr2}", callback_data=calls.ChangeTransactionsFilter(pr=2).pack()),
        ],
        [
        InlineKeyboardButton(text=f"{pr3} Карта RU {pr3}", callback_data=calls.ChangeTransactionsFilter(pr=3).pack()), 
        InlineKeyboardButton(text=f"{pr4} Карта BY {pr4}", callback_data=calls.ChangeTransactionsFilter(pr=4).pack()),
        ],
        [
        InlineKeyboardButton(text=f"{pr5} Иностранная карта {pr5}", callback_data=calls.ChangeTransactionsFilter(pr=5).pack()), 
        InlineKeyboardButton(text=f"{pr6} ЮMoney {pr6}", callback_data=calls.ChangeTransactionsFilter(pr=6).pack()),
        ],
        [
        InlineKeyboardButton(text=f"{pr7} USDT (TRC20) {pr7}", callback_data=calls.ChangeTransactionsFilter(pr=7).pack()), 
        InlineKeyboardButton(text=f"{pr8} С заморозки {pr8}", callback_data=calls.ChangeTransactionsFilter(pr=8).pack()),
        ],
        [InlineKeyboardButton(text=f"{pr9} Все {pr9}", callback_data=calls.ChangeTransactionsFilter(pr=9).pack()),],
        [InlineKeyboardButton(text="━━━  СУММА  ━━━", callback_data="null_answer")],
        [
        InlineKeyboardButton(text=f"{min_sym} От: {min_val} {min_sym}", callback_data="enter_transactions_filter_min_value"), 
        InlineKeyboardButton(text=f"{max_sym} До: {max_val} {max_sym}", callback_data="enter_transactions_filter_max_value"), 
        ],
        [InlineKeyboardButton(text=f"{val} Не учитывать {val}", callback_data=calls.ChangeTransactionsFilter(min_val=0, max_val=0).pack())],
        [InlineKeyboardButton(text="━━━  ДАТА  ━━━", callback_data="null_answer")],
        [
        InlineKeyboardButton(text=f"{from_sym} От: {from_dt} {from_sym}", callback_data="enter_transactions_filter_from_date"), 
        InlineKeyboardButton(text=f"{to_sym} До: {to_dt} {to_sym}", callback_data="enter_transactions_filter_to_date"), 
        ],
        [InlineKeyboardButton(text=f"{dt} Не учитывать {dt}", callback_data=calls.ChangeTransactionsFilter(from_dt="clear", to_dt="clear").pack())],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.TransactionsPagination(page=last_page).pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb