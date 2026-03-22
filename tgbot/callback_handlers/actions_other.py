from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from pathlib import Path
from collections import deque
import shutil
import os

from playerokapi.enums import ItemDealStatuses
from settings import Settings as sett

from .. import templates as templ
from .. import callback_datas as calls
from .. import states
from ..helpful import throw_float_message
from .navigation import *
from .pagination import *
from .page import callback_module_page


router = Router()


@router.callback_query(F.data == "destroy")
async def callback_back(callback: CallbackQuery):
    await callback.message.delete()


@router.callback_query(calls.DeleteIncludedRestoreItem.filter())
async def callback_delete_included_restore_item(callback: CallbackQuery, callback_data: calls.DeleteIncludedRestoreItem, state: FSMContext):
    try:
        await state.set_state(None)
        
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        
        index = callback_data.index
        if index is None:
            return await callback_included_restore_items_pagination(
                callback,
                calls.IncludedRestoreItemsPagination(page=last_page),
                state
            )
        
        auto_restore_items = sett.get("auto_restore_items")
        auto_restore_items["included"].pop(index)
        sett.set("auto_restore_items", auto_restore_items)
        
        return await callback_included_restore_items_pagination(
            callback,
            calls.IncludedRestoreItemsPagination(page=last_page),
            state
        )
    except Exception as e:
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
        
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        
        index = callback_data.index
        if index is None:
            return await callback_excluded_restore_items_pagination(
                callback,
                calls.ExcludedRestoreItemsPagination(page=last_page),
                state
            )
        
        auto_restore_items = sett.get("auto_restore_items")
        auto_restore_items["excluded"].pop(index)
        sett.set("auto_restore_items", auto_restore_items)
        
        return await callback_excluded_restore_items_pagination(
            callback,
            calls.ExcludedRestoreItemsPagination(page=last_page),
            state
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.settings_restore_included_float_text(e),
            reply_markup=templ.back_kb(calls.IncludedRestoreItemsPagination(page=last_page).pack())
        )


@router.callback_query(calls.DeleteIncludedCompleteDeal.filter())
async def callback_delete_included_complete_deal(callback: CallbackQuery, callback_data: calls.DeleteIncludedCompleteDeal, state: FSMContext):
    try:
        await state.set_state(None)
        
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        
        index = callback_data.index
        if index is None:
            return await callback_included_complete_deals_pagination(
                callback,
                calls.IncludedRestoreItemsPagination(page=last_page),
                state
            )
        
        auto_complete_deals = sett.get("auto_complete_deals")
        auto_complete_deals["included"].pop(index)
        sett.set("auto_complete_deals", auto_complete_deals)
        
        return await callback_included_complete_deals_pagination(
            callback,
            calls.IncludedCompleteDealsPagination(page=last_page),
            state
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.settings_complete_included_float_text(e),
            reply_markup=templ.back_kb(calls.IncludedCompleteDealsPagination(page=last_page).pack())
        )


@router.callback_query(calls.DeleteExcludedCompleteDeal.filter())
async def callback_delete_excluded_complete_deal(callback: CallbackQuery, callback_data: calls.DeleteExcludedCompleteDeal, state: FSMContext):
    try:
        await state.set_state(None)
        
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        
        index = callback_data.index
        if index is None:
            return await callback_excluded_complete_deals_pagination(
                callback,
                calls.ExcludedRestoreItemsPagination(page=last_page),
                state
            )
        
        auto_complete_deals = sett.get("auto_complete_deals")
        auto_complete_deals["excluded"].pop(index)
        sett.set("auto_complete_deals", auto_complete_deals)
        
        return await callback_excluded_complete_deals_pagination(
            callback,
            calls.ExcludedCompleteDealsPagination(page=last_page),
            state
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.settings_complete_included_float_text(e),
            reply_markup=templ.back_kb(calls.IncludedCompleteDealsPagination(page=last_page).pack())
        )


@router.callback_query(calls.DeleteIncludedBumpItem.filter())
async def callback_delete_included_bump_item(callback: CallbackQuery, callback_data: calls.DeleteIncludedBumpItem, state: FSMContext):
    try:
        await state.set_state(None)
        
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        
        index = callback_data.index
        if index is None:
            return await callback_included_bump_items_pagination(
                callback,
                calls.IncludedBumpItemsPagination(page=last_page),
                state
            )
        
        auto_bump_items = sett.get("auto_bump_items")
        auto_bump_items["included"].pop(index)
        sett.set("auto_bump_items", auto_bump_items)
        
        return await callback_included_bump_items_pagination(
            callback,
            calls.IncludedBumpItemsPagination(page=last_page),
            state
        )
    except Exception as e:
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
        
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        
        index = callback_data.index
        if index is None:
            return await callback_excluded_bump_items_pagination(
                callback,
                calls.ExcludedBumpItemsPagination(page=last_page),
                state
            )
        
        auto_bump_items = sett.get("auto_bump_items")
        auto_bump_items["excluded"].pop(index)
        sett.set("auto_bump_items", auto_bump_items)
        
        return await callback_excluded_bump_items_pagination(
            callback,
            calls.ExcludedBumpItemsPagination(page=last_page),
            state
        )
    except Exception as e:
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
        await state.set_state(states.ActionsStates.waiting_for_message_content)
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.do_action_text(f"💬 Введите <b>сообщение</b> для отправки <b>{username}</b>:"),
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
            text=templ.do_action_text(f'📦✔️ Подтвердите <b>возврат</b> <a href="https://playerok.com/deal/{deal_id}">сделки</a>:'),
            reply_markup=templ.confirm_kb(confirm_cb="refund_deal", cancel_cb="destroy"),
            callback=callback,
            send=True
        )
    if do == "complete":
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.do_action_text(f'☑️✔️ Подтвердите <b>выполнение</b> <a href="https://playerok.com/deal/{deal_id}">сделки</a>:'),
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
    
    return await callback_settings_navigation(
        callback,
        calls.SettingsNavigation(to="withdrawal"),
        state
    )


@router.callback_query(calls.SelectSbpBank.filter())
async def callback_select_sbp_bank(callback: CallbackQuery, callback_data: calls.SelectSbpBank, state: FSMContext):
    await state.set_state(states.SettingsStates.waiting_for_sbp_bank_phone_number)
    
    bank_id = callback_data.id
    await state.update_data(sbp_bank_id=bank_id)
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.settings_withdrawal_sbp_float_text(f"📲 Введите <b>номер телефона</b>, на который нужно будет совершать вывод:"),
        reply_markup=templ.back_kb(calls.SettingsNavigation(to="withdrawal").pack())
    )


@router.callback_query(calls.SetNewDelivPiece.filter())
async def callback_set_new_deliv_piece(callback: CallbackQuery, callback_data: calls.SetNewDelivPiece, state: FSMContext):
    await state.set_state(None)

    data = await state.get_data()
    last_page = data.get("last_page", 0)
    
    value = callback_data.val
    await state.update_data(new_auto_delivery_piece=value)
    
    if value:
        await state.set_state(states.AutoDeliveriesStates.waiting_for_new_auto_delivery_goods)
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.settings_new_deliv_float_text(
                f"📦 Отправьте <b>товары</b> для поштучной выдачи (1 строка = 1 товар, можно прислать .txt файл с товарами):"
            ),
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack()),
            callback=callback
        )
    else:
        await state.set_state(states.AutoDeliveriesStates.waiting_for_new_auto_delivery_message)
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.settings_new_deliv_float_text(
                f"💬 Введите <b>сообщение авто-выдачи</b>, которое будет отправляться после покупки товара:"
            ),
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack()),
            callback=callback
        )


@router.callback_query(F.data == "refund_deal")
async def callback_refund_deal(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    
    from plbot.playerokbot import get_playerok_bot
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
    await state.set_state(None)
    
    from plbot.playerokbot import get_playerok_bot
    
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
        await state.set_state(None)
        
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.events_float_text(f"⬆️ Идёт <b>поднятие предметов</b>, ожидайте (см. консоль)..."),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="events").pack())
        )

        from plbot.playerokbot import get_playerok_bot
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
        await state.set_state(None)
        
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.events_float_text(f"💸 Создаю <b>транзакцию на вывод средств</b>, ожидайте (см. консоль)..."),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="events").pack())
        )

        from plbot.playerokbot import get_playerok_bot
        success = get_playerok_bot().request_withdrawal()
        
        if success:
            await throw_float_message(
                state=state,
                message=callback.message,
                text=templ.events_float_text(f"✅ <b>Транзакция на вывод средств</b> была успешно создана"),
                reply_markup=templ.back_kb(calls.MenuNavigation(to="events").pack())
            )
        else:
            await throw_float_message(
                state=state,
                message=callback.message,
                text=templ.events_float_text(f"❌ Не удалось создать <b>транзакцию на вывод средств</b> (см. консоль на наличие ошибок)"),
                reply_markup=templ.back_kb(calls.MenuNavigation(to="events").pack())
            )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.events_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="events").pack())
        )


@router.callback_query(F.data == "clean_fp_proxy")
async def callback_clean_fp_proxy(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    
    config = sett.get("config")
    config["playerok"]["api"]["proxy"] = ""
    sett.set("config", config)
    
    return await callback_settings_navigation(
        callback,
        calls.SettingsNavigation(to="conn"),
        state
    )


@router.callback_query(F.data == "clean_tg_proxy")
async def callback_clean_tg_proxy(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    
    config = sett.get("config")
    config["telegram"]["api"]["proxy"] = ""
    sett.set("config", config)
    
    return await callback_settings_navigation(
        callback,
        calls.SettingsNavigation(to="conn"),
        state
    )


@router.callback_query(F.data == "clean_tg_logging_chat_id")
async def callback_clean_tg_logging_chat_id(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    
    config = sett.get("config")
    config["playerok"]["tg_logging"]["chat_id"] = ""
    sett.set("config", config)
    
    return await callback_settings_navigation(
        callback,
        calls.SettingsNavigation(to="logger"),
        state
    )


@router.callback_query(F.data == "send_new_included_restore_items_keyphrases_file")
async def callback_send_new_included_restore_items_keyphrases_file(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    
    await state.set_state(states.RestoreItemsStates.waiting_for_new_included_restore_items_keyphrases_file)
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.settings_new_restore_included_float_text(
            "📄 Отправьте <b>.txt</b> файл с <b>ключевыми фразами</b>, по одной записи в строке "
            "(для каждого товара указываются через запятую, например, \"samp аккаунт, со всеми данными\")"
        ),
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
        text=templ.settings_new_restore_excluded_float_text(
            "📄 Отправьте <b>.txt</b> файл с <b>ключевыми фразами</b>, по одной записи в строке "
            "(для каждого товара указываются через запятую, например, \"samp аккаунт, со всеми данными\")"
        ),
        reply_markup=templ.back_kb(calls.ExcludedRestoreItemsPagination(page=last_page).pack())
    )


@router.callback_query(F.data == "send_new_included_complete_deals_keyphrases_file")
async def callback_send_new_included_complete_deals_keyphrases_file(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    
    await state.set_state(states.CompleteDealsStates.waiting_for_new_included_complete_deals_keyphrases_file)
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.settings_new_complete_included_float_text(
            "📄 Отправьте <b>.txt</b> файл с <b>ключевыми фразами</b>, по одной записи в строке "
            "(для каждого товара указываются через запятую, например, \"samp аккаунт, со всеми данными\")"
        ),
        reply_markup=templ.back_kb(calls.IncludedCompleteDealsPagination(page=last_page).pack())
    )


@router.callback_query(F.data == "send_new_excluded_complete_deals_keyphrases_file")
async def callback_send_new_excluded_complete_deals_keyphrases_file(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    
    await state.set_state(states.CompleteDealsStates.waiting_for_new_excluded_complete_deals_keyphrases_file)
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.settings_new_complete_excluded_float_text(
            "📄 Отправьте <b>.txt</b> файл с <b>ключевыми фразами</b>, по одной записи в строке "
            "(для каждого товара указываются через запятую, например, \"samp аккаунт, со всеми данными\")"
        ),
        reply_markup=templ.back_kb(calls.ExcludedCompleteDealsPagination(page=last_page).pack())
    )


@router.callback_query(F.data == "send_new_included_bump_items_keyphrases_file")
async def callback_send_new_included_bump_items_keyphrases_file(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    
    await state.set_state(states.BumpItemsStates.waiting_for_new_included_bump_items_keyphrases_file)
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.settings_new_bump_included_float_text(
            "📄 Отправьте <b>.txt</b> файл с <b>ключевыми фразами</b>, по одной записи в строке "
            "(для каждого товара указываются через запятую, например, \"samp аккаунт, со всеми данными\")"
        ),
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
        text=templ.settings_new_bump_excluded_float_text(
            "📄 Отправьте <b>.txt</b> файл с <b>ключевыми фразами</b>, по одной записи в строке "
            "(для каждого товара указываются через запятую, например, \"samp аккаунт, со всеми данными\")"
        ),
        reply_markup=templ.back_kb(calls.ExcludedBumpItemsPagination(page=last_page).pack())
    )


@router.callback_query(F.data == "add_new_custom_command")
async def callback_add_new_custom_command(callback: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(None)
        
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        
        custom_commands = sett.get("custom_commands")
        command = data.get("new_custom_command")
        answer = data.get("new_custom_command_answer")
        
        if not all((command, answer)):
            return await callback_custom_commands_pagination(
                callback,
                calls.CustomCommandsPagination(page=last_page),
                state
            )

        custom_commands[command] = answer.splitlines()
        sett.set("custom_commands", custom_commands)
        
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.settings_new_comm_float_text(f"✅ <b>Команда</b> <code>{command}</code> была успешно добавлена"),
            reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack())
        )
    except Exception as e:
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
        last_page = data.get("last_page", 0)
        
        command = data.get("custom_command")
        if not command:
            return await callback_custom_commands_pagination(
                callback,
                calls.CustomCommandsPagination(page=last_page),
                state
            )
        
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.settings_comm_page_float_text(f"🗑️ Подтвердите <b>удаление команды</b> <code>{command}</code>"),
            reply_markup=templ.confirm_kb(
                confirm_cb="delete_custom_command", 
                cancel_cb=calls.CustomCommandPage(command=command).pack()
            )
        )
    except Exception as e:
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

        command = data.get("custom_command")
        if not command:
            return await callback_custom_commands_pagination(
                callback,
                calls.CustomCommandsPagination(page=last_page),
                state
            )
        
        custom_commands = sett.get("custom_commands")
        del custom_commands[command]
        sett.set("custom_commands", custom_commands)
        
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.settings_comm_page_float_text(f"✅ <b>Команда</b> <code>{command}</code> была удалена"),
            reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack())
        )
    except Exception as e:
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
        
        keyphrases = data.get("new_auto_delivery_keyphrases")
        piece = data.get("new_auto_delivery_piece")
        message = data.get("new_auto_delivery_message")
        goods = data.get("new_auto_delivery_goods")
        
        if (
            not keyphrases 
            or piece is None
            or (piece is True and not goods)
            or (piece is False and not message)
        ):
            return await callback_auto_deliveries_pagination(
                callback,
                calls.AutoDeliveriesPagination(page=last_page),
                state
            )
        
        auto_deliveries = sett.get("auto_deliveries")
        auto_deliveries.append({
            "piece": piece,
            "keyphrases": keyphrases, 
            "message": message.splitlines() if message and not piece else "",
            "goods": goods if goods and piece else [],
        })
        sett.set("auto_deliveries", auto_deliveries)
        
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.settings_new_deliv_float_text(f"✅ <b>Авто-выдача</b> была успешно добавлена"),
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
        )
    except Exception as e:
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
        last_page = data.get("last_page", 0)
        index = data.get("auto_delivery_index")
        
        if index is None:
            return await callback_auto_deliveries_pagination(
                callback,
                calls.AutoDeliveriesPagination(page=last_page),
                state
            )
       
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.settings_deliv_page_float_text(
                "🗑️ Подтвердите <b>удаление авто-выдачи</b>:"
            ),
            reply_markup=templ.confirm_kb(
                confirm_cb="delete_auto_delivery", 
                cancel_cb=calls.AutoDeliveryPage(index=index).pack()
            )
        )
    except Exception as e:
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
        last_page = data.get("last_page", 0)
        
        index = data.get("auto_delivery_index")
        if index is None:
            return await callback_auto_deliveries_pagination(
                callback,
                calls.AutoDeliveriesPagination(page=last_page),
                state
            )
        
        auto_deliveries = sett.get("auto_deliveries")
        del auto_deliveries[index]
        sett.set("auto_deliveries", auto_deliveries)
        
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.settings_deliv_page_float_text("✅ <b>Авто-выдача</b> была удалена"),
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.settings_deliv_page_float_text(e),
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
        )


@router.callback_query(calls.DeleteDelivGood.filter())
async def callback_delete_deliv_good(callback: CallbackQuery, callback_data: calls.DeleteDelivGood, state: FSMContext):
    try:
        await state.set_state(None)
        index = callback_data.index
        
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        deliv_index = data.get("auto_delivery_index")
        
        if deliv_index is None:
            return await callback_auto_deliveries_pagination(
                callback,
                calls.AutoDeliveriesPagination(page=last_page),
                state
            )
        
        auto_deliveries = sett.get("auto_deliveries")
        auto_deliveries[deliv_index]["goods"].pop(index)
        sett.set("auto_deliveries", auto_deliveries)
        
        return await callback_deliv_goods_pagination(
            callback,
            calls.DelivGoodsPagination(page=last_page),
            state
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.settings_deliv_goods_float_text(e),
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
        )


@router.callback_query(F.data == "reload_module")
async def callback_reload_module(callback: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(None)
        
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        uuid = data.get("module_uuid")
        
        if not uuid:
            return await callback_modules_pagination(
                callback, 
                calls.ModulePage(page=last_page), 
                state
            )
        
        from core.modules import reload_module
        await reload_module(uuid)
        
        return await callback_module_page(
            callback, 
            calls.ModulePage(uuid=uuid), 
            state
        )
    except Exception as e:
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.module_page_float_text(e), 
            reply_markup=templ.back_kb(calls.ModulesPagination(page=last_page).pack())
        )


@router.callback_query(F.data == "select_logs_file_lines")
async def callback_select_logs_file_lines(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.logs_float_text("Выберите объём файла:"),
        reply_markup=templ.logs_file_lines_kb()
    )


@router.callback_query(calls.SendLogsFile.filter())
async def callback_send_logs_file(callback: CallbackQuery, callback_data: calls.SendLogsFile, state: FSMContext):
    await state.set_state(None)
    
    lines = callback_data.lines
    
    try:
        src_dir = Path(__file__).resolve().parents[2]
        logs_file = os.path.join(src_dir, "logs", "latest.log")
        txt_file = os.path.join(src_dir, "logs", "Лог работы.txt")
        
        if lines > 0:
            with open(logs_file, 'r', encoding='utf-8') as f:
                last_lines = deque(f, lines)
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.writelines(last_lines)
        else:
            shutil.copy(logs_file, txt_file)
        
        await callback.message.answer_document(
            document=FSInputFile(txt_file),
            reply_markup=templ.destroy_kb()
        )
        try:
            await callback.bot.answer_callback_query(callback.id, cache_time=0)
        except:
            pass

        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.logs_text(),
            reply_markup=templ.logs_kb()
        )
    finally:
        try:
            os.remove(txt_file)
        except:
            pass