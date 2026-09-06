import os
import re
import sys
import ctypes
import hashlib
import tempfile
import logging
import pkg_resources
import subprocess
import shlex
import curl_cffi
import random
import time
import asyncio
from colorlog import ColoredFormatter
from threading import Thread
from logging import getLogger


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


LOCK_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # корень бота, а не текущая директория
LOCK_PATH = os.path.join(LOCK_FOLDER, "bot_data", ".instance.lock")
LOCK_PREFIX = "playerok-universal"
LOCK_OFFSET = 1024  # лочим байт в стороне от PID, чтобы второй процесс мог его прочитать (на win лок блокирует чтение региона)
PID_WIDTH = 32

_instance_locks = []

if sys.platform == "win32":
    import msvcrt

    def _lock_region(file):
        file.seek(LOCK_OFFSET)
        msvcrt.locking(file.fileno(), msvcrt.LK_NBLCK, 1)

    def _unlock_region(file):
        file.seek(LOCK_OFFSET)
        msvcrt.locking(file.fileno(), msvcrt.LK_UNLCK, 1)
else:
    import fcntl

    def _lock_region(file):
        fcntl.flock(file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

    def _unlock_region(file):
        fcntl.flock(file.fileno(), fcntl.LOCK_UN)


def acquire_lock(path: str, attempts: int = 12, delay: float = 0.25) -> int | None:
    """
    Пытается занять лок-файл. Лок снимает операционная система при завершении процесса, 
    так что зависших локов после падения бота не остаётся.
    Если лок взять не получилось из-за ошибки (нет прав, недоступна папка), бот всё равно запускается — 
    защита от двойного запуска не должна мешать работе, но в консоль уходит предупреждение.

    :param path: Путь к лок-файлу.
    :type path: str

    :param attempts: Кол-во попыток занять лок (нужны при перезапуске, когда старый процесс ещё не умер).
    :type attempts: int

    :param delay: Пауза между попытками в секундах.
    :type delay: float

    :return: None, если лок занят нами, иначе PID процесса, который его держит (0 — если PID не удалось прочитать).
    """

    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        file = os.fdopen(os.open(path, os.O_RDWR | os.O_CREAT | getattr(os, "O_BINARY", 0), 0o644), "rb+")
    except Exception as e:
        logger.warning(f"Не удалось открыть файл лока \"{path}\": {e}. Бот запустится без защиты от двойного запуска")
        return None

    for attempt in range(attempts):
        try:
            _lock_region(file)
            break
        except OSError:
            if attempt < attempts - 1:
                time.sleep(delay)
        except Exception as e:
            logger.warning(f"Не удалось занять лок \"{path}\": {e}. Бот запустится без защиты от двойного запуска")
            file.close()
            return None
    else:
        pid = 0
        try:
            file.seek(0)
            pid = int(file.read(PID_WIDTH).decode("utf-8", "ignore").strip())
        except:
            pass
        file.close()
        return pid

    try:
        file.seek(0)
        file.write(str(os.getpid()).ljust(PID_WIDTH).encode("utf-8"))
        file.flush()
    except:
        pass

    _instance_locks.append(file)
    return None


def acquire_instance_lock(attempts: int = 12, delay: float = 0.25) -> int | None:
    """Лок папки бота — не даёт запустить одну и ту же папку дважды."""
    return acquire_lock(LOCK_PATH, attempts, delay)


def acquire_account_lock(account_id: str, attempts: int = 12, delay: float = 0.25) -> int | None:
    """Лок аккаунта Playerok — не даёт запустить два бота на одном аккаунте из разных папок."""
    digest = hashlib.sha256(str(account_id).encode("utf-8")).hexdigest()[:16]
    return acquire_lock(os.path.join(tempfile.gettempdir(), f"{LOCK_PREFIX}-{digest}.lock"), attempts, delay)


def release_instance_locks():
    global _instance_locks

    for file in _instance_locks:
        try:
            _unlock_region(file)
        except:
            pass
        try:
            file.close()
        except:
            pass
    _instance_locks = []


def restart(from_tg=False):
    python = sys.executable
    args = sys.argv.copy()

    if from_tg:
        args.append("--from_tg")

    release_instance_locks() # иначе новый процесс упрётся в локи, которые держит ещё живой старый
    logger.info("Перезапуск бота...")
    os.execv(python, [python] + args)


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
    """
    Проверяет, установлена ли библиотека.

    :param requirement_string: Строка пакета из файла зависимостей.
    :type requirement_string: str
    """
    
    try:
        parts = shlex.split(requirement_string)
        if not parts:
            return True

        requirement = parts[0]
        pkg_resources.require(requirement)

        return True
    except:
        return False


def install_requirements(requirements_path: str):
    """
    Устанавливает зависимости из файла.

    :param requirements_path: Путь к файлу зависимостей.
    :type requirements_path: str
    """
    
    try:
        if not os.path.exists(requirements_path):
            return

        with open(requirements_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue

            parts = shlex.split(line)
            if not parts:
                continue

            pkg_name = parts[0]
            extra_args = parts[1:]

            if not is_package_installed(pkg_name):
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", "-r", requirements_path
                ])
                return
    except Exception as e:
        logger.error(f"Не удалось установить зависимости из файла \"{requirements_path}\": {e}")


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
            
            logger.debug(f"{url} — {err}. Пробую отправить запрос снова через {delay} сек.")
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