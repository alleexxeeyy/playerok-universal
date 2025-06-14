import asyncio
from colorama import Fore, Style
import logging
logger = logging.getLogger("UNIVERSAL.TelegramBot")

from aiogram import Bot, Dispatcher, Router
from aiogram.types import BotCommand, BotName

from tgbot import router as main_router
import tgbot.templates.user_templates as Templates

from settings import Config

from core.modules_manager import ModulesManager
from core.handlers_manager import HandlersManager

PREFIX = f"{Fore.LIGHTCYAN_EX}[telegram bot]{Fore.WHITE}"

class TelegramBot:
    """ Класс, запускающий и инициализирующий Telegram бота """

    def __init__(self, bot_token: str):
        self.config = Config.get()
        self.admin_id = self.config["tg_admin_id"]
        self.bot_token = bot_token
        
        logging.getLogger("aiogram").setLevel(logging.CRITICAL)
        logging.getLogger("aiogram.event").setLevel(logging.CRITICAL)

        try:
            self.bot = Bot(token=self.bot_token)
        except:
            logger.error(f"{PREFIX} Не удалось подключиться к вашему Telegram боту. Возможно вы указали неверный токен бота в конфиге.")
            print(f"{Fore.LIGHTWHITE_EX}Начать снова настройку конфига? +/-")
            a = input(f"{Fore.WHITE}> {Fore.LIGHTWHITE_EX}")
            if a == "+":
                Config.configure_config()
                print(f"\n{Fore.LIGHTWHITE_EX}Перезапустите бота, чтобы продолжить работу.")
                raise SystemExit(1)
            else:
                logger.info(f"{PREFIX} Вы отказались от настройки конфига. Пробуем снова подключиться к вашему Telegram боту...")
                return TelegramBot().run_bot()
        self.dp = Dispatcher()
        
        for module in ModulesManager.get_modules():
            for router in module.telegram_bot_routers:
                main_router.include_router(router)
        self.dp.include_router(main_router)

    async def set_main_menu(self):
        """ Задаёт меню из команд боту """
        main_menu_commands = [
            BotCommand(command="/start",
                    description="Главное меню"),
            BotCommand(command="/settings",
                    description="Настройки бота"),
            BotCommand(command="/stats",
                    description="Статистика бота")
        ]
        await self.bot.set_my_commands(main_menu_commands)

    async def run_bot(self):
        """ Функция-запускатор бота. """
        await self.set_main_menu()
        bot_event_handlers = HandlersManager.get_bot_event_handlers()
        async def handle_on_telegram_bot_init():
            """ 
            Запускается преред инициализацией Telegram бота. 
            Запускает за собой все хендлеры ON_TELEGRAM_BOT_INIT
            """
            if "ON_TELEGRAM_BOT_INIT" in bot_event_handlers:
                for handler in bot_event_handlers["ON_TELEGRAM_BOT_INIT"]:
                    try:
                        await handler(self)
                    except Exception as e:
                        logger.error(f"{Fore.LIGHTRED_EX}Ошибка при обработке хендлера в ивента ON_TELEGRAM_BOT_INIT: {Fore.WHITE}{e}")
        await handle_on_telegram_bot_init()
        
        me = await self.bot.get_me()
        logger.info(f"{PREFIX} Telegram бот {Fore.LIGHTWHITE_EX}@{me.username} {Fore.WHITE}запущен и активен")
        await self.dp.start_polling(self.bot, skip_updates=True, handle_signals=False)
        
    async def call_seller(self, calling_name: str, chat_id: int | str):
        """
        Пишет админу в Telegram с просьбой о помощи от заказчика.
                
        :param calling_name: Никнейм покупателя
        :type calling_name: `str`

        :param chat_id: ID чата с заказчиком
        :type chat_id: `int` or `str`
        """
        await self.bot.send_message(chat_id=self.admin_id, 
                                    text=Templates.Callbacks.CallSeller.text(calling_name, f"https://playerok.com/chats/{chat_id}"),
                                    parse_mode="HTML")

if __name__ == "__main__":
    config = Config.get()
    asyncio.run(TelegramBot(config["tg_bot_token"]).run_bot())