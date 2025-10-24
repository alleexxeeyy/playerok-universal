import math
import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from plbot.playerokbot import get_playerok_bot

from .. import callback_datas as calls
from ...settings import Settings as sett
from ...meta import NAME, VERSION


def menu_text():
    txt = textwrap.dedent(f"""
        📝 <b>Меню {NAME}</b>

        <b>{NAME}</b> v{VERSION}
        Модуль, позволяющий заполнять анкеты

        <b>Ссылки:</b>
        ┣ <b>@alleexxeeyy</b> — главный и единственный разработчик
        ┗ <b>@alexey_production_bot</b> — бот для покупки официальных модулей

        Перемещайтесь по разделам ниже ↓
    """)
    return txt

def menu_kb():
    rows = [
        [
        InlineKeyboardButton(text="⚙️", callback_data=calls.FORMS_MenuNavigation(to="settings").pack())
        ],
        [InlineKeyboardButton(text="📖 Инструкция", callback_data=calls.FORMS_InstructionNavigation(to="default").pack())], 
        [
        InlineKeyboardButton(text="👨‍💻 Разработчик", url="https://t.me/alleexxeeyy"), 
        InlineKeyboardButton(text="🤖 Наш бот", url="https://t.me/alexey_production_bot")
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb

def menu_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        📝 <b>Меню {NAME}</b>
        \n{placeholder}
    """)
    return txt


def instruction_text():
    txt = textwrap.dedent(f"""
        📖 <b>Инструкция {NAME}</b>
        В этом разделе описаны инструкции по работе с модулем

        Перемещайтесь по разделам ниже ↓
    """)
    return txt

def instruction_kb():
    rows = [
        [InlineKeyboardButton(text="⌨️ Команды", callback_data=calls.FORMS_InstructionNavigation(to="commands").pack())],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.FORMS_MenuNavigation(to="default").pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb

def instruction_comms_text():
    txt = textwrap.dedent(f"""
        📖 <b>Инструкция {NAME}</b> → ⌨️ <b>Команды</b>

        <code>!мояанкета</code> — отображает данные заполненной анкеты
        <code>!заполнить</code> — начинает процесс заполнения анкеты

        Выберите действие ↓
    """)
    return txt

def instruction_comms_kb():
    rows = [[InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.FORMS_InstructionNavigation(to="default").pack())]]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def settings_text():
    txt = textwrap.dedent(f"""
        ⚙️ <b>Настройки {NAME}</b>

        Перемещайтесь по разделам ниже, чтобы изменять значения параметров ↓
    """)
    return txt

def settings_kb():
    config = sett.get("config")
    log_states = "🟢 Включено" if config["playerok"]["bot"]["log_states"] else "🔴 Выключено"
    rows = [
        [InlineKeyboardButton(text=f"👁️ Логгировать состояния в консоль: {log_states}", callback_data="forms_switch_log_states")],
        [InlineKeyboardButton(text=f"💬 Сообщения", callback_data=calls.FORMS_MessagesPagination(page=0).pack())],
        [
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.FORMS_MenuNavigation(to="default").pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.FORMS_MenuNavigation(to="settings").pack())
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb

def settings_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        ⚙️ <b>Настройки {NAME}</b>
        \n{placeholder}
    """)
    return txt


def settings_mess_text():
    messages = sett.get("messages")
    txt = textwrap.dedent(f"""
        ⚙️ <b>Настройки</b> → ✉️ <b>Сообщения</b>
        Всего <b>{len(messages.keys())}</b> настраиваемых сообщений в конфиге

        Перемещайтесь по разделам ниже. Нажмите на сообщение, чтобы перейти в его редактирование ↓
    """)
    return txt

def settings_mess_kb(page: int = 0):
    messages = sett.get("messages")
    rows = []
    items_per_page = 8
    total_pages = math.ceil(len(messages.keys()) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    for mess_id, info in list(messages.items())[start_offset:end_offset]:
        enabled = "🟢" if info["enabled"] else "🔴"
        text_joined = "\n".join(info["text"])
        rows.append([InlineKeyboardButton(text=f"{enabled} {mess_id} | {text_joined}", callback_data=calls.FORMS_MessagePage(message_id=mess_id).pack())])

    buttons_row = []
    btn_back = InlineKeyboardButton(text="←", callback_data=calls.FORMS_MessagesPagination(page=page-1).pack()) if page > 0 else InlineKeyboardButton(text="🛑", callback_data="123")
    buttons_row.append(btn_back)
    buttons_row.append(InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="forms_enter_messages_page"))

    btn_next = InlineKeyboardButton(text="→", callback_data=calls.FORMS_MessagesPagination(page=page+1).pack()) if page < total_pages - 1 else InlineKeyboardButton(text="🛑", callback_data="123")
    buttons_row.append(btn_next)
    rows.append(buttons_row)

    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.FORMS_MenuNavigation(to="settings").pack()),
                 InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.FORMS_MessagesPagination(page=page).pack())])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb

def settings_mess_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        ⚙️ <b>Настройки</b> → ✉️ <b>Сообщения</b>
        \n{placeholder}
    """)
    return txt


def settings_mess_page_text(message_id: int):
    messages = sett.get("messages")
    enabled = "🟢 Включено" if messages[message_id]["enabled"] else "🔴Выключено"
    message_text = "\n".join(messages[message_id]["text"]) or "❌ Не задано"
    txt = textwrap.dedent(f"""
        ✒️ <b>Редактирование сообщения</b>

        🆔 <b>ID сообщения:</b> {message_id}
        💡 <b>Состояние:</b> {enabled}
        💬 <b>Текст сообщения:</b> <blockquote>{message_text}</blockquote>

        Выберите параметр для изменения ↓
    """)
    return txt

def settings_mess_page_kb(message_id: int, page: int = 0):
    messages = sett.get("messages")
    enabled = "🟢 Включено" if messages[message_id]["enabled"] else "🔴Выключено"
    message_text = "\n".join(messages[message_id]["text"]) or "❌ Не задано"
    rows = [
        [InlineKeyboardButton(text=f"💡 Состояние: {enabled}", callback_data="forms_switch_message_enabled")],
        [InlineKeyboardButton(text=f"💬 Текст сообщения: {message_text}", callback_data="forms_enter_message_text")],
        [
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.FORMS_MessagesPagination(page=page).pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.FORMS_MessagePage(message_id=message_id).pack())
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb

def settings_mess_page_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        ✒️ <b>Редактирование сообщения</b>
        \n{placeholder}
    """)
    return txt