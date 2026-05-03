import textwrap
from datetime import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from playerokapi.types import UserBankCard, SBPBankMember
from settings import Settings as sett
from utils import get_event_next_time

from .. import callback_datas as calls


def withdrawal_text(card: UserBankCard = None, sbp_bank: SBPBankMember = None):
    config = sett.get("config")
    
    enabled = "✅" if config["playerok"]["auto_withdrawal"]["enabled"] else "❌"
    interval = config["playerok"]["auto_withdrawal"]["interval"]
    usdt_address = config["playerok"]["auto_withdrawal"]["usdt_address"]
    
    if card: 
        card_name = f"{card.card_first_six}****{card.card_last_four}"
        details = f"{card_name} ({card.card_type.name})"
    elif sbp_bank:
        sbp_phone_number = config["playerok"]["auto_withdrawal"]["sbp_phone_number"]
        details = f"{sbp_phone_number} ({sbp_bank.name})"
    elif usdt_address: 
        details = f"{usdt_address} (USDT TRC20)"
    else: 
        details = "Не указано"
    
    last_time_iso = config["playerok"]["auto_withdrawal"]["last_time"]
    last_time = datetime.fromisoformat(last_time_iso).strftime("%d.%m.%Y %H:%M:%S") if last_time_iso else "никогда"

    if config["playerok"]["auto_withdrawal"]["enabled"]:
        if not last_time_iso:
            next_time = "прямо сейчас"
        else:
            next_time = get_event_next_time(last_time_iso, config["playerok"]["auto_withdrawal"]["interval"]).strftime("%d.%m.%Y %H:%M:%S")
    else:
        next_time = "никогда"
    
    txt = textwrap.dedent(f"""
        <b>💸 Авто-вывод</b>
        <blockquote><b>(?)</b> Бот будет автоматически с указанным интервалом создавать вывод всех средств на аккаунте по указанным реквизитам.</blockquote>

        <b>💡 Включено:</b> {enabled}
        <b>⏰ Интервал:</b> {interval} сек.

        <b>💳 Реквизиты:</b> {details}

        ⏮️ Последний раз было <b>{last_time}</b>
        ⏭️ Следующий раз будет <b>{next_time}</b>
    """)
    return txt


def withdrawal_kb(card: UserBankCard = None, sbp_bank: SBPBankMember = None):
    config = sett.get("config")
    
    enabled = "✅" if config["playerok"]["auto_withdrawal"]["enabled"] else "❌"
    interval = config["playerok"]["auto_withdrawal"]["interval"]
    usdt_address = config["playerok"]["auto_withdrawal"]["usdt_address"]
    
    if card: 
        card_name = f"{card.card_first_six}****{card.card_last_four}"
        details = f"{card_name} ({card.card_type.name})"
    elif sbp_bank:
        sbp_phone_number = config["playerok"]["auto_withdrawal"]["sbp_phone_number"]
        details = f"{sbp_phone_number} ({sbp_bank.name})"
    elif usdt_address: 
        details = f"{usdt_address} (USDT TRC20)"
    else: 
        details = "Не указано"

    rows = [
        [InlineKeyboardButton(text=f"💸 Создать вывод", callback_data="confirm_withdrawal")],
        [InlineKeyboardButton(text=f"💡 Включено: {enabled}", callback_data="switch_auto_withdrawal_enabled")],
        [InlineKeyboardButton(text=f"⏰ Интервал: {interval} сек.", callback_data="enter_auto_withdrawal_interval")],
        [InlineKeyboardButton(text=f"💳 Реквизиты: {details}", callback_data=calls.BankCardsPagination(page=0).pack())],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def withdrawal_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>💸 Авто-вывод</b>
        \n{placeholder}
    """)
    return txt