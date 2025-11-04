from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from .. import templates as templ
from .. import callback_datas as calls
from ..helpful import throw_float_message


router = Router()


@router.callback_query(calls.CustomCommandPage.filter())
async def callback_custom_command_page(callback: CallbackQuery, callback_data: calls.CustomCommandPage, state: FSMContext):
    await state.set_state(None)
    command = callback_data.command
    data = await state.get_data()
    await state.update_data(custom_command=command)
    last_page = data.get("last_page", 0)
    await throw_float_message(state, callback.message, templ.settings_comm_page_text(command), templ.settings_comm_page_kb(command, last_page), callback)


@router.callback_query(calls.AutoDeliveryPage.filter())
async def callback_custom_command_page(callback: CallbackQuery, callback_data: calls.AutoDeliveryPage, state: FSMContext):
    await state.set_state(None)
    index = callback_data.index
    data = await state.get_data()
    await state.update_data(auto_delivery_index=index)
    last_page = data.get("last_page", 0)
    await throw_float_message(state, callback.message, templ.settings_deliv_page_text(index), templ.settings_deliv_page_kb(index, last_page), callback)
    

@router.callback_query(calls.MessagePage.filter())
async def callback_message_page(callback: CallbackQuery, callback_data: calls.MessagePage, state: FSMContext):
    await state.set_state(None)
    message_id = callback_data.message_id
    data = await state.get_data()
    await state.update_data(message_id=message_id)
    last_page = data.get("last_page", 0)
    await throw_float_message(state, callback.message, templ.settings_mess_page_text(message_id), templ.settings_mess_page_kb(message_id, last_page), callback)


@router.callback_query(calls.ModulePage.filter())
async def callback_module_page(callback: CallbackQuery, callback_data: calls.ModulePage, state: FSMContext):
    await state.set_state(None)
    module_uuid = callback_data.uuid
    data = await state.get_data()
    await state.update_data(module_uuid=module_uuid)
    last_page = data.get("last_page", 0)
    await throw_float_message(state, callback.message, templ.module_page_text(module_uuid), templ.module_page_kb(module_uuid, last_page), callback)