from core.modules_manager import ModulesManager
from core.handlers_manager import HandlersManager

from core.console import set_title, setup_logger
import asyncio
from threading import Thread
import ctypes
from settings import Config
import traceback
from logging import getLogger
logger = getLogger("UNIVERSAL")
from colorama import init, Fore, Style
init()

from plbot.playerokbot import PlayerokBot
from services.updater import Updater

from tgbot import set_telegram_bot, set_loop


async def start_playerok_bot():
    """ Запускает FunPay бота в отдельном потоке. """
    plbot_loop = asyncio.new_event_loop()
    plbot = PlayerokBot()

    def run():
        plbot_loop.run_until_complete(plbot.run_bot())
    Thread(target=run, daemon=True).start()

async def start_telegram_bot():
    """ Запускает Telegram бота. """
    from tgbot.telegrambot import TelegramBot
    config = Config.get()
    tgbot = TelegramBot(config["tg_bot_token"])
    set_telegram_bot(tgbot)
    set_loop(asyncio.get_running_loop())
    await tgbot.run_bot()

if __name__ == "__main__":
    """ Запуск всех ботов """
    from bot_settings.app import CURRENT_VERSION
    try:
        setup_logger()
        set_title(f"Playerok Universal v{CURRENT_VERSION} by @alleexxeeyy")
        print(f"\n   {Fore.CYAN}Playerok Universal {Fore.WHITE}v{Fore.LIGHTWHITE_EX}{CURRENT_VERSION}"
              f"\n   {Fore.WHITE}→ tg: {Fore.LIGHTWHITE_EX}@alleexxeeyy"
              f"\n   {Fore.WHITE}→ tg channel: {Fore.LIGHTWHITE_EX}@alexeyproduction\n")
        
        if Updater.check_for_updates():
            exit()

        config = Config.get()
        if not config["token"]:
            print(f"{Fore.WHITE}🫸  Постойте... Не обнаружил в конфиге необходимых для работы бота данных. "
                  f"Возможно вы запускаете его впервые, поэтому давайте проведём быструю настройку конфига, чтобы вы смогли приступить к работе.")
            Config.configure_config()
        
        print(f"{Fore.WHITE}⏳ Загружаю и подключаю модули...")
        modules = ModulesManager.load_modules()
        if len(modules) == 0:
            print(f"{Fore.WHITE}Модулей не обнаружено")
        ModulesManager.set_modules(modules)
        
        if len(modules) > 0:
            ModulesManager.connect_modules(modules)
        
        for module in modules:
            if "ON_MODULE_CONNECTED" in module.bot_event_handlers and module.enabled:
                for handler in module.bot_event_handlers["ON_MODULE_CONNECTED"]:
                    try:
                        handler(module)
                    except Exception as e:
                        logger.error(f"{Fore.LIGHTRED_EX}Ошибка при обработке хендлера ивента ON_MODULE_CONNECTED: {Fore.WHITE}{e}")

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
        asyncio.run(start_telegram_bot())
    except Exception as e:
        traceback.print_exc()