from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from .. import templates as templ
from ..helpful import throw_float_message, do_auth
from settings import Settings as sett

router = Router()


@router.message(Command("start"))
async def handler_start(message: types.Message, state: FSMContext):
    await state.set_state(None)
    config = sett.get("config")
    if message.from_user.id not in config["telegram"]["bot"]["signed_users"]:
        return await do_auth(message, state)
    await throw_float_message(state=state,
                            message=message,
                            text=templ.menu_text(),
                            reply_markup=templ.menu_kb())