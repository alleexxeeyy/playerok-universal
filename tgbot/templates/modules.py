import math
import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from core.modules import get_modules

from .. import callback_datas as calls

                    
def modules_text():
    modules = get_modules()
    txt = textwrap.dedent(f"""
        <b>🔌 Модули</b>

        Всего <b>{len(modules)}</b> подключенных модулей:
    """)
    return txt


def modules_kb(page: int = 0):
    modules = get_modules()
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

    if total_pages > 1:
        buttons_row = []
        btn_back = InlineKeyboardButton(text="←", callback_data=calls.ModulesPagination(page=page - 1).pack()) if page > 0 else InlineKeyboardButton(text="🛑", callback_data="123")
        buttons_row.append(btn_back)

        btn_pages = InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="enter_module_page")
        buttons_row.append(btn_pages)

        btn_next = InlineKeyboardButton(text="→", callback_data=calls.ModulesPagination(page=page+1).pack()) if page < total_pages - 1 else InlineKeyboardButton(text="🛑", callback_data="123")
        buttons_row.append(btn_next)
        rows.append(buttons_row)

    rows.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack())
    ])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb