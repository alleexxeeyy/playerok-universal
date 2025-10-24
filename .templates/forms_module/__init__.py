from core.modules import Module
from logging import getLogger

from playerokapi.enums import EventTypes

from .plbot.handlers import on_playerok_bot_init, on_new_message
from .tgbot._handlers import on_telegram_bot_init
from .tgbot import router
from .meta import *


logger = getLogger(f"forms")
_module: Module = None


def set_module(new: Module):
    global _module
    _module = new

def get_module():
    return _module

def on_module_connected(module: Module):
    set_module(module)
    logger.info(f"{PREFIX} Модуль подключен и активен")


BOT_EVENT_HANDLERS = {
    "ON_MODULE_CONNECTED": [on_module_connected],
    "ON_MODULE_ENABLED": [on_module_connected],
    "ON_MODULE_RELOADED": [on_module_connected],
    "ON_PLAYEROK_BOT_INIT": [on_playerok_bot_init],
    "ON_TELEGRAM_BOT_INIT": [on_telegram_bot_init]
}
PLAYEROK_EVENT_HANDLERS = {
    EventTypes.NEW_MESSAGE: [on_new_message]
}
TELEGRAM_BOT_ROUTERS = [router]