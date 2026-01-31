from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from playerokapi.enums import ItemDealStatuses
from settings import Settings as sett

from .. import templates as templ
from .. import callback_datas as calls
from .. import states
from ..helpful import throw_float_message
from .navigation import *
from .pagination import (
    callback_included_restore_items_pagination, 
    callback_excluded_restore_items_pagination,
    callback_included_bump_items_pagination,
    callback_excluded_bump_items_pagination
)
from .page import callback_module_page


router = Router()


@router.callback_query(F.data == "destroy")
async def callback_back(callback: CallbackQuery):
    await callback.message.delete()


@router.callback_query(calls.DeleteIncludedRestoreItem.filter())
async def callback_delete_included_restore_item(callback: CallbackQuery, callback_data: calls.DeleteIncludedRestoreItem, state: FSMContext):
    try:
        await state.set_state(None)
        index = callback_data.index
        if index is None:
            raise Exception("❌ Включенный предмет не был найден, повторите процесс с самого начала")
        
        auto_restore_items = sett.get("auto_restore_items")
        auto_restore_items["included"].pop(index)
        sett.set("auto_restore_items", auto_restore_items)

        data = await state.get_data()
        last_page = data.get("last_page", 0)
        return await callback_included_restore_items_pagination(callback, calls.IncludedRestoreItemsPagination(page=last_page), state)
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_restore_included_float_text(e), 
            reply_markup=templ.back_kb(calls.IncludedRestoreItemsPagination(page=last_page).pack())
        )


@router.callback_query(calls.DeleteExcludedRestoreItem.filter())
async def callback_delete_excluded_restore_item(callback: CallbackQuery, callback_data: calls.DeleteExcludedRestoreItem, state: FSMContext):
    try:
        await state.set_state(None)
        index = callback_data.index
        if index is None:
            raise Exception("❌ Исключенный предмет не был найден, повторите процесс с самого начала")
        
        auto_restore_items = sett.get("auto_restore_items")
        auto_restore_items["excluded"].pop(index)
        sett.set("auto_restore_items", auto_restore_items)

        data = await state.get_data()
        last_page = data.get("last_page", 0)
        return await callback_excluded_restore_items_pagination(callback, calls.ExcludedRestoreItemsPagination(page=last_page), state)
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_restore_included_float_text(e), 
            reply_markup=templ.back_kb(calls.IncludedRestoreItemsPagination(page=last_page).pack())
        )


@router.callback_query(calls.DeleteIncludedBumpItem.filter())
async def callback_delete_included_bump_item(callback: CallbackQuery, callback_data: calls.DeleteIncludedBumpItem, state: FSMContext):
    try:
        await state.set_state(None)
        index = callback_data.index
        if index is None:
            raise Exception("❌ Не удалось найти предмет, повторите процесс с начала")
        
        auto_bump_items = sett.get("auto_bump_items")
        auto_bump_items["included"].pop(index)
        sett.set("auto_bump_items", auto_bump_items)

        data = await state.get_data()
        last_page = data.get("last_page", 0)
        return await callback_included_bump_items_pagination(callback, calls.IncludedBumpItemsPagination(page=last_page), state)
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_bump_included_float_text(e), 
            reply_markup=templ.back_kb(calls.IncludedBumpItemsPagination(page=last_page).pack())
        )


@router.callback_query(calls.DeleteExcludedBumpItem.filter())
async def callback_delete_excluded_bump_item(callback: CallbackQuery, callback_data: calls.DeleteExcludedBumpItem, state: FSMContext):
    try:
        await state.set_state(None)
        index = callback_data.index
        if index is None:
            raise Exception("❌ Не удалось найти предмет, повторите процесс с начала")
        
        auto_bump_items = sett.get("auto_bump_items")
        auto_bump_items["excluded"].pop(index)
        sett.set("auto_bump_items", auto_bump_items)

        data = await state.get_data()
        last_page = data.get("last_page", 0)
        return await callback_excluded_bump_items_pagination(callback, calls.ExcludedBumpItemsPagination(page=last_page), state)
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_bump_excluded_float_text(e), 
            reply_markup=templ.back_kb(calls.ExcludedBumpItemsPagination(page=last_page).pack())
        )


@router.callback_query(calls.RememberUsername.filter())
async def callback_remember_username(callback: CallbackQuery, callback_data: calls.RememberUsername, state: FSMContext):
    await state.set_state(None)
    username = callback_data.name
    do = callback_data.do
    await state.update_data(username=username)
    if do == "send_mess":
        await state.set_state(states.ActionsStates.waiting_for_message_text)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.do_action_text(f"💬 Введите <b>сообщение</b> для отправки <b>{username}</b> ↓"), 
            reply_markup=templ.destroy_kb(),
            callback=callback,
            send=True
        )


@router.callback_query(calls.RememberDealId.filter())
async def callback_remember_deal_id(callback: CallbackQuery, callback_data: calls.RememberDealId, state: FSMContext):
    await state.set_state(None)
    deal_id = callback_data.de_id
    do = callback_data.do
    await state.update_data(deal_id=deal_id)
    if do == "refund":
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.do_action_text(f'📦✔️ Подтвердите <b>возврат</b> <a href="https://playerok.com/deal/{deal_id}">сделки</a> ↓'), 
            reply_markup=templ.confirm_kb(confirm_cb="refund_deal", cancel_cb="destroy"),
            callback=callback,
            send=True
        )
    if do == "complete":
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.do_action_text(f'☑️✔️ Подтвердите <b>выполнение</b> <a href="https://playerok.com/deal/{deal_id}">сделки</a> ↓'), 
            reply_markup=templ.confirm_kb(confirm_cb="complete_deal", cancel_cb="destroy"),
            callback=callback,
            send=True
        )


@router.callback_query(calls.SelectBankCard.filter())
async def callback_select_bank_card(callback: CallbackQuery, callback_data: calls.SelectBankCard, state: FSMContext):
    await state.set_state(None)
    card_id = callback_data.id

    config = sett.get("config")
    config["playerok"]["auto_withdrawal"]["credentials_type"] = "card"
    config["playerok"]["auto_withdrawal"]["card_id"] = card_id
    sett.set("config", config)
    
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="withdrawal"), state)


@router.callback_query(calls.SelectSbpBank.filter())
async def callback_select_sbp_bank(callback: CallbackQuery, callback_data: calls.SelectSbpBank, state: FSMContext):
    await state.set_state(None)
    bank_id = callback_data.id

    await state.update_data(sbp_bank_id=bank_id)
    await state.set_state(states.SettingsStates.waiting_for_sbp_bank_phone_number)
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_withdrawal_sbp_float_text(f"📲 Введите <b>номер телефона</b>, на который нужно будет совершать вывод:"), 
        reply_markup=templ.back_kb(calls.SettingsNavigation(to="withdrawal").pack())
    )
        

@router.callback_query(F.data == "refund_deal")
async def callback_refund_deal(callback: CallbackQuery, state: FSMContext):
    from plbot.playerokbot import get_playerok_bot
    await state.set_state(None)
    plbot = get_playerok_bot()
    data = await state.get_data()
    deal_id = data.get("deal_id")
    plbot.playerok_account.update_deal(deal_id, ItemDealStatuses.ROLLED_BACK)
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.do_action_text(f"✅ По сделке <b>https://playerok.com/deal/{deal_id}</b> был оформлен возврат"), 
        reply_markup=templ.destroy_kb()
    )
        

@router.callback_query(F.data == "complete_deal")
async def callback_complete_deal(callback: CallbackQuery, state: FSMContext):
    from plbot.playerokbot import get_playerok_bot
    await state.set_state(None)
    plbot = get_playerok_bot()
    data = await state.get_data()
    deal_id = data.get("deal_id")
    plbot.playerok_account.update_deal(deal_id, ItemDealStatuses.SENT)
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.do_action_text(f"✅ Сделка <b>https://playerok.com/deal/{deal_id}</b> была помечена вами, как выполненная"), 
        reply_markup=templ.destroy_kb()
    )


@router.callback_query(F.data == "bump_items")
async def callback_bump_items(callback: CallbackQuery, state: FSMContext):
    try:
        from plbot.playerokbot import get_playerok_bot
        await state.set_state(None)
        
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.events_float_text(f"⬆️ Идёт <b>поднятие предметов</b>, ожидайте (см. консоль)..."), 
            reply_markup=templ.back_kb(calls.MenuNavigation(to="events").pack())
        )

        get_playerok_bot().bump_items()
        
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.events_float_text(f"⬆️✅ <b>Предметы</b> были успешно подняты"), 
            reply_markup=templ.back_kb(calls.MenuNavigation(to="events").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.events_float_text(e), 
            reply_markup=templ.back_kb(calls.MenuNavigation(to="events").pack())
        )


@router.callback_query(F.data == "request_withdrawal")
async def callback_request_withdrawal(callback: CallbackQuery, state: FSMContext):
    try:
        from plbot.playerokbot import get_playerok_bot
        await state.set_state(None)
        
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.events_float_text(f"💸 Создаю <b>транзакцию на вывод средств</b>, ожидайте (см. консоль)..."), 
            reply_markup=templ.back_kb(calls.MenuNavigation(to="events").pack())
        )

        success = get_playerok_bot().request_withdrawal()
        
        if success:
            await throw_float_message(
                state=state, 
                message=callback.message, 
                text=templ.events_float_text(f"💸✅ <b>Транзакция на вывод средств</b> была успешно создана"), 
                reply_markup=templ.back_kb(calls.MenuNavigation(to="events").pack())
            )
        else:
            await throw_float_message(
                state=state, 
                message=callback.message, 
                text=templ.events_float_text(f"💸❌ Не удалось создать <b>транзакцию на вывод средств</b> (см. консоль на наличие ошибок)"), 
                reply_markup=templ.back_kb(calls.MenuNavigation(to="events").pack())
            )
    except Exception as e:
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.events_float_text(e), 
            reply_markup=templ.back_kb(calls.MenuNavigation(to="events").pack())
        )


@router.callback_query(F.data == "clean_proxy")
async def callback_clean_proxy(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    config = sett.get("config")
    proxy = config["playerok"]["api"]["proxy"] = ""
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="conn"), state)


@router.callback_query(F.data == "clean_tg_logging_chat_id")
async def callback_clean_tg_logging_chat_id(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    config = sett.get("config")
    config["playerok"]["tg_logging"]["chat_id"] = ""
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="logger"), state)


@router.callback_query(F.data == "send_new_included_restore_items_keyphrases_file")
async def callback_send_new_included_restore_items_keyphrases_file(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    await state.set_state(states.RestoreItemsStates.waiting_for_new_included_restore_items_keyphrases_file)
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_new_restore_included_float_text(f"📄 Отправьте <b>.txt</b> файл с <b>ключевыми фразами</b>, по одной записи в строке (для каждого товара указываются через запятую, например, \"samp аккаунт, со всеми данными\")"), 
        reply_markup=templ.back_kb(calls.IncludedRestoreItemsPagination(page=last_page).pack())
    )


@router.callback_query(F.data == "send_new_excluded_restore_items_keyphrases_file")
async def callback_send_new_excluded_restore_items_keyphrases_file(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    await state.set_state(states.RestoreItemsStates.waiting_for_new_excluded_restore_items_keyphrases_file)
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_new_restore_excluded_float_text(f"📄 Отправьте <b>.txt</b> файл с <b>ключевыми фразами</b>, по одной записи в строке (для каждого товара указываются через запятую, например, \"samp аккаунт, со всеми данными\")"), 
        reply_markup=templ.back_kb(calls.ExcludedRestoreItemsPagination(page=last_page).pack())
    )


@router.callback_query(F.data == "send_new_included_bump_items_keyphrases_file")
async def callback_send_new_included_bump_items_keyphrases_file(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    await state.set_state(states.BumpItemsStates.waiting_for_new_included_bump_items_keyphrases_file)
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_new_bump_included_float_text(f"📄 Отправьте <b>.txt</b> файл с <b>ключевыми фразами</b>, по одной записи в строке (для каждого товара указываются через запятую, например, \"samp аккаунт, со всеми данными\")"), 
        reply_markup=templ.back_kb(calls.IncludedBumpItemsPagination(page=last_page).pack())
    )


@router.callback_query(F.data == "send_new_excluded_bump_items_keyphrases_file")
async def callback_send_new_excluded_bump_items_keyphrases_file(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    await state.set_state(states.BumpItemsStates.waiting_for_new_excluded_bump_items_keyphrases_file)
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_new_bump_excluded_float_text(f"📄 Отправьте <b>.txt</b> файл с <b>ключевыми фразами</b>, по одной записи в строке (для каждого товара указываются через запятую, например, \"samp аккаунт, со всеми данными\")"), 
        reply_markup=templ.back_kb(calls.ExcludedBumpItemsPagination(page=last_page).pack())
    )


@router.callback_query(F.data == "add_new_custom_command")
async def callback_add_new_custom_command(callback: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(None)
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        custom_commands = sett.get("custom_commands")
        new_custom_command = data.get("new_custom_command")
        new_custom_command_answer = data.get("new_custom_command_answer")
        if not new_custom_command:
            raise Exception("❌ Новая команда не была найдена, повторите процесс с самого начала")
        if not new_custom_command_answer:
            raise Exception("❌ Ответ на новую команду не был найден, повторите процесс с самого начала")

        custom_commands[new_custom_command] = new_custom_command_answer.splitlines()
        sett.set("custom_commands", custom_commands)
        last_page = data.get("last_page", 0)
        
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_new_comm_float_text(f"✅ <b>Команда</b> <code>{new_custom_command}</code> была добавлена"), 
            reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack())
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_new_comm_float_text(e), 
            reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack())
        )


@router.callback_query(F.data == "confirm_deleting_custom_command")
async def callback_confirm_deleting_custom_command(callback: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(None)
        data = await state.get_data()
        custom_command = data.get("custom_command")
        if not custom_command:
            raise Exception("❌ Команда не была найдена, повторите процесс с самого начала")
        
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_comm_page_float_text(f"🗑️ Подтвердите <b>удаление команды</b> <code>{custom_command}</code>"), 
            reply_markup=templ.confirm_kb(confirm_cb="delete_custom_command", cancel_cb=calls.CustomCommandPage(command=custom_command).pack())
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_comm_page_float_text(e), 
            reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack())
        )


@router.callback_query(F.data == "delete_custom_command")
async def callback_delete_custom_command(callback: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(None)
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        custom_commands = sett.get("custom_commands")
        custom_command = data.get("custom_command")
        if not custom_command:
            raise Exception("❌ Команда не была найдена, повторите процесс с самого начала")
        
        del custom_commands[custom_command]
        sett.set("custom_commands", custom_commands)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_comm_page_float_text(f"✅ <b>Команда</b> <code>{custom_command}</code> была удалена"), 
            reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack())
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_comm_page_float_text(e), 
            reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack())
        )


@router.callback_query(F.data == "add_new_auto_delivery")
async def callback_add_new_auto_delivery(callback: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(None)
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        auto_deliveries = sett.get("auto_deliveries")
        new_auto_delivery_keyphrases = data.get("new_auto_delivery_keyphrases")
        new_auto_delivery_message = data.get("new_auto_delivery_message")
        if not new_auto_delivery_keyphrases:
            raise Exception("❌ Ключевые фразы авто-выдачи не были найдены, повторите процесс с самого начала")
        if not new_auto_delivery_message:
            raise Exception("❌ Сообщение авто-выдачи не было найдено, повторите процесс с самого начала")
        
        auto_deliveries.append({"keyphrases": new_auto_delivery_keyphrases, "message": new_auto_delivery_message.splitlines()})
        sett.set("auto_deliveries", auto_deliveries)
        
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_new_deliv_float_text(f"✅ <b>Авто-выдача</b> была добавлена"), 
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_new_deliv_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
        )



@router.callback_query(F.data == "confirm_deleting_auto_delivery")
async def callback_confirm_deleting_auto_delivery(callback: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(None)
        data = await state.get_data()
        auto_delivery_index = data.get("auto_delivery_index")
        if auto_delivery_index is None:
            raise Exception("❌ Авто-выдача не была найдена, повторите процесс с самого начала")
        

        auto_deliveries = sett.get("auto_deliveries")
        auto_delivery_keyphrases = "</code>, <code>".join(auto_deliveries[auto_delivery_index]["keyphrases"]) or "❌ Не задано"
       
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_deliv_page_float_text(f"🗑️ Подтвердите <b>удаление авто-выдачи</b> для ключевых фраз <code>{auto_delivery_keyphrases}</code>"), 
            reply_markup=templ.confirm_kb(confirm_cb="delete_auto_delivery", cancel_cb=calls.AutoDeliveryPage(index=auto_delivery_index).pack())
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_deliv_page_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
        )


@router.callback_query(F.data == "delete_auto_delivery")
async def callback_delete_auto_delivery(callback: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(None)
        data = await state.get_data()
        auto_delivery_index = data.get("auto_delivery_index")
        if auto_delivery_index is None:
            raise Exception("❌ Авто-выдача не была найдена, повторите процесс с самого начала")
        
        auto_deliveries = sett.get("auto_deliveries")
        del auto_deliveries[auto_delivery_index]
        sett.set("auto_deliveries", auto_deliveries)
        last_page = data.get("last_page", 0)
        
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_deliv_page_float_text(f"✅ <b>Авто-выдача</b> была удалена"), 
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_deliv_page_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
        )


@router.callback_query(F.data == "reload_module")
async def callback_reload_module(callback: CallbackQuery, state: FSMContext):
    from core.modules import reload_module
    try:
        await state.set_state(None)
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        module_uuid = data.get("module_uuid")
        if not module_uuid:
            raise Exception("❌ UUID модуля не был найден, повторите процесс с самого начала")
        
        await reload_module(module_uuid)
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