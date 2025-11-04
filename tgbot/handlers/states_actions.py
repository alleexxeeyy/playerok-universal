from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from .. import templates as templ
from .. import states
from ..helpful import throw_float_message


router = Router()


@router.message(states.ActionsStates.waiting_for_message_text, F.text)
async def handler_waiting_for_password(message: types.Message, state: FSMContext):
    try: 
        await state.set_state(None)
        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком короткий текст")

        from plbot.playerokbot import get_playerok_bot
        
        data = await state.get_data()
        plbot = get_playerok_bot()
        username = data.get("username")
        chat = plbot.get_chat_by_username(username)
        plbot.send_message(chat_id=chat.id, text=message.text.strip())

        await throw_float_message(
            state=state,
            message=message,
            text=templ.do_action_text(f"✅ Пользователю <b>{username}</b> было отправлено сообщение: <blockquote>{message.text.strip()}</blockquote>"),
            reply_markup=templ.destroy_kb()
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.do_action_text(e), 
            reply_markup=templ.destroy_kb()
        )