from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from .. import templates as templ
from .. import callback_datas as calls
from ..helpful import throw_float_message

router = Router()



@router.callback_query(calls.MenuNavigation.filter())
async def callback_menu_navigation(callback: CallbackQuery, callback_data: calls.MenuNavigation, state: FSMContext):
    await state.set_state(None)
    to = callback_data.to
    if to == "default":
        await throw_float_message(state, callback.message, templ.menu_text(), templ.menu_kb(), callback)
    elif to == "stats":
        await throw_float_message(state, callback.message, templ.stats_text(), templ.stats_kb(), callback)
    elif to == "profile":
        await throw_float_message(state, callback.message, templ.profile_text(), templ.profile_kb(), callback)

@router.callback_query(calls.InstructionNavigation.filter())
async def callback_instruction_navgiation(callback: CallbackQuery, callback_data: calls.InstructionNavigation, state: FSMContext):
    await state.set_state(None)
    to = callback_data.to
    if to == "default":
        await throw_float_message(state, callback.message, templ.instruction_text(), templ.instruction_kb(), callback)
    elif to == "commands":
        await throw_float_message(state, callback.message, templ.instruction_comms_text(), templ.instruction_comms_kb(), callback)

@router.callback_query(calls.SettingsNavigation.filter())
async def callback_settings_navigation(callback: CallbackQuery, callback_data: calls.SettingsNavigation, state: FSMContext):
    await state.set_state(None)
    to = callback_data.to
    if to == "default":
        await throw_float_message(state, callback.message, templ.settings_text(), templ.settings_kb(), callback)
    elif to == "auth":
        await throw_float_message(state, callback.message, templ.settings_auth_text(), templ.settings_auth_kb(), callback)
    elif to == "conn":
        await throw_float_message(state, callback.message, templ.settings_conn_text(), templ.settings_conn_kb(), callback)
    elif to == "items":
        await throw_float_message(state, callback.message, templ.settings_items_text(), templ.settings_items_kb(), callback)
    elif to == "logger":
        await throw_float_message(state, callback.message, templ.settings_logger_text(), templ.settings_logger_kb(), callback)
    elif to == "other":
        await throw_float_message(state, callback.message, templ.settings_other_text(), templ.settings_other_kb(), callback)


@router.callback_query(calls.CustomCommandsPagination.filter())
async def callback_custom_commands_pagination(callback: CallbackQuery, callback_data: calls.CustomCommandsPagination, state: FSMContext):
    await state.set_state(None)
    page = callback_data.page
    await state.update_data(last_page=page)
    await throw_float_message(state, callback.message, templ.settings_comm_text(), templ.settings_comm_kb(page), callback)

@router.callback_query(calls.CustomCommandPage.filter())
async def callback_custom_command_page(callback: CallbackQuery, callback_data: calls.CustomCommandPage, state: FSMContext):
    await state.set_state(None)
    command = callback_data.command
    data = await state.get_data()
    await state.update_data(custom_command=command)
    last_page = data.get("last_page") or 0
    await throw_float_message(state, callback.message, templ.settings_comm_page_text(command), templ.settings_comm_page_kb(command, last_page), callback)


@router.callback_query(calls.AutoDeliveriesPagination.filter())
async def callback_auto_delivery_pagination(callback: CallbackQuery, callback_data: calls.AutoDeliveriesPagination, state: FSMContext):
    try:
        await state.set_state(None)
        page = callback_data.page
        await state.update_data(last_page=page)
        await throw_float_message(state, callback.message, templ.settings_deliv_text(), templ.settings_deliv_kb(page), callback)
    except:
        import traceback
        traceback.print_exc()

@router.callback_query(calls.AutoDeliveryPage.filter())
async def callback_custom_command_page(callback: CallbackQuery, callback_data: calls.AutoDeliveryPage, state: FSMContext):
    try:
        await state.set_state(None)
        index = callback_data.index
        data = await state.get_data()
        await state.update_data(auto_delivery_index=index)
        last_page = data.get("last_page") or 0
        await throw_float_message(state, callback.message, templ.settings_deliv_page_text(index), templ.settings_deliv_page_kb(index, last_page), callback)
    except:
        import traceback
        traceback.print_exc()


@router.callback_query(calls.MessagesPagination.filter())
async def callback_messages_pagination(callback: CallbackQuery, callback_data: calls.MessagesPagination, state: FSMContext):
    await state.set_state(None)
    page = callback_data.page
    await state.update_data(last_page=page)
    await throw_float_message(state, callback.message, templ.settings_mess_text(), templ.settings_mess_kb(page), callback)
    
@router.callback_query(calls.MessagePage.filter())
async def callback_message_page(callback: CallbackQuery, callback_data: calls.MessagePage, state: FSMContext):
    await state.set_state(None)
    message_id = callback_data.message_id
    data = await state.get_data()
    await state.update_data(message_id=message_id)
    last_page = data.get("last_page") or 0
    await throw_float_message(state, callback.message, templ.settings_mess_page_text(message_id), templ.settings_mess_page_kb(message_id, last_page), callback)


@router.callback_query(calls.ModulesPagination.filter())
async def callback_modules_pagination(callback: CallbackQuery, callback_data: calls.ModulesPagination, state: FSMContext):
    await state.set_state(None)
    page = callback_data.page
    await state.update_data(last_page=page)
    await throw_float_message(state, callback.message, templ.modules_text(), templ.modules_kb(page), callback)

@router.callback_query(calls.ModulePage.filter())
async def callback_module_page(callback: CallbackQuery, callback_data: calls.ModulePage, state: FSMContext):
    await state.set_state(None)
    module_uuid = callback_data.uuid
    data = await state.get_data()
    await state.update_data(module_uuid=module_uuid)
    last_page = data.get("last_page") or 0
    await throw_float_message(state, callback.message, templ.module_page_text(module_uuid), templ.module_page_kb(module_uuid, last_page), callback)