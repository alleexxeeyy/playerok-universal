from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import math
import textwrap

from utils import github_str_to_dt

from .. import callback_datas as calls


def releases_text(releases: list):
    if not releases:
        txt = textwrap.dedent(f"""
            <b>📜 История обновлений</b>
            <blockquote>Обновлений пока нет</blockquote>
        """)
        return txt

    txt = textwrap.dedent(f"""
        <b>📜 История обновлений</b>
        Всего <b>{len(releases)}</b> обновлений:
    """)
    return txt


def releases_kb(releases: list, page=0):
    rows = []
    items_per_page = 8
    total_pages = math.ceil(len(releases)/items_per_page)
    total_pages = total_pages if total_pages > 0 else 1

    if page < 0: page = 0
    elif page >= total_pages: page = total_pages-1

    start_offset = page * items_per_page
    end_offset = start_offset + items_per_page

    for index, release in enumerate(releases[start_offset:end_offset], start=start_offset):
        tag = release.get("tag_name") or "?"
        published_at = release.get("published_at")
        if published_at:
            try:
                published_at = github_str_to_dt(published_at).strftime("%d.%m.%Y")
            except:
                published_at = None

        text = f"🚀 {tag}" + (f" — {published_at}" if published_at else "")
        rows.append([InlineKeyboardButton(
            text=text,
            callback_data=calls.ReleasePage(index=index).pack())
        ])

    if total_pages > 1:
        buttons_row = []

        btn_back = InlineKeyboardButton(text="←", callback_data=calls.ReleasesPagination(page=page-1).pack()) if page > 0 else InlineKeyboardButton(text="🛑", callback_data="null_answer")
        buttons_row.append(btn_back)

        btn_pages = InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="null_answer")
        buttons_row.append(btn_pages)

        btn_next = InlineKeyboardButton(text="→", callback_data=calls.ReleasesPagination(page=page+1).pack()) if page < total_pages - 1 else InlineKeyboardButton(text="🛑", callback_data="null_answer")
        buttons_row.append(btn_next)

        rows.append(buttons_row)

    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="updates").pack())])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def releases_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>📜 История обновлений</b>
    """) + f"\n{placeholder}\n"
    return txt
