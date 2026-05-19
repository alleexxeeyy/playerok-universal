from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from core.modules import (
    get_module_by_uuid, 
    enable_module, 
    disable_module
)
from settings import Settings as sett

from .. import templates as templ
from .. import callback_datas as calls
from .. import states as states
from ..helpful import throw_float_message
from ..callback_handlers.page import (
    callback_message_page, 
    callback_module_page,
    callback_auto_delivery_page
)
from .navigation import *
from .pagination import *


router = Router()


@router.callback_query(F.data == "switch_auto_restore_items_sold")
async def callback_switch_auto_restore_items_sold(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["auto_restore_items"]["sold"] = not config["playerok"]["auto_restore_items"]["sold"]
    sett.set("config", config)
    
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="restore"), state
    )


@router.callback_query(F.data == "switch_auto_restore_items_expired")
async def callback_switch_auto_restore_items_expired(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["auto_restore_items"]["expired"] = not config["playerok"]["auto_restore_items"]["expired"]
    sett.set("config", config)
    
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="restore"), state
    )


@router.callback_query(F.data == "switch_auto_restore_items_all")
async def callback_switch_auto_restore_items_all(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["auto_restore_items"]["all"] = not config["playerok"]["auto_restore_items"]["all"]
    sett.set("config", config)
    
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="restore"), state
    )


@router.callback_query(F.data == "switch_auto_bump_items_enabled")
async def callback_switch_auto_bump_items_enabled(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["auto_bump_items"]["enabled"] = not config["playerok"]["auto_bump_items"]["enabled"]
    sett.set("config", config)
    
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="bump"), state
    )


@router.callback_query(F.data == "switch_auto_bump_items_all")
async def callback_switch_auto_bump_items_all(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["auto_bump_items"]["all"] = not config["playerok"]["auto_bump_items"]["all"]
    sett.set("config", config)
    
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="bump"), state
    )


@router.callback_query(F.data == "switch_read_chat_enabled")
async def callback_switch_read_chat_enabled(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["read_chat"] = not config["playerok"]["read_chat"]
    sett.set("config", config)
    
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="other"), state
    )


@router.callback_query(F.data == "switch_auto_complete_deals_enabled")
async def callback_switch_auto_complete_deals_enabled(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["auto_complete_deals"]["enabled"] = not config["playerok"]["auto_complete_deals"]["enabled"]
    sett.set("config", config)
    
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="complete"), state
    )


@router.callback_query(F.data == "switch_auto_complete_deals_all")
async def callback_switch_auto_complete_deals_all(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["auto_complete_deals"]["all"] = not config["playerok"]["auto_complete_deals"]["all"]
    sett.set("config", config)
    
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="complete"), state
    )


@router.callback_query(F.data == "switch_auto_delivery_piece")
async def callback_switch_auto_delivery_piece(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    index = data.get("auto_delivery_index", 0)

    auto_deliveries = sett.get("auto_deliveries")
    auto_deliveries[index]["piece"] = not auto_deliveries[index].get("piece", False)
    sett.set("auto_deliveries", auto_deliveries)

    return await callback_auto_delivery_page(
        callback, calls.AutoDeliveryPage(index=index), state
    )


@router.callback_query(F.data == "switch_auto_withdrawal_enabled")
async def callback_switch_auto_withdrawal_enabled(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["auto_withdrawal"]["enabled"] = not config["playerok"]["auto_withdrawal"]["enabled"]
    sett.set("config", config)
    
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="withdrawal"), state
    )


@router.callback_query(F.data == "switch_watermark_enabled")
async def callback_switch_watermark_enabled(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["watermark"]["enabled"] = not config["playerok"]["watermark"]["enabled"]
    sett.set("config", config)
    
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="other"), state
    )


@router.callback_query(F.data == "switch_notifications_enabled")
async def callback_switch_notifications_enabled(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["notifications"]["enabled"] = not config["playerok"]["notifications"]["enabled"]
    sett.set("config", config)
    
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="notifications"), state
    )


@router.callback_query(F.data == "switch_notifications_new_user_message")
async def callback_switch_notifications_new_user_message(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["notifications"]["events"]["new_user_message"] = not config["playerok"]["notifications"]["events"]["new_user_message"]
    sett.set("config", config)
    
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="notifications"), state
    )


@router.callback_query(F.data == "switch_notifications_new_system_message")
async def callback_switch_notifications_new_system_message(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["notifications"]["events"]["new_system_message"] = not config["playerok"]["notifications"]["events"]["new_system_message"]
    sett.set("config", config)
    
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="notifications"), state
    )


@router.callback_query(F.data == "switch_notifications_new_deal")
async def callback_switch_notifications_new_deal(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["notifications"]["events"]["new_deal"] = not config["playerok"]["notifications"]["events"]["new_deal"]
    sett.set("config", config)
    
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="notifications"), state
    )


@router.callback_query(F.data == "switch_notifications_new_review")
async def callback_switch_notifications_new_review(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["notifications"]["events"]["new_review"] = not config["playerok"]["notifications"]["events"]["new_review"]
    sett.set("config", config)
    
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="notifications"), state
    )


@router.callback_query(F.data == "switch_notifications_new_problem")
async def callback_switch_notifications_new_problem(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["notifications"]["events"]["new_problem"] = not config["playerok"]["notifications"]["events"]["new_problem"]
    sett.set("config", config)
    
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="notifications"), state
    )


@router.callback_query(F.data == "switch_notifications_deal_status_changed")
async def callback_switch_notifications_deal_status_changed(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["notifications"]["events"]["deal_status_changed"] = not config["playerok"]["notifications"]["events"]["deal_status_changed"]
    sett.set("config", config)
    
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="notifications"), state
    )


@router.callback_query(F.data == "switch_notifications_item_restored")
async def callback_switch_notifications_item_restored(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["notifications"]["events"]["item_restored"] = not config["playerok"]["notifications"]["events"]["item_restored"]
    sett.set("config", config)
    
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="notifications"), state
    )


@router.callback_query(F.data == "switch_notifications_item_bumped")
async def callback_switch_notifications_item_bumped(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["notifications"]["events"]["item_bumped"] = not config["playerok"]["notifications"]["events"]["item_bumped"]
    sett.set("config", config)
    
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="notifications"), state
    )


@router.callback_query(F.data == "switch_notifications_withdrawal_requested")
async def callback_switch_notifications_withdrawal_requested(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["notifications"]["events"]["withdrawal_requested"] = not config["playerok"]["notifications"]["events"]["withdrawal_requested"]
    sett.set("config", config)
    
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="notifications"), state
    )


@router.callback_query(F.data == "switch_updates_auto_update")
async def callback_switch_updates_auto_update(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["updates"]["auto_update"] = not config["updates"]["auto_update"]
    sett.set("config", config)
    
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="updates"), state
    )


@router.callback_query(F.data == "switch_updates_notify")
async def callback_switch_updates_notify(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["updates"]["notify"] = not config["updates"]["notify"]
    sett.set("config", config)
    
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="updates"), state
    )


@router.callback_query(F.data == "switch_message_enabled")
async def callback_switch_message_enabled(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        
        message_id = data.get("message_id")
        if not message_id:
            return await callback_messages_pagination(
                callback, calls.MessagesPagination(page=last_page), state
            )
        
        messages = sett.get("messages")
        messages[message_id]["enabled"] = not messages[message_id]["enabled"]
        sett.set("messages", messages)
        
        return await callback_message_page(
            callback, calls.MessagePage(message_id=message_id), state
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.mess_float_text(e),
            reply_markup=templ.back_kb(calls.MessagesPagination(page=last_page).pack())
        )


@router.callback_query(F.data == "switch_module_enabled")
async def callback_switch_module_enabled(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        
        module_uuid = data.get("module_uuid")
        module = get_module_by_uuid(module_uuid)
        if not all((module_uuid, module)):
            return await callback_modules_pagination(
                callback, calls.ModulesPagination(page=last_page), state
            )

        if module.enabled:
            await disable_module(module_uuid)
        else:
            await enable_module(module_uuid)
        
        return await callback_module_page(
            callback, calls.ModulePage(uuid=module_uuid), state
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.module_page_float_text(e),
            reply_markup=templ.back_kb(calls.ModulesPagination(page=last_page).pack())
        )