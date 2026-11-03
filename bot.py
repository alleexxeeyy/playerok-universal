import os
import sys
import asyncio
import traceback
from threading import Thread
from colorama import Fore, init as init_colorama
from logging import getLogger

from __init__ import ACCENT_COLOR, VERSION
from core.utils import (
    set_title, 
    setup_logger, 
    install_requirements, 
    patch_requests, 
    init_main_loop, 
    acquire_instance_lock
)
from core.modules import get_modules
from core.handlers import call_bot_event
from core import bootreport
from core.startup import (
    diagnose,
    enter_setup_mode,
    start_modules,
    start_telegram_bot,
    start_playerok_bot
)
from updater import (
    check_for_updates, 
    check_new_releases_task
)
from utils import configure_config


logger = getLogger("universal")

try:
    main_loop = asyncio.get_running_loop()
except RuntimeError:
    main_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(main_loop)

# патч colorama: на Linux без TTY (запуск через systemd или os.execv)
# winterm=None и colorama падает в convert_osc -> set_title
# патчим convert_osc напрямую чтобы это работало при любом способе запуска
import colorama.ansitowin32 as _a32
if not sys.stdout.isatty():
    class _FakeWinTerm:
        def set_title(self, t): pass
        def set_cursor_position(self, *a, **k): pass
        def set_foreground(self, *a, **k): pass
        def set_background(self, *a, **k): pass
        def reset_all(self, *a, **k): pass
        def style(self, *a, **k): pass
    _a32.winterm = _FakeWinTerm()
    _orig_osc = _a32.AnsiToWin32.convert_osc
    def _safe_osc(self, text):
        try: return _orig_osc(self, text)
        except (AttributeError, TypeError): return text
    _a32.AnsiToWin32.convert_osc = _safe_osc

init_colorama()
init_main_loop(main_loop)


async def clear_logs_task():
    from settings import Settings as sett
    
    path = "logs/latest.log"
    while True:
        if os.path.exists(path):
            file_size_bytes = os.path.getsize(path)
            file_size_mb = file_size_bytes / (1024 * 1024)
            
            config = sett.get("config")
            if file_size_mb > config["logs"]["max_file_size"]:
                with open(path, 'w'):
                    pass
        await asyncio.sleep(30)


def show_panel(title: str, body: str, color: str):
    try:
        from core.console import print_panel
        print_panel(title, body, color, width=72)
    except Exception: # rich ещё не установлен или сам и упал — пишем как есть
        print(f"\n{title}\n{body}\n")


if __name__ == "__main__":
    running_pid = acquire_instance_lock()
    if running_pid is not None:
        show_panel(
            f"{Fore.LIGHTRED_EX}■ Бот уже запущен",
            f"Playerok Universal из этой папки уже работает в другом окне{f' (процесс {running_pid})' if running_pid else ''}. "
            f"Закройте это окно — если запустить одного бота дважды, заказы и сообщения будут обрабатываться по два раза.\n\n"
            f"{Fore.LIGHTBLACK_EX}Если бот на самом деле не запущен — завершите зависший процесс python и попробуйте снова.",
            "red"
        )
        sys.exit(1)

    try:
        install_requirements("requirements.txt") # установка недостающих зависимостей, если таковые есть
        patch_requests()
        setup_logger()
        bootreport.start_capture()
        
        set_title(f"Playerok Universal v{VERSION} by @friedfluoride")
        from core.console import print_panel
        print_panel(
            f"{ACCENT_COLOR}Playerok Universal {Fore.LIGHTWHITE_EX}v{VERSION} {Fore.LIGHTBLACK_EX}· by {Fore.LIGHTYELLOW_EX}@friedfluoride (3xtra)",
            [
                ("GitHub", "github.com/alleexxeeyy/playerok-universal"),
                ("Новости", "t.me/friedplayerok"),
                ("Плагины", "t.me/friedshopbot")
            ],
            color="yellow",
            width=72
        )
        
        check_for_updates()
        configure_config() # в консоли — только токен Telegram, остальное настраивается в самом ТГ-боте

        problem = diagnose()
        if problem: # Playerok не подключается — поднимаем один ТГ-бот, чинить будем там
            main_loop.run_until_complete(start_telegram_bot())
            enter_setup_mode(problem)
        else:
            start_modules()
            main_loop.run_until_complete(start_telegram_bot())
            main_loop.run_until_complete(start_playerok_bot())
            asyncio.run(call_bot_event("ON_INIT"))
            Thread(target=bootreport.send_report, args=(get_modules(),), daemon=True).start()

        main_loop.create_task(clear_logs_task())
        main_loop.create_task(check_new_releases_task())
        
        main_loop.run_forever()
    except Exception as e:
        trace = traceback.format_exc()
        traceback.print_exc()
        show_panel(
            f"{Fore.LIGHTRED_EX}■ Бот словил непредвиденную ошибку и был выключен",
            f"Попробуйте найти свою проблему в статье с самыми частыми ошибками:\n"
            f"{Fore.LIGHTWHITE_EX}https://devfried.com/docs/faq/ {Fore.LIGHTBLACK_EX}(CTRL + Клик ЛКМ)",
            "red"
        )
        bootreport.notify_crash(trace)
    except KeyboardInterrupt:
        show_panel(f"{Fore.YELLOW}Работа бота остановлена", f"{Fore.LIGHTBLACK_EX}Вы нажали Ctrl + C", "yellow")