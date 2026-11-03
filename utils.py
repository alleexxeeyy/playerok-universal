import os
import json
import glob
import time
import pytz
import re
import sys
import base64
import string
import queue
import logging
import requests
from html import escape
from threading import Thread
from urllib.parse import urlparse, unquote, quote
from logging import getLogger
from colorama import Fore
from datetime import datetime, timedelta, timezone
from collections import Counter

from playerokapi.account import Account
from playerokapi.exceptions import BotCheckDetectedException, UnauthorizedError, RequestFailedError

from settings import Settings as sett, set_json
from data import Data as data


logger = getLogger("universal")


def strip_html(text):
    return re.sub(r'<[^>]+>', '', text or '')


def escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def parse_date(date_str: str) -> datetime | None:
    formats = [
        "%d.%m.%Y",
        "%d.%m.%y",
        "%-d.%-m.%Y",
        "%-d.%-m.%y",
        "%-d.%m.%Y",
        "%-d.%m.%y",
        "%d.%-m.%Y",
        "%d.%-m.%y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def get_event_next_time(last_time_iso, interval):
    return (
        datetime.fromisoformat(last_time_iso) + timedelta(seconds=interval)
        if last_time_iso else datetime.now()
    )


def parse_day_time(text: str) -> str | None:
    text = (text or "").strip()

    match = re.fullmatch(r"(\d{1,2})\s*[:.,\-]\s*(\d{1,2})", text)
    if match:
        hours, minutes = int(match.group(1)), int(match.group(2))
    elif text.isdigit() and len(text) in (3, 4):
        hours, minutes = int(text[:-2]), int(text[-2:])
    elif text.isdigit() and len(text) <= 2:
        hours, minutes = int(text), 0
    else:
        return None

    if hours > 23 or minutes > 59:
        return None
    return f"{hours:02d}:{minutes:02d}"


def is_night_time(time_from: str, time_to: str, now: datetime | None = None) -> bool:
    start = parse_day_time(time_from)
    end = parse_day_time(time_to)
    if not start or not end or start == end:
        return False

    current = (now or datetime.now()).strftime("%H:%M")
    if start < end:
        return start <= current < end
    return current >= start or current < end


def get_next_day_time(time_str: str, now: datetime | None = None) -> datetime | None:
    parsed = parse_day_time(time_str)
    if not parsed:
        return None

    now = now or datetime.now()
    hours, minutes = (int(part) for part in parsed.split(":"))
    next_time = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)
    if next_time <= now:
        next_time += timedelta(days=1)
    return next_time


def is_bump_night_now(config: dict, now: datetime | None = None) -> bool:
    night = config["playerok"]["auto_bump_items"]["night"]
    return bool(night["enabled"]) and is_night_time(night["time_from"], night["time_to"], now)


def get_current_bump_interval(config: dict, now: datetime | None = None) -> int:
    if is_bump_night_now(config, now):
        return config["playerok"]["auto_bump_items"]["night"]["interval"] or 0
    return config["playerok"]["auto_bump_items"]["interval"] or 0


def get_current_bump_position(config: dict, now: datetime | None = None) -> int:
    if is_bump_night_now(config, now):
        return config["playerok"]["auto_bump_items"]["night"]["position"] or 0
    return config["playerok"]["auto_bump_items"]["position"] or 0


def get_bump_next_switch(config: dict, now: datetime) -> datetime | None:
    night = config["playerok"]["auto_bump_items"]["night"]
    if not night["enabled"]:
        return None

    if is_bump_night_now(config, now):
        return get_next_day_time(night["time_to"], now)
    return get_next_day_time(night["time_from"], now)


def get_bump_next_time(config: dict, last_time_iso: str, now: datetime | None = None) -> datetime | None:
    now = now or datetime.now()
    last_time = datetime.fromisoformat(last_time_iso) if last_time_iso else datetime.min

    cursor = now
    for _ in range(1000):
        interval = get_current_bump_interval(config, cursor)
        due = max(last_time + timedelta(seconds=interval), cursor) if interval else None
        switch = get_bump_next_switch(config, cursor)

        if due and (not switch or due < switch):
            return due
        if not switch:
            return None
        cursor = switch
    return None


def get_tg_log_chats():
    config = sett.get("config")
    chat_id = config["playerok"]["notifications"]["chat_id"]

    if not chat_id:
        return config["telegram"]["bot"]["signed_users"]
    else:
        return [chat_id]


def github_str_to_dt(date_str: str) -> datetime:
    return datetime.fromisoformat(
        date_str.replace("Z", "+00:00")
    ).replace(tzinfo=timezone.utc).astimezone(
        pytz.timezone("Europe/Moscow")
    )


def is_cookies_valid(cookie_str: str) -> bool:
    if not cookie_str or "=" not in cookie_str:
        return False

    parts = cookie_str.split(";")

    for part in parts:
        part = part.strip()
        if "=" not in part:
            return False

        key, value = part.split("=", 1)

        if not key or not value:
            return False

    return True


def is_token_valid(token: str) -> bool:
    if not re.match(r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$", token):
        return False
    try:
        header, payload, signature = token.split('.')
        for part in (header, payload, signature):
            padding = '=' * (-len(part) % 4)
            base64.urlsafe_b64decode(part + padding)
        return True
    except Exception:
        return False


def is_pl_account_working() -> tuple[bool, str]:
    try:
        config = sett.get("config")
        Account(
            cookies=config["playerok"]["api"]["cookies"],
            user_agent=config["playerok"]["api"]["user_agent"],
            requests_timeout=config["playerok"]["api"]["requests_timeout"],
            proxy=config["playerok"]["api"]["proxy"] or None
        ).get()
        return True, ""
    except BotCheckDetectedException:
        return False, "Бот-проверка заметила подозрительную активность при подключении к аккаунту Playerok. Чтобы продолжить работу, вам нужно указать актуальные Cookie-данные вашего авторизованного Playerok аккаунта."
    except:
        return False, ""


def is_pl_account_banned() -> bool:
    try:
        config = sett.get("config")
        acc = Account(
            cookies=config["playerok"]["api"]["cookies"],
            user_agent=config["playerok"]["api"]["user_agent"],
            requests_timeout=config["playerok"]["api"]["requests_timeout"],
            proxy=config["playerok"]["api"]["proxy"] or None
        ).get()
        return acc.profile.is_blocked
    except:
        return False


def is_user_agent_valid(ua: str) -> bool:
    if not ua or not (10 <= len(ua) <= 512):
        return False
    allowed_chars = string.ascii_letters + string.digits + string.punctuation + ' '
    return all(c in allowed_chars for c in ua)


def is_proxy_valid(proxy: str) -> bool:
    ip_pattern = r'(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)'
    pattern_ip_port = re.compile(
        rf'^{ip_pattern}\.{ip_pattern}\.{ip_pattern}\.{ip_pattern}:(\d+)$'
    )
    pattern_auth_ip_port = re.compile(
        rf'^[^:@]+:[^:@]+@{ip_pattern}\.{ip_pattern}\.{ip_pattern}\.{ip_pattern}:(\d+)$'
    )
    match = pattern_ip_port.match(proxy)
    if match:
        port = int(match.group(1))
        return 1 <= port <= 65535
    match = pattern_auth_ip_port.match(proxy)
    if match:
        port = int(match.group(1))
        return 1 <= port <= 65535
    return False


def is_proxy_working(proxy: str, test_url="https://playerok.com", timeout=30) -> bool:
    proxies = {
        "http": f"http://{proxy}",
        "https": f"http://{proxy}"
    }
    try:
        response = requests.get(test_url, proxies=proxies, timeout=timeout)
        return response.status_code < 404
    except Exception:
        return False


def is_tg_token_valid(token: str) -> bool:
    pattern = r'^\d{7,12}:[A-Za-z0-9_-]{35}$'
    return bool(re.match(pattern, token))


def is_url_valid(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def normalize_custom_api_url(cust_api_url: str) -> str:
    if not (
        cust_api_url.startswith("http://")
        or cust_api_url.startswith("https://")
    ):
        cust_api_url = "https://" + cust_api_url
    return cust_api_url.rstrip("/")


def is_custom_api_url_working(cust_api_url: str) -> bool:
    try:
        config = sett.get("config")
        token = config["telegram"]["api"]["token"]
        proxy = config["telegram"]["api"]["proxy"]

        if proxy:
            proxies = {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}",
            }
        else:
            proxies = None

        response = requests.get(
            f"{normalize_custom_api_url(cust_api_url)}/bot{token}/getMe",
            proxies=proxies,
            timeout=30
        )

        data = response.json()
        return data.get("ok", False) is True and data.get("result", {}).get("is_bot", False) is True
    except Exception:
        return False


def is_password_valid(password: str) -> bool:
    if len(password) < 6 or len(password) > 64:
        return False
    common_passwords = {
        "123456", "1234567", "12345678", "123456789", "password", "qwerty",
        "admin", "123123", "111111", "abc123", "letmein", "welcome",
        "monkey", "login", "root", "pass", "test", "000000", "user",
        "qwerty123", "iloveyou"
    }
    if password.lower() in common_passwords:
        return False
    return True


ITEM_UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
ITEM_SLUG_RE = re.compile(r"^[^\s/\\]{1,200}$")
ITEM_REFS_LIMIT = 50
ITEM_REFS_DELAY = 0.34
BINDING_SETTINGS = (
    "auto_deliveries",
    "data_replacement",
    "auto_bump_items",
    "auto_restore_items",
    "auto_complete_deals"
)
MODULES_DIRS = ("modules", "modules_off", "modules_clients")


def parse_item_ref(text: str) -> tuple[str, str]:
    ref = (text or "").strip()
    if not ref:
        raise Exception("пустая строка")

    if "/" in ref or "playerok.com" in ref.lower():
        parsed = urlparse(ref if "://" in ref else f"https://{ref}")
        host = (parsed.netloc or "").split("@")[-1].split(":")[0].lower()
        if host.startswith("www."):
            host = host[4:]
        if host != "playerok.com":
            raise Exception("ссылка не с playerok.com")

        parts = [part for part in (parsed.path or "").split("/") if part]
        if len(parts) < 2 or parts[-2] not in ("products", "product"):
            raise Exception("в ссылке нет пути /products/")
        ref = unquote(parts[-1])

    if ITEM_UUID_RE.match(ref):
        return "id", ref.lower()
    if ITEM_SLUG_RE.match(ref):
        return "slug", ref
    raise Exception("не похоже ни на ссылку, ни на slug, ни на ID")


def resolve_item_ref(account: Account, text: str) -> dict:
    kind, value = parse_item_ref(text)

    try:
        item = account.get_item(**{kind: value})
    except Exception as e:
        raise Exception(f"не удалось получить товар ({e})")
    if not item:
        raise Exception("товар не найден")

    owner_id = getattr(getattr(item, "user", None), "id", None)
    if not owner_id or not account.id:
        raise Exception("не удалось определить владельца товара")
    if owner_id != account.id:
        raise Exception("это не ваш товар")

    return {
        "id": item.id,
        "slug": item.slug,
        "name": item.name or item.slug or item.id
    }


def resolve_item_refs(
    account: Account,
    lines: list[str],
    limit: int = ITEM_REFS_LIMIT,
    delay: float = ITEM_REFS_DELAY
) -> tuple[list[dict], list[str]]:
    refs = [line.strip() for line in (lines or []) if line.strip()]
    if not refs:
        raise Exception("❌ Не удалось извлечь ни одной ссылки на товар")
    if len(refs) > limit:
        raise Exception(f"❌ За один раз можно добавить не больше <b>{limit}</b> товаров")

    resolved, errors = [], []
    for i, ref in enumerate(refs):
        if i:
            time.sleep(delay)
        try:
            item = resolve_item_ref(account, ref)
        except Exception as e:
            errors.append(f"{escape_html(ref[:64])} — {escape_html(str(e))}")
            continue

        if any(r["id"] == item["id"] for r in resolved):
            errors.append(f"{escape_html(ref[:64])} — указан дважды")
            continue
        resolved.append(item)

    return resolved, errors


def normalize_binding(entry) -> dict:
    if isinstance(entry, dict):
        return entry
    if isinstance(entry, list):
        return {"keyphrases": [str(phrase) for phrase in entry]}
    return {}


def binding_items(entry) -> list[dict]:
    items = normalize_binding(entry).get("items")
    if not isinstance(items, list):
        return []
    return [bound for bound in items if isinstance(bound, dict)]


def binding_phrases(entry) -> list[str]:
    phrases = normalize_binding(entry).get("keyphrases")
    if not isinstance(phrases, list):
        return []
    return [str(phrase) for phrase in phrases if phrase]


def item_matches_binding(item, entry) -> bool:
    item_id = getattr(item, "id", None)
    item_slug = getattr(item, "slug", None)
    for bound in binding_items(entry):
        if item_id and bound.get("id") == item_id:
            return True
        if item_slug and bound.get("slug") == item_slug:
            return True

    name = (getattr(item, "name", None) or "").lower()
    if name:
        for phrase in binding_phrases(entry):
            if phrase.lower() in name:
                return True
    return False


def item_matches_any_binding(item, entries: list) -> bool:
    return any(item_matches_binding(item, entry) for entry in (entries or []))


def collect_binding_ids(entries: list) -> set:
    return {
        bound.get("id")
        for entry in (entries or [])
        for bound in binding_items(entry)
        if bound.get("id")
    }


def split_new_items(items: list[dict], entries: list) -> tuple[list[dict], list[str]]:
    existing = collect_binding_ids(entries)
    fresh, dupes = [], []

    for item in items:
        if item.get("id") in existing:
            name = item.get("name") or item.get("slug") or item.get("id")
            dupes.append(f"{escape_html(str(name))} — уже добавлен")
            continue
        fresh.append(item)
        existing.add(item.get("id"))

    return fresh, dupes


def item_url(bound: dict) -> str | None:
    slug = (bound or {}).get("slug")
    if not slug:
        return None
    # slug бывает кириллическим — в кнопку-ссылку такой URL нужно отдавать закодированным
    return f"https://playerok.com/products/{quote(str(slug), safe='')}"


def binding_links(entry, empty: str = "❌ Не указано") -> str:
    parts = []
    for bound in binding_items(entry):
        name = str(bound.get("name") or bound.get("slug") or bound.get("id") or "").strip()
        if not name:
            continue
        url = item_url(bound)
        parts.append(f'<a href="{url}">{escape_html(name)}</a>' if url else escape_html(name))
    if parts:
        return ", ".join(parts)

    phrases = binding_phrases(entry)
    if phrases:
        return "🔑 " + escape_html(", ".join(phrases))
    return empty


def binding_single_url(entry) -> str | None:
    items = binding_items(entry)
    if len(items) != 1:
        return None
    return item_url(items[0])


def binding_key(entry) -> tuple:
    entry = normalize_binding(entry)
    ids = tuple(sorted(
        str(bound.get("id") or bound.get("slug") or "")
        for bound in binding_items(entry)
    ))
    phrases = tuple(sorted(phrase.lower() for phrase in binding_phrases(entry)))
    return ids, phrases


def binding_title(entry, empty: str = "❌ Не указано") -> str:
    names = [
        (bound.get("name") or bound.get("slug") or bound.get("id") or "").strip()
        for bound in binding_items(entry)
    ]
    names = [name for name in names if name]
    if names:
        return ", ".join(names)

    phrases = binding_phrases(entry)
    if phrases:
        return "🔑 " + ", ".join(phrases)
    return empty


def _rebind_in_obj(obj, old_id: str, new: dict) -> int:
    changed = 0
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "items" and isinstance(value, list):
                # список items бывает и списком привязок (аккаунты autosteamoffline),
                # поэтому не-товары обходим дальше вглубь
                for bound in value:
                    if isinstance(bound, dict) and bound.get("id") == old_id:
                        bound.update(new)
                        changed += 1
                        continue
                    changed += _rebind_in_obj(bound, old_id, new)
                continue
            changed += _rebind_in_obj(value, old_id, new)
    elif isinstance(obj, list):
        for value in obj:
            changed += _rebind_in_obj(value, old_id, new)
    return changed


def rebind_item(old_id: str, new: dict) -> int:
    new_id = (new or {}).get("id")
    if not old_id or not new_id or old_id == new_id:
        return 0

    payload = {"id": new_id}
    if new.get("slug"):
        payload["slug"] = new["slug"]
    if new.get("name"):
        payload["name"] = new["name"]
    changed = 0

    for name in BINDING_SETTINGS:
        try:
            settings = sett.get(name)
            if settings is None:
                continue
            cnt = _rebind_in_obj(settings, old_id, payload)
            if cnt:
                sett.set(name, settings)
                changed += cnt
        except Exception as e:
            logger.error(
                f"{Fore.LIGHTRED_EX}Не удалось перепривязать товар в настройке "
                f"{Fore.WHITE}{name}{Fore.LIGHTRED_EX}: {Fore.WHITE}{e}"
            )

    root = os.path.dirname(os.path.abspath(__file__))
    for modules_dir in MODULES_DIRS:
        pattern = os.path.join(root, modules_dir, "*", "module_settings", "*.json")
        for path in glob.glob(pattern):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
            except Exception:
                continue

            try:
                cnt = _rebind_in_obj(settings, old_id, payload)
                if not cnt:
                    continue
                set_json(path, settings)
                changed += cnt
            except Exception as e:
                logger.error(
                    f"{Fore.LIGHTRED_EX}Не удалось перепривязать товар в {Fore.WHITE}{path}"
                    f"{Fore.LIGHTRED_EX}: {Fore.WHITE}{e}"
                )

    return changed



TG_RETRY_DELAYS = (10, 30, 60, 120, 300)
NOT_CONFIGURED_EXIT_DELAY = 60
_console_queue: queue.Queue | None = None


def normalize_proxy(proxy: str) -> str:
    proxy = (proxy or "").strip()
    if proxy.count(":") == 3 and "@" not in proxy:
        ip, port, user, passwd = proxy.split(":")
        proxy = f"{user}:{passwd}@{ip}:{port}"
    return proxy


def check_cookies(str_cookies: str) -> bool:
    if not is_cookies_valid(str_cookies):
        return False
    cookies = {
        c.split("=", 1)[0].strip(): c.split("=", 1)[1].strip() for c
        in str_cookies.split(";") if c.strip() and "=" in c
    }
    return "token" in cookies and is_token_valid(cookies["token"])


def mask_proxy(proxy: str) -> str:
    if not proxy:
        return ""
    address = proxy.split("@")[-1]
    ip, _, port = address.partition(":")
    parts = ip.split(".")
    return ".".join(parts[:2] + ["*"] * len(parts[2:])) + (f":{port}" if port else "")


def probe_telegram(token: str, proxy: str = "", custom_api_url: str = "", timeout: int = 15) -> tuple[str, str | None]:
    from core.notify import api_base, proxies

    try:
        response = requests.get(
            f"{api_base(custom_api_url)}/bot{token}/getMe",
            proxies=proxies(proxy),
            timeout=(5, timeout)
        )
        result = response.json()
    except Exception:
        return "network", None

    if result.get("ok") and result.get("result", {}).get("is_bot"):
        return "ok", result["result"].get("username")
    if result.get("error_code") == 401:
        return "unauthorized", None
    return "network", None


def connect_telegram(token: str) -> tuple[str, str | None, tuple | None]:
    api = sett.get("config")["telegram"]["api"]
    configured = (api["proxy"], api["custom_api_url"])

    candidates = []
    for candidate in (configured, ("", configured[1]), (configured[0], ""), ("", "")):
        if candidate not in candidates:
            candidates.append(candidate)

    unauthorized = False
    for proxy, custom_api_url in candidates:
        status, username = probe_telegram(token, proxy, custom_api_url)
        if status == "ok":
            return status, username, (proxy, custom_api_url)
        # 401 мог отдать и кривой прокси или воркер — токен считаем мёртвым, только если ни одно подключение не прошло
        unauthorized = unauthorized or status == "unauthorized"
    return ("unauthorized" if unauthorized else "network"), None, None


def _describe_fallback(configured: tuple, connection: tuple) -> str:
    lost = []
    if configured[0] and not connection[0]:
        lost.append("прокси для Telegram")
    if configured[1] and not connection[1]:
        lost.append("кастомный URL Telegram API")
    return (
        f"Не отвечает {' и '.join(lost)} — бот подключился к Telegram без них. "
        f"Замените их в настройках, иначе бот может потерять связь с Telegram"
    )


def _exit_not_configured(reason: str):
    from core.console import print_panel
    print_panel(
        f"{Fore.LIGHTRED_EX}■ {reason}",
        f"Если бот стоит на сервере — подключитесь к нему и выполните: {Fore.CYAN}pluniversal setup{Fore.RESET}\n"
        f"Если на компьютере — запустите бота заново в окне консоли.",
        color="red", width=72
    )
    time.sleep(NOT_CONFIGURED_EXIT_DELAY) # иначе systemd перезапускает бота каждые 5 секунд
    sys.exit(1)


def _console_reader() -> queue.Queue:
    # ввод в отдельном потоке — автоповтор подключения не ждёт, пока юзер что-то напечатает
    global _console_queue
    if _console_queue is None:
        _console_queue = queue.Queue()

        def read():
            from core.console import hide_prompt
            while True:
                try:
                    line = input()
                except Exception as e: # EOF и пр. — пробрасываем в того, кто ждёт ввода, иначе он повиснет
                    _console_queue.put(e)
                    return
                hide_prompt(erase=False) # Enter уже перевёл строку — иначе следующий лог сотрёт введённое
                _console_queue.put(line)

        Thread(target=read, daemon=True).start()
    return _console_queue


def _read_console(timeout: float = None) -> str | None:
    from core.console import show_prompt, hide_prompt

    if _console_queue is None and timeout is None:
        show_prompt()
        try:
            return input().strip()
        finally:
            hide_prompt(erase=False)
    try:
        line = _console_reader().get_nowait() # ввели, пока бот подключался: строка уже на экране, приглашение не нужно
    except queue.Empty:
        show_prompt()
        try:
            line = _console_reader().get(timeout=timeout)
        except queue.Empty:
            return None # приглашение остаётся внизу: ввести можно и во время следующей попытки
    if isinstance(line, BaseException):
        raise line
    return line.strip()


def _ask_token() -> str:
    from core.console import print_panel, print_line

    while True:
        print_panel(
            f"{Fore.CYAN}🔑 Введите токен Telegram бота",
            f"Бота нужно создать у @BotFather (https://t.me/BotFather).\n"
            f"Всё остальное — аккаунт Playerok, прокси, доступы — настраивается дальше в самом Telegram боте.\n\n"
            f"{Fore.LIGHTBLACK_EX}Пример: {Fore.RESET}7257913369:AAG2KjLL3-zvvfSQFSVhaTb4w7tR2iXsJXM",
            color="yellow", width=72
        )
        token = _read_console()

        if is_tg_token_valid(token):
            config = sett.get("config")
            config["telegram"]["api"]["token"] = token
            sett.set("config", config)
            print_line(f"{Fore.YELLOW}Токен Telegram бота сохранён в конфиг")
            return token
        print_line(f"{Fore.LIGHTRED_EX}Похоже, вы ввели некорректный токен — проверьте формат и попробуйте ещё раз", logging.ERROR)


def _apply_console_connection(text: str):
    if not text:
        return

    from core.console import print_line

    config = sett.get("config")
    proxy = normalize_proxy(text)
    if is_proxy_valid(proxy):
        config["telegram"]["api"]["proxy"] = proxy
        sett.set("config", config)
        print_line(f"{Fore.YELLOW}Прокси для Telegram сохранён в конфиг, проверяю подключение...")
        return

    custom_api_url = normalize_custom_api_url(text)
    if is_url_valid(custom_api_url) and "." in urlparse(custom_api_url).netloc:
        config["telegram"]["api"]["custom_api_url"] = custom_api_url
        sett.set("config", config)
        print_line(f"{Fore.YELLOW}Кастомный URL Telegram API сохранён в конфиг, проверяю подключение...")
        return

    print_line(f"{Fore.LIGHTRED_EX}Это не похоже ни на прокси (user:pass@ip:port), ни на URL — проверяю подключение как есть...", logging.WARNING)


def configure_telegram() -> str:
    from core import notify, bootreport
    from core.console import print_line, print_panel, show_prompt, hide_prompt

    tty = sys.stdin.isatty()
    attempt = 0

    while True:
        config = sett.get("config")
        token = config["telegram"]["api"]["token"]
        if not token:
            if not tty:
                _exit_not_configured("Бот не настроен: не указан токен Telegram бота.")
            token = _ask_token()

        status, username, connection = connect_telegram(token)

        if status == "ok":
            hide_prompt() # подключились — приглашение ввести прокси больше не нужно
            api = sett.get("config")["telegram"]["api"]
            configured = (api["proxy"], api["custom_api_url"])
            notify.set_connection(*connection)
            if connection != configured:
                note = _describe_fallback(configured, connection)
                logger.warning(f"{Fore.LIGHTYELLOW_EX}{note}")
                bootreport.add_note(note)
            logger.info(f"{Fore.LIGHTYELLOW_EX}Telegram бот @{username} успешно подключён.")
            if not logging.getLogger().handlers: # `setup` из install.sh зовёт без логгера — иначе юзер не увидит итог
                print_line(f"{Fore.LIGHTYELLOW_EX}Telegram бот @{username} успешно подключён")
            return username

        if status == "unauthorized":
            print_line(
                f"{Fore.LIGHTRED_EX}Telegram не принял токен бота — скорее всего, его отозвали или пересоздали в @BotFather",
                logging.ERROR
            )
            if not tty:
                _exit_not_configured("Укажите новый токен Telegram бота.")
            _ask_token() # старый токен не стираем, пока не введён новый
            attempt = 0
            continue

        delay = TG_RETRY_DELAYS[min(attempt, len(TG_RETRY_DELAYS) - 1)]
        attempt += 1
        print_line(
            f"{Fore.LIGHTRED_EX}Не удалось подключиться к Telegram{Fore.RESET} (попытка {attempt}) — повторю через {delay} сек. "
            f"{Fore.LIGHTBLACK_EX}Если вы в России — Telegram нужно подключать через прокси или URL Telegram API (Cloudflare Worker)",
            logging.WARNING
        )
        if tty:
            print_panel(
                "✎ Можно не ждать",
                "Введите прокси для Telegram (user:pass@ip:port)\nили URL Telegram API и нажмите Enter",
                color="yellow"
            )
            text = _read_console(timeout=delay)
            if text is not None:
                _apply_console_connection(text)
                show_prompt() # пока проверяем введённое, можно ввести другое — и лог не встанет поверх набора
        else:
            time.sleep(delay)


def print_owner_link(bot_username: str):
    from core.access import get_signed_users, get_owner_link, is_legacy_password_login

    if get_signed_users():
        return

    from core.console import print_panel

    link = get_owner_link(bot_username)
    body = (
        f"Перейдите по ссылке ниже и нажмите «Запустить» — бот запомнит вас как владельца.\n"
        f"{Fore.LIGHTBLACK_EX}Ссылка одноразовая. Дальше вся настройка — прямо в Telegram боте."
    )
    if is_legacy_password_login():
        body += f"\n{Fore.LIGHTBLACK_EX}Или войдите в бота со своим старым паролем — сработает один раз."
    # печатаем мимо логгера: latest.log пересылают разработчику, а по ссылке можно стать владельцем
    print_panel(f"{Fore.CYAN}🔗 Откройте Telegram бота", body, color="bright_cyan", width=80)
    print(f"\n  {Fore.LIGHTWHITE_EX}{link}{Fore.RESET}\n") # вне рамки: перенос внутри неё ломает копирование ссылки


def configure_config():
    bot_username = configure_telegram()
    print_owner_link(bot_username)
    return bot_username


DIAGNOSE_TIMEOUT = 60


class FutureTimeout(Exception):
    pass


def _run_with_timeout(func, timeout: float):
    # daemon-поток, а не ThreadPoolExecutor: зависший запрос не должен держать выход из бота по Ctrl+C
    result = {}

    def target():
        try:
            result["value"] = func()
        except BaseException as e:
            result["error"] = e

    thread = Thread(target=target, daemon=True)
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        raise FutureTimeout()
    if "error" in result:
        raise result["error"]
    return result.get("value")


def is_proxy_alive(proxy: str, url: str = "https://playerok.com", timeout: int = 15) -> bool:
    try:
        requests.get(url, proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"}, timeout=(10, timeout))
        return True # любой ответ сайта — значит прокси жив, даже если сам Playerok отдал 5xx
    except Exception:
        return False


def diagnose_playerok() -> dict | None:
    api = sett.get("config")["playerok"]["api"]

    if not api["cookies"]:
        return {"code": "no_cookies", "text": "Не указаны Cookie-данные аккаунта Playerok", "transient": False}

    if api["proxy"] and not is_proxy_alive(api["proxy"]):
        return {"code": "proxy", "text": "Прокси для Playerok не отвечает", "transient": True}

    # запросы к Playerok сами повторяются на 429/5xx с паузами до 2 минут — ограничиваем общее время проверки
    try:
        account = _run_with_timeout(lambda: Account(
            cookies=api["cookies"],
            user_agent=api["user_agent"],
            requests_timeout=api["requests_timeout"],
            proxy=api["proxy"] or None
        ).get(), DIAGNOSE_TIMEOUT)
    except FutureTimeout:
        return {"code": "server", "text": f"Playerok не ответил за {DIAGNOSE_TIMEOUT} сек", "transient": True}
    except UnauthorizedError:
        return {
            "code": "cookies",
            "text": "Playerok не принял Cookie-данные — скорее всего, они устарели. Скопируйте свежие из браузера, где вы вошли в аккаунт",
            "transient": False
        }
    except BotCheckDetectedException:
        return {
            "code": "bot_check",
            "text": "Playerok включил проверку на бота — нужны свежие Cookie-данные из браузера, где вы вошли в аккаунт",
            "transient": False
        }
    except RequestFailedError as e:
        return {"code": "server", "text": f"Playerok временно не отвечает (ошибка {e.status_code})", "transient": True}
    except Exception as e:
        reason = str(e).strip()
        if api["proxy"]: # в тексте ошибки бывает адрес прокси, иногда вместе с логином и паролем
            host = api["proxy"].split("@")[-1].split(":")[0]
            reason = reason.replace(api["proxy"], mask_proxy(api["proxy"]))
            if "@" in api["proxy"]:
                reason = reason.replace(api["proxy"].split("@")[0], "***")
            reason = reason.replace(host, mask_proxy(host))
        reason = escape(reason[:200]) or type(e).__name__
        return {"code": "network", "text": f"Не удалось подключиться к Playerok: {reason}", "transient": True}

    if account.profile.is_blocked:
        return {"code": "banned", "text": "Аккаунт Playerok заблокирован — на нём бот работать не может", "transient": False}
    return None


def get_stats():
    cached_orders = data.get("cached_orders")

    now = datetime.now(pytz.timezone("Europe/Moscow"))
    day_ago = now - timedelta(days=1)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    day_orders = [o for o in cached_orders.values() if datetime.fromisoformat(o["date"]) >= day_ago]
    week_orders = [o for o in cached_orders.values() if datetime.fromisoformat(o["date"]) >= week_ago]
    month_orders = [o for o in cached_orders.values() if datetime.fromisoformat(o["date"]) >= month_ago]
    all_orders = list(cached_orders.values())

    day_active = [o for o in day_orders if not o["status"].startswith("CONFIRMED") and not o["status"].startswith("ROLLED_BACK")]
    week_active = [o for o in week_orders if not o["status"].startswith("CONFIRMED") and not o["status"].startswith("ROLLED_BACK")]
    month_active = [o for o in month_orders if not o["status"].startswith("CONFIRMED") and not o["status"].startswith("ROLLED_BACK")]
    all_active = [o for o in all_orders if not o["status"].startswith("CONFIRMED") and not o["status"].startswith("ROLLED_BACK")]

    day_completed = [o for o in day_orders if o["status"].startswith("CONFIRMED")]
    week_completed = [o for o in week_orders if o["status"].startswith("CONFIRMED")]
    month_completed = [o for o in month_orders if o["status"].startswith("CONFIRMED")]
    all_completed = [o for o in all_orders if o["status"].startswith("CONFIRMED")]

    day_refunded = [o for o in day_orders if o["status"].startswith("ROLLED_BACK")]
    week_refunded = [o for o in week_orders if o["status"].startswith("ROLLED_BACK")]
    month_refunded = [o for o in month_orders if o["status"].startswith("ROLLED_BACK")]
    all_refunded = [o for o in all_orders if o["status"].startswith("ROLLED_BACK")]

    day_profit = round(sum(o["price"] for o in day_orders if o["status"].startswith("CONFIRMED")), 2)
    week_profit = round(sum(o["price"] for o in week_orders if o["status"].startswith("CONFIRMED")), 2)
    month_profit = round(sum(o["price"] for o in month_orders if o["status"].startswith("CONFIRMED")), 2)
    all_profit = round(sum(o["price"] for o in all_orders if o["status"].startswith("CONFIRMED")), 2)

    day_best = Counter(o["item_name"] for o in day_orders).most_common(1)[0][0] if day_orders else "-"
    week_best = Counter(o["item_name"] for o in week_orders).most_common(1)[0][0] if day_orders else "-"
    month_best = Counter(o["item_name"] for o in month_orders).most_common(1)[0][0] if day_orders else "-"
    all_best = Counter(o["item_name"] for o in all_orders).most_common(1)[0][0] if day_orders else "-"

    return {
        "day": {
            "orders": len(day_orders),
            "active": len(day_active),
            "completed": len(day_completed),
            "refunded": len(day_refunded),
            "profit": day_profit,
            "best": day_best
        },
        "week": {
            "orders": len(week_orders),
            "active": len(week_active),
            "completed": len(week_completed),
            "refunded": len(week_refunded),
            "profit": week_profit,
            "best": week_best
        },
        "month": {
            "orders": len(month_orders),
            "active": len(month_active),
            "completed": len(month_completed),
            "refunded": len(month_refunded),
            "profit": month_profit,
            "best": month_best
        },
        "all": {
            "orders": len(all_orders),
            "active": len(all_active),
            "completed": len(all_completed),
            "refunded": len(all_refunded),
            "profit": all_profit,
            "best": all_best
        }
    }