from __future__ import annotations
import asyncio
import textwrap
import logging
from colorama import Fore
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, InlineKeyboardMarkup

from __init__ import ACCENT_COLOR
from settings import Settings as sett
from core.modules import get_modules
from core.handlers import call_bot_event

from . import router as main_router
from . import templates as templ


logger = logging.getLogger("universal.telegram")


def get_telegram_bot() -> TelegramBot | None:
    if hasattr(TelegramBot, "instance"):
        return getattr(TelegramBot, "instance")


def get_telegram_bot_loop() -> asyncio.AbstractEventLoop | None:
    if hasattr(get_telegram_bot(), "loop"):
        return getattr(get_telegram_bot(), "loop")


class TelegramBot:
    def __new__(cls, *args, **kwargs) -> TelegramBot:
        if not hasattr(cls, "instance"):
            cls.instance = super(TelegramBot, cls).__new__(cls)
        return getattr(cls, "instance")

    def __init__(self):
        logging.getLogger("aiogram").setLevel(logging.ERROR)
        logging.getLogger("aiogram.event").setLevel(logging.ERROR)
        
        config = sett.get("config")
        self.bot = Bot(token=config["telegram"]["api"]["token"])
        self.dp = Dispatcher()

        for module in get_modules():
            for router in module.telegram_bot_routers:
                main_router.include_router(router)
        self.dp.include_router(main_router)

    async def _set_main_menu(self):
        try:
            main_menu_commands = [BotCommand(command="/start", description="🏠 Главное меню")]
            await self.bot.set_my_commands(main_menu_commands)
        except:
            pass

    async def _set_short_description(self):
        try:
            short_description = textwrap.dedent(f"""
                Playerok Universal — Современный бот-помощник для Playerok 🟦
                
                ・ Канал — @alexeyproduction
                ・ Бот — @alexey_production_bot
            """)
            await self.bot.set_my_short_description(short_description=short_description)
        except:
            pass

    async def _set_description(self):
        try:
            description = textwrap.dedent(f"""
                🟢 Вечный онлайн
                ♻️ Авто-восстановление товаров
                ⬆️ Авто-поднятие товаров
                📦 Авто-выдача
                🕹️ Команды
                💬 Вызов продавца в чат
                👋 Приветственное сообщение
                🖌️ Полная кастомизация
                🔌 Плагины
                                        
                ⬇️ Скачать бота: https://github.com/alleexxeeyy/playerok-universal
                
                📣 Канал — @alexeyproduction
                🤖 Бот — @alexey_production_bot
                🧑‍💻 Автор — @alleexxeeyy
            """)
            await self.bot.set_my_description(description=description)
        except:
            pass

    async def run_bot(self):
        self.loop = asyncio.get_running_loop()

        await self._set_main_menu()
        await self._set_short_description()
        await self._set_description()
        
        await call_bot_event("ON_TELEGRAM_BOT_INIT", [self])
        
        me = await self.bot.get_me()
        logger.info(f"{ACCENT_COLOR}Telegram бот {Fore.LIGHTCYAN_EX}@{me.username} {ACCENT_COLOR}запущен и активен")
        await self.dp.start_polling(self.bot, skip_updates=True, handle_signals=False)

    async def call_seller(self, calling_name: str, chat_id: int | str):
        config = sett.get("config")
        for user_id in config["telegram"]["bot"]["signed_users"]:
            await self.bot.send_message(
                chat_id=user_id, 
                text=templ.call_seller_text(calling_name, f"https://playerok.com/chats/{chat_id}"),
                reply_markup=templ.destroy_kb(),
                parse_mode="HTML"
            )
        
    async def log_event(self, text: str, kb: InlineKeyboardMarkup | None = None):
        config = sett.get("config")
        chat_id = config["playerok"]["tg_logging"]["chat_id"]
        if not chat_id:
            for user_id in config["telegram"]["bot"]["signed_users"]:
                await self.bot.send_message(
                    chat_id=user_id, 
                    text=text, 
                    reply_markup=kb, 
                    parse_mode="HTML"
                )
        else:
            await self.bot.send_message(
                chat_id=chat_id, 
                text=f'{text}\n<span class="tg-spoiler">Переключите чат логов на чат с ботом, чтобы отображалась меню с действиями</span>', 
                reply_markup=None, 
                parse_mode="HTML"
            )