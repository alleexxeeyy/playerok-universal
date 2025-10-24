from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from settings import Settings as main_sett
from tgbot.helpful import throw_float_message, do_auth

from .. import templates as templ


router = Router()


@router.message(Command("forms"))
async def cmd_forms(message: types.Message, state: FSMContext):
    from ... import get_module
    await state.set_state(None)
    main_config = main_sett.get("config")
    if not get_module().enabled:
        return
    if message.from_user.id not in main_config["telegram"]["bot"]["signed_users"]:
        return await do_auth(message, state)
    await throw_float_message(state, message, templ.menu_text(), templ.menu_kb())