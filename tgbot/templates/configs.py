import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from core.configs import BACKUPS_DIR, MAX_BACKUPS

from .. import callback_datas as calls


def configs_text():
    txt = textwrap.dedent(f"""
        <b>🗂 Конфиги</b>

        Здесь вы можете <b>выгрузить</b> конфиги бота, чтобы перенести их на другое устройство, или <b>импортировать</b> их обратно.
        <blockquote><b>(?)</b> <b>Основной конфиг</b> — только config.json.
        <b>Все конфиги</b> — архив со всеми настройками из папки bot_settings.
        <b>Конфиги + дата</b> — то же самое плюс данные бота из папки bot_data (кэш заказов, сохранённые предметы, список инициализированных пользователей).
        <b>Создать бэкап</b> — сохраняет копию текущих конфигов и данных в папку {BACKUPS_DIR} на этом же устройстве. Бот делает это и сам перед каждым импортом, храня последние {MAX_BACKUPS} копий.</blockquote>

        ❗ <b>Не передавайте конфиги третьим лицам</b> — в них лежат ваши Cookie-данные, токен Telegram бота и ключ-пароль
    """)
    return txt


def configs_kb():
    rows = [
        [InlineKeyboardButton(text="📄 Основной конфиг", callback_data="export_main_config")],
        [InlineKeyboardButton(text="📦 Все конфиги", callback_data="export_all_configs")],
        [InlineKeyboardButton(text="🗃 Конфиги + дата", callback_data="export_full_configs")],
        [InlineKeyboardButton(text="📥 Импортировать", callback_data="send_config_file")],
        [InlineKeyboardButton(text="💾 Создать бэкап", callback_data="make_config_backup")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def configs_secrets_kb():
    rows = [
        [InlineKeyboardButton(text="🔑 Перенести креды из файла", callback_data="import_config_take_secrets")],
        [InlineKeyboardButton(text="🛡 Оставить текущие", callback_data="import_config_keep_secrets")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="import_config_cancel")]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def configs_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>🗂 Конфиги</b>
        \n{placeholder}
    """)
    return txt
