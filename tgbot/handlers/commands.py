from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from __init__ import VERSION
from settings import Settings as sett
from core.utils import restart

from .. import templates as templ
from ..helpful import throw_float_message, do_auth


router = Router()


@router.message(Command("start"))
async def handler_start(message: types.Message, state: FSMContext):
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

    from updater import latest_release
    if latest_release and latest_release.get("tag_name") != VERSION:
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
    
    await throw_float_message(
        state=state,
        message=message,
        text="🔄️ <b>Перезагружаю бота</b>, подождите...",
        reply_markup=templ.destroy_kb()
    )
    
    restart(from_tg=True)