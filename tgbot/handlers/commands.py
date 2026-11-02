from aiogram import types, Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from packaging.version import Version

from __init__ import VERSION
from settings import Settings as sett
from core.utils import restart
from core.bootreport import set_marker
from core import access

from .. import templates as templ
from ..helpful import throw_float_message, do_auth
from .setup import open_home


router = Router()


@router.message(Command("start"))
async def handler_start(message: types.Message, state: FSMContext, command: CommandObject):
    await state.set_state(None)

    args = command.args or ""
    if args.startswith(access.OWNER_PREFIX) and access.claim_owner(message.from_user.id, args[len(access.OWNER_PREFIX):]):
        return await open_home(message, state, welcome=True)
    
    config = sett.get("config")
    if message.from_user.id not in config["telegram"]["bot"]["signed_users"]:
        return await do_auth(message, state)
    
    await throw_float_message(
        state=state,
        message=message,
        text=templ.menu_text(),
        reply_markup=templ.menu_kb()
    )

    from updater import latest_release
    if latest_release and Version(VERSION) < Version(latest_release["tag_name"]): # GitHub мог не ответить при запуске
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
    await state.set_state(None)
    
    config = sett.get("config")
    if message.from_user.id not in config["telegram"]["bot"]["signed_users"]:
        return await do_auth(message, state)
    
    mess = await throw_float_message(
        state=state,
        message=message,
        text="🔄️ <b>Перезагружаю бота</b>, подождите...",
        reply_markup=templ.destroy_kb()
    )
    
    set_marker("restart", message.chat.id, mess.message_id if mess else None)
    restart(from_tg=True)