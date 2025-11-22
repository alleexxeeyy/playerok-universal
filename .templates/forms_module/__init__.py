from core.modules import Module
from logging import getLogger

from playerokapi.enums import EventTypes

from .plbot.handlers import (
    on_new_message,
    run_cycles,
    stop_cycles
)
from .tgbot._handlers import on_telegram_bot_init
from .tgbot import router
from .meta import *


logger = getLogger(NAME)
_module: Module = None


def set_module(new: Module):
    global _module
    _module = new


def get_module():
    return _module


async def on_module_enabled(module: Module):
    set_module(module)
    logger.info(f"{PREFIX} Модуль подключен и активен")


BOT_EVENT_HANDLERS = {
    "ON_MODULE_ENABLED": [on_module_enabled, run_cycles],
    "ON_MODULE_DISABLED": [stop_cycles],
    "ON_TELEGRAM_BOT_INIT": [on_telegram_bot_init]
}
PLAYEROK_EVENT_HANDLERS = {
    EventTypes.NEW_MESSAGE: [on_new_message]
}
TELEGRAM_BOT_ROUTERS = [router]