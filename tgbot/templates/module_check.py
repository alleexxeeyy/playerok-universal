from html import escape
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from core.bootreport import explain_error
from .. import callback_datas as calls


def module_check_text(header: str, checks: list[dict]):
    lines = [header, "", "🧪 <b>Проверка запуска:</b>"]
    for check in checks:
        name = f"<b>{escape(check['name'])}</b>"
        status = check["status"]
        if status == "ok":
            lines.append(f"✅ {name} — запускается")
        elif status == "timeout":
            lines.append(f"⏳ {name} — не успел проверить, проверится при перезагрузке")
        elif status == "deleted":
            lines.append(f"🗑️ {name} — удалён")
        elif status == "rolled_back":
            lines.append(f"↩️ {name} — возвращена прежняя версия")
        else:
            lines.append(f"❌ {name} — не запустится")
            lines.append(f"<blockquote>{explain_error(check['trace'])}</blockquote>")

    if any(check["status"] in ("ok", "timeout", "rolled_back") for check in checks):
        lines += ["", "❗ Для подключения <b>необходима перезагрузка</b> — /restart"]
    if any(check["status"] == "error" for check in checks):
        lines += ["", "Модуль с ошибкой можно удалить или вернуть его прежнюю версию кнопками ниже"]
    return "\n".join(lines)


def module_check_kb(checks: list[dict], back_cb: str):
    rows = []
    for i, check in enumerate(checks):
        if check["status"] != "error":
            continue
        row = [InlineKeyboardButton(text=f"📄 {check['name']}", callback_data=calls.ModuleCheckAction(idx=i, do="trace").pack())]
        if check.get("has_backup"):
            row.append(InlineKeyboardButton(text="↩️ Откатить", callback_data=calls.ModuleCheckAction(idx=i, do="rollback").pack()))
        else:
            row.append(InlineKeyboardButton(text="🗑️ Удалить", callback_data=calls.ModuleCheckAction(idx=i, do="delete").pack()))
        rows.append(row)
    if any(check["status"] in ("ok", "timeout", "rolled_back") for check in checks):
        rows.append([InlineKeyboardButton(text="🔄 Перезагрузить сейчас", callback_data="module_check_restart")])
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=back_cb)])
    return InlineKeyboardMarkup(inline_keyboard=rows)
