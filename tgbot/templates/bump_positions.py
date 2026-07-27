import math
import textwrap
from datetime import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett
from utils import get_current_bump_position

from .. import callback_datas as calls


def get_item_positions() -> list[dict]:
    from plbot.playerokbot import get_playerok_bot
    plbot = get_playerok_bot()
    if not plbot:
        return []

    with plbot.bump_lock:
        positions = [dict(pos) for pos in (plbot.item_positions or {}).values()]
    return sorted(positions, key=lambda p: p["position"])


def bump_positions_text():
    config = sett.get("config")
    position = get_current_bump_position(config)
    positions = get_item_positions()

    last_check_iso = config["playerok"]["auto_bump_items"]["last_check_time"]
    last_check = datetime.fromisoformat(last_check_iso).strftime("%d.%m.%Y %H:%M:%S") if last_check_iso else "никогда"

    if positions:
        out_of_range = len([p for p in positions if p["position"] > position])
        body = textwrap.dedent(f"""
            <b>🔴 Вне позиции:</b> {out_of_range}
        """).lstrip("\n")
    else:
        body = textwrap.dedent(f"""
            <blockquote>Проверок ещё не было. Включите авто-поднятие, выберите способ <b>По позиции</b> и подождите первую проверку.</blockquote>
        """)

    txt = textwrap.dedent(f"""
        <b>⬆️📊 Позиции товаров</b>
        <blockquote><b>(?)</b> Позиции товаров, которые бот отслеживает в способе поднятия <b>По позиции</b>. Обновляются при каждой проверке.</blockquote>

        <b>📊 Позиция поднятия сейчас:</b> {position}
        <b>📦 Отслеживается:</b> {len(positions)}
    """) + body + textwrap.dedent(f"""
        ⏮️ Последняя проверка была <b>{last_check}</b>
    """)
    return txt


def bump_positions_kb(page=0):
    config = sett.get("config")
    position = get_current_bump_position(config)
    positions = get_item_positions()

    rows = []
    items_per_page = 7
    total_pages = math.ceil(len(positions) / items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages - 1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    for pos in positions[start_offset:end_offset]:
        name_frmtd = pos["name"][:28] + ("..." if len(pos["name"]) > 28 else "")
        marker = "🔴" if pos["position"] > position else "🟢"
        rows.append([
            InlineKeyboardButton(text=f"{marker} {pos['position']} — {name_frmtd}", callback_data="null_answer")
        ])

    if total_pages > 1:
        buttons_row = []
        btn_back = InlineKeyboardButton(text="←", callback_data=calls.BumpItemsPositionsPagination(page=page-1).pack()) if page > 0 else InlineKeyboardButton(text="🛑", callback_data="null_answer")
        buttons_row.append(btn_back)

        btn_pages = InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="null_answer")
        buttons_row.append(btn_pages)

        btn_next = InlineKeyboardButton(text="→", callback_data=calls.BumpItemsPositionsPagination(page=page+1).pack()) if page < total_pages - 1 else InlineKeyboardButton(text="🛑", callback_data="null_answer")
        buttons_row.append(btn_next)
        rows.append(buttons_row)

    rows.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="bump").pack()),
    ])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb
