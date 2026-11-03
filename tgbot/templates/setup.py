from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett
from utils import mask_proxy


SETUP_STEPS = 3


def _step(step: int | None) -> str:
    return f"<b>Шаг {step}/{SETUP_STEPS}</b> · " if step else ""


def setup_float_text(placeholder: str):
    return f"<b>⚙️ Подключение Playerok</b>\n\n{placeholder}"


def setup_text(problem: dict | None, placeholder: str = None):
    api = sett.get("config")["playerok"]["api"]

    txt = "<b>⚙️ Подключение Playerok</b>"
    if problem:
        txt += f"\n\n<b>⚠️ Работа с Playerok остановлена:</b> <blockquote>{problem['text']}</blockquote>"
    else:
        txt += "\n"
    txt += (
        f"\n<b>🍪 Cookie-данные:</b> {'указаны' if api['cookies'] else '❌ Не указаны'}"
        f"\n<b>🎩 User Agent:</b> {'указан' if api['user_agent'] else 'не указан'}"
        f"\n<b>🌐 Прокси:</b> {mask_proxy(api['proxy']) if api['proxy'] else 'не указан'}"
    )
    if problem and problem.get("transient"):
        txt += "\n\n<blockquote><b>(?)</b> Если это сбой сети — бот сам проверит связь ещё раз через 5 минут.</blockquote>"
    if placeholder:
        txt += f"\n\n{placeholder}"
    return txt


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


def _with_error(txt: str, error: str | None) -> str:
    return setup_float_text(f"{error}\n\n{txt}" if error else txt)


def setup_cookies_text(step: int = None, error: str = None):
    return _with_error(
        f"{_step(step)}🍪 Отправьте <b>Cookie-данные</b> аккаунта Playerok"
        "\n<blockquote>1. Войдите в свой аккаунт на playerok.com в браузере"
        "\n2. Установите расширение <b>Cookie-Editor</b>"
        "\n3. Откройте его на сайте Playerok → <b>Export</b> → <b>Header String</b>"
        "\n4. Пришлите скопированный текст сюда (или .txt файлом)</blockquote>"
        "\n\n🔐 Сообщение с куками бот сразу удалит из чата",
        error
    )


def setup_user_agent_text(step: int = None, error: str = None):
    return _with_error(
        f"{_step(step)}🎩 Отправьте <b>User Agent</b> вашего браузера"
        "\n<blockquote><b>(?)</b> Скопировать его можно на сайте whatmyuseragent.com — откройте его в том же браузере, "
        "где брали куки. Необязательно — можно пропустить.</blockquote>",
        error
    )


def setup_proxy_text(step: int = None, error: str = None):
    return _with_error(
        f"{_step(step)}🌐 Отправьте <b>HTTP-прокси</b> для Playerok"
        "\n<blockquote><b>(?)</b> Формат: <code>user:pass@ip:port</code>, <code>ip:port:user:pass</code> или <code>ip:port</code>. "
        "Необязательно — можно пропустить.</blockquote>",
        error
    )


def setup_input_kb(skip: bool):
    rows = []
    if skip:
        rows.append([InlineKeyboardButton(text="⏭️ Пропустить", callback_data="setup_skip")])
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="setup_open")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def setup_announce_text(problem: dict | None, notes: list[str] = None):
    txt = "<b>⚠️ Работа с Playerok остановлена</b>"
    if problem:
        txt += f"\n\n<b>🤬 Причина:</b> <blockquote>{problem['text']}</blockquote>"
    for note in notes or []:
        txt += f"\n<b>⚠️ Внимание:</b> <blockquote>{note}</blockquote>"
    txt += "\n\n❗ Бот работает, но заказы не обрабатывает — нажмите кнопку ниже, всё можно исправить прямо здесь, без консоли"
    return txt


def setup_announce_kb():
    rows = [[InlineKeyboardButton(text="⚙️ Открыть настройку", callback_data="setup_open")]]
    return InlineKeyboardMarkup(inline_keyboard=rows)
