from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from packaging.version import Version
from datetime import datetime, timezone
from logging import getLogger
from time import monotonic

from __init__ import VERSION
from settings import Settings as sett
from core.utils import restart

from .. import templates as templ
from ..helpful import throw_float_message, do_auth


router = Router()
logger = getLogger("universal.telegram")


def log_slow_update(command: str, message: types.Message):
    sent_at = message.date
    if sent_at.tzinfo is None:
        sent_at = sent_at.replace(tzinfo=timezone.utc)
    age = (datetime.now(timezone.utc) - sent_at).total_seconds()
    if age > 2:
        logger.warning("Telegram %s получена с задержкой %.1f сек.", command, age)


def log_slow_reply(command: str, started: float):
    elapsed = monotonic() - started
    if elapsed > 2:
        logger.warning("Ответ на Telegram %s занял %.1f сек.", command, elapsed)


@router.message(Command("start"))
async def handler_start(message: types.Message, state: FSMContext):
    started = monotonic()
    log_slow_update('/start', message)
    await state.set_state(None)
    
    config = sett.get("config")
    if message.from_user.id not in config["telegram"]["bot"]["signed_users"]:
        return await do_auth(message, state)
    
    await throw_float_message(
        state=state,
        message=message,
        text=templ.menu_text(),
        reply_markup=templ.menu_kb()
    )
    log_slow_reply('/start', started)

    from updater import latest_release
    if Version(VERSION) < Version(latest_release["tag_name"]):
        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_release_text(latest_release),
            reply_markup=templ.new_release_kb(),
            disable_web_page_preview=True,
            send=True
        )


@router.message(Command("restart"))
async def handler_restart(message: types.Message, state: FSMContext):
    started = monotonic()
    log_slow_update('/restart', message)
    await state.set_state(None)
    
    config = sett.get("config")
    if message.from_user.id not in config["telegram"]["bot"]["signed_users"]:
        return await do_auth(message, state)
    
    await throw_float_message(
        state=state,
        message=message,
        text="🔄️ <b>Перезагружаю бота</b>, подождите...",
        reply_markup=templ.destroy_kb()
    )
    
    log_slow_reply('/restart', started)
    restart(from_tg=True)
