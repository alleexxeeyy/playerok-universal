from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from settings import Settings as sett

from .. import templates as templ
from .. import states
from .. import callback_datas as calls
from ..helpful import throw_float_message


router = Router()


@router.message(states.MessagesStates.waiting_for_page, F.text)
async def handler_waiting_for_messages_page(message: types.Message, state: FSMContext):
    try: 
        await state.set_state(None)
        if not message.text.strip().isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")
        
        await state.update_data(last_page=int(message.text.strip())-1)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_mess_text(),
            reply_markup=templ.settings_mess_kb(int(message.text)-1)
        )
    except Exception as e:
        data = await state.get_data()
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_mess_float_text(e),
            reply_markup=templ.back_kb(calls.MessagesPagination(page=data.get("last_page", 0)).pack())
        )
        
        
@router.message(states.MessagesStates.waiting_for_message_text, F.text)
async def handler_waiting_for_message_text(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком короткий текст")

        data = await state.get_data()
        messages = sett.get("messages")
        message_split_lines = message.text.strip().split('\n')
        messages[data["message_id"]]["text"] = message_split_lines
        sett.set("messages", messages)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_mess_page_float_text(f"✅ <b>Текст сообщения</b> <code>{data['message_id']}</code> был успешно изменён на <blockquote>{message.text.strip()}</blockquote>"),
            reply_markup=templ.back_kb(calls.MessagePage(message_id=data.get("message_id")).pack())
        )
    except Exception as e:
        data = await state.get_data()
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_mess_page_float_text(e), 
            reply_markup=templ.back_kb(calls.MessagePage(message_id=data.get("message_id")).pack())
        )