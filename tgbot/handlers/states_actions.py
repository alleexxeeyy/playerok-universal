from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from tempfile import NamedTemporaryFile
import os
import asyncio

from .. import templates as templ
from .. import states
from ..helpful import throw_float_message


router = Router()


@router.message(states.ActionsStates.waiting_for_message_content, F.text | F.photo)
async def handler_waiting_for_message_content(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        await throw_float_message(state, message, "⌛")

        data = await state.get_data()
        username = data.get("username")
        
        from plbot.playerokbot import get_playerok_bot
        plbot = get_playerok_bot()
        chat = plbot.get_chat_by_username(username)
        
        sent_msg = ""

        if message.text:
            if len(message.text.strip()) <= 0:
                raise Exception("❌ Слишком короткий текст")
            plbot.send_message(chat_id=chat.id, text=message.text.strip())
            sent_msg += message.text.strip()
        
        elif message.photo:
            photo = message.photo[-1]
            with NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                await message.bot.download(photo, destination=tmp.name)
                tmp_path = tmp.name

            if message.caption:
                plbot.send_message(chat_id=chat.id, text=message.caption.strip())
                sent_msg += f"{message.caption.strip()}, "
                await asyncio.sleep(1)

            plbot.send_message(chat_id=chat.id, photo_file_path=tmp_path)
            os.remove(tmp_path)
            sent_msg += f"<b>Изображение</b>"

        await throw_float_message(
            state=state,
            message=message,
            text=templ.do_action_text(f"✅ Пользователю <b>{username}</b> было отправлено сообщение: <blockquote>{sent_msg}</blockquote>"),
            reply_markup=templ.destroy_kb()
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.do_action_text(e), 
            reply_markup=templ.destroy_kb()
        )