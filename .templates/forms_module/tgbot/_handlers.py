from aiogram.types import BotCommand
from tgbot.telegrambot import TelegramBot
from logging import getLogger

from ..meta import NAME


logger = getLogger(f"{NAME}.telegram")


async def on_telegram_bot_init(tgbot: TelegramBot) -> None:
    try:
        main_menu_commands = await tgbot.bot.get_my_commands()
        forms_menu_commands = [BotCommand(command=f"/{NAME}", description=f"📝📈 Управление модулем {NAME}")]
        await tgbot.bot.set_my_commands(list(main_menu_commands + forms_menu_commands))
    except:
        pass