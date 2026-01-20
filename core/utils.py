import os
import re
import sys
import ctypes
import string
import logging
import requests
import pkg_resources
import subprocess
import curl_cffi
import random
import time
import asyncio
import base64
from colorlog import ColoredFormatter
from colorama import Fore
from threading import Thread
from logging import getLogger

from playerokapi.account import Account
from settings import Settings as sett


logger = getLogger("universal.utils")
main_loop = None


def init_main_loop(loop):
    global main_loop 
    main_loop = loop


def get_main_loop():
    return main_loop


def shutdown():
    for task in asyncio.all_tasks(main_loop):
        task.cancel()
    main_loop.call_soon_threadsafe(main_loop.stop)


def restart():
    python = sys.executable
    os.execv(python, [python] + sys.argv)


def set_title(title: str):
    if sys.platform == "win32":
        ctypes.windll.kernel32.SetConsoleTitleW(title)
    elif sys.platform.startswith("linux"):
        sys.stdout.write(f"\x1b]2;{title}\x07")
        sys.stdout.flush()
    elif sys.platform == "darwin":
        sys.stdout.write(f"\x1b]0;{title}\x07")
        sys.stdout.flush()


def setup_logger(log_file: str = "logs/latest.log"):
    class ShortLevelFormatter(ColoredFormatter):
        def format(self, record):
            record.shortLevel = record.levelname[0]
            return super().format(record)

    os.makedirs("logs", exist_ok=True)
    LOG_FORMAT = "%(light_black)s%(asctime)s · %(log_color)s%(shortLevel)s: %(reset)s%(white)s%(message)s"
    formatter = ShortLevelFormatter(
        LOG_FORMAT,
        datefmt="%d.%m.%Y %H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG': 'light_blue',
            'INFO': 'light_green',
            'WARNING': 'yellow',
            'ERROR': 'bold_red',
            'CRITICAL': 'red',
        },
        style='%'
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    class StripColorFormatter(logging.Formatter):
        ansi_escape = re.compile(r'\x1b\[[0-9;]*[A-Za-z]')
        def format(self, record):
            message = super().format(record)
            return self.ansi_escape.sub('', message)
        
    file_handler.setFormatter(StripColorFormatter(
        "[%(asctime)s] %(levelname)-1s · %(name)-20s %(message)s",
        datefmt="%d.%m.%Y %H:%M:%S",
    ))

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger
    

def is_package_installed(requirement_string: str) -> bool:
    try:
        pkg_resources.require(requirement_string)
        return True
    except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict):
        return False


def install_requirements(requirements_path: str):
    try:
        if not os.path.exists(requirements_path):
            return
        with open(requirements_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        missing_packages = []
        for line in lines:
            pkg = line.strip()
            if not pkg or pkg.startswith("#"):
                continue
            if not is_package_installed(pkg):
                missing_packages.append(pkg)
        if missing_packages:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing_packages])
    except:
        logger.error(f"{Fore.LIGHTRED_EX}Не удалось установить зависимости из файла \"{requirements_path}\"")


def patch_requests():
    _orig_request = curl_cffi.Session.request

    def _request(self, method, url, **kwargs):  # type: ignore
        for attempt in range(6):
            resp = _orig_request(self, method, url, **kwargs)
            text_head = (resp.text or "")[:1200]
            statuses = {
                429: "Too Many Requests",
                502: "Bad Gateway",
                503: "Service Unavailable"
            }

            for st_code in statuses.keys():
                if resp.status_code == st_code:
                    err = st_code
                    break
            else:
                for st in statuses.values():
                    if st.lower() in text_head.lower():
                        err = st
                        break
                else:
                    return resp
            
            retry_hdr = resp.headers.get("Retry-After")
            try: delay = float(retry_hdr) if retry_hdr else min(120.0, 5.0 * (2 ** attempt))
            except: delay = min(120.0, 5.0 * (2 ** attempt))
            
            logger.warning(f"{Fore.LIGHTYELLOW_EX}{url} {Fore.WHITE}— {Fore.YELLOW}{err}. {Fore.WHITE}Пробую отправить запрос снова через {delay} сек.")
            delay += random.uniform(0.2, 0.8)  # небольшой джиттер
            time.sleep(delay)
        return resp

    curl_cffi.Session.request = _request  # type: ignore


def run_async_in_thread(func: callable, args: list = [], kwargs: dict = {}):
    def run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(func(*args, **kwargs))
        finally:
            loop.close()

    Thread(target=run, daemon=True).start()


def run_forever_in_thread(func: callable, args: list = [], kwargs: dict = {}):
    def run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(func(*args, **kwargs))
        try:
            loop.run_forever()
        finally:
            loop.close()

    Thread(target=run, daemon=True).start()


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


def is_pl_account_working() -> bool:
    try:
        config = sett.get("config")
        Account(
            token=config["playerok"]["api"]["token"],
            user_agent=config["playerok"]["api"]["user_agent"],
            requests_timeout=config["playerok"]["api"]["requests_timeout"],
            proxy=config["playerok"]["api"]["proxy"] or None
        ).get()
        return True
    except:
        return False


def is_pl_account_banned() -> bool:
    try:
        config = sett.get("config")
        acc = Account(
            token=config["playerok"]["api"]["token"],
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


def is_proxy_working(proxy: str, timeout: int = 10) -> bool:
    proxies = {
        "http": f"http://{proxy}",
        "https": f"http://{proxy}"
    }
    test_url = "https://playerok.com"
    try:
        response = requests.get(test_url, proxies=proxies, timeout=timeout)
        return response.status_code in [200, 403]
    except Exception:
        return False


def is_tg_token_valid(token: str) -> bool:
    pattern = r'^\d{7,12}:[A-Za-z0-9_-]{35}$'
    return bool(re.match(pattern, token))


def is_tg_bot_exists() -> bool:
    try:
        config = sett.get("config")
        response = requests.get(
            f"https://api.telegram.org/bot{config['telegram']['api']['token']}/getMe", 
            timeout=5
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