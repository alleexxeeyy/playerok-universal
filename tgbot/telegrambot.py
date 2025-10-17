from __future__ import annotations
import asyncio
from colorama import Fore
import textwrap
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, InlineKeyboardMarkup
import logging
logger = logging.getLogger(f"universal.telegram")

from . import router as main_router
from . import templates as templ
from settings import Settings as sett
from core.modules import get_modules
from core.handlers import get_bot_event_handlers


def get_telegram_bot_loop() -> None | asyncio.AbstractEventLoop:
    if hasattr(TelegramBot, "loop"):
        return getattr(TelegramBot, "loop")

def get_telegram_bot() -> None | TelegramBot:
    if hasattr(TelegramBot, "instance"):
        return getattr(TelegramBot, "instance")

class TelegramBot:
    def __new__(cls, *args, **kwargs) -> TelegramBot:
        if not hasattr(cls, "instance"):
            cls.instance = super(TelegramBot, cls).__new__(cls)
            cls.loop = asyncio.get_running_loop()
        return getattr(cls, "instance")

    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        logging.getLogger("aiogram").setLevel(logging.CRITICAL)
        logging.getLogger("aiogram.event").setLevel(logging.CRITICAL)
        self.bot = Bot(token=self.bot_token)
        self.dp = Dispatcher()
        
        for module in get_modules():
            for router in module.telegram_bot_routers:
                main_router.include_router(router)
        self.dp.include_router(main_router)

    async def set_main_menu(self):
        try:
            main_menu_commands = [BotCommand(command="/start", description="🏠 Главное меню")]
            await self.bot.set_my_commands(main_menu_commands)
        except:
            pass

    async def set_short_description(self):
        try:
            short_description = textwrap.dedent(f"""
                Playerok Universal — Современный бот-помощник для Playerok 🟦
                ┕ Канал — @alexeyproduction
                ┕ Бот — @alexey_production_bot
            """)
            await self.bot.set_my_short_description(short_description=short_description)
        except:
            pass

    async def set_description(self):
        try:
            description = textwrap.dedent(f"""
                Playerok Universal — Бесплатный современный бот-помощник для Playerok 🟦
                                        
                🟢 Вечный онлайн
                ♻️ Авто-восстановление товаров
                📦 Авто-выдача
                🕹️ Команды
                💬 Вызов продавца в чат
                                        
                ⬇️ Скачать бота: https://github.com/alleexxeeyy/funpay-universal
                
                📣 Канал — @alexeyproduction
                🤖 Бот — @alexey_production_bot
                🧑‍💻 Автор — @alleexxeeyy
            """)
            await self.bot.set_my_description(description=description)
        except:
            pass
    
    async def run_bot(self):
        await self.set_main_menu()
        await self.set_short_description()
        await self.set_description()
        
        bot_event_handlers = get_bot_event_handlers()
        async def handle_on_telegram_bot_init():
            """ 
            Запускается преред инициализацией Telegram бота. 
            Запускает за собой все хендлеры ON_TELEGRAM_BOT_INIT.
            """
            for handler in bot_event_handlers.get("ON_TELEGRAM_BOT_INIT", []):
                try:
                    await handler(self)
                except Exception as e:
                    logger.error(f"{Fore.LIGHTRED_EX}{Fore.LIGHTRED_EX}Ошибка при обработке хендлера ивента ON_TELEGRAM_BOT_INIT: {Fore.WHITE}{e}")
        await handle_on_telegram_bot_init()
        
        me = await self.bot.get_me()
        logger.info(f"{Fore.LIGHTBLUE_EX}Telegram бот {Fore.CYAN}@{me.username} {Fore.LIGHTBLUE_EX}запущен и активен")
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
        
    async def log_event(self, text: str, kb: InlineKeyboardMarkup | None = None):
        """
        Логирует событие в чат TG бота.
                
        :param text: Текст лога.
        :type text: `str`
                
        :param kb: Клавиатура с кнопками.
        :type kb: `aiogram.types.InlineKeyboardMarkup` or `None`
        """
        config = sett.get("config")
        chat_id = config["funpay"]["bot"]["tg_logging_chat_id"]
        if not chat_id:
            for user_id in config["telegram"]["bot"]["signed_users"]:
                await self.bot.send_message(chat_id=user_id, text=text, reply_markup=kb, parse_mode="HTML")
        else:
            await self.bot.send_message(chat_id=chat_id, text=f'{text}\n<span class="tg-spoiler">Переключите чат логов на чат с ботом, чтобы отображалась меню с действиями</span>', reply_markup=None, parse_mode="HTML")


if __name__ == "__main__":
    config = sett.get("config")
    asyncio.run(TelegramBot(config["telegram"]["api"]["token"]).run_bot())