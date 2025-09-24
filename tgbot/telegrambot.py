import asyncio
from colorama import Fore
import logging
import textwrap
logger = logging.getLogger("universal.telegram")

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.exceptions import TelegramUnauthorizedError

from tgbot import router as main_router
from tgbot import templates as templ

import settings
from settings import Settings as sett

from core.modules_manager import ModulesManager as modules_m
from core.handlers_manager import HandlersManager as handlers_m
from core.console import restart
from . import set_telegram_bot, set_telegram_bot_loop
from __init__ import ACCENT_COLOR

PREFIX = f"{Fore.LIGHTCYAN_EX}[TG]{Fore.WHITE}"



class TelegramBot:
    """
    Класс, описывающий Telegram бота.

    :param bot_token: Токен бота.
    :type bot_token: `str`
    """

    def __init__(self, bot_token: str):
        self.config = sett.get("config")
        self.bot_token = bot_token

        logging.getLogger("aiogram").setLevel(logging.CRITICAL)
        logging.getLogger("aiogram.event").setLevel(logging.CRITICAL)

        self.bot = Bot(token=self.bot_token)
        self.dp = Dispatcher()
        
        for module in modules_m.get_modules():
            for router in module.telegram_bot_routers:
                main_router.include_router(router)
        self.dp.include_router(main_router)
        
        set_telegram_bot_loop(asyncio.get_running_loop())
        set_telegram_bot(self)

    async def set_main_menu(self):
        main_menu_commands = [BotCommand(command="/start", description="🏠 Главное меню")]
        await self.bot.set_my_commands(main_menu_commands)

    async def set_short_description(self):
        short_description = textwrap.dedent(f"""
            Playerok Universal — Современный бот-помощник для Playerok 🟦
            ┕ Канал — @alexeyproduction
            ┕ Бот — @alexey_production_bot
        """)
        await self.bot.set_my_short_description(short_description=short_description)
    
    async def run_bot(self):
        try:
            await self.set_main_menu()
            await self.set_short_description()
        except TelegramUnauthorizedError:
            logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}Не удалось подключиться к вашему Telegram боту. {Fore.WHITE}Возможно вы указали неверный токен бота в конфиге.")
            print(f"{Fore.WHITE}🤖  Указать новый {Fore.LIGHTCYAN_EX}токен бота{Fore.WHITE}? +/-")
            a = input(f"{Fore.WHITE}→ {Fore.LIGHTWHITE_EX}")
            if a == "+":
                param = {"telegram": {"api": {"token": settings.DATA["config"]["params"]["telegram"]["api"]["token"]}}}
                sett.configure("config", ACCENT_COLOR, params=param)
                restart()
            else:
                logger.info(f"{PREFIX} Вы отказались от настройки конфига. Перезагрузим бота и попробуем снова подключиться к Telegram боту...")
                restart()
        
        bot_event_handlers = handlers_m.get_bot_event_handlers()
        async def handle_on_telegram_bot_init():
            """ 
            Запускается преред инициализацией Telegram бота. 
            Запускает за собой все хендлеры ON_TELEGRAM_BOT_INIT.
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
                
        :param calling_name: Никнейм покупателя.
        :type calling_name: `str`

        :param chat_id: ID чата с заказчиком.
        :type chat_id: `int` or `str`
        """
        config = sett.get("config")
        for user_id in config["telegram"]["bot"]["signed_users"]:
            await self.bot.send_message(chat_id=user_id, 
                                        text=templ.call_seller_text(calling_name, f"https://playerok.com/chats/{chat_id}"),
                                        reply_markup=templ.destroy_kb(),
                                        parse_mode="HTML")
        
    async def log_event(self, text: str):
        """
        Логирует событие в чат TG бота.
                
        :param text: Текст лога.
        :type text: `str`
        """
        config = sett.get("config")
        chat_id = config["playerok"]["bot"]["tg_logging_chat_id"]
        if not chat_id:
            for user_id in config["telegram"]["bot"]["signed_users"]:
                await self.bot.send_message(chat_id=user_id, text=text, parse_mode="HTML")
        else:
            await self.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")


if __name__ == "__main__":
    config = sett.get("config")
    asyncio.run(TelegramBot(config["telegram"]["api"]["token"]).run_bot())