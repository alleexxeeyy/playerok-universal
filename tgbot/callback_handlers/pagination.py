import copy
import math
from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

import asyncio

from settings import Settings as sett
from playerokapi.enums import MessageTemplateTypes, SortDirections, ReviewStatuses

from .. import templates as templ
from .. import callback_datas as calls
from .. import states
from ..helpful import throw_float_message


router = Router()


async def render_signed_users(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None):
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=message,
        text=templ.signed_users_text(),
        reply_markup=await templ.signed_users_kb(page),
        callback=callback
    )


@router.callback_query(calls.SignedUsersPagination.filter())
async def callback_signed_users_pagination(callback: CallbackQuery, callback_data: calls.SignedUsersPagination, state: FSMContext):
    await state.set_state(None)
    await render_signed_users(callback.message, state, callback_data.page, callback)


async def render_restore_included(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None):
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=message,
        text=templ.restore_included_text(),
        reply_markup=templ.restore_included_kb(page),
        callback=callback
    )


@router.callback_query(calls.IncludedRestoreItemsPagination.filter())
async def callback_included_restore_items_pagination(callback: CallbackQuery, callback_data: calls.IncludedRestoreItemsPagination, state: FSMContext):
    await state.set_state(None)
    await render_restore_included(callback.message, state, callback_data.page, callback)


async def render_restore_excluded(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None):
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=message,
        text=templ.restore_excluded_text(),
        reply_markup=templ.restore_excluded_kb(page),
        callback=callback
    )


@router.callback_query(calls.ExcludedRestoreItemsPagination.filter())
async def callback_excluded_restore_items_pagination(callback: CallbackQuery, callback_data: calls.ExcludedRestoreItemsPagination, state: FSMContext):
    await state.set_state(None)
    await render_restore_excluded(callback.message, state, callback_data.page, callback)


async def render_complete_included(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None):
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=message,
        text=templ.complete_included_text(),
        reply_markup=templ.complete_included_kb(page),
        callback=callback
    )


@router.callback_query(calls.IncludedCompleteDealsPagination.filter())
async def callback_included_complete_deals_pagination(callback: CallbackQuery, callback_data: calls.IncludedCompleteDealsPagination, state: FSMContext):
    await state.set_state(None)
    await render_complete_included(callback.message, state, callback_data.page, callback)


async def render_complete_excluded(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None):
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=message,
        text=templ.complete_excluded_text(),
        reply_markup=templ.complete_excluded_kb(page),
        callback=callback
    )


@router.callback_query(calls.ExcludedCompleteDealsPagination.filter())
async def callback_excluded_complete_deals_pagination(callback: CallbackQuery, callback_data: calls.ExcludedCompleteDealsPagination, state: FSMContext):
    await state.set_state(None)
    await render_complete_excluded(callback.message, state, callback_data.page, callback)


async def render_bump_included(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None):
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=message,
        text=templ.bump_included_text(),
        reply_markup=templ.bump_included_kb(page),
        callback=callback
    )


@router.callback_query(calls.IncludedBumpItemsPagination.filter())
async def callback_included_bump_items_pagination(callback: CallbackQuery, callback_data: calls.IncludedBumpItemsPagination, state: FSMContext):
    await state.set_state(None)
    await render_bump_included(callback.message, state, callback_data.page, callback)


async def render_bump_excluded(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None):
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=message,
        text=templ.bump_excluded_text(),
        reply_markup=templ.bump_excluded_kb(page),
        callback=callback
    )


@router.callback_query(calls.ExcludedBumpItemsPagination.filter())
async def callback_excluded_bump_items_pagination(callback: CallbackQuery, callback_data: calls.ExcludedBumpItemsPagination, state: FSMContext):
    await state.set_state(None)
    await render_bump_excluded(callback.message, state, callback_data.page, callback)


async def render_bump_positions(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None):
    await state.update_data(last_page=page)

    await throw_float_message(
        state=state,
        message=message,
        text=templ.bump_positions_text(),
        reply_markup=templ.bump_positions_kb(page),
        callback=callback
    )


@router.callback_query(calls.BumpItemsPositionsPagination.filter())
async def callback_bump_items_positions_pagination(callback: CallbackQuery, callback_data: calls.BumpItemsPositionsPagination, state: FSMContext):
    await state.set_state(None)
    await render_bump_positions(callback.message, state, callback_data.page, callback)


async def render_custom_commands(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None):
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=message,
        text=templ.comms_text(),
        reply_markup=templ.comms_kb(page),
        callback=callback
    )


@router.callback_query(calls.CustomCommandsPagination.filter())
async def callback_custom_commands_pagination(callback: CallbackQuery, callback_data: calls.CustomCommandsPagination, state: FSMContext):
    await state.set_state(None)
    await render_custom_commands(callback.message, state, callback_data.page, callback)


async def render_auto_deliveries(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None):
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=message,
        text=templ.delivs_text(),
        reply_markup=templ.delivs_kb(page),
        callback=callback
        )


@router.callback_query(calls.AutoDeliveriesPagination.filter())
async def callback_auto_deliveries_pagination(callback: CallbackQuery, callback_data: calls.AutoDeliveriesPagination, state: FSMContext):
    await state.set_state(None)
    await render_auto_deliveries(callback.message, state, callback_data.page, callback)


async def render_deliv_goods(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None):
    data = await state.get_data()
    index = data.get("auto_delivery_index")
    
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=message,
        text=templ.deliv_goods_text(index),
        reply_markup=templ.deliv_goods_kb(index, page),
        callback=callback
    )


@router.callback_query(calls.DelivGoodsPagination.filter())
async def callback_deliv_goods_pagination(callback: CallbackQuery, callback_data: calls.DelivGoodsPagination, state: FSMContext):
    await state.set_state(None)
    await render_deliv_goods(callback.message, state, callback_data.page, callback)


async def render_data_replacements(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None):
    await state.update_data(last_page=page)

    await throw_float_message(
        state=state,
        message=message,
        text=templ.data_replacements_text(),
        reply_markup=templ.data_replacements_kb(page),
        callback=callback
    )


@router.callback_query(calls.DataReplacementsPagination.filter())
async def callback_data_replacements_pagination(callback: CallbackQuery, callback_data: calls.DataReplacementsPagination, state: FSMContext):
    await state.set_state(None)
    await render_data_replacements(callback.message, state, callback_data.page, callback)


async def render_data_replacement_values(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None):
    data = await state.get_data()
    index = data.get("data_replacement_index")

    await state.update_data(data_replacement_values_page=page)

    await throw_float_message(
        state=state,
        message=message,
        text=templ.data_replacement_values_text(index),
        reply_markup=templ.data_replacement_values_kb(index, page),
        callback=callback
    )


@router.callback_query(calls.DataReplacementValuesPagination.filter())
async def callback_data_replacement_values_pagination(callback: CallbackQuery, callback_data: calls.DataReplacementValuesPagination, state: FSMContext):
    await state.set_state(None)
    await render_data_replacement_values(callback.message, state, callback_data.page, callback)


async def render_messages(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None):
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=message,
        text=templ.mess_text(),
        reply_markup=templ.mess_kb(page),
        callback=callback
    )


@router.callback_query(calls.MessagesPagination.filter())
async def callback_messages_pagination(callback: CallbackQuery, callback_data: calls.MessagesPagination, state: FSMContext):
    await state.set_state(None)
    await render_messages(callback.message, state, callback_data.page, callback)


async def render_fast_replies(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None):
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=message,
        text=templ.fast_replies_text(),
        reply_markup=templ.fast_replies_kb(page),
        callback=callback
    )


@router.callback_query(calls.FastRepliesPagination.filter())
async def callback_fast_replies_pagination(callback: CallbackQuery, callback_data: calls.FastRepliesPagination, state: FSMContext):
    await state.set_state(None)
    await render_fast_replies(callback.message, state, callback_data.page, callback)


async def render_fast_sel_fast_reply(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None):
    data = await state.get_data()
    chat_id = data.get("fast_reply_chat_id")
    await state.update_data(last_page=page)

    await throw_float_message(
        state=state,
        message=message,
        text=templ.do_action_text(f"⚡ Выберите <b>быстрый ответ</b> для отправки:"),
        reply_markup=templ.fast_sel_fast_reply_kb(chat_id, page),
        callback=callback
    )


@router.callback_query(calls.FastSelFastReplyPagination.filter())
async def callback_fast_sel_fast_replies_pagination(callback: CallbackQuery, callback_data: calls.FastSelFastReplyPagination, state: FSMContext):
    await state.set_state(None)
    await state.update_data(fast_reply_chat_id=callback_data.id)
    await render_fast_sel_fast_reply(callback.message, state, callback_data.page, callback)


async def render_sel_fast_reply(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None):
    data = await state.get_data()
    chat_id = data.get("fast_reply_chat_id")
    await state.update_data(last_page=page)

    await throw_float_message(
        state=state,
        message=message,
        text=templ.do_action_text(f"⚡ Выберите <b>быстрый ответ</b> для отправки:"),
        reply_markup=templ.sel_fast_reply_kb(chat_id, page),
        callback=callback
    )


@router.callback_query(calls.SelFastReplyPagination.filter())
async def callback_sel_fast_replies_pagination(callback: CallbackQuery, callback_data: calls.SelFastReplyPagination, state: FSMContext):
    await state.set_state(None)
    await state.update_data(fast_reply_chat_id=callback_data.id)
    await render_sel_fast_reply(callback.message, state, callback_data.page, callback)


async def render_modules(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None):
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=message,
        text=templ.modules_text(),
        reply_markup=templ.modules_kb(page),
        callback=callback
    )


@router.callback_query(calls.ModulesPagination.filter())
async def callback_modules_pagination(callback: CallbackQuery, callback_data: calls.ModulesPagination, state: FSMContext):
    await state.set_state(None)
    await render_modules(callback.message, state, callback_data.page, callback)


async def render_bank_cards(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None):
    await state.update_data(last_page=page)
    
    data = await state.get_data()
    bank_cards = data.get("bank_cards", [])
    
    await throw_float_message(
        state=state,
        message=message,
        text=templ.withdrawal_cards_text(bank_cards),
        reply_markup=templ.withdrawal_cards_kb(bank_cards, page),
        callback=callback
    )


@router.callback_query(calls.BankCardsPagination.filter())
async def callback_bank_cards_pagination(callback: CallbackQuery, callback_data: calls.BankCardsPagination, state: FSMContext):
    await state.set_state(None)
    await render_bank_cards(callback.message, state, callback_data.page, callback)


async def render_sbp_banks(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None):
    await state.update_data(last_page=page)
    
    data = await state.get_data()
    sbp_banks = data.get("sbp_banks", [])
    
    await throw_float_message(
        state=state,
        message=message,
        text=templ.withdrawal_sbp_text(sbp_banks),
        reply_markup=templ.withdrawal_sbp_kb(sbp_banks, page),
        callback=callback
    )


@router.callback_query(calls.SbpBanksPagination.filter())
async def callback_sbp_banks_pagination(callback: CallbackQuery, callback_data: calls.SbpBanksPagination, state: FSMContext):
    await state.set_state(None)
    await render_sbp_banks(callback.message, state, callback_data.page, callback)


MAX_PAGE_LOAD_REQUESTS = 10


async def load_cursor_list(state: FSMContext, message: Message, key: str, page: int, fetch, reset: bool = False) -> list:
    data = await state.get_data()
    objects = [] if reset else list(data.get(key) or [])
    end_cursor = None if reset else data.get(f"{key}_end_cursor")
    is_all_loaded = False if reset else (data.get(f"is_all_{key}_loaded") or False)

    requests = 0
    try:
        while not is_all_loaded and len(objects) < (page + 1) * 12 + 1 and requests < MAX_PAGE_LOAD_REQUESTS:
            if requests == 0:
                await throw_float_message(state, message, "⌛️")

            batch, end_cursor = await asyncio.to_thread(fetch, end_cursor)
            objects.extend(batch or [])
            if len(batch or []) < 24 or not end_cursor:
                is_all_loaded = True
            requests += 1
    finally:
        if requests:
            await state.update_data(**{
                key: objects,
                f"{key}_end_cursor": end_cursor,
                f"is_all_{key}_loaded": is_all_loaded
            })
    return objects


async def render_chats(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None, upd: bool = False):
    try:
        from plbot.playerokbot import get_playerok_bot as plbot

        def fetch(after_cursor):
            chat_lst = plbot().account.get_chats(
                count=24,
                after_cursor=after_cursor
            )
            return chat_lst.chats, chat_lst.page_info.end_cursor

        chats = await load_cursor_list(state, message, "chats", page, fetch, reset=upd)
        page = min(page, max(math.ceil(len(chats) / 12), 1) - 1)
        await state.update_data(last_page=page)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.chats_text(chats, page),
            reply_markup=templ.chats_kb(chats, page),
            callback=callback
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.chats_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="default").pack()),
            callback=callback
        )


@router.callback_query(calls.ChatsPagination.filter())
async def callback_chats_pagination(callback: CallbackQuery, callback_data: calls.ChatsPagination, state: FSMContext):
    await state.set_state(None)
    await render_chats(callback.message, state, callback_data.page, callback, upd=callback_data.upd)


async def render_deals(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None, upd: bool = False):
    try:
        data = await state.get_data()
        deals_filter = data.get("deals_filter")
        last_deals_filter = data.get("last_deals_filter")

        if not deals_filter:
            deals_filter = {"direction": None, "statuses": []}
            await state.update_data(deals_filter=deals_filter)

        await state.update_data(last_deals_filter=copy.deepcopy(deals_filter))
        filter_updated = deals_filter != last_deals_filter

        from plbot.playerokbot import get_playerok_bot as plbot

        def fetch(after_cursor):
            deal_lst = plbot().account.get_deals(
                count=24,
                direction=deals_filter["direction"],
                statuses=deals_filter["statuses"] or None,
                after_cursor=after_cursor
            )
            return deal_lst.deals, deal_lst.page_info.end_cursor

        deals = await load_cursor_list(state, message, "deals", page, fetch, reset=upd or filter_updated)
        page = min(page, max(math.ceil(len(deals) / 12), 1) - 1)
        await state.update_data(last_page=page)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.deals_text(deals, page),
            reply_markup=templ.deals_kb(deals, page),
            callback=callback
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.deals_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="default").pack()),
            callback=callback
        )


@router.callback_query(calls.DealsPagination.filter())
async def callback_deals_pagination(callback: CallbackQuery, callback_data: calls.DealsPagination, state: FSMContext):
    await state.set_state(None)
    await render_deals(callback.message, state, callback_data.page, callback, upd=callback_data.upd)


async def render_sel_message_template(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None):
    data = await state.get_data()
    deal_id = data.get("deal_id")
    type_int = data.get("message_template_type")
    try:
        from plbot.playerokbot import get_playerok_bot as plbot
        acc = plbot().account

        await state.update_data(last_page=page)

        if type_int == 0:
            type = MessageTemplateTypes.ACTIVE_DEAL_PROBLEM
        else:
            type = MessageTemplateTypes.FINISHED_DEAL_PROBLEM

        deal = data.get("deal")
        if not deal:
            deal = acc.get_deal(id=deal_id)

        data = await state.get_data()
        mt = data.get("mts") or []

        if not mt:
            await throw_float_message(state, message, "⌛️")
            mt_list = acc.get_message_templates(count=24, type=type)
            mt = mt_list.message_templates
            await state.update_data(mts=mt)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.deal_float_text("🗂️ Выберите <b>категорию проблемы</b>:"),
            reply_markup=templ.sel_message_template_kb(mt, deal_id, type_int, page),
            callback=callback
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.deal_float_text(e),
            reply_markup=templ.back_kb(calls.DealPage(id=deal_id).pack()),
            callback=callback
        )


@router.callback_query(calls.SelMessageTemplatePagination.filter())
async def callback_sel_message_template_pagination(callback: CallbackQuery, callback_data: calls.SelMessageTemplatePagination, state: FSMContext):
    await state.set_state(None)
    await state.update_data(deal_id=callback_data.id, message_template_type=callback_data.type)
    await render_sel_message_template(callback.message, state, callback_data.page, callback)


async def render_fast_sel_message_template(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None):
    data = await state.get_data()
    deal_id = data.get("deal_id")
    type_int = data.get("message_template_type")
    try:
        from plbot.playerokbot import get_playerok_bot as plbot
        acc = plbot().account

        await state.update_data(last_page=page)

        if type_int == 0:
            type = MessageTemplateTypes.ACTIVE_DEAL_PROBLEM
        else:
            type = MessageTemplateTypes.FINISHED_DEAL_PROBLEM

        data = await state.get_data()
        mt = data.get("mts") or []

        if not mt:
            await throw_float_message(state, message, "⌛️")
            mt_list = acc.get_message_templates(count=24, type=type)
            mt = mt_list.message_templates
            await state.update_data(mts=mt)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.deal_float_text("🗂️ Выберите <b>категорию проблемы</b>:"),
            reply_markup=templ.fast_sel_message_template_kb(mt, deal_id, type_int, page),
            callback=callback
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.deal_float_text(e),
            reply_markup=templ.back_kb(calls.DealPage(id=deal_id).pack()),
            callback=callback
        )


@router.callback_query(calls.FastSelMessageTemplatePagination.filter())
async def callback_fast_sel_message_template_pagination(callback: CallbackQuery, callback_data: calls.FastSelMessageTemplatePagination, state: FSMContext):
    await state.set_state(None)
    await state.update_data(deal_id=callback_data.id, message_template_type=callback_data.type)
    await render_fast_sel_message_template(callback.message, state, callback_data.page, callback)


async def render_items(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None, upd: bool = False):
    try:
        data = await state.get_data()
        items_filter = data.get("items_filter")
        last_items_filter = data.get("last_items_filter")

        if not items_filter:
            items_filter = {"statuses": [], "game_id": None, "game_name": None, "category_id": None, "category_name": None}
            await state.update_data(items_filter=items_filter)

        await state.update_data(last_items_filter=copy.deepcopy(items_filter))
        filter_updated = items_filter != last_items_filter

        from plbot.playerokbot import get_playerok_bot as plbot

        def fetch(after_cursor):
            item_lst = plbot().account.get_my_items(
                game_id=items_filter["game_id"],
                category_id=items_filter["category_id"],
                statuses=items_filter["statuses"] or None,
                count=24,
                after_cursor=after_cursor
            )
            return item_lst.items, item_lst.page_info.end_cursor

        items = await load_cursor_list(state, message, "items", page, fetch, reset=upd or filter_updated)
        page = min(page, max(math.ceil(len(items) / 12), 1) - 1)
        await state.update_data(last_page=page)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.items_text(items, page),
            reply_markup=templ.items_kb(items, page),
            callback=callback
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.items_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="default").pack()),
            callback=callback
        )


@router.callback_query(calls.ItemsPagination.filter())
async def callback_items_pagination(callback: CallbackQuery, callback_data: calls.ItemsPagination, state: FSMContext):
    await state.set_state(None)
    await render_items(callback.message, state, callback_data.page, callback, upd=callback_data.upd)


async def render_transactions(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None, upd: bool = False):
    try:
        data = await state.get_data()
        transactions_filter = data.get("transactions_filter")
        last_transactions_filter = data.get("last_transactions_filter")

        if not transactions_filter:
            transactions_filter = {
                "operation": None,
                "status": None,
                "provider_id": None,
                "min_value": None,
                "max_value": None,
                "from_date": None,
                "to_date": None
            }
            await state.update_data(transactions_filter=transactions_filter)

        await state.update_data(last_transactions_filter=copy.deepcopy(transactions_filter))
        filter_updated = transactions_filter != last_transactions_filter

        from plbot.playerokbot import get_playerok_bot as plbot

        def fetch(after_cursor):
            transaction_lst = plbot().account.get_transactions(
                status=transactions_filter["status"],
                operation=transactions_filter["operation"],
                provider_id=transactions_filter["provider_id"],
                min_value=transactions_filter["min_value"],
                max_value=transactions_filter["max_value"],
                from_date=transactions_filter["from_date"],
                to_date=transactions_filter["to_date"],
                count=24,
                after_cursor=after_cursor
            )
            return transaction_lst.transactions, transaction_lst.page_info.end_cursor

        transactions = await load_cursor_list(state, message, "transactions", page, fetch, reset=upd or filter_updated)
        page = min(page, max(math.ceil(len(transactions) / 12), 1) - 1)
        await state.update_data(last_page=page)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.transactions_text(transactions, page),
            reply_markup=templ.transactions_kb(transactions, page),
            callback=callback
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.transactions_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="default").pack()),
            callback=callback
        )


@router.callback_query(calls.TransactionsPagination.filter())
async def callback_transactions_pagination(callback: CallbackQuery, callback_data: calls.TransactionsPagination, state: FSMContext):
    await state.set_state(None)
    await render_transactions(callback.message, state, callback_data.page, callback, upd=callback_data.upd)


async def render_reviews(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None, upd: bool = False):
    try:
        data = await state.get_data()
        reviews_filter = data.get("reviews_filter")
        last_reviews_filter = data.get("last_reviews_filter")

        if not reviews_filter:
            reviews_filter = {
                "status": None,
                "comment_required": False,
                "rating": None,
                "game_id": None,
                "game_name": None,
                "category_id": None,
                "category_name": None,
                "min_item_price": None,
                "max_item_price": None,
                "sort_direction": SortDirections.DESC
            }
            await state.update_data(reviews_filter=reviews_filter)

        await state.update_data(last_reviews_filter=copy.deepcopy(reviews_filter))
        filter_updated = reviews_filter != last_reviews_filter

        from plbot.playerokbot import get_playerok_bot as plbot

        def fetch(after_cursor):
            review_lst = plbot().account.get_my_reviews(
                status=reviews_filter["status"],
                comment_required=reviews_filter["comment_required"],
                rating=reviews_filter["rating"],
                game_id=reviews_filter["game_id"],
                category_id=reviews_filter["category_id"],
                min_item_price=reviews_filter["min_item_price"],
                max_item_price=reviews_filter["max_item_price"],
                sort_direction=reviews_filter["sort_direction"],
                count=24,
                after_cursor=after_cursor
            )
            return review_lst.reviews, review_lst.page_info.end_cursor

        reviews = await load_cursor_list(state, message, "reviews", page, fetch, reset=upd or filter_updated)
        page = min(page, max(math.ceil(len(reviews) / 12), 1) - 1)
        await state.update_data(last_page=page)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.reviews_text(reviews, page),
            reply_markup=templ.reviews_kb(reviews, page),
            callback=callback
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.reviews_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="default").pack()),
            callback=callback
        )


@router.callback_query(calls.ReviewsPagination.filter())
async def callback_reviews_pagination(callback: CallbackQuery, callback_data: calls.ReviewsPagination, state: FSMContext):
    await state.set_state(None)
    await render_reviews(callback.message, state, callback_data.page, callback, upd=callback_data.upd)


async def render_releases(message: Message, state: FSMContext, page: int, callback: CallbackQuery = None):
    from updater import get_cached_releases

    await state.update_data(rel_last_page=page)

    try:
        releases = await asyncio.to_thread(get_cached_releases)
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.releases_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="updates").pack()),
            callback=callback
        )
        return

    await throw_float_message(
        state=state,
        message=message,
        text=templ.releases_text(releases),
        reply_markup=templ.releases_kb(releases, page),
        callback=callback
    )


@router.callback_query(calls.ReleasesPagination.filter())
async def callback_releases_pagination(callback: CallbackQuery, callback_data: calls.ReleasesPagination, state: FSMContext):
    await state.set_state(None)
    await render_releases(callback.message, state, callback_data.page, callback)


PAGES = {
    "signed_users": (render_signed_users, templ.signed_users_float_text),
    "restore_included": (render_restore_included, templ.restore_included_float_text),
    "restore_excluded": (render_restore_excluded, templ.restore_excluded_float_text),
    "complete_included": (render_complete_included, templ.complete_included_float_text),
    "complete_excluded": (render_complete_excluded, templ.complete_excluded_float_text),
    "bump_included": (render_bump_included, templ.bump_included_float_text),
    "bump_excluded": (render_bump_excluded, templ.bump_excluded_float_text),
    "bump_positions": (render_bump_positions, templ.bump_positions_float_text),
    "custom_commands": (render_custom_commands, templ.comms_float_text),
    "auto_deliveries": (render_auto_deliveries, templ.deliv_float_text),
    "deliv_goods": (render_deliv_goods, templ.deliv_goods_float_text),
    "data_replacements": (render_data_replacements, templ.data_replacements_float_text),
    "data_replacement_values": (render_data_replacement_values, templ.data_replacement_values_float_text),
    "messages": (render_messages, templ.mess_float_text),
    "fast_replies": (render_fast_replies, templ.fast_replies_float_text),
    "fast_sel_fast_reply": (render_fast_sel_fast_reply, templ.do_action_text),
    "sel_fast_reply": (render_sel_fast_reply, templ.do_action_text),
    "modules": (render_modules, templ.modules_float_text),
    "bank_cards": (render_bank_cards, templ.withdrawal_cards_float_text),
    "sbp_banks": (render_sbp_banks, templ.withdrawal_sbp_float_text),
    "chats": (render_chats, templ.chats_float_text),
    "deals": (render_deals, templ.deals_float_text),
    "sel_message_template": (render_sel_message_template, templ.deal_float_text),
    "fast_sel_message_template": (render_fast_sel_message_template, templ.deal_float_text),
    "items": (render_items, templ.items_float_text),
    "transactions": (render_transactions, templ.transactions_float_text),
    "reviews": (render_reviews, templ.reviews_float_text),
    "releases": (render_releases, templ.releases_float_text)
}


@router.callback_query(calls.PageEnter.filter())
async def callback_page_enter(callback: CallbackQuery, callback_data: calls.PageEnter, state: FSMContext):
    if callback_data.to not in PAGES:
        return await callback.answer()

    enter = callback_data.model_dump()
    enter["state"] = await state.get_state()
    await state.update_data(page_enter=enter)
    await state.set_state(states.PageStates.waiting_for_page)

    _, float_text = PAGES[callback_data.to]
    pages_range = f" (1–{callback_data.total})" if callback_data.total else ""
    await throw_float_message(
        state=state,
        message=callback.message,
        text=float_text(f"📃 Введите <b>номер страницы</b> для перехода{pages_range}:"),
        reply_markup=templ.back_kb(calls.PageBack(to=callback_data.to, page=callback_data.page).pack()),
        callback=callback
    )


@router.callback_query(calls.PageBack.filter())
async def callback_page_back(callback: CallbackQuery, callback_data: calls.PageBack, state: FSMContext):
    if callback_data.to not in PAGES:
        return await callback.answer()

    if await state.get_state() == states.PageStates.waiting_for_page:
        data = await state.get_data()
        await state.set_state((data.get("page_enter") or {}).get("state"))

    render, _ = PAGES[callback_data.to]
    await render(callback.message, state, callback_data.page, callback)
