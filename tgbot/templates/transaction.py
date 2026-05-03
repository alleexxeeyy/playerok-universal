import textwrap
import pytz
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

from playerokapi.types import Transaction
from playerokapi.enums import TransactionStatuses, TransactionDirections, TransactionOperations

from .. import callback_datas as calls


def transaction_text(transaction: Transaction):
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

    iso_dt = transaction.created_at
    cr_date = "-"

    if iso_dt:
        if iso_dt.endswith("Z"):
            iso_dt = iso_dt[:-1] + "+00:00"
        dt = datetime.fromisoformat(iso_dt).astimezone(pytz.timezone("Europe/Moscow"))
        cr_date = dt.strftime("%d.%m %H:%M:%S")
    
    txt = textwrap.dedent(f"""
        <b>📄💳 Страница транзакции</b>
        
        <b>🏷️ Операция:</b> {operation_str} ({sum}₽)
        <b>💵 Способ оплаты:</b> {provider}
        <b>🔃 Статус:</b> {status_str}
        
        <b>📅 Дата создания:</b> {cr_date}
    """)
    return txt


def transaction_kb(transaction: Transaction, last_page=0):
    rows = [[InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.TransactionsPagination(page=last_page).pack())]]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def transaction_float_text(placeholder):
    txt = textwrap.dedent(f"""
        <b>📄💳 Страница транзакции</b>
        \n{placeholder}
    """)
    return txt