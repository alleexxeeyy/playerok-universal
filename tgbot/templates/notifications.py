import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def notifications_text():
    config = sett.get("config")
    
    enabled = "✅" if config["playerok"]["notifications"]["enabled"] else "❌"
    chat_id = config["playerok"]["notifications"]["chat_id"] or "Текущий"
    events = config["playerok"]["notifications"]["events"] or {}
    
    new_user_message = "🟢" if events["new_user_message"] else "🔴"
    new_system_message = "🟢" if events["new_system_message"] else "🔴"
    new_deal = "🟢" if events["new_deal"] else "🔴"
    new_review = "🟢" if events["new_review"] else "🔴"
    new_problem = "🟢" if events["new_problem"] else "🔴"
    deal_status_changed = "🟢" if events["deal_status_changed"] else "🔴"
    item_restored = "🟢" if events["item_restored"] else "🔴"
    item_bumped = "🟢" if events["item_bumped"] else "🔴"
    withdrawal_requested = "🟢" if events["withdrawal_requested"] else "🔴"
    
    txt = textwrap.dedent(f"""
        <b>🔔 Уведомления</b>

        <b>💡 Включено:</b> {enabled}
        <b>💬 Чат:</b> {chat_id}
        
        {new_user_message} Новое сообщение
        {new_system_message} Системное сообщение
        {new_deal} Новая сделка
        {new_review} Новый отзыв
        {new_problem} Проблема сделке
        {deal_status_changed} Статус сделки изменился
        {item_restored} Товар восстановлен
        {item_bumped} Товар поднят
        {withdrawal_requested} Вывод средств
    """)
    return txt


def notifications_kb():
    config = sett.get("config")
    
    enabled = "✅" if config["playerok"]["notifications"]["enabled"] else "❌"
    chat_id = config["playerok"]["notifications"]["chat_id"] or "Текущий"
    events = config["playerok"]["notifications"]["events"] or {}
    
    new_user_message = "🟢" if events["new_user_message"] else "🔴"
    new_system_message = "🟢" if events["new_system_message"] else "🔴"
    new_deal = "🟢" if events["new_deal"] else "🔴"
    new_review = "🟢" if events["new_review"] else "🔴"
    new_problem = "🟢" if events["new_problem"] else "🔴"
    deal_status_changed = "🟢" if events["deal_status_changed"] else "🔴"
    item_restored = "🟢" if events["item_restored"] else "🔴"
    item_bumped = "🟢" if events["item_bumped"] else "🔴"
    withdrawal_requested = "🟢" if events["withdrawal_requested"] else "🔴"
    
    rows = [
        [InlineKeyboardButton(text=f"💡 Включено: {enabled}", callback_data="switch_notifications_enabled")],
        [InlineKeyboardButton(text=f"💬 Чат: {chat_id}", callback_data="enter_notifications_chat_id")],
        [InlineKeyboardButton(text=f"{new_user_message} Новое сообщение", callback_data="switch_notifications_new_user_message")],
        [InlineKeyboardButton(text=f"{new_system_message} Системное сообщение", callback_data="switch_notifications_new_system_message")],
        [InlineKeyboardButton(text=f"{new_deal} Новая сделка", callback_data="switch_notifications_new_deal")],
        [InlineKeyboardButton(text=f"{new_review} Новый отзыв", callback_data="switch_notifications_new_review")],
        [InlineKeyboardButton(text=f"{new_problem} Проблема в сделке", callback_data="switch_notifications_new_problem")],
        [InlineKeyboardButton(text=f"{deal_status_changed} Статус сделки изменился", callback_data="switch_notifications_deal_status_changed")],
        [InlineKeyboardButton(text=f"{item_restored} Товар восстановлен", callback_data="switch_notifications_item_restored")],
        [InlineKeyboardButton(text=f"{item_bumped} Товар поднят", callback_data="switch_notifications_item_bumped")],
        [InlineKeyboardButton(text=f"{withdrawal_requested} Вывод средств", callback_data="switch_notifications_withdrawal_requested")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack())]
    ]
    
    if config["playerok"]["notifications"]["chat_id"]:
        rows[1].append(InlineKeyboardButton(text=f"❌ Очистить", callback_data="clean_notifications_chat_id"))
    
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def notifications_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>🔔 Уведомления</b>
        \n{placeholder}
    """)
    return txt