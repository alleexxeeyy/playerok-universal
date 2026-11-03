from html import escape
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from core.bootreport import explain_error
from .. import callback_datas as calls


CHECK_BUDGET = 3400 # лимит Telegram 4096 вместе с шапкой экрана и заголовком импорта
CONFIRM_LABELS = {"delete": "🗑️ Да, удалить", "rollback": "↩️ Да, откатить"}


def module_check_text(header: str, checks: list[dict]):
    lines = [header, "", "<b>🧪 Проверка загрузки:</b>"]
    size = sum(len(line) + 1 for line in lines)
    hidden = 0
    for check in checks:
        name = f"<b>{escape(check['name'])}</b>"
        status = check["status"]
        if status == "ok":
            block = f"✅ {name} — загружается"
        elif status == "timeout":
            block = f"⏳ {name} — не успел проверить, проверится при перезагрузке"
        elif status == "deleted":
            block = f"🗑️ {name} — удалён"
        elif status == "rolled_back":
            block = f"↩️ {name} — возвращена прежняя версия"
        else:
            block = f"<blockquote>❌ {name} — ошибка при загрузке\n{explain_error(check['trace'])}</blockquote>"
        if check.get("confirm"):
            action = "удалить модуль" if check["confirm"] == "delete" else "вернуть прежнюю версию"
            block += f"\n⚠️ Точно {action} {name}? Подтвердите кнопкой ниже"

        if size + len(block) + 1 > CHECK_BUDGET:
            hidden += 1
            continue
        lines.append(block)
        size += len(block) + 1

    if hidden:
        lines.append(f"...и ещё {hidden} — подробности по кнопкам ниже")
    if any(check["status"] in ("ok", "timeout", "rolled_back") for check in checks):
        lines += ["", "❗ Для подключения <b>необходима перезагрузка</b> — /restart"]
    if any(check["status"] == "error" for check in checks):
        lines += [
            "",
            "<blockquote><b>(?)</b> Проверка запускает модуль отдельно от бота — если модуль рассчитан только на работу внутри бота, "
            "ошибка может быть ложной. Удалить модуль или вернуть прежнюю версию можно кнопками ниже.</blockquote>"
        ]
    return "\n".join(lines)


def module_check_kb(checks: list[dict], back_cb: str, token: int):
    def cb(i: int, do: str) -> str:
        return calls.ModuleCheckAction(token=token, idx=i, do=do).pack()

    rows = []
    for i, check in enumerate(checks):
        status = check["status"]
        if status not in ("error", "timeout"):
            continue
        if check.get("confirm"):
            rows.append([
                InlineKeyboardButton(text=CONFIRM_LABELS[check["confirm"]], callback_data=cb(i, f"{check['confirm']}_yes")),
                InlineKeyboardButton(text="✖️ Отмена", callback_data=cb(i, "cancel"))
            ])
            continue
        if status == "timeout":
            if check.get("has_backup"):
                rows.append([InlineKeyboardButton(text=f"↩️ Откатить {check['name']}", callback_data=cb(i, "rollback"))])
            continue
        row = [InlineKeyboardButton(text=f"📄 {check['name']}", callback_data=cb(i, "trace"))]
        if check.get("has_backup"):
            row.append(InlineKeyboardButton(text="↩️ Откатить", callback_data=cb(i, "rollback")))
        else:
            row.append(InlineKeyboardButton(text="🗑️ Удалить", callback_data=cb(i, "delete")))
        rows.append(row)
    if any(check["status"] in ("ok", "timeout", "rolled_back") for check in checks):
        rows.append([InlineKeyboardButton(text="🔄 Перезагрузить сейчас", callback_data="module_check_restart")])
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=back_cb)])
    return InlineKeyboardMarkup(inline_keyboard=rows)
