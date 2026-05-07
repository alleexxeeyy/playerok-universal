from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from pathlib import Path
from collections import deque
import shutil
import os

from playerokapi.enums import (
    ItemDealDirections, 
    ItemDealStatuses,
    ItemStatuses,
    TransactionStatuses, 
    TransactionOperations, 
    TransactionProviderIds
)
from settings import Settings as sett

from .. import templates as templ
from .. import callback_datas as calls
from .. import states
from ..helpful import throw_float_message, do_auth
from .navigation import *
from .pagination import *
from .page import *
from .actions_playerok import *

from utils import parse_date


router = Router()


@router.callback_query(F.data == "destroy")
async def callback_destroy(callback: CallbackQuery):
    await callback.message.delete()

@router.callback_query(F.data == "null_answer")
async def callback_null_answer(callback: CallbackQuery):
    await callback.bot.answer_callback_query(callback.id)


@router.callback_query(calls.DeleteSignedUser.filter())
async def callback_delete_signed_user(callback: CallbackQuery, callback_data: calls.DeleteSignedUser, state: FSMContext):
    try:
        await state.set_state(None)
        id = callback_data.id

        data = await state.get_data()
        last_page = data.get("last_page", 0)
        
        config = sett.get("config")
        config["telegram"]["bot"]["signed_users"].remove(id)
        sett.set("config", config)
        
        if callback.from_user.id == id:
            return await do_auth(callback.message, state)
        else:
            return await callback_signed_users_pagination(
                callback, calls.SignedUsersPagination(page=last_page), state
            )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.signed_users_float_text(e),
            reply_markup=templ.back_kb(calls.SignedUsersPagination(page=last_page).pack())
        )

        
@router.callback_query(F.data == "change_password")
async def callback_change_password(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)

    data = await state.get_data()
    last_page = data.get("last_page", 0)
    new_password = data.get("new_password")
    
    config = sett.get("config")
    config["telegram"]["bot"]["password"] = new_password
    config["telegram"]["bot"]["signed_users"] = [callback.from_user.id]
    sett.set("config", config)
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.signed_users_float_text(f"✅ Пароль <b>успешно изменён</b>"),
        reply_markup=templ.back_kb(calls.SignedUsersPagination(page=last_page).pack()),
        callback=callback
    )


@router.callback_query(calls.DeleteIncludedRestoreItem.filter())
async def callback_delete_included_restore_item(callback: CallbackQuery, callback_data: calls.DeleteIncludedRestoreItem, state: FSMContext):
    try:
        await state.set_state(None)
        
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        
        index = callback_data.index
        if index is None:
            return await callback_included_restore_items_pagination(
                callback, calls.IncludedRestoreItemsPagination(page=last_page), state
            )
        
        auto_restore_items = sett.get("auto_restore_items")
        auto_restore_items["included"].pop(index)
        sett.set("auto_restore_items", auto_restore_items)
        
        return await callback_included_restore_items_pagination(
            callback, calls.IncludedRestoreItemsPagination(page=last_page), state
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.restore_included_float_text(e),
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
                callback, calls.ExcludedRestoreItemsPagination(page=last_page), state
            )
        
        auto_restore_items = sett.get("auto_restore_items")
        auto_restore_items["excluded"].pop(index)
        sett.set("auto_restore_items", auto_restore_items)
        
        return await callback_excluded_restore_items_pagination(
            callback, calls.ExcludedRestoreItemsPagination(page=last_page), state
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.restore_included_float_text(e),
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
                callback, calls.IncludedRestoreItemsPagination(page=last_page), state
            )
        
        auto_complete_deals = sett.get("auto_complete_deals")
        auto_complete_deals["included"].pop(index)
        sett.set("auto_complete_deals", auto_complete_deals)
        
        return await callback_included_complete_deals_pagination(
            callback, calls.IncludedCompleteDealsPagination(page=last_page), state
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.complete_included_float_text(e),
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
                callback, calls.ExcludedRestoreItemsPagination(page=last_page), state
            )
        
        auto_complete_deals = sett.get("auto_complete_deals")
        auto_complete_deals["excluded"].pop(index)
        sett.set("auto_complete_deals", auto_complete_deals)
        
        return await callback_excluded_complete_deals_pagination(
            callback, calls.ExcludedCompleteDealsPagination(page=last_page), state
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.complete_included_float_text(e),
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
                callback, calls.IncludedBumpItemsPagination(page=last_page), state
            )
        
        auto_bump_items = sett.get("auto_bump_items")
        auto_bump_items["included"].pop(index)
        sett.set("auto_bump_items", auto_bump_items)
        
        return await callback_included_bump_items_pagination(
            callback, calls.IncludedBumpItemsPagination(page=last_page), state
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.bump_included_float_text(e),
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
                callback, calls.ExcludedBumpItemsPagination(page=last_page), state
            )
        
        auto_bump_items = sett.get("auto_bump_items")
        auto_bump_items["excluded"].pop(index)
        sett.set("auto_bump_items", auto_bump_items)
        
        return await callback_excluded_bump_items_pagination(
            callback, calls.ExcludedBumpItemsPagination(page=last_page), state
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.bump_excluded_float_text(e),
            reply_markup=templ.back_kb(calls.ExcludedBumpItemsPagination(page=last_page).pack())
        )


@router.callback_query(calls.RememberChatId.filter())
async def callback_remember_chat_id(callback: CallbackQuery, callback_data: calls.RememberChatId, state: FSMContext):
    await state.set_state(None)
    
    chat_id = callback_data.id
    do = callback_data.do

    await state.update_data(chat_id=chat_id)
    
    if do == "send_mess":
        await state.set_state(states.ActionsStates.waiting_for_fast_answer_message)
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.do_action_text(f"💬 Введите <b>сообщение</b> для отправки в чат:"),
            reply_markup=templ.destroy_kb(),
            callback=callback,
            reply_to=callback.message.message_id
        )

    if do == "send_fast_reply":
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.do_action_text(f"⚡ Выберите <b>быстрый ответ</b> для отправки:"),
            reply_markup=templ.fast_sel_fast_reply_kb(chat_id=chat_id, page=0),
            callback=callback,
            reply_to=callback.message.message_id
        )


@router.callback_query(calls.RememberDealId.filter())
async def callback_remember_deal_id(callback: CallbackQuery, callback_data: calls.RememberDealId, state: FSMContext):
    await state.set_state(None)
    
    deal_id = callback_data.de_id
    do = callback_data.do
    
    await state.update_data(deal_id=deal_id)
    
    if do == "refund":
        await callback_fast_change_deal_status(
            callback, calls.FastChangeDealStatus(id=deal_id, st="ROLLED_BACK"), state
        )
    if do == "complete":
        await callback_fast_change_deal_status(
            callback, calls.FastChangeDealStatus(id=deal_id, st="SENT"), state
        )


@router.callback_query(calls.SelectBankCard.filter())
async def callback_select_bank_card(callback: CallbackQuery, callback_data: calls.SelectBankCard, state: FSMContext):
    await state.set_state(None)
    card_id = callback_data.id

    config = sett.get("config")
    config["playerok"]["auto_withdrawal"]["credentials_type"] = "card"
    config["playerok"]["auto_withdrawal"]["card_id"] = card_id
    sett.set("config", config)
    
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="withdrawal"), state
    )


@router.callback_query(calls.SelectSbpBank.filter())
async def callback_select_sbp_bank(callback: CallbackQuery, callback_data: calls.SelectSbpBank, state: FSMContext):
    await state.set_state(states.SettingsStates.waiting_for_sbp_bank_phone_number)
    
    bank_id = callback_data.id
    await state.update_data(sbp_bank_id=bank_id)
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.withdrawal_sbp_float_text(f"📲 Введите <b>номер телефона</b>, на который нужно будет совершать вывод:"),
        reply_markup=templ.back_kb(calls.MenuNavigation(to="withdrawal").pack())
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
            text=templ.new_deliv_float_text(
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
            text=templ.new_deliv_float_text(
                f"💬 Введите <b>сообщение авто-выдачи</b>, которое будет отправляться после покупки товара:"
            ),
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack()),
            callback=callback
        )


@router.callback_query(calls.DeleteFastReply.filter())
async def callback_delete_fast_reply(callback: CallbackQuery, callback_data: calls.DeleteFastReply, state: FSMContext):
    try:
        await state.set_state(None)
        
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        
        index = callback_data.index
        if index is None:
            return await callback_fast_replies_pagination(
                callback, calls.FastRepliesPagination(page=last_page), state
            )
        
        fast_replies = sett.get("fast_replies")
        fast_replies.pop(index)
        sett.set("fast_replies", fast_replies)
        
        return await callback_fast_replies_pagination(
            callback, calls.FastRepliesPagination(page=last_page), state
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.fast_replies_float_text(e),
            reply_markup=templ.back_kb(calls.FastRepliesPagination(page=last_page).pack())
        )


@router.callback_query(F.data == "refund_deal")
async def callback_refund_deal(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    
    from plbot.playerokbot import get_playerok_bot
    plbot = get_playerok_bot()
    
    data = await state.get_data()
    deal_id = data.get("deal_id")
    
    plbot.account.update_deal(deal_id, ItemDealStatuses.ROLLED_BACK)
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.do_action_text(f"✅ По сделке <b>https://playerok.com/deal/{deal_id}</b> был оформлен возврат"),
        reply_markup=templ.destroy_kb(),
        reply_to=callback.message.message_id
    )


@router.callback_query(F.data == "complete_deal")
async def callback_complete_deal(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    
    from plbot.playerokbot import get_playerok_bot
    
    plbot = get_playerok_bot()
    data = await state.get_data()
    deal_id = data.get("deal_id")
    
    plbot.account.update_deal(deal_id, ItemDealStatuses.SENT)
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.do_action_text(f"✅ Сделка <b>https://playerok.com/deal/{deal_id}</b> была помечена вами, как выполненная"),
        reply_markup=templ.destroy_kb(),
        reply_to=callback.message.message_id
    )


@router.callback_query(F.data == "bump_items")
async def callback_bump_items(callback: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(None)
        
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.bump_float_text(f"⬆️ Идёт <b>поднятие товаров</b>, ожидайте (см. консоль)..."),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="bump").pack())
        )

        from plbot.playerokbot import get_playerok_bot as plbot
        success, total, cnt, error = plbot().bump_items()
        
        if success:
            await throw_float_message(
                state=state,
                message=callback.message,
                text=templ.bump_float_text(f"✅ Успешно поднято <b>{cnt}/{total} товаров</b>"),
                reply_markup=templ.back_kb(calls.MenuNavigation(to="bump").pack())
            )
        else:
            await throw_float_message(
                state=state,
                message=callback.message,
                text=templ.bump_float_text(f"❌ Не удалось <b>поднять товары</b>: <blockquote>{error}</blockquote>"),
                reply_markup=templ.back_kb(calls.MenuNavigation(to="bump").pack())
            )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.bump_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="bump").pack())
        )


@router.callback_query(F.data == "request_withdrawal")
async def callback_request_withdrawal(callback: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(None)
        
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.withdrawal_float_text(f"💸 Создаю <b>транзакцию на вывод средств</b>, ожидайте (см. консоль)..."),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="withdrawal").pack())
        )

        from plbot.playerokbot import get_playerok_bot as plbot
        success, bal, error = plbot().request_withdrawal()
        
        if success:
            await throw_float_message(
                state=state,
                message=callback.message,
                text=templ.withdrawal_float_text(f"✅ Успешно создана <b>транзакция на вывод {bal}₽</b>"),
                reply_markup=templ.back_kb(calls.MenuNavigation(to="withdrawal").pack())
            )
        else:
            await throw_float_message(
                state=state,
                message=callback.message,
                text=templ.withdrawal_float_text(f"❌ Не удалось <b>создать транзакцию на вывод</b>: <blockquote>{error}</blockquote>"),
                reply_markup=templ.back_kb(calls.MenuNavigation(to="withdrawal").pack())
            )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.withdrawal_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="withdrawal").pack())
        )


@router.callback_query(F.data == "clean_fp_proxy")
async def callback_clean_fp_proxy(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    
    config = sett.get("config")
    config["playerok"]["api"]["proxy"] = ""
    sett.set("config", config)
    
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="conn"), state
    )


@router.callback_query(F.data == "clean_tg_proxy")
async def callback_clean_tg_proxy(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    
    config = sett.get("config")
    config["telegram"]["api"]["proxy"] = ""
    sett.set("config", config)
    
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="conn"), state
    )


@router.callback_query(F.data == "clean_notifications_chat_id")
async def callback_clean_notifications_chat_id(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    
    config = sett.get("config")
    config["playerok"]["notifications"]["chat_id"] = ""
    sett.set("config", config)
    
    return await callback_menu_navigation(
        callback, calls.MenuNavigation(to="notifications"), state
    )


@router.callback_query(F.data == "send_new_included_restore_items_keyphrases_file")
async def callback_send_new_included_restore_items_keyphrases_file(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    
    await state.set_state(states.RestoreItemsStates.waiting_for_new_included_restore_items_keyphrases_file)
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.new_restore_included_float_text(
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
        text=templ.new_restore_excluded_float_text(
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
        text=templ.new_complete_included_float_text(
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
        text=templ.new_complete_excluded_float_text(
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
        text=templ.new_bump_included_float_text(
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
        text=templ.new_bump_excluded_float_text(
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
                callback, calls.CustomCommandsPagination(page=last_page), state
            )

        custom_commands[command] = answer.splitlines()
        sett.set("custom_commands", custom_commands)
        
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.new_comm_float_text(f"✅ <b>Команда</b> <code>{command}</code> была успешно добавлена"),
            reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.new_comm_float_text(e),
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
                callback, calls.CustomCommandsPagination(page=last_page), state
            )
        
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.comm_page_float_text(f"🗑️ Подтвердите <b>удаление команды</b> <code>{command}</code>"),
            reply_markup=templ.confirm_kb(
                confirm_cb="delete_custom_command", 
                cancel_cb=calls.CustomCommandPage(command=command).pack()
            )
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.comm_page_float_text(e),
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
                callback, calls.CustomCommandsPagination(page=last_page), state
            )
        
        custom_commands = sett.get("custom_commands")
        del custom_commands[command]
        sett.set("custom_commands", custom_commands)
        
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.comm_page_float_text(f"✅ <b>Команда</b> <code>{command}</code> была удалена"),
            reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.comm_page_float_text(e),
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
                callback, calls.AutoDeliveriesPagination(page=last_page), state
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
            text=templ.new_deliv_float_text(f"✅ <b>Авто-выдача</b> была успешно добавлена"),
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.new_deliv_float_text(e),
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
                callback, calls.AutoDeliveriesPagination(page=last_page), state
            )
       
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.deliv_page_float_text(
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
            text=templ.deliv_page_float_text(e),
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
                callback, calls.AutoDeliveriesPagination(page=last_page), state
            )
        
        auto_deliveries = sett.get("auto_deliveries")
        del auto_deliveries[index]
        sett.set("auto_deliveries", auto_deliveries)
        
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.deliv_page_float_text("✅ <b>Авто-выдача</b> была удалена"),
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.deliv_page_float_text(e),
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
                callback, calls.AutoDeliveriesPagination(page=last_page), state
            )
        
        auto_deliveries = sett.get("auto_deliveries")
        auto_deliveries[deliv_index]["goods"].pop(index)
        sett.set("auto_deliveries", auto_deliveries)
        
        return await callback_deliv_goods_pagination(
            callback, calls.DelivGoodsPagination(page=last_page), state
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.deliv_goods_float_text(e),
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
                callback, calls.ModulePage(page=last_page), state
            )
        
        from core.modules import reload_module
        await reload_module(uuid)
        
        return await callback_module_page(
            callback, calls.ModulePage(uuid=uuid), state
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


@router.callback_query(F.data == "mark_chat_as_read")
async def callback_mark_chat_as_read(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    
    data = await state.get_data()
    chat_id = data.get("chat_id")

    from plbot.playerokbot import get_playerok_bot as plbot
    plbot().account.mark_chat_as_read(chat_id)

    return await callback_chat_page(
        callback, calls.ChatPage(id=chat_id), state
    )


@router.callback_query(F.data == "deals_filter")
async def callback_deals_filter(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)

    data = await state.get_data()
    last_page = data.get("last_page", 0)
    deals_filter = data.get("deals_filter") 

    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.deals_float_text("✨ Настройте <b>фильтр</b> сделок:"),
        reply_markup=templ.deals_filter_kb(deals_filter, last_page)
    )


@router.callback_query(calls.ChangeDealsFilter.filter())
async def callback_change_deals_filter(callback: CallbackQuery, callback_data: calls.ChangeDealsFilter, state: FSMContext):
    await state.set_state(None)
    
    di = callback_data.di
    st = callback_data.st

    data = await state.get_data()
    filter = data.get("deals_filter")
    
    if 0 < di < 3:
        if not filter["statuses"]:
            filter["statuses"] = [ItemDealStatuses.PAID]
    if di == 1:
        filter["direction"] = ItemDealDirections.IN
    if di == 2:
        filter["direction"] = ItemDealDirections.OUT
    if di == 3:
        filter["direction"] = None
        filter["statuses"] = []

    if 0 < st < 5:
        if not filter["direction"]:
            filter["direction"] = ItemDealDirections.IN
    if st == 1:
        filter["statuses"] = [ItemDealStatuses.PAID]
    if st == 2:
        filter["statuses"] = [ItemDealStatuses.SENT]
    if st == 3:
        filter["statuses"] = [ItemDealStatuses.CONFIRMED]
    if st == 4:
        filter["statuses"] = [ItemDealStatuses.ROLLED_BACK]
    if st == 5:
        filter["direction"] = None
        filter["statuses"] = []

    await state.update_data(deals_filter=filter)
    await callback.bot.answer_callback_query(callback.id)

    await callback_deals_filter(callback, state)


@router.callback_query(F.data == "items_filter")
async def callback_items_filter(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)

    data = await state.get_data()
    last_page = data.get("last_page", 0)
    items_filter = data.get("items_filter") 

    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.items_float_text("✨ Настройте <b>фильтр</b> товаров:"),
        reply_markup=templ.items_filter_kb(items_filter, last_page)
    )


@router.callback_query(calls.ChangeItemsFilter.filter())
async def callback_change_items_filter(callback: CallbackQuery, callback_data: calls.ChangeItemsFilter, state: FSMContext):
    await state.set_state(None)
    data = await state.get_data()
    
    st = callback_data.st
    ga_id = callback_data.ga_id
    ca_id = callback_data.ca_id

    filter = data.get("items_filter")

    if st == 1:
        if ItemStatuses.PENDING_APPROVAL in filter["statuses"]:
            filter["statuses"].remove(ItemStatuses.PENDING_APPROVAL)
        else:
            filter["statuses"].append(ItemStatuses.PENDING_APPROVAL)
    if st == 2:
        if ItemStatuses.PENDING_MODERATION in filter["statuses"]:
            filter["statuses"].remove(ItemStatuses.PENDING_MODERATION)
        else:
            filter["statuses"].append(ItemStatuses.PENDING_MODERATION)
    if st == 3:
        if ItemStatuses.APPROVED in filter["statuses"]:
            filter["statuses"].remove(ItemStatuses.APPROVED)
        else:
            filter["statuses"].append(ItemStatuses.APPROVED)
    if st == 4:
        if ItemStatuses.DECLINED in filter["statuses"]:
            filter["statuses"].remove(ItemStatuses.DECLINED)
        else:
            filter["statuses"].append(ItemStatuses.DECLINED)
    if st == 5:
        if ItemStatuses.BLOCKED in filter["statuses"]:
            filter["statuses"].remove(ItemStatuses.BLOCKED)
        else:
            filter["statuses"].append(ItemStatuses.BLOCKED)
    if st == 6:
        if ItemStatuses.EXPIRED in filter["statuses"]:
            filter["statuses"].remove(ItemStatuses.EXPIRED)
        else:
            filter["statuses"].append(ItemStatuses.EXPIRED)
    if st == 7:
        if ItemStatuses.SOLD in filter["statuses"]:
            filter["statuses"].remove(ItemStatuses.SOLD)
        else:
            filter["statuses"].append(ItemStatuses.SOLD)
    if st == 8:
        if ItemStatuses.DRAFT in filter["statuses"]:
            filter["statuses"].remove(ItemStatuses.DRAFT)
        else:
            filter["statuses"].append(ItemStatuses.DRAFT)
    if st == 9:
        filter["statuses"] = []

    if ga_id == "all":
        filter["game_id"] = None
    elif ga_id != "":
        games = data.get("games") or []
        game = next((g for g in games if g.id == ga_id), None)
        
        filter["game_id"] = ga_id
        filter["game_name"] = game.name

    if ca_id == "all":
        filter["category_id"] = None
    elif ca_id != "":
        cats = data.get("cats") or []
        cat = next((c for c in cats if c.id == ca_id), None)
        
        filter["category_id"] = ca_id
        filter["category_name"] = cat.name

    await state.update_data(items_filter=filter)
    await callback.bot.answer_callback_query(callback.id)

    await callback_items_filter(callback, state)


@router.callback_query(F.data == "sel_items_filter_category")
async def callback_sel_items_filter_category(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)

    data = await state.get_data()
    games = data.get("games") or []
    filter = data.get("items_filter") or {}
    
    game_id = filter.get("game_id")
    game_name = filter.get("game_name")
    game = next((g for g in games if g.id == game_id), None)

    cats = game.categories
    await state.update_data(cats=cats)
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.items_float_text(f"📂 У игры <b>{game_name}</b> всего <b>{len(cats)} категорий</b>:"),
        reply_markup=templ.items_filter_categories_kb(cats),
        callback=callback
    )


@router.callback_query(F.data == "sel_item_pr_status")
async def callback_sel_item_pr_status(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)

    data = await state.get_data()
    item = data.get("item")

    from plbot.playerokbot import get_playerok_bot as plbot
    pr_statuses = plbot().account.get_item_priority_statuses(item.id, item.raw_price)
    await state.update_data(item_pr_statuses=pr_statuses)

    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.item_float_text("⚡ Выберите <b>статус приоритета</b> товара:"),
        reply_markup=templ.sel_item_pr_status_kb(item, pr_statuses)
    )


@router.callback_query(F.data == "transactions_filter")
async def callback_transactions_filter(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)

    data = await state.get_data()
    last_page = data.get("last_page", 0)
    transactions_filter = data.get("transactions_filter") 

    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.transactions_float_text("✨ Настройте <b>фильтр</b> транзакций:"),
        reply_markup=templ.transactions_filter_kb(transactions_filter, last_page)
    )


@router.callback_query(calls.ChangeTransactionsFilter.filter())
async def callback_change_transactions_filter(callback: CallbackQuery, callback_data: calls.ChangeTransactionsFilter, state: FSMContext):
    await state.set_state(None)
    
    st = callback_data.st
    op = callback_data.op
    pr = callback_data.pr

    min_val = callback_data.min_val
    max_val = callback_data.max_val
    from_dt = callback_data.from_dt
    to_dt = callback_data.to_dt

    data = await state.get_data()
    filter = data.get("transactions_filter")

    if st == 1:
        filter["status"] = TransactionStatuses.PENDING
    elif st == 2:
        filter["status"] = TransactionStatuses.PROCESSING
    elif st == 3:
        filter["status"] = TransactionStatuses.CONFIRMED
    elif st == 4:
        filter["status"] = TransactionStatuses.ROLLED_BACK
    elif st == 5:
        filter["status"] = TransactionStatuses.FAILED
    elif st == 6:
        filter["status"] = None

    if op == 1:
        filter["operation"] = TransactionOperations.DEPOSIT
    elif op == 2:
        filter["operation"] = TransactionOperations.BUY
    elif op == 3:
        filter["operation"] = TransactionOperations.SELL
    elif op == 4:
        filter["operation"] = TransactionOperations.ITEM_PREMIUM_PRIORITY
    elif op == 5:
        filter["operation"] = TransactionOperations.WITHDRAW
    elif op == 6:
        filter["operation"] = TransactionOperations.MANUAL_BALANCE_INCREASE
    elif op == 7:
        filter["operation"] = TransactionOperations.MANUAL_BALANCE_DECREASE
    elif op == 8:
        filter["operation"] = TransactionOperations.REFERRAL_BONUS
    elif op == 9:
        filter["operation"] = TransactionOperations.STEAM_DEPOSIT
    elif op == 10:
        filter["operation"] = None

    if pr == 1:
        filter["provider_id"] = TransactionProviderIds.LOCAL
    elif pr == 2:
        filter["provider_id"] = TransactionProviderIds.SBP
    elif pr == 3:
        filter["provider_id"] = TransactionProviderIds.BANK_CARD_RU
    elif pr == 4:
        filter["provider_id"] = TransactionProviderIds.BANK_CARD_BY
    elif pr == 5:
        filter["provider_id"] = TransactionProviderIds.BANK_CARD
    elif pr == 6:
        filter["provider_id"] = TransactionProviderIds.YMONEY
    elif pr == 7:
        filter["provider_id"] = TransactionProviderIds.USDT
    elif pr == 8:
        filter["provider_id"] = TransactionProviderIds.PENDING_INCOME
    elif pr == 9:
        filter["provider_id"] = None

    if min_val >= 0:
        filter["min_value"] = min_val or None
    if max_val >= 0:
        filter["max_value"] = max_val or None

    if len(from_dt) > 0:
        date = parse_date(from_dt)
        filter["from_date"] = date
    elif from_dt == "clear":
        filter["from_date"] = None
        
    if len(to_dt) > 0:
        date = parse_date(to_dt)
        filter["to_date"] = date
    elif to_dt == "clear":
        filter["to_date"] = None

    await state.update_data(transactions_filter=filter)
    await callback.bot.answer_callback_query(callback.id)

    await callback_transactions_filter(callback, state)


@router.callback_query(F.data == "reviews_filter")
async def callback_reviews_filter(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)

    data = await state.get_data()
    last_page = data.get("last_page", 0)
    reviews_filter = data.get("reviews_filter") 

    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.reviews_float_text("✨ Настройте <b>фильтр</b> отзывов:"),
        reply_markup=templ.reviews_filter_kb(reviews_filter, last_page)
    )


@router.callback_query(calls.ChangeReviewsFilter.filter())
async def callback_change_reviews_filter(callback: CallbackQuery, callback_data: calls.ChangeReviewsFilter, state: FSMContext):
    await state.set_state(None)
    
    st = callback_data.st
    cr = callback_data.cr
    rt = callback_data.rt
    ga_id = callback_data.ga_id
    ca_id = callback_data.ca_id

    min_pr = callback_data.min_pr
    max_pr = callback_data.max_pr

    data = await state.get_data()
    filter = data.get("reviews_filter")

    if st == 1:
        filter["status"] = ReviewStatuses.APPROVED
    elif st == 2:
        filter["status"] = ReviewStatuses.DELETED
    elif st == 3:
        filter["status"] = None

    if cr == 1:
        filter["comment_required"] = not filter["comment_required"]

    if 1 <= rt <= 5:
        filter["rating"] = rt
    elif rt == 0:
        filter["rating"] = None

    if ga_id == "all":
        filter["game_id"] = None
    elif ga_id != "":
        games = data.get("games") or []
        game = next((g for g in games if g.id == ga_id), None)
        
        filter["game_id"] = ga_id
        filter["game_name"] = game.name

    if ca_id == "all":
        filter["category_id"] = None
    elif ca_id != "":
        cats = data.get("cats") or []
        cat = next((c for c in cats if c.id == ca_id), None)
        
        filter["category_id"] = ca_id
        filter["category_name"] = cat.name

    if min_pr >= 0:
        filter["min_item_price"] = min_pr or None
    if max_pr >= 0:
        filter["max_item_price"] = max_pr or None

    await state.update_data(reviews_filter=filter)
    await callback.bot.answer_callback_query(callback.id)

    await callback_reviews_filter(callback, state)


@router.callback_query(F.data == "sel_reviews_filter_category")
async def callback_sel_reviews_filter_category(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)

    data = await state.get_data()
    games = data.get("games") or []
    filter = data.get("reviews_filter") or {}
    
    game_id = filter.get("game_id")
    game_name = filter.get("game_name")
    game = next((g for g in games if g.id == game_id), None)

    cats = game.categories
    await state.update_data(cats=cats)
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.reviews_float_text(f"📂 У игры <b>{game_name}</b> всего <b>{len(cats)} категорий</b>:"),
        reply_markup=templ.reviews_filter_categories_kb(cats),
        callback=callback
    )