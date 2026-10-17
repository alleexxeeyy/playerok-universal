import textwrap
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import Settings as sett

from .. import callback_datas as calls


def conn_text():
    config = sett.get("config")
    
    pl_proxy = config["playerok"]["api"]["proxy"] or "❌ Не задано"
    tg_proxy = config["telegram"]["api"]["proxy"] or "❌ Не задано"
    tg_custom_api_url = config["telegram"]["api"]["custom_api_url"] or "❌ Не задано"
    requests_timeout = config["playerok"]["api"]["requests_timeout"] or "❌ Не задано"
    proxy_check_failures = config["playerok"]["api"]["proxy_check_failures"]
    proxy_check_timeout = config["playerok"]["api"]["proxy_check_timeout"]
    proxy_check_interval = config["playerok"]["api"]["proxy_check_interval"]

    txt = textwrap.dedent(f"""
        <b>🛜 Соединение</b>

        <b>🌐 Прокси для Playerok:</b> {pl_proxy}
        <b>🌐 Прокси для Telegram:</b> {tg_proxy}

        <b>🔗 Кастомный URL Telegram API:</b> {tg_custom_api_url}
        <blockquote><b>(?)</b> Если Telegram заблокирован, можно указать URL Cloudflare Worker-прокси (или другого reverse-proxy) вместо api.telegram.org. Изменения вступят в силу после перезагрузки бота.</blockquote>

        <b>📶 Таймаут подключения к playerok.com:</b> {requests_timeout} сек.
        <blockquote><b>(?)</b> Это максимальное время, за которое должен прийти ответ на запрос с сайта Playerok. Если время истекло, а ответ не пришёл — бот выдаст ошибку. Если у вас слабый интернет, указывайте значение больше.</blockquote>

        <b>🩺 Пауза между проверками прокси Playerok:</b> {proxy_check_interval} сек.
        <b>⏱ Ожидание ответа проверки:</b> {proxy_check_timeout} сек.
        <b>⚠️ Предупредить после:</b> {proxy_check_failures} неудачных проверок подряд.
        <blockquote><b>(?)</b> Эти параметры относятся только к отдельной проверке прокси. После изменения новый интервал начнёт действовать по окончании текущего ожидания.</blockquote>
    """)
    return txt


def conn_kb():
    config = sett.get("config")
    
    pl_proxy = config["playerok"]["api"]["proxy"] or "❌ Не задано"
    tg_proxy = config["telegram"]["api"]["proxy"] or "❌ Не задано"
    tg_custom_api_url = config["telegram"]["api"]["custom_api_url"] or "❌ Не задано"
    requests_timeout = config["playerok"]["api"]["requests_timeout"] or "❌ Не задано"
    proxy_check_failures = config["playerok"]["api"]["proxy_check_failures"]
    proxy_check_timeout = config["playerok"]["api"]["proxy_check_timeout"]
    proxy_check_interval = config["playerok"]["api"]["proxy_check_interval"]

    rows = [
        [InlineKeyboardButton(text=f"🌐 Прокси для Playerok: {pl_proxy}", callback_data="enter_pl_proxy")],
        [InlineKeyboardButton(text=f"🌐 Прокси для Telegram: {tg_proxy}", callback_data="enter_tg_proxy")],
        [InlineKeyboardButton(text=f"🔗 Кастомный URL Telegram API: {tg_custom_api_url}", callback_data="enter_tg_custom_api_url")],
        [InlineKeyboardButton(text=f"🛜 Таймаут подключения к playerok.com: {requests_timeout} сек.", callback_data="enter_requests_timeout")],
        [InlineKeyboardButton(text=f"🩺 Пауза между проверками: {proxy_check_interval} сек.", callback_data="enter_proxy_check_interval")],
        [InlineKeyboardButton(text=f"⏱ Ждать ответ проверки {proxy_check_timeout} сек.", callback_data="enter_proxy_check_timeout")],
        [InlineKeyboardButton(text=f"⚠️ Предупредить после {proxy_check_failures} ошибок подряд", callback_data="enter_proxy_check_failures")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=calls.MenuNavigation(to="default").pack())]
    ]
    if config["playerok"]["api"]["proxy"]:
        rows[0].append(InlineKeyboardButton(text=f"❌ Убрать прокси", callback_data="clean_pl_proxy"))
    if config["telegram"]["api"]["proxy"]:
        rows[1].append(InlineKeyboardButton(text=f"❌ Убрать прокси", callback_data="clean_tg_proxy"))
    if config["telegram"]["api"]["custom_api_url"]:
        rows[2].append(InlineKeyboardButton(text=f"❌ Убрать URL", callback_data="clean_tg_custom_api_url"))
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb


def conn_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>🛜 Соединение</b>
        \n{placeholder}
    """)
    return txt
