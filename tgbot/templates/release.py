from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from html import escape
import textwrap

from utils import github_str_to_dt

from .. import callback_datas as calls


def release_text(release: dict):
    tag = escape(str(release.get("tag_name") or "?"), quote=False)
    desc = escape(str(release.get("body") or "Без описания"), quote=False)
    url = release.get("html_url")

    header = f'<a href="{url}">{tag}</a>' if url else tag
    txt = textwrap.dedent(f"""
        <b>📄🚀 Обновление {header}</b>
    """) + f"\n<b>💎 Изменения:</b>\n<blockquote>{desc}</blockquote>\n"

    if release.get("published_at"):
        try:
            published_at = github_str_to_dt(release["published_at"]).strftime("%d.%m.%Y %H:%M:%S")
            txt += f"\n<b>📅 Дата выхода:</b> {published_at}\n"
        except:
            pass

    return txt


def release_kb(page=0):
    rows = [
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.ReleasesPagination(page=page).pack())]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def release_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>📄🚀 Обновление</b>
    """) + f"\n{placeholder}\n"
    return txt
