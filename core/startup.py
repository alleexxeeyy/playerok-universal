import time
import asyncio
import traceback
from threading import Thread, Lock
from colorama import Fore
from logging import getLogger

from core import bootreport
from core.modules import load_modules, set_modules, get_modules, connect_modules
from core.handlers import call_bot_event
from core.utils import get_main_loop, run_async_in_thread, restart


logger = getLogger("universal.startup")

DIAGNOSE_ATTEMPTS = 3
DIAGNOSE_DELAY = 20
AUTO_RECHECK_INTERVAL = 300

_problem: dict | None = None
_launch_lock = Lock()


def is_setup_mode() -> bool:
    return _problem is not None


def get_problem() -> dict | None:
    return _problem


def set_problem(problem: dict | None):
    global _problem
    _problem = problem


def is_launching() -> bool:
    return _launch_lock.locked()


def diagnose(attempts: int = DIAGNOSE_ATTEMPTS, delay: int = DIAGNOSE_DELAY) -> dict | None:
    from utils import diagnose_playerok

    for attempt in range(attempts):
        problem = diagnose_playerok()
        if not problem or not problem["transient"] or attempt == attempts - 1:
            return problem
        logger.warning(f"{Fore.LIGHTYELLOW_EX}{problem['text']}. {Fore.WHITE}Проверю ещё раз через {delay} сек...")
        bootreport.update_marker_message(
            f"🔄️ <b>Перезагружаю бота</b>, подождите..."
            f"\n\n⏳ Playerok пока не отвечает — пробую ещё раз (попытка {attempt + 2} из {attempts})"
            f"\n<blockquote>{problem['text']}</blockquote>"
        )
        time.sleep(delay)


async def start_telegram_bot():
    from tgbot.telegrambot import TelegramBot
    run_async_in_thread(TelegramBot().run_bot)


async def start_playerok_bot():
    from plbot.playerokbot import PlayerokBot
    await PlayerokBot().run_bot()


def start_modules(attach_routers=None) -> list:
    modules = load_modules()
    set_modules(modules)
    if attach_routers: # роутеры до хуков модулей — как при обычном запуске
        attach_routers(modules)
    asyncio.run(connect_modules(modules))
    return modules


def enter_setup_mode(problem: dict):
    set_problem(problem)
    logger.info("")
    logger.warning(f"{Fore.LIGHTRED_EX}Работа с Playerok остановлена: {Fore.WHITE}{problem['text']}")
    logger.warning(f"{Fore.WHITE}Бот ждёт настройки — откройте своего Telegram бота, там всё можно исправить.")
    logger.info("")
    Thread(target=_announce_setup, daemon=True).start()
    Thread(target=_auto_recheck_loop, daemon=True).start()


def _announce_setup():
    try:
        bootreport.wait_telegram_bot()
        bootreport.stop_capture()
        from tgbot import templates as templ

        marker = bootreport.pop_marker()
        bootreport._deliver(
            marker,
            templ.setup_announce_text(get_problem(), bootreport.get_notes()),
            templ.setup_announce_kb(),
            to_all=True
        )
    except Exception as e:
        logger.error(f"Не удалось сообщить в Telegram о настройке: {e}")


def _auto_recheck_loop():
    # сетевые сбои часто проходят сами — не заставляем юзера жать «проверить»
    while is_setup_mode():
        time.sleep(AUTO_RECHECK_INTERVAL)
        problem = get_problem()
        if not problem or not problem["transient"] or is_launching():
            continue
        new_problem = diagnose(attempts=1)
        if new_problem:
            set_problem(new_problem)
            continue
        logger.info(f"{Fore.LIGHTYELLOW_EX}Связь с Playerok восстановилась — запускаю бота")
        launch()


def launch(chat_id: int = None, message_id: int = None) -> bool:
    if not _launch_lock.acquire(blocking=False):
        return False
    Thread(target=_launch, args=(chat_id, message_id), daemon=True).start()
    return True


def _launch(chat_id: int | None, message_id: int | None):
    try:
        from tgbot.telegrambot import get_telegram_bot

        bootreport.reset()
        bootreport.start_capture()

        tgbot = get_telegram_bot()
        start_modules(attach_routers=tgbot.attach_modules)
        asyncio.run_coroutine_threadsafe(tgbot.refresh_polling(), tgbot.loop).result(30)

        asyncio.run_coroutine_threadsafe(start_playerok_bot(), get_main_loop()).result(300)
        asyncio.run(call_bot_event("ON_INIT"))

        set_problem(None)
        logger.info(f"{Fore.LIGHTYELLOW_EX}Бот запущен без перезагрузки")
        bootreport.set_marker("setup", chat_id, message_id)
        bootreport.send_report(get_modules())
    except Exception:
        logger.error(f"{Fore.LIGHTRED_EX}Не удалось запустить бота без перезагрузки, перезагружаю: {Fore.WHITE}{traceback.format_exc()}")
        bootreport.set_marker("setup", chat_id, message_id)
        restart()
    finally:
        _launch_lock.release()
