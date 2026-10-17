import os
import sys
import asyncio
import traceback
from colorama import Fore, init as init_colorama
from logging import getLogger

from __init__ import ACCENT_COLOR, VERSION
from core.utils import (
    set_title, 
    setup_logger, 
    install_requirements, 
    patch_requests, 
    init_main_loop, 
    run_async_in_thread, 
    acquire_instance_lock
)
from core.modules import (
    load_modules, 
    set_modules, 
    connect_modules
)
from core.handlers import call_bot_event
from updater import (
    check_for_updates, 
    check_new_releases_task
)
from utils import configure_config, check_playerok_connection


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


async def start_telegram_bot():
    from tgbot.telegrambot import TelegramBot
    run_async_in_thread(TelegramBot().run_bot)


async def start_playerok_bot(in_thread=False):
    from plbot.playerokbot import PlayerokBot
    playerok_bot = await asyncio.to_thread(PlayerokBot) if in_thread else PlayerokBot()
    await playerok_bot.run_bot()


async def monitor_playerok_proxy(startup_unavailable=False, notified=False):
    from settings import Settings as sett, PROXY_CHECK_LIMITS
    from startup_alert import deliver_playerok_alert, deliver_playerok_recovery, deliver_playerok_reconnected
    from proxy_utils import ProxyCheckState
    from utils import is_proxy_working

    health = ProxyCheckState()
    last_proxy = None
    while True:
        config = sett.get("config")
        minimum, maximum = PROXY_CHECK_LIMITS["proxy_check_interval"]
        interval = max(minimum, min(config["playerok"]["api"]["proxy_check_interval"], maximum))
        await asyncio.sleep(interval)
        config = sett.get("config")
        playerok_api = config["playerok"]["api"]
        proxy = playerok_api["proxy"]
        if proxy != last_proxy:
            health.failures = 0
            last_proxy = proxy
        if not proxy:
            continue

        minimum, maximum = PROXY_CHECK_LIMITS["proxy_check_timeout"]
        timeout = max(minimum, min(playerok_api["proxy_check_timeout"], maximum))
        minimum, maximum = PROXY_CHECK_LIMITS["proxy_check_failures"]
        threshold = max(minimum, min(playerok_api["proxy_check_failures"], maximum))
        working = await asyncio.to_thread(is_proxy_working, proxy, timeout=timeout)
        if startup_unavailable:
            if not working:
                continue
            try:
                await start_playerok_bot(in_thread=True)
            except Exception:
                logger.exception("Прокси отвечает, но подключить Playerok пока не удалось; повторю попытку.")
                continue
            startup_unavailable = False
            logger.info("Playerok автоматически подключён после восстановления прокси.")
            if notified:
                await asyncio.to_thread(deliver_playerok_reconnected, config)
            notified = False
            continue

        event = health.record(working, threshold)
        if event == "recovered":
            from plbot.playerokbot import get_playerok_bot
            playerok_bot = get_playerok_bot()
            if playerok_bot is not None:
                playerok_bot.connection_unavailable = False
            logger.info("Прокси Playerok снова отвечает; статус соединения восстановлен.")
            if notified:
                await asyncio.to_thread(deliver_playerok_recovery, config)
            notified = False
        elif health.unavailable and not notified:
            problem = "Прокси Playerok перестал отвечать во время работы."
            if event == "unavailable":
                from plbot.playerokbot import get_playerok_bot
                playerok_bot = get_playerok_bot()
                if playerok_bot is not None:
                    playerok_bot.connection_unavailable = True
                logger.error("%s Telegram-бот остаётся активным.", problem)
            notified = await asyncio.to_thread(deliver_playerok_alert, config, problem)


if __name__ == "__main__":
    running_pid = acquire_instance_lock()
    if running_pid is not None:
        print(
            f"\n\n   {Fore.LIGHTRED_EX}┌───────────────────────────────────────┐\n"
            f"\n     {Fore.LIGHTRED_EX}Бот уже запущен!"
            f"\n"
            f"\n     {Fore.WHITE}Playerok Universal из этой папки уже работает"
            f"\n     в другом окне{f' (процесс {running_pid})' if running_pid else ''}."
            f"\n     Закройте это окно — если запустить одного бота дважды,"
            f"\n     заказы и сообщения будут обрабатываться по два раза."
            f"\n"
            f"\n     {Fore.LIGHTBLACK_EX}Если бот на самом деле не запущен — завершите"
            f"\n     зависший процесс python и попробуйте снова."
            f"\n\n   {Fore.LIGHTRED_EX}└───────────────────────────────────────┘\n\n"
        )
        sys.exit(1)

    try:
        from_tg = "--from_tg" in sys.argv

        install_requirements("requirements.txt") # установка недостающих зависимостей, если таковые есть
        patch_requests()
        setup_logger()
        
        set_title(f"Playerok Universal v{VERSION} by @friedfluoride")
        print(
            f"\n\n   {Fore.LIGHTYELLOW_EX}┌───────────────────────────────────────┐\n"
            f"\n     {ACCENT_COLOR}Playerok Universal {Fore.WHITE}v{Fore.LIGHTWHITE_EX}{VERSION}"
            f"\n       {Fore.WHITE}by {Fore.LIGHTYELLOW_EX}@friedfluoride (3xtra)"
            f"\n"
            f"\n     {Fore.WHITE}· GitHub: {Fore.LIGHTWHITE_EX}github.com/alleexxeeyy/playerok-universal"
            f"\n     {Fore.WHITE}· Новости: {Fore.LIGHTWHITE_EX}t.me/friedplayerok"
            f"\n     {Fore.WHITE}· Плагины: {Fore.LIGHTWHITE_EX}t.me/friedshopbot"
            f"\n\n   {Fore.LIGHTYELLOW_EX}└───────────────────────────────────────┘\n\n"
        )
        
        check_for_updates()
        configure_config()

        modules = load_modules()
        set_modules(modules)
        asyncio.run(connect_modules(modules))

        main_loop.run_until_complete(start_telegram_bot())
        if from_tg:
            from settings import Settings as sett
            from startup_alert import deliver_restart_started
            deliver_restart_started(sett.get("config"))
        playerok_problem = main_loop.run_until_complete(asyncio.to_thread(check_playerok_connection))
        if not playerok_problem:
            try:
                main_loop.run_until_complete(start_playerok_bot())
            except Exception:
                logger.exception("Не удалось запустить Playerok")
                playerok_problem = "Не удалось запустить Playerok. Проверьте Cookie-данные и прокси."
                from plbot.playerokbot import get_playerok_bot
                playerok_bot = get_playerok_bot()
                if playerok_bot is not None:
                    playerok_bot.connection_unavailable = True

        startup_alert_sent = False
        if playerok_problem:
            from settings import Settings as sett
            from startup_alert import deliver_playerok_alert
            logger.error("Playerok недоступен: %s Telegram-бот остаётся активным.", playerok_problem)
            startup_alert_sent = deliver_playerok_alert(sett.get("config"), playerok_problem)
            if not startup_alert_sent:
                logger.error("Не удалось отправить предупреждение владельцу; проверьте Telegram и журнал.")
        elif from_tg:
            from settings import Settings as sett
            from startup_alert import deliver_playerok_connected
            deliver_playerok_connected(sett.get("config"))

        main_loop.create_task(clear_logs_task())
        main_loop.create_task(check_new_releases_task())
        if not playerok_problem:
            main_loop.create_task(monitor_playerok_proxy())
        elif playerok_problem in (
            "Прокси Playerok не отвечает.",
            "Не удалось подключиться к аккаунту Playerok. Проверьте Cookie-данные и прокси.",
        ):
            main_loop.create_task(monitor_playerok_proxy(startup_unavailable=True, notified=startup_alert_sent))

        asyncio.run(call_bot_event("ON_INIT"))
        
        main_loop.run_forever()
    except Exception as e:
        traceback.print_exc()
        print(
            f"\n\n{Fore.LIGHTRED_EX}Ваш бот словил непредвиденную ошибку и был выключен."
            f"\n\n{Fore.WHITE}Пожалуйста, попробуйте найти свою проблему в нашей статье, в которой собраны все самые частые ошибки.",
            f"\nСтатья: {Fore.LIGHTWHITE_EX}https://telegra.ph/FunPay-Universal--chastye-oshibki-i-ih-resheniya-08-26 {Fore.WHITE}(CTRL + Клик ЛКМ)\n\n"
        )
    except KeyboardInterrupt:
        print(
            f"\n\n{Fore.YELLOW}Работа бота остановлена "
            f"\n{Fore.WHITE}(вы нажали Ctrl + C)\n\n"
        )
