from core.modules_manager import ModulesManager
from core.handlers_manager import HandlersManager

from core.console import set_title, setup_logger, install_requirements, patch_requests
import asyncio
import time
from threading import Thread
from settings import Settings as sett
import traceback
from logging import getLogger
logger = getLogger("universal")
from colorama import init, Fore, Style
from plbot import get_playerok_bot
init()

from services.updater import Updater
from __init__ import ACCENT_COLOR, VERSION



async def start_telegram_bot():
    from tgbot.telegrambot import TelegramBot
    config = sett.get("config")
    tgbot = TelegramBot(config["telegram"]["api"]["token"])
    await tgbot.run_bot()

async def start_playerok_bot():
    from plbot.playerokbot import PlayerokBot
    def run():
        asyncio.new_event_loop().run_until_complete(PlayerokBot().run_bot())
    Thread(target=run, daemon=True).start()


if __name__ == "__main__":
    try:
        install_requirements("requirements.txt") # установка недостающих зависимостей, если таковые есть
        patch_requests()
        setup_logger()
        set_title(f"Playerok Universal v{VERSION} by @alleexxeeyy")
        print(f"\n   {ACCENT_COLOR}Playerok Universal {Fore.WHITE}v{Fore.LIGHTWHITE_EX}{VERSION}"
              f"\n   {Fore.WHITE}→ tg: {Fore.LIGHTWHITE_EX}@alleexxeeyy"
              f"\n   {Fore.WHITE}→ tg channel: {Fore.LIGHTWHITE_EX}@alexeyproduction\n")
        
        if Updater.check_for_updates():
            exit()
        
        config = sett.get("config")
        if not config["playerok"]["api"]["token"]:
            print(f"{Fore.WHITE}🫸  Постойте... Не обнаружил в конфиге необходимых для работы бота данных. "
                  f"Возможно вы запускаете его впервые, поэтому давайте проведём быструю настройку конфига, чтобы вы смогли приступить к работе.")
            sett.configure("config", ACCENT_COLOR)
        
        print(f"{Fore.WHITE}⏳ Загружаю и подключаю модули...")
        modules = ModulesManager.load_modules()
        if len(modules) == 0:
            print(f"{Fore.WHITE}Модулей не обнаружено")
        ModulesManager.set_modules(modules)

        if len(modules) > 0:
            ModulesManager.connect_modules(modules)

        bot_event_handlers = HandlersManager.get_bot_event_handlers()
        def handle_on_init():
            """ 
            Запускается при инициализации софта.
            Запускает за собой все хендлеры ON_INIT
            """
            if "ON_INIT" in bot_event_handlers:
                for handler in bot_event_handlers["ON_INIT"]:
                    try:
                        handler()
                    except Exception as e:
                        logger.error(f"{Fore.LIGHTRED_EX}Ошибка при обработке хендлера ивента ON_INIT: {Fore.WHITE}{e}")
        handle_on_init()
        
        print(f"{Fore.WHITE}🤖 Запускаю бота...\n")
        asyncio.run(start_playerok_bot())
        while get_playerok_bot() is None:
            time.sleep(0.5)
        if get_playerok_bot() is None:
            raise Exception("Не удалось запустить Playerok бота")
        asyncio.run(start_telegram_bot())
    except Exception as e:
        traceback.print_exc()
    print(f"\n   {Fore.LIGHTRED_EX}Ваш бот словил непредвиденную ошибку и был выключен."
          f"\n   {Fore.WHITE}Пожалуйста, напишите в Telegram разработчика {Fore.LIGHTWHITE_EX}@alleexxeeyy{Fore.WHITE}, для уточнения причин")
    raise SystemExit(1)