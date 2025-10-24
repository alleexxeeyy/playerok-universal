from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from tgbot.helpful import throw_float_message

from .. import templates as templ
from .. import callback_datas as calls


router = Router()


@router.callback_query(calls.FORMS_MenuNavigation.filter())
async def callback_menu_navigation(callback: CallbackQuery, callback_data: calls.FORMS_MenuNavigation, state: FSMContext):
    await state.set_state(None)
    to = callback_data.to
    if to == "default":
        await throw_float_message(state, callback.message, templ.menu_text(), templ.menu_kb(), callback)
    elif to == "settings":
        await throw_float_message(state, callback.message, templ.settings_text(), templ.settings_kb(), callback)

@router.callback_query(calls.FORMS_InstructionNavigation.filter())
async def callback_instruction_navgiation(callback: CallbackQuery, callback_data: calls.FORMS_InstructionNavigation, state: FSMContext):
    await state.set_state(None)
    to = callback_data.to
    if to == "default":
        await throw_float_message(state, callback.message, templ.instruction_text(), templ.instruction_kb(), callback)
    elif to == "commands":
        await throw_float_message(state, callback.message, templ.instruction_comms_text(), templ.instruction_comms_kb(), callback)

    
@router.callback_query(calls.FORMS_MessagesPagination.filter())
async def callback_messages_pagination(callback: CallbackQuery, callback_data: calls.FORMS_MessagesPagination, state: FSMContext):
    await state.set_state(None)
    page = callback_data.page
    await state.update_data(last_page=page)
    await throw_float_message(state, callback.message, templ.settings_mess_text(), templ.settings_mess_kb(page), callback)
    
@router.callback_query(calls.FORMS_MessagePage.filter())
async def callback_message_page(callback: CallbackQuery, callback_data: calls.FORMS_MessagePage, state: FSMContext):
    message_id = callback_data.message_id
    data = await state.get_data()
    await state.update_data(message_id=message_id)
    last_page = data.get("last_page") or 0
    await throw_float_message(state, callback.message, templ.settings_mess_page_text(message_id), templ.settings_mess_page_kb(message_id, last_page), callback)