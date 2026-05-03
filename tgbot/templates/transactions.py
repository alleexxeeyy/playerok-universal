import math
import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from playerokapi.types import Transaction
from playerokapi.enums import TransactionStatuses, TransactionDirections, TransactionOperations

from .. import callback_datas as calls


def _get_transaction_info(transaction: Transaction):
    sum_sym = "+" if transaction.direction == TransactionDirections.IN else "-"
    sum = f"{sum_sym}{transaction.value}"
    provider = transaction.provider.name

    operation = transaction.operation
    if operation:
        if operation == TransactionOperations.DEPOSIT:
            operation_str = "💳 Пополнение"
        elif operation == TransactionOperations.BUY:
            operation_str = "🛒 Покупка"
        elif operation == TransactionOperations.SELL:
            operation_str = "🤑 Продажа"
        elif operation == TransactionOperations.ITEM_DEFAULT_PRIORITY:
            operation_str = "🛍️ Выставление"
        elif operation == TransactionOperations.ITEM_PREMIUM_PRIORITY:
            operation_str = "🚀 Премиум"
        elif operation == TransactionOperations.WITHDRAW:
            operation_str = "💰 Выплата"
        elif operation == TransactionOperations.MANUAL_BALANCE_INCREASE:
            operation_str = "➕ Начисление"
        elif operation == TransactionOperations.MANUAL_BALANCE_DECREASE:
            operation_str = "➖ Списание"
        elif operation == TransactionOperations.REFERRAL_BONUS:
            operation_str = "👤 Реферал"
        elif operation == TransactionOperations.STEAM_DEPOSIT:
            operation_str = "🎮 Steam пополнение"

    status = transaction.status
    if status:
        if status == TransactionStatuses.PENDING:
            status_str = "В ожидании"
        elif status == TransactionStatuses.PROCESSING:
            status_str = "В заморозке"
        elif status == TransactionStatuses.CONFIRMED:
            status_str = "Успешно"
        elif status == TransactionStatuses.ROLLED_BACK:
            status_str = "Возврат"
        elif status == TransactionStatuses.FAILED:
            status_str = "Ошибка"

    return sum, provider, operation_str, status_str

                    
def transactions_text(transactions: list[Transaction], page=0):
    items_per_page = 12
    
    total_pages = math.ceil(len(transactions) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    transactions_frmtd = ""
    for transaction in list(transactions)[start_offset:end_offset]:
        sum, provider, operation_str, status_str = _get_transaction_info(transaction)
        transactions_frmtd += (
            f"<b>{operation_str} ({provider})</b> ・ {sum}₽"
            f"\n      ┗ {status_str}\n\n"
        )

    transactions_frmtd = transactions_frmtd.strip()
    if not transactions_frmtd:
        transactions_frmtd = "Нету транзакций по заданным фильтрам. Попробуйте обновить страницу"

    txt = textwrap.dedent(f"""
        <b>💳 Транзакции</b>
        \n{transactions_frmtd}
    """)
    return txt


def transactions_kb(transactions: list[Transaction], page=0):
    rows = []
    items_per_page = 12
    transactions_per_row = 1
    
    total_pages = math.ceil(len(transactions) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    dynamic_btns = []
    for transaction in list(transactions)[start_offset:end_offset]:
        sum, _, operation_str, _ = _get_transaction_info(transaction)
        dynamic_btns.append(InlineKeyboardButton(
            text=f"{operation_str} ・ {sum}₽", 
            callback_data=calls.TransactionPage(id=transaction.id).pack())
        )
    for i in range(0, len(dynamic_btns), transactions_per_row):
        rows.append(dynamic_btns[i:i+transactions_per_row])

    if total_pages > 1:
        buttons_row = []
        btn_back = InlineKeyboardButton(text="←", callback_data=calls.TransactionsPagination(page=page-1).pack()) if page > 0 else InlineKeyboardButton(text="🛑", callback_data="123")
        buttons_row.append(btn_back)

        btn_pages = InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="enter_transactions_page")
        buttons_row.append(btn_pages)

        btn_next = InlineKeyboardButton(text="→", callback_data=calls.TransactionsPagination(page=page+1).pack()) if page < total_pages - 1 else InlineKeyboardButton(text="🛑", callback_data="123")
        buttons_row.append(btn_next)
        rows.append(buttons_row)

    rows.append([
        InlineKeyboardButton(text="✨ Фильтр", callback_data="transactions_filter"),
        InlineKeyboardButton(text="💳 На сайте", url="https://playerok.com/wallet/add")
    ])
    rows.append([InlineKeyboardButton(text="💸 Вывод", callback_data="enter_new_transaction")]) # TODO: доделать
    rows.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.TransactionsPagination(page=page, upd=True).pack())
    ])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def transactions_float_text(placeholder):
    txt = textwrap.dedent(f"""
        <b>💳 Транзакции</b>
        \n{placeholder}
    """)
    return txt