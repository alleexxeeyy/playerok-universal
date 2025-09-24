import os
import sys
import ctypes
import logging
from colorlog import ColoredFormatter
from colorama import Fore
import pkg_resources
import subprocess
import requests
import time
import random



def restart():
    """ 
    Перезагружает бота. 
    """
    print(f"{Fore.WHITE}Перезапуск бота...\n")
    os.execv(sys.executable, [sys.executable] + sys.argv)
    exit()

def set_title(title):
    """
    Устанавливает заголовок консоли (кросс-платформенно).
    Работает на Windows, Linux и macOS.

    :param title: Заголовок консоли.
    :type title: `str`
    """
    if sys.platform == "win32":
        ctypes.windll.kernel32.SetConsoleTitleW(title)
    elif sys.platform.startswith("linux"):
        sys.stdout.write(f"\x1b]2;{title}\x07")
        sys.stdout.flush()
    elif sys.platform == "darwin":
        sys.stdout.write(f"\x1b]0;{title}\x07")
        sys.stdout.flush()
    else:
        print(f"Заголовок консоли не поддерживается на {sys.platform}")

def setup_logger():
    """ 
    Настраивает глобальный логгер. 
    """
    LOG_FORMAT = "%(light_black)s[%(asctime)s] %(log_color)s%(levelname)-8s %(message)s"
    formatter = ColoredFormatter(
        LOG_FORMAT,
        datefmt="%d.%m.%Y %H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'white',
            'WARNING': 'lightyellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    logger.addHandler(console_handler)
    
def is_package_installed(requirement_string: str) -> bool:
    """ Проверяет, установлена ли библотека. """
    try:
        pkg_resources.require(requirement_string)
        return True
    except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict):
        return False

def install_requirements(requirements_path: str):
    """
    Устанавливает зависимости с файла requirements.txt,
    если они не установлены.

    :param requirements_path: Путь к файлу requirements.txt.
    :type requirements_path: str
    """
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
        print(f"{Fore.WHITE}⚙️  Установка недостающих зависимостей: {Fore.LIGHTYELLOW_EX}{f'{Fore.WHITE}, {Fore.LIGHTYELLOW_EX}'.join(missing_packages)}{Fore.WHITE}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing_packages])

def patch_requests():
    """
    Патчит запросы requests на кастомные, с обработкой
    429 Too Many Requests, 520 Bat Gateway и повторной отправкой запроса при этих ошибках.
    """
    _orig_request = requests.Session.request

    def _request(self, method, url, **kwargs):  # type: ignore
        for attempt in range(6):
            resp = _orig_request(self, method, url, **kwargs)
            try:
                text_head = (resp.text or "")[:1200]
            except Exception:
                text_head = ""
            statuses = {
                "429": "Too Many Requests",
                "502": "Bad Gateway",
                "503": "Service Unavailable"
            }
            if str(resp.status_code) not in statuses:
                for status in statuses.values():
                    if status in text_head:
                        break
                else: 
                    return resp

            retry_hdr = resp.headers.get("Retry-After")
            try:
                delay = float(retry_hdr) if retry_hdr else min(120.0, 5.0 * (2 ** attempt))
            except Exception:
                delay = min(120.0, 5.0 * (2 ** attempt))
            delay += random.uniform(0.2, 0.8)  # небольшой джиттер
            time.sleep(delay)
        return resp
    requests.Session.request = _request  # type: ignore