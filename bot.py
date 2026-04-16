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
    run_async_in_thread
)
from core.modules import (
    load_modules, 
    set_modules, 
    connect_modules
)
from core.handlers import call_bot_event
from updater import check_for_updates
from utils import configure_config


logger = getLogger("universal")

try:
    main_loop = asyncio.get_running_loop()
except RuntimeError:
    main_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(main_loop)

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


async def start_telegram_bot(from_tg=False):
    from tgbot.telegrambot import TelegramBot
    run_async_in_thread(TelegramBot().run_bot, (from_tg,))


async def start_playerok_bot():
    from plbot.playerokbot import PlayerokBot
    await PlayerokBot().run_bot()


if __name__ == "__main__":
    try:
        from_tg = "--from_tg" in sys.argv

        install_requirements("requirements.txt") # установка недостающих зависимостей, если таковые есть
        patch_requests()
        setup_logger()
        
        set_title(f"Playerok Universal v{VERSION} by @alleexxeeyy")
        print(
            f"\n\n"
            f"\n   {ACCENT_COLOR}Playerok Universal {Fore.WHITE}v{Fore.LIGHTWHITE_EX}{VERSION}"
            f"\n"
            f"\n   {Fore.YELLOW}Наши ссылки:"
            f"\n   {Fore.WHITE}· TG бот: {Fore.LIGHTWHITE_EX}https://t.me/alexey_production_bot"
            f"\n   {Fore.WHITE}· TG канал: {Fore.LIGHTWHITE_EX}https://t.me/alexeyproduction"
            f"\n   {Fore.WHITE}· GitHub: {Fore.LIGHTWHITE_EX}https://github.com/alleexxeeyy/playerok-universal"
            f"\n\n\n"
        )
        
        check_for_updates()
        configure_config()

        modules = load_modules()
        set_modules(modules)
        asyncio.run(connect_modules(modules))

        main_loop.run_until_complete(start_telegram_bot(from_tg))
        main_loop.run_until_complete(start_playerok_bot())
        main_loop.create_task(clear_logs_task())

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