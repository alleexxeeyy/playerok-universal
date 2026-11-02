from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett
from utils import mask_proxy


SETUP_STEPS = 3


def _step(step: int | None) -> str:
    return f"<b>Шаг {step}/{SETUP_STEPS}</b> · " if step else ""


def setup_text(problem: dict | None, placeholder: str = None):
    api = sett.get("config")["playerok"]["api"]

    lines = ["⚙️ <b>Подключение Playerok</b>", ""]
    if problem:
        lines += ["⚠️ Работа с Playerok остановлена:", f"<blockquote>{problem['text']}</blockquote>", ""]
    lines += [
        f"🍪 <b>Cookie-данные:</b> {'указаны' if api['cookies'] else '❌ не указаны'}",
        f"🎩 <b>User Agent:</b> {'указан' if api['user_agent'] else 'не указан'}",
        f"🌐 <b>Прокси:</b> {mask_proxy(api['proxy']) if api['proxy'] else 'не указан'}"
    ]
    if problem and problem.get("transient"):
        lines += ["", "🔁 Если это сбой сети — бот сам проверит связь ещё раз через 5 минут."]
    if placeholder:
        lines += ["", str(placeholder)]
    return "\n".join(lines)


def setup_kb():
    api = sett.get("config")["playerok"]["api"]
    rows = [
        [InlineKeyboardButton(text="🍪 Cookie-данные", callback_data="setup_cookies")],
        [
            InlineKeyboardButton(text="🎩 User Agent", callback_data="setup_user_agent"),
            InlineKeyboardButton(text="🌐 Прокси", callback_data="setup_proxy")
        ]
    ]
    if api["proxy"]:
        rows.append([InlineKeyboardButton(text="🗑️ Убрать прокси", callback_data="setup_remove_proxy")])
    rows.append([InlineKeyboardButton(text="🔁 Проверить и запустить", callback_data="setup_check")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def setup_float_text(placeholder: str):
    return f"⚙️ <b>Подключение Playerok</b>\n\n{placeholder}"


def setup_cookies_text(step: int = None, error: str = None):
    lines = [
        f"{_step(step)}🍪 Отправьте <b>Cookie-данные</b> аккаунта Playerok",
        "",
        "Как получить:",
        "1. Войдите в свой аккаунт на playerok.com в браузере",
        "2. Установите расширение <b>Cookie-Editor</b>",
        "3. Откройте его на сайте Playerok → <b>Export</b> → <b>Header String</b>",
        "4. Пришлите скопированный текст сюда (или .txt файлом)",
        "",
        "🔐 Сообщение с куками бот сразу удалит из чата."
    ]
    if error:
        lines = [str(error), ""] + lines
    return setup_float_text("\n".join(lines))


def setup_user_agent_text(step: int = None, error: str = None):
    lines = [
        f"{_step(step)}🎩 Отправьте <b>User Agent</b> вашего браузера",
        "",
        "Скопировать его можно на сайте whatmyuseragent.com — откройте в том же браузере, где брали куки.",
        "",
        "Необязательно — можно пропустить."
    ]
    if error:
        lines = [str(error), ""] + lines
    return setup_float_text("\n".join(lines))


def setup_proxy_text(step: int = None, error: str = None):
    lines = [
        f"{_step(step)}🌐 Отправьте <b>HTTP-прокси</b> для Playerok",
        "",
        "Формат: <code>user:pass@ip:port</code>, <code>ip:port:user:pass</code> или <code>ip:port</code>",
        "",
        "Необязательно — можно пропустить."
    ]
    if error:
        lines = [str(error), ""] + lines
    return setup_float_text("\n".join(lines))


def setup_input_kb(skip: bool):
    rows = []
    if skip:
        rows.append([InlineKeyboardButton(text="⏭️ Пропустить", callback_data="setup_skip")])
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="setup_open")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def setup_announce_text(problem: dict | None, notes: list[str] = None):
    lines = ["⚠️ <b>Бот запущен, но работа с Playerok остановлена</b>"]
    if problem:
        lines += ["", f"<blockquote>{problem['text']}</blockquote>"]
    for note in notes or []:
        lines.append(f"\n⚠️ {note}")
    lines += ["", "Нажмите кнопку ниже — всё можно исправить прямо здесь, без консоли."]
    return "\n".join(lines)


def setup_announce_kb():
    rows = [[InlineKeyboardButton(text="⚙️ Открыть настройку", callback_data="setup_open")]]
    return InlineKeyboardMarkup(inline_keyboard=rows)
