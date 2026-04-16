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

        text = ""
        if message.text:
            if len(message.text.strip()) <= 0:
                raise Exception("❌ Слишком короткий текст")

            text = message.text
            sent_msg += message.text.strip()

        photo_paths = []
        if message.photo:
            photos_messages = [message]

            if message.media_group_id:
                await asyncio.sleep(1)
                data = await state.get_data()
                photos_messages = data.get("album_messages", []) + [message]
                await state.update_data(album_messages=photos_messages)

            for msg in photos_messages:
                photo = msg.photo[-1]

                with NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                    await message.bot.download(photo, destination=tmp.name)
                    photo_paths.append(tmp.name)

            if message.caption:
                text = message.caption
                await asyncio.sleep(1)

            plbot.account.send_message(
                chat_id=chat.id,
                photo_file_paths=photo_paths
            )

            for path in photo_paths:
                try:
                    os.remove(path)
                except:
                    pass

            sent_msg += f", <b>Изображения ({len(photo_paths)})</b>"

        plbot.account.send_message(
            chat_id=chat.id, 
            text=text,
            photo_file_paths=photo_paths
        )

        await throw_float_message(
            state=state,
            message=message,
            text=templ.do_action_text(
                f"✅ Пользователю <b>{username}</b> было отправлено сообщение: <blockquote>{sent_msg.strip()}</blockquote>"
            ),
            reply_markup=templ.destroy_kb()
        )

    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.do_action_text(e),
            reply_markup=templ.destroy_kb()
        )