from __init__ import VERSION
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import math
import textwrap
from datetime import datetime, timedelta

from .. import callback_datas as calls
from plbot import get_playerok_bot
from settings import Settings as sett
from data import Data as data
from plbot.stats import get_stats

from uuid import UUID



def error_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>❌ Возникла ошибка </b>

        <blockquote>{placeholder}</blockquote>
    """)
    return txt

def back_kb(cb: str):
    rows = [[InlineKeyboardButton(text="⬅️ Назад", callback_data=cb)]]
    return InlineKeyboardMarkup(inline_keyboard=rows)

def confirm_kb(confirm_cb: str, cancel_cb: str):
    rows = [[
        InlineKeyboardButton(text="✅ Подтвердить", callback_data=confirm_cb),
        InlineKeyboardButton(text="❌ Отменить", callback_data=cancel_cb)
    ]]
    return InlineKeyboardMarkup(inline_keyboard=rows)

def destroy_kb():
    rows = [[InlineKeyboardButton(text="❌ Закрыть", callback_data="destroy")]]
    return InlineKeyboardMarkup(inline_keyboard=rows)

def log_text(title: str, text: str, by: str = "playerokuniversal"):
    txt = textwrap.dedent(f"""
        <b>{title}</b>
        \n{text}
        \n<i>{by}</i>
    """)
    return txt
        


def sign_text(placeholder: str):
    txt = textwrap.dedent(f"""
        🔐 <b>Авторизация</b>
        \n{placeholder}
    """)
    return txt


def menu_text():
    txt = textwrap.dedent(f"""
        🏠 <b>Главное меню</b>

        <b>Playerok UNIVERSAL</b> v{VERSION}
        Бот-помощник для Playerok

        <b>Ссылки:</b>
        ┣ <b>@alleexxeeyy</b> — главный и единственный разработчик
        ┣ <b>@alexeyproduction</b> — канал, где публикуются новости
        ┗ <b>@alexey_production_bot</b> — бот для покупки официальных модулей

        Перемещайтесь по разделам ниже ↓
    """)
    return txt

def menu_kb():
    rows = [
        [
        InlineKeyboardButton(text="⚙️", callback_data=calls.SettingsNavigation(to="default").pack()), 
        InlineKeyboardButton(text="👤", callback_data=calls.MenuNavigation(to="profile").pack()), 
        InlineKeyboardButton(text="🔌", callback_data=calls.ModulesPagination(page=0).pack()),
        InlineKeyboardButton(text="📊", callback_data=calls.MenuNavigation(to="stats").pack())
        ],
        [InlineKeyboardButton(text="📖 Инструкция", callback_data=calls.InstructionNavigation(to="default").pack())], 
        [
        InlineKeyboardButton(text="👨‍💻 Разработчик", url="https://t.me/alleexxeeyy"), 
        InlineKeyboardButton(text="📢 Наш канал", url="https://t.me/alexeyproduction"), 
        InlineKeyboardButton(text="🤖 Наш бот", url="https://t.me/alexey_production_bot")
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def stats_text():
    stats = get_stats()
    txt = textwrap.dedent(f"""
        📊 <b>Статистика Playerok бота</b>

        Дата запуска бота: <b>{stats.bot_launch_time.strftime("%d.%m.%Y %H:%M:%S") or 'Не запущен'}</b>

        <b>Статистика с момента запуска:</b>
        ┣ Выполнено: <b>{stats.orders_completed}</b>
        ┣ Возвратов: <b>{stats.orders_refunded}</b>
        ┗ Заработано: <b>{stats.earned_money}</b>₽

        Выберите действие ↓
    """)
    return txt

def stats_kb():
    rows = [
        [
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.MenuNavigation(to="stats").pack())
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def profile_text():
    plbot = get_playerok_bot()
    profile = plbot.playerok_account.profile
    txt = textwrap.dedent(f"""
        👤 <b>Мой профиль</b>

        ID: <code>{profile.id}</code>
        Никнейм: <b>{profile.username}</b>
        Email: <b>{profile.email}</b>
        Роль: <b>{profile.role.name}</b>
        Рейтинг: <b>{profile.rating}</b>
        Кол-во отзывов: <b>{profile.reviews_count}</b>
        
        Баланс:
        ┣ Всего: <b>{profile.balance.value}</b>
        ┣ Доступно: <b>{profile.balance.available}</b>
        ┣ Ожидает зачисления: <b>{profile.balance.pending_income}</b>
        ┗ Заморожено: <b>{profile.balance.frozen}</b>
        
        Предметы:
        ┣ Всего: <b>{profile.stats.items.total}</b>
        ┗ Истёкших: <b>{profile.stats.items.finished}</b>
        
        Сделки:
        ┣ Всего входящих: <b>{profile.stats.deals.incoming.total}</b>
        ┣ Завершено входящих: <b>{profile.stats.deals.incoming.finished}</b>
        ┣ Всего исходящих: <b>{profile.stats.deals.outgoing.total}</b>
        ┗ Завершено исходящих: <b>{profile.stats.deals.outgoing.finished}</b>
        
        Дата создания: <b>{datetime.fromisoformat(profile.created_at.replace('Z', '+00:00')).strftime('%d.%m.%Y %H:%M:%S')}</b>

        Выберите действие ↓
    """)
    return txt

def profile_kb():
    rows = [
        [
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.MenuNavigation(to="profile").pack())
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb
                
        
def instruction_text():
    txt = textwrap.dedent(f"""
        📖 <b>Инструкция</b>
        В этом разделе описаны инструкции по работе с ботом

        Перемещайтесь по разделам ниже ↓
    """)
    return txt

def instruction_kb():
    rows = [
        [InlineKeyboardButton(text="⌨️ Команды", callback_data=calls.InstructionNavigation(to="commands").pack())],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def instruction_comms_text():
    txt = textwrap.dedent(f"""
        📖 <b>Инструкция → ⌨️ Команды</b>
                          
        Команды покупателя:
        ┣ <code>!команды</code> — отображает меню с доступными для покупателя командами
        ┗ <code>!продавец</code> — уведомляет и вызывает продавца в диалог с покупателем (пишет вам в Telegram сообщение с просьбой о помощи)

        Выберите действие ↓
    """)
    return txt

def instruction_comms_kb():
    rows = [[InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.InstructionNavigation(to="default").pack())]]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def settings_text():
    config = sett.get("config")
    token = config["playerok"]["api"]["token"][:5] + ("*" * 10) or "❌ Не задано"
    user_agent = config["playerok"]["api"]["user_agent"] or "❌ Не задано"
    txt = textwrap.dedent(f"""
        ⚙️ <b>Настройки</b>

        <b>Основные настройки:</b>
        ┣ Токен: <b>{token}</b>
        ┗ User-Agent: <b>{user_agent}</b>

        Перемещайтесь по разделам ниже, чтобы изменить значения параметров ↓
    """)
    return txt

def settings_kb():
    rows = [
        [
        InlineKeyboardButton(text="🔑 Авторизация", callback_data=calls.SettingsNavigation(to="auth").pack()),
        InlineKeyboardButton(text="📶 Соединение", callback_data=calls.SettingsNavigation(to="conn").pack()),
        InlineKeyboardButton(text="📦 Предметы", callback_data=calls.SettingsNavigation(to="items").pack())
        ],
        [
        InlineKeyboardButton(text="✉️ Сообщения", callback_data=calls.MessagesPagination(page=0).pack()),
        InlineKeyboardButton(text="⌨️ Команды", callback_data=calls.CustomCommandsPagination(page=0).pack()),
        InlineKeyboardButton(text="🚀 Авто-выдача", callback_data=calls.AutoDeliveriesPagination(page=0).pack())
        ],
        [
        InlineKeyboardButton(text="👀 Логгер", callback_data=calls.SettingsNavigation(to="logger").pack()),
        InlineKeyboardButton(text="🔧 Прочее", callback_data=calls.SettingsNavigation(to="other").pack())
        ],
        [
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.SettingsNavigation(to="default").pack())
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def settings_auth_text():
    config = sett.get("config")
    token = config["playerok"]["api"]["token"][:5] + ("*" * 10) or "❌ Не задано"
    user_agent = config["playerok"]["api"]["user_agent"] or "❌ Не задано"
    txt = textwrap.dedent(f"""
        ⚙️ <b>Настройки → 🔑 Авторизация</b>

        🔐 <b>Токен:</b> {token}
        🎩 <b>User-Agent:</b> {user_agent}

        Выберите параметр для изменения ↓
    """)
    return txt

def settings_auth_kb():
    config = sett.get("config")
    token = config["playerok"]["api"]["token"][:5] + ("*" * 10) or "❌ Не задано"
    user_agent = config["playerok"]["api"]["user_agent"] or "❌ Не задано"
    rows = [
        [InlineKeyboardButton(text=f"🔐 Токен: {token}", callback_data="enter_token")],
        [InlineKeyboardButton(text=f"🎩 User-Agent: {user_agent}", callback_data="enter_user_agent")],
        [
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.SettingsNavigation(to="default").pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.SettingsNavigation(to="authorization").pack())
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb

def settings_auth_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        ⚙️ <b>Настройки → 🔑 Авторизация</b>
        \n{placeholder}
    """)
    return txt


def settings_conn_text():
    config = sett.get("config")
    proxy = config["playerok"]["api"]["proxy"] or "❌ Не задано"
    requests_timeout = config["playerok"]["api"]["requests_timeout"] or "❌ Не задано"
    listener_requests_delay = config["playerok"]["api"]["listener_requests_delay"] or "❌ Не задано"
    txt = textwrap.dedent(f"""
        ⚙️ <b>Настройки → 📶 Соединение</b>

        🌐 <b>Прокси:</b> {proxy}
        🛜 <b>Таймаут подключения к playerok.com:</b> {requests_timeout}
        ⏱️ <b>Периодичность запросов к playerok.com:</b> {listener_requests_delay}

        <b>Что такое таймаут подключения к playerok.com?</b>
        Это максимальное время, за которое должен прийти ответ на запрос с сайта Playerok. Если время истекло, а ответ не пришёл — бот выдаст ошибку. Если у вас слабый интернет, указывайте значение больше

        <b>Что такое периодичность запросов к playerok.com?</b>
        С какой периодичностью будут отправляться запросы на Playerok для получения событий. Не рекомендуем ставить ниже 4 секунд, так как Playerok попросту может забанить ваш IP адрес, и вы уже не сможете отправлять с него запросы

        Выберите параметр для изменения ↓
    """)
    return txt

def settings_conn_kb():
    config = sett.get("config")
    proxy = config["playerok"]["api"]["proxy"] or "❌ Не задано"
    requests_timeout = config["playerok"]["api"]["requests_timeout"] or "❌ Не задано"
    listener_requests_delay = config["playerok"]["api"]["listener_requests_delay"] or "❌ Не задано"
    rows = [
        [InlineKeyboardButton(text=f"🌐 Прокси: {proxy}", callback_data="enter_proxy")],
        [InlineKeyboardButton(text=f"🛜 Таймаут подключения к playerok.com: {requests_timeout}", callback_data="enter_requests_timeout")],
        [InlineKeyboardButton(text=f"⏱️ Периодичность запросов к playerok.com: {listener_requests_delay}", callback_data="enter_listener_requests_delay")],
        [
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.SettingsNavigation(to="default").pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.SettingsNavigation(to="conn").pack())
        ]
    ]
    if config["playerok"]["api"]["proxy"]: rows[0].append(InlineKeyboardButton(text=f"❌🌐 Убрать прокси", callback_data="remove_proxy"))
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb

def settings_conn_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        ⚙️ <b>Настройки → 📶 Соединение</b>
        \n{placeholder}
    """)
    return txt


def settings_items_text():
    config = sett.get("config")
    auto_restore_items_enabled = "🟢 Включено" if config["playerok"]["bot"]["auto_restore_items_enabled"] else "🔴 Выключено"
    if config["playerok"]["bot"]["auto_restore_items_priority_status"] == "DEFAULT": auto_restore_items_priority_status = "🆓 Бесплатный"
    elif config["playerok"]["bot"]["auto_restore_items_priority_status"] == "PREMIUM": auto_restore_items_priority_status = "⚡ Премиум"
    else: auto_restore_items_priority_status = "❌ Не задано"
    txt = textwrap.dedent(f"""
        ⚙️ <b>Настройки → 📦 Предметы</b>

        ♻️ <b>Авто-восстановление предметов:</b> {auto_restore_items_enabled}
        📊 <b>Приоритет восстановленных предметов:</b> {auto_restore_items_priority_status}

        <b>Что такое автоматическое восстановление предметов?</b>
        На Playerok как только ваш товар покупают - он исчезает из продажи. Эта функция позволит автоматически восстанавливать (заново выставлять) предмет, который только что купили, чтобы он снова был на продаже.
        
        <b>Что такое cтатус приоритета для восстановленных предметов?</b>
        С каким статусом будет выставлять на продажу предмет, который был автоматически восстановлен. Учтите, что за премиум статус нужно платить, и если у вас не будет денег на балансе аккаунта для этого, товар будет выставляен по бесплатному приоритету.

        Выберите параметр для изменения ↓
    """)
    return txt

def settings_items_kb():
    config = sett.get("config")
    auto_restore_items_enabled = "🟢 Включено" if config["playerok"]["bot"]["auto_restore_items_enabled"] else "🔴 Выключено"
    if config["playerok"]["bot"]["auto_restore_items_priority_status"] == "DEFAULT": auto_restore_items_priority_status = "🆓 Бесплатный"
    elif config["playerok"]["bot"]["auto_restore_items_priority_status"] == "PREMIUM": auto_restore_items_priority_status = "⚡ Премиум"
    else: auto_restore_items_priority_status = "❌ Не задано"
    rows = [
        [InlineKeyboardButton(text=f"♻️ Авто-восстановление предметов: {auto_restore_items_enabled}", callback_data="switch_auto_restore_items_enabled")],
        [InlineKeyboardButton(text=f"📊 Приоритет восстановленных предметов: {auto_restore_items_priority_status}", callback_data="switch_auto_restore_items_priority_status")],
        [
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.SettingsNavigation(to="default").pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.SettingsNavigation(to="items").pack())
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb

def settings_items_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        ⚙️ <b>Настройки → 📦 Предметы</b>
        \n{placeholder}
    """)
    return txt


def settings_comm_text():
    custom_commands = sett.get("custom_commands")
    txt = textwrap.dedent(f"""
        ⚙️ <b>Настройки</b> → ⌨️ <b>Пользовательские команды</b>
        Всего <b>{len(custom_commands.keys())}</b> пользовательских команд в конфиге

        Перемещайтесь по разделам ниже. Нажмите на команду, чтобы перейти в её редактирование ↓
    """)
    return txt

def settings_comm_kb(page: int = 0):
    custom_commands = sett.get("custom_commands")
    rows = []
    items_per_page = 7
    total_pages = math.ceil(len(custom_commands.keys())/items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages-1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    for command in list(custom_commands.keys())[start_offset:end_offset]:
        command_text = "\n".join(custom_commands[command])
        rows.append([InlineKeyboardButton(text=f'{command} → {command_text}', callback_data=calls.CustomCommandPage(command=command).pack())])
        
    buttons_row = []
    if page > 0: btn_back = InlineKeyboardButton(text="←", callback_data=calls.CustomCustomCommandsPagination(page=page-1).pack())
    else: btn_back = InlineKeyboardButton(text="🛑",callback_data="123")
    buttons_row.append(btn_back)
        
    btn_pages = InlineKeyboardButton(text=f"{page+1}/{total_pages}",callback_data="enter_custom_commands_page")
    buttons_row.append(btn_pages)
    
    if page < total_pages-1: btn_next = InlineKeyboardButton(text="→", callback_data=calls.CustomCustomCommandsPagination(page=page+1).pack())
    else: btn_next = InlineKeyboardButton(text="🛑", callback_data="123")
    buttons_row.append(btn_next)
    rows.append(buttons_row)

    rows.append([InlineKeyboardButton(text="➕⌨️ Добавить",callback_data="enter_new_custom_command")])
    rows.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.SettingsNavigation(to="default").pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.CustomCommandsPagination(page=page).pack())
        ])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb

def settings_comm_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        ⚙️ <b>Настройки</b> → ⌨️ <b>Пользовательские команды</b>
        \n{placeholder}
    """)
    return txt

def adding_new_comm_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        ⚙️ <b>Добавление пользовательской команды</b>
        \n{placeholder}
    """)
    return txt


def settings_comm_page_text(command: str):
    custom_commands = sett.get("custom_commands")
    command_text = "\n".join(custom_commands[command]) or "❌ Не задано"
    txt = textwrap.dedent(f"""
        ✏️ <b>Редактирование пользовательской команды</b>

        ⌨️ <b>Команда:</b> {command}
        💬 <b>Ответ:</b> 
        <blockquote>{command_text}</blockquote>

        Выберите параметр для изменения ↓
    """)
    return txt

def settings_comm_page_kb(command: str, page: int = 0):
    custom_commands = sett.get("custom_commands")
    command_text = "\n".join(custom_commands[command]) or "❌ Не задано"
    rows = [
        [InlineKeyboardButton(text=f"✍️ Ответ: {command_text}", callback_data="enter_custom_command_answer")],
        [InlineKeyboardButton(text="🗑️ Удалить команду", callback_data="confirm_deleting_custom_command")],
        [
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.CustomCommandsPagination(page=page).pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.CustomCommandPage(command=command).pack())
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb

def settings_comm_page_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        ✏️ <b>Редактирование пользовательской команды</b>
        \n{placeholder}
    """)
    return txt


def settings_deliv_text():
    auto_deliveries = sett.get("auto_deliveries")
    txt = textwrap.dedent(f"""
        ⚙️ <b>Настройки</b> → 🚀 <b>Авто-выдача</b>
        Всего <b>{len(auto_deliveries)}</b> настроенных лотов для авто-выдачи в конфиге

        Перемещайтесь по разделам ниже. Нажмите на ID лота, чтобы перейти в редактирование его авто-выдачи ↓
    """)
    return txt

def settings_deliv_kb(page: int = 0):
    auto_deliveries: list = sett.get("auto_deliveries")
    rows = []
    items_per_page = 7
    total_pages = math.ceil(len(auto_deliveries) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    for deliv in list(auto_deliveries)[start_offset:end_offset]:
        keyphrases = ", ".join(deliv.get("keyphrases")) or "❌ Не задано"
        message = "\n".join(deliv.get("message")) or "❌ Не задано"
        rows.append([InlineKeyboardButton(text=f"{keyphrases[:32] + ('...' if len(keyphrases) > 32 else '')} → {message}", callback_data=calls.AutoDeliveryPage(index=auto_deliveries.index(deliv)).pack())])

    buttons_row = []
    if page > 0: btn_back = InlineKeyboardButton(text="←", callback_data=calls.AutoDeliveriesPagination(page=page-1).pack())
    else: btn_back = InlineKeyboardButton(text="🛑", callback_data="123")
    buttons_row.append(btn_back)

    btn_pages = InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="enter_auto_deliveries_page")
    buttons_row.append(btn_pages)

    if page < total_pages - 1: btn_next = InlineKeyboardButton(text="→", callback_data=calls.AutoDeliveriesPagination(page=page+1).pack())
    else: btn_next = InlineKeyboardButton(text="🛑", callback_data="123")
    buttons_row.append(btn_next)

    rows.append(buttons_row)
    rows.append([InlineKeyboardButton(text="➕🚀 Добавить", callback_data="enter_new_auto_delivery_keyphrases")])
    rows.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.SettingsNavigation(to="default").pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.AutoDeliveriesPagination(page=page).pack())
        ])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb

def settings_deliv_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        ⚙️ <b>Настройки</b> → ⌨️ <b>Авто-выдача</b>
        \n{placeholder}
    """)
    return txt

def adding_new_deliv_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        🚀 <b>Добавление пользовательской авто-выдачи</b>
        \n{placeholder}
    """)
    return txt


def settings_deliv_page_text(index: int):
    auto_deliveries = sett.get("auto_deliveries")
    keyphrases = "</code>, <code>".join(auto_deliveries[index].get("keyphrases")) or "❌ Не задано"
    message = "\n".join(auto_deliveries[index].get("message")) or "❌ Не задано"
    txt = textwrap.dedent(f"""
        ✏️ <b>Редактирование авто-выдачи</b>

        🔑 <b>Ключевые фразы:</b> <code>{keyphrases}</code>
        💬 <b>Сообщение:</b> <blockquote>{message}</blockquote>

        Выберите параметр для изменения ↓
    """)
    return txt

def settings_deliv_page_kb(index: int, page: int = 0):
    auto_deliveries = sett.get("auto_deliveries")
    keyphrases = ", ".join(auto_deliveries[index].get("keyphrases")) or "❌ Не задано"
    message = "\n".join(auto_deliveries[index].get("message")) or "❌ Не задано"
    rows = [
        [InlineKeyboardButton(text=f"🔑 Ключевые фразы: {keyphrases}", callback_data="enter_auto_delivery_keyphrases")],
        [InlineKeyboardButton(text=f"💬 Сообщение: {message}", callback_data="enter_auto_delivery_message")],
        [InlineKeyboardButton(text="🗑️ Удалить авто-выдачу", callback_data="confirm_deleting_auto_delivery")],
        [
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.AutoDeliveriesPagination(page=page).pack()), 
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.AutoDeliveryPage(index=index).pack())
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb

def settings_deliv_page_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        ✏️ <b>Редактирование авто-выдачи</b>
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

    for mess_id, mess_text in list(messages.items())[start_offset:end_offset]:
        mess_text_joined = "\n".join(mess_text)
        rows.append([InlineKeyboardButton(text=f"{mess_id} | {mess_text_joined}", callback_data=calls.MessagePage(message_id=mess_id).pack())])

    buttons_row = []
    btn_back = InlineKeyboardButton(text="←", callback_data=calls.MessagesPagination(page=page-1).pack()) if page > 0 else InlineKeyboardButton(text="🛑", callback_data="123")
    buttons_row.append(btn_back)
    buttons_row.append(InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="enter_messages_page"))

    btn_next = InlineKeyboardButton(text="→", callback_data=calls.MessagesPagination(page=page+1).pack()) if page < total_pages - 1 else InlineKeyboardButton(text="🛑", callback_data="123")
    buttons_row.append(btn_next)
    rows.append(buttons_row)

    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.SettingsNavigation(to="default").pack()),
                 InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.MessagesPagination(page=page).pack())])
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
    message_text = "\n".join(messages[message_id]) or "❌ Не задано"
    txt = textwrap.dedent(f"""
        ✒️ <b>Редактирование сообщения</b>

        🆔 <b>ID сообщения:</b> {message_id}
        💬 <b>Текст сообщения:</b> <blockquote>{message_text}</blockquote>

        Выберите параметр для изменения ↓
    """)
    return txt

def settings_mess_page_kb(message_id: int, page: int = 0):
    messages = sett.get("messages")
    message_text = "\n".join(messages[message_id]) or "❌ Не задано"
    rows = [
        [InlineKeyboardButton(text=f"💬 Текст сообщения: {message_text}", callback_data="enter_message_text")],
        [
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MessagesPagination(page=page).pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.MessagePage(message_id=message_id).pack())
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


def settings_logger_text():
    config = sett.get("config")
    tg_logging_enabled = "🟢 Включено" if config["playerok"]["bot"]["tg_logging_enabled"] else "🔴 Выключено"
    tg_logging_chat_id = config["playerok"]["bot"]["tg_logging_chat_id"] or "✔️ Ваш чат с ботом"
    tg_logging_events = config["playerok"]["bot"]["tg_logging_events"] or {}
    event_new_user_message = "🟢" if tg_logging_events.get("new_user_message") else "🔴"
    event_new_system_message = "🟢" if tg_logging_events.get("new_system_message") else "🔴"
    event_new_deal = "🟢" if tg_logging_events.get("new_deal") else "🔴"
    event_new_problem = "🟢" if tg_logging_events.get("new_problem") else "🔴"
    event_deal_status_changed = "🟢" if tg_logging_events.get("deal_status_changed") else "🔴"
    txt = textwrap.dedent(f"""
        ⚙️ <b>Настройки → 👀 Логгер</b>

        👀 <b>Логгирование ивентов Playerok в Telegram:</b> {tg_logging_enabled}
        💬 <b>ID чата для логов:</b> <b>{tg_logging_chat_id}</b>
        📢 <b>Ивенты логгирования:</b>
        ┣ {event_new_user_message} <b>💬👤 Новое сообщение от пользователя</b>
        ┣ {event_new_system_message} <b>💬⚙️ Новое системное сообщение</b>
        ┣ {event_new_deal} <b>📋 Новая сделка</b>
        ┣ {event_new_problem} <b>🤬 Новая жалоба в сделке</b>
        ┗ {event_deal_status_changed} <b>🔄️📋 Статус сделки изменился</b>
        
        Выберите параметр для изменения ↓
    """)
    return txt

def settings_logger_kb():
    config = sett.get("config")
    tg_logging_enabled = "🟢 Включено" if config["playerok"]["bot"]["tg_logging_enabled"] else "🔴 Выключено"
    tg_logging_chat_id = config["playerok"]["bot"]["tg_logging_chat_id"] or "✔️ Ваш чат с ботом"
    tg_logging_events = config["playerok"]["bot"]["tg_logging_events"] or {}
    event_new_user_message = "🟢" if tg_logging_events.get("new_user_message") else "🔴"
    event_new_system_message = "🟢" if tg_logging_events.get("new_system_message") else "🔴"
    event_new_deal = "🟢" if tg_logging_events.get("new_deal") else "🔴"
    event_new_problem = "🟢" if tg_logging_events.get("new_problem") else "🔴"
    event_deal_status_changed = "🟢" if tg_logging_events.get("deal_status_changed") else "🔴"
    rows = [
        [InlineKeyboardButton(text=f"👀 Логгирование ивентов Playerok в Telegram: {tg_logging_enabled}", callback_data="switch_tg_logging_enabled")],
        [InlineKeyboardButton(text=f"💬 ID чата для логов: {tg_logging_chat_id}", callback_data="enter_tg_logging_chat_id")],
        [
        InlineKeyboardButton(text=f"{event_new_user_message} 💬👤 Новое сообщение от пользователя", callback_data="switch_tg_logging_event_new_user_message"),
        InlineKeyboardButton(text=f"{event_new_system_message} 💬⚙️ Новое системное сообщение", callback_data="switch_tg_logging_event_new_system_message"),
        ],
        [
        InlineKeyboardButton(text=f"{event_new_deal} 📋 Новая сделка", callback_data="switch_tg_logging_event_new_deal"),
        InlineKeyboardButton(text=f"{event_new_problem} 🤬 Новая жалоба в сделке", callback_data="switch_tg_logging_event_new_problem"),
        InlineKeyboardButton(text=f"{event_deal_status_changed} 🔄️📋 Статус сделки изменился", callback_data="switch_tg_logging_event_deal_status_changed")
        ],
        [
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.SettingsNavigation(to="default").pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.SettingsNavigation(to="logger").pack())
        ]
    ]
    if config["playerok"]["bot"]["tg_logging_chat_id"]:
        rows[1].append(InlineKeyboardButton(text=f"❌💬 Очистить", callback_data="clean_tg_logging_chat_id"))
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb

def settings_logger_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        ⚙️ <b>Настройки → 👀 Логгер</b>
        \n{placeholder}
    """)
    return txt
    

def settings_other_text():
    config = sett.get("config")
    read_chat_before_sending_message_enabled = "🟢 Включено" if config["playerok"]["bot"]["read_chat_before_sending_message_enabled"] else "🔴 Выключено"
    auto_complete_deals_enabled = "🟢 Включено" if config["playerok"]["bot"]["auto_complete_deals_enabled"] else "🔴 Выключено"
    first_message_enabled = "🟢 Включено" if config["playerok"]["bot"]["first_message_enabled"] else "🔴 Выключено"
    custom_commands_enabled = "🟢 Включено" if config["playerok"]["bot"]["custom_commands_enabled"] else "🔴 Выключено"
    auto_deliveries_enabled = "🟢 Включено" if config["playerok"]["bot"]["auto_deliveries_enabled"] else "🔴 Выключено"
    messages_watermark_enabled = "🟢 Включено" if config["playerok"]["bot"]["messages_watermark_enabled"] else "🔴 Выключено"
    messages_watermark = config["playerok"]["bot"]["messages_watermark"] or "❌ Не задано"
    txt = textwrap.dedent(f"""
        ⚙️ <b>Настройки → 🔧 Прочее</b>

        👀 <b>Чтение чата перед отправкой сообщения:</b> {read_chat_before_sending_message_enabled}
        ☑️ <b>Авто-подтверждение заказов:</b> {auto_complete_deals_enabled}
        👋 <b>Приветственное сообщение:</b> {first_message_enabled}
        🔧 <b>Пользовательские команды:</b> {custom_commands_enabled}
        🚀 <b>Авто-выдача:</b> {auto_deliveries_enabled}
        ©️ <b>Водяной знак под сообщениями:</b> {messages_watermark_enabled}
        ✍️©️ <b>Водяной знак:</b> {messages_watermark}

        <b>Что такое автоматические ответы на отзывы?</b>
        Когда покупатель будет оставлять отзыв, бот будет автоматически отвечать на него. В ответе на отзыв будут написаны детали заказа.

        Выберите параметр для изменения ↓
    """)
    return txt

def settings_other_kb():
    config = sett.get("config")
    read_chat_before_sending_message_enabled = "🟢 Включено" if config["playerok"]["bot"]["read_chat_before_sending_message_enabled"] else "🔴 Выключено"
    auto_complete_deals_enabled = "🟢 Включено" if config["playerok"]["bot"]["auto_complete_deals_enabled"] else "🔴 Выключено"
    first_message_enabled = "🟢 Включено" if config["playerok"]["bot"]["first_message_enabled"] else "🔴 Выключено"
    custom_commands_enabled = "🟢 Включено" if config["playerok"]["bot"]["custom_commands_enabled"] else "🔴 Выключено"
    auto_deliveries_enabled = "🟢 Включено" if config["playerok"]["bot"]["auto_deliveries_enabled"] else "🔴 Выключено"
    messages_watermark_enabled = "🟢 Включено" if config["playerok"]["bot"]["messages_watermark_enabled"] else "🔴 Выключено"
    messages_watermark = config["playerok"]["bot"]["messages_watermark"] or "❌ Не задано"
    rows = [
        [InlineKeyboardButton(text=f"👀 Чтение чата перед отправкой сообщения: {read_chat_before_sending_message_enabled}", callback_data="switch_read_chat_before_sending_message_enabled")],
        [InlineKeyboardButton(text=f"☑️ Авто-подтверждение заказов: {auto_complete_deals_enabled}", callback_data="switch_auto_complete_deals_enabled")],
        [InlineKeyboardButton(text=f"👋 Приветственное сообщение: {first_message_enabled}", callback_data="switch_first_message_enabled")],
        [InlineKeyboardButton(text=f"🔧 Пользовательские команды: {custom_commands_enabled}", callback_data="switch_custom_commands_enabled")],
        [InlineKeyboardButton(text=f"🚀 Авто-выдача: {auto_deliveries_enabled}", callback_data="switch_auto_deliveries_enabled")],
        [InlineKeyboardButton(text=f"©️ Водяной знак под сообщениями: {messages_watermark_enabled}", callback_data="switch_messages_watermark_enabled")],
        [InlineKeyboardButton(text=f"✍️©️ Водяной знак: {messages_watermark}", callback_data="enter_messages_watermark")],
        [
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.SettingsNavigation(to="default").pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.SettingsNavigation(to="other").pack())
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb

def settings_other_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        ⚙️ <b>Настройки → 🔧 Прочее</b>
        \n{placeholder}
    """)
    return txt

                    
def modules_text():
    from core.modules_manager import ModulesManager
    modules = ModulesManager.get_modules()
    txt = textwrap.dedent(f"""
        🔌 <b>Модули</b>
        Всего <b>{len(modules)}</b> загруженных модулей

        Перемещайтесь по разделам ниже. Нажмите на название модуля, чтобы перейти в его управление ↓
    """)
    return txt

def modules_kb(page: int = 0):
    from core.modules_manager import ModulesManager
    modules = ModulesManager.get_modules()
    rows = []
    items_per_page = 7
    total_pages = math.ceil(len(modules) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    for module in list(modules)[start_offset:end_offset]:
        rows.append([InlineKeyboardButton(text=module.meta.name, callback_data=calls.ModulePage(uuid=module.uuid).pack())])

    buttons_row = []
    if page > 0: btn_back = InlineKeyboardButton(text="←", callback_data=calls.ModulesPagination(page=page - 1).pack())
    else: btn_back = InlineKeyboardButton(text="🛑", callback_data="123")
    buttons_row.append(btn_back)

    buttons_row.append(InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="enter_module_page"))

    if page < total_pages - 1: btn_next = InlineKeyboardButton(text="→", callback_data=calls.ModulesPagination(page=page+1).pack())
    else: btn_next = InlineKeyboardButton(text="🛑", callback_data="123")
    buttons_row.append(btn_next)
    rows.append(buttons_row)

    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack())])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def module_page_text(module_uuid: UUID):
    from core.modules_manager import ModulesManager, Module
    module: Module = ModulesManager.get_module_by_uuid(module_uuid)
    if not module: raise Exception("Не удалось найти модуль")
    txt = textwrap.dedent(f"""
        🔧 <b>Управление модулем</b>

        <b>Модуль</b> <code>{module.meta.name}</code>:          
        ┣ UUID: <b>{module.uuid}</b>
        ┣ Версия: <b>{module.meta.version}</b>
        ┣ Описание: <blockquote>{module.meta.description}</blockquote>
        ┣ Авторы: <b>{module.meta.authors}</b>
        ┗ Ссылки: <b>{module.meta.links}</b>

        🔌 <b>Состояние:</b> {'🟢 Включен' if module.enabled else '🔴 Выключен'}

        Выберите действие для управления ↓
    """)
    return txt

def module_page_kb(module_uuid: UUID, page: int = 0):
    from core.modules_manager import ModulesManager, Module
    module: Module = ModulesManager.get_module_by_uuid(module_uuid)
    if not module: raise Exception("Не удалось найти модуль")
    rows = [
        [InlineKeyboardButton(text="🔴 Отключить модуль" if module.enabled else "🟢 Подключить модуль", callback_data="switch_module_enabled")],
        [
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.ModulesPagination(page=page).pack()),
        InlineKeyboardButton(text="🔄️ Обновить", callback_data=calls.ModulePage(uuid=module_uuid).pack())
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb

def module_page_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        🔧 <b>Управление модулем</b>
        \n{placeholder}
    """)
    return txt


def call_seller_text(calling_name, chat_link):
    txt = textwrap.dedent(f"""
        🆘 <b>{calling_name}</b> требуется ваша помощь!
        {chat_link}
    """)
    return txt