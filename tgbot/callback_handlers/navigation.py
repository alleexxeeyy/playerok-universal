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
    elif to == "restore":
        await throw_float_message(state, callback.message, templ.settings_restore_text(), templ.settings_restore_kb(), callback)
    elif to == "logger":
        await throw_float_message(state, callback.message, templ.settings_logger_text(), templ.settings_logger_kb(), callback)
    elif to == "other":
        await throw_float_message(state, callback.message, templ.settings_other_text(), templ.settings_other_kb(), callback)