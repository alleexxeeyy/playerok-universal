from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramAPIError

from tgbot.helpful import throw_float_message
from tgbot import templates as main_templ

from .. import templates as templ
from .. import callback_datas as calls
from .. import states
from ...settings import Settings as sett
from .navigation import *


router = Router()


@router.callback_query(F.data == "forms_switch_log_states")
async def callback_forms_switch_log_states(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    config = sett.get("config")
    config["playerok"]["bot"]["log_states"] = not config["playerok"]["bot"]["log_states"]
    sett.set("config", config)
    return await callback_menu_navigation(callback, calls.FORMS_MenuNavigation(to="settings"), state)

@router.callback_query(F.data == "forms_enter_messages_page")
async def callback_forms_enter_messages_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page") or 0
    await state.set_state(states.FORMS_MessagesStates.entering_page)
    await throw_float_message(state=state, 
                              message=callback.message, 
                              text=templ.settings_mess_float_text(f"📃 Введите номер страницы для перехода ↓"), 
                              reply_markup=main_templ.back_kb(calls.FORMS_MessagesPagination(page=last_page).pack()))

@router.callback_query(F.data == "forms_switch_message_enabled")
async def callback_forms_switch_message_enabled(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        last_page = data.get("last_page") or 0
        message_id = data.get("message_id")
        if not message_id:
            raise Exception("❌ ID сообщения не был найден, повторите процесс с самого начала")
        
        messages = sett.get("messages")
        messages[message_id]["enabled"] = not messages[message_id]["enabled"]
        sett.set("messages", messages)
        return await callback_message_page(callback, calls.FORMS_MessagePage(message_id=message_id), state)
    except Exception as e:
        if e is not TelegramAPIError:
            data = await state.get_data()
            last_page = data.get("last_page") or 0
            await throw_float_message(state=state, 
                                      message=callback.message, 
                                      text=templ.settings_mess_float_text(e), 
                                      reply_markup=main_templ.back_kb(calls.FORMS_MessagesPagination(page=last_page).pack()))

@router.callback_query(F.data == "forms_enter_message_text")
async def callback_forms_enter_message_text(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        last_page = data.get("last_page") or 0
        message_id = data.get("message_id")
        if not message_id:
            raise Exception("❌ ID сообщения не был найден, повторите процесс с самого начала")
        
        await state.set_state(states.FORMS_MessagePageStates.entering_message_text)
        messages = sett.get("messages")
        mess_text = "\n".join(messages[message_id]["text"]) or "❌ Не задано"
        await throw_float_message(state=state, 
                                  message=callback.message, 
                                  text=templ.settings_mess_float_text(f"💬 Введите новый <b>текст сообщения</b> «{sett.get_message_label(message_id)}» ↓\n┗ Текущее: <blockquote>{mess_text}</blockquote>"), 
                                  reply_markup=main_templ.back_kb(calls.FORMS_MessagesPagination(page=last_page).pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            data = await state.get_data()
            last_page = data.get("last_page") or 0
            await throw_float_message(state=state, 
                                      message=callback.message, 
                                      text=templ.settings_mess_float_text(e), 
                                      reply_markup=main_templ.back_kb(calls.FORMS_MessagesPagination(page=last_page).pack()))