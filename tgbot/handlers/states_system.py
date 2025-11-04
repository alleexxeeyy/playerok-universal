from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from settings import Settings as sett

from .. import templates as templ
from .. import states
from ..helpful import throw_float_message


router = Router()


@router.message(states.SystemStates.waiting_for_password, F.text)
async def handler_waiting_for_password(message: types.Message, state: FSMContext):
    try: 
        await state.set_state(None)
        config = sett.get("config")
        if message.text.strip() != config["telegram"]["bot"]["password"]:
            raise Exception("❌ Неверный ключ-пароль.")
        
        config["telegram"]["bot"]["signed_users"].append(message.from_user.id)
        sett.set("config", config)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.menu_text(),
            reply_markup=templ.menu_kb()
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.sign_text(e), 
            reply_markup=templ.destroy_kb()
        )