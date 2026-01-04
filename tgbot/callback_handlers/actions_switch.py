from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from core.modules import get_module_by_uuid, enable_module, disable_module
from settings import Settings as sett

from .. import templates as templ
from .. import callback_datas as calls
from .. import states as states
from ..helpful import throw_float_message
from .navigation import *
from ..callback_handlers.page import callback_message_page, callback_module_page


router = Router()


@router.callback_query(F.data == "switch_auto_restore_items_sold")
async def callback_switch_auto_restore_items_sold(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["auto_restore_items"]["sold"] = not config["playerok"]["auto_restore_items"]["sold"]
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="restore"), state)


@router.callback_query(F.data == "switch_auto_restore_items_expired")
async def callback_switch_auto_restore_items_expired(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["auto_restore_items"]["expired"] = not config["playerok"]["auto_restore_items"]["expired"]
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="restore"), state)


@router.callback_query(F.data == "switch_auto_restore_items_all")
async def callback_switch_auto_restore_items_all(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["auto_restore_items"]["all"] = not config["playerok"]["auto_restore_items"]["all"]
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="restore"), state)


@router.callback_query(F.data == "switch_auto_bump_items_enabled")
async def callback_switch_auto_bump_items_enabled(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["auto_bump_items"]["enabled"] = not config["playerok"]["auto_bump_items"]["enabled"]
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="bump"), state)


@router.callback_query(F.data == "switch_auto_bump_items_all")
async def callback_switch_auto_bump_items_all(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["auto_bump_items"]["all"] = not config["playerok"]["auto_bump_items"]["all"]
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="bump"), state)


@router.callback_query(F.data == "switch_read_chat_enabled")
async def callback_switch_read_chat_enabled(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["read_chat"]["enabled"] = not config["playerok"]["read_chat"]["enabled"]
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="other"), state)


@router.callback_query(F.data == "switch_auto_complete_deals_enabled")
async def callback_switch_auto_complete_deals_enabled(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["auto_complete_deals"]["enabled"] = not config["playerok"]["auto_complete_deals"]["enabled"]
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="other"), state)


@router.callback_query(F.data == "switch_custom_commands_enabled")
async def callback_switch_custom_commands_enabled(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["custom_commands"]["enabled"] = not config["playerok"]["custom_commands"]["enabled"]
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="other"), state)


@router.callback_query(F.data == "switch_auto_deliveries_enabled")
async def callback_switch_auto_deliveries_enabled(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["auto_deliveries"]["enabled"] = not config["playerok"]["auto_deliveries"]["enabled"]
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="other"), state)


@router.callback_query(F.data == "switch_watermark_enabled")
async def callback_switch_watermark_enabled(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["watermark"]["enabled"] = not config["playerok"]["watermark"]["enabled"]
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="other"), state)


@router.callback_query(F.data == "switch_tg_logging_enabled")
async def callback_switch_tg_logging_enabled(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["tg_logging"]["enabled"] = not config["playerok"]["tg_logging"]["enabled"]
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="logger"), state)


@router.callback_query(F.data == "switch_tg_logging_event_new_user_message")
async def callback_switch_tg_logging_event_new_user_message(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["tg_logging"]["events"]["new_user_message"] = not config["playerok"]["tg_logging"]["events"]["new_user_message"]
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="logger"), state)


@router.callback_query(F.data == "switch_tg_logging_event_new_system_message")
async def callback_switch_tg_logging_event_new_system_message(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["tg_logging"]["events"]["new_system_message"] = not config["playerok"]["tg_logging"]["events"]["new_system_message"]
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="logger"), state)


@router.callback_query(F.data == "switch_tg_logging_event_new_deal")
async def callback_switch_tg_logging_event_new_deal(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["tg_logging"]["events"]["new_deal"] = not config["playerok"]["tg_logging"]["events"]["new_deal"]
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="logger"), state)


@router.callback_query(F.data == "switch_tg_logging_event_new_review")
async def callback_switch_tg_logging_event_new_review(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["tg_logging"]["events"]["new_review"] = not config["playerok"]["tg_logging"]["events"]["new_review"]
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="logger"), state)


@router.callback_query(F.data == "switch_tg_logging_event_new_problem")
async def callback_switch_tg_logging_event_new_problem(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["tg_logging"]["events"]["new_problem"] = not config["playerok"]["tg_logging"]["events"]["new_problem"]
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="logger"), state)


@router.callback_query(F.data == "switch_tg_logging_event_deal_status_changed")
async def callback_switch_tg_logging_event_deal_status_changed(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["tg_logging"]["events"]["deal_status_changed"] = not config["playerok"]["tg_logging"]["events"]["deal_status_changed"]
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="logger"), state)


@router.callback_query(F.data == "switch_message_enabled")
async def callback_switch_message_enabled(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        message_id = data.get("message_id")
        if not message_id:
            raise Exception("❌ ID сообщения не был найден, повторите процесс с самого начала")
        
        messages = sett.get("messages")
        messages[message_id]["enabled"] = not messages[message_id]["enabled"]
        sett.set("messages", messages)
        
        return await callback_message_page(callback, calls.MessagePage(message_id=message_id), state)
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_mess_float_text(e), 
            reply_markup=templ.back_kb(calls.MessagesPagination(page=last_page).pack())
        )


@router.callback_query(F.data == "switch_module_enabled")
async def callback_switch_module_enabled(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        module_uuid = data.get("module_uuid")
        if not module_uuid:
            raise Exception("❌ UUID модуля не был найден, повторите процесс с самого начала")
        module = get_module_by_uuid(module_uuid)
        if not module:
            raise Exception("❌ Модуль с этим UUID не был найден, повторите процесс с самого начала")

        await disable_module(module_uuid) if module.enabled else await enable_module(module_uuid)
        return await callback_module_page(callback, calls.ModulePage(uuid=module_uuid), state)
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.module_page_float_text(e), 
            reply_markup=templ.back_kb(calls.ModulesPagination(page=last_page).pack())
        )