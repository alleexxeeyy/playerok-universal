import copy
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from settings import Settings as sett
from playerokapi.enums import MessageTemplateTypes, SortDirections, ReviewStatuses

from .. import templates as templ
from .. import callback_datas as calls
from ..helpful import throw_float_message


router = Router()


@router.callback_query(calls.SignedUsersPagination.filter())
async def callback_signed_users_pagination(callback: CallbackQuery, callback_data: calls.SignedUsersPagination, state: FSMContext):
    await state.set_state(None)
    
    page = callback_data.page
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.signed_users_text(),
        reply_markup=await templ.signed_users_kb(page),
        callback=callback
    )


@router.callback_query(calls.IncludedRestoreItemsPagination.filter())
async def callback_included_restore_items_pagination(callback: CallbackQuery, callback_data: calls.IncludedRestoreItemsPagination, state: FSMContext):
    await state.set_state(None)
    
    page = callback_data.page
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.restore_included_text(),
        reply_markup=templ.restore_included_kb(page),
        callback=callback
    )


@router.callback_query(calls.ExcludedRestoreItemsPagination.filter())
async def callback_excluded_restore_items_pagination(callback: CallbackQuery, callback_data: calls.ExcludedRestoreItemsPagination, state: FSMContext):
    await state.set_state(None)
    
    page = callback_data.page
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.restore_excluded_text(),
        reply_markup=templ.restore_excluded_kb(page),
        callback=callback
    )


@router.callback_query(calls.IncludedCompleteDealsPagination.filter())
async def callback_included_complete_deals_pagination(callback: CallbackQuery, callback_data: calls.IncludedCompleteDealsPagination, state: FSMContext):
    await state.set_state(None)
    
    page = callback_data.page
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.complete_included_text(),
        reply_markup=templ.complete_included_kb(page),
        callback=callback
    )


@router.callback_query(calls.ExcludedCompleteDealsPagination.filter())
async def callback_excluded_complete_deals_pagination(callback: CallbackQuery, callback_data: calls.ExcludedCompleteDealsPagination, state: FSMContext):
    await state.set_state(None)
    
    page = callback_data.page
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.complete_excluded_text(),
        reply_markup=templ.complete_excluded_kb(page),
        callback=callback
    )


@router.callback_query(calls.IncludedBumpItemsPagination.filter())
async def callback_included_bump_items_pagination(callback: CallbackQuery, callback_data: calls.IncludedBumpItemsPagination, state: FSMContext):
    await state.set_state(None)
    
    page = callback_data.page
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.bump_included_text(),
        reply_markup=templ.bump_included_kb(page),
        callback=callback
    )


@router.callback_query(calls.ExcludedBumpItemsPagination.filter())
async def callback_excluded_bump_items_pagination(callback: CallbackQuery, callback_data: calls.ExcludedBumpItemsPagination, state: FSMContext):
    await state.set_state(None)
    
    page = callback_data.page
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.bump_excluded_text(),
        reply_markup=templ.bump_excluded_kb(page),
        callback=callback
    )


@router.callback_query(calls.CustomCommandsPagination.filter())
async def callback_custom_commands_pagination(callback: CallbackQuery, callback_data: calls.CustomCommandsPagination, state: FSMContext):
    await state.set_state(None)
    
    page = callback_data.page
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.comms_text(),
        reply_markup=templ.comms_kb(page),
        callback=callback
    )


@router.callback_query(calls.AutoDeliveriesPagination.filter())
async def callback_auto_deliveries_pagination(callback: CallbackQuery, callback_data: calls.AutoDeliveriesPagination, state: FSMContext):
    await state.set_state(None)
    
    page = callback_data.page
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.delivs_text(),
        reply_markup=templ.delivs_kb(page),
        callback=callback
        )


@router.callback_query(calls.DelivGoodsPagination.filter())
async def callback_deliv_goods_pagination(callback: CallbackQuery, callback_data: calls.DelivGoodsPagination, state: FSMContext):
    await state.set_state(None)

    data = await state.get_data()
    index = data.get("auto_delivery_index")
    
    page = callback_data.page
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.deliv_goods_text(index),
        reply_markup=templ.deliv_goods_kb(index, page),
        callback=callback
    )


@router.callback_query(calls.MessagesPagination.filter())
async def callback_messages_pagination(callback: CallbackQuery, callback_data: calls.MessagesPagination, state: FSMContext):
    await state.set_state(None)
    
    page = callback_data.page
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.mess_text(),
        reply_markup=templ.mess_kb(page),
        callback=callback
    )


@router.callback_query(calls.FastRepliesPagination.filter())
async def callback_fast_replies_pagination(callback: CallbackQuery, callback_data: calls.FastRepliesPagination, state: FSMContext):
    await state.set_state(None)
    
    page = callback_data.page
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.fast_replies_text(),
        reply_markup=templ.fast_replies_kb(page),
        callback=callback
    )


@router.callback_query(calls.FastSelFastReplyPagination.filter())
async def callback_fast_sel_fast_replies_pagination(callback: CallbackQuery, callback_data: calls.FastSelFastReplyPagination, state: FSMContext):
    await state.set_state(None)
    
    chat_id = callback_data.id
    page = callback_data.page
    await state.update_data(last_page=page)

    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.do_action_text(f"⚡ Выберите <b>быстрый ответ</b> для отправки:"),
        reply_markup=templ.fast_sel_fast_reply_kb(chat_id, page),
        callback=callback
    )


@router.callback_query(calls.SelFastReplyPagination.filter())
async def callback_sel_fast_replies_pagination(callback: CallbackQuery, callback_data: calls.SelFastReplyPagination, state: FSMContext):
    await state.set_state(None)
    
    chat_id = callback_data.id
    page = callback_data.page
    await state.update_data(last_page=page)

    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.do_action_text(f"⚡ Выберите <b>быстрый ответ</b> для отправки:"),
        reply_markup=templ.sel_fast_reply_kb(chat_id, page),
        callback=callback
    )


@router.callback_query(calls.ModulesPagination.filter())
async def callback_modules_pagination(callback: CallbackQuery, callback_data: calls.ModulesPagination, state: FSMContext):
    await state.set_state(None)
    
    page = callback_data.page
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.modules_text(),
        reply_markup=templ.modules_kb(page),
        callback=callback
    )


@router.callback_query(calls.BankCardsPagination.filter())
async def callback_bank_cards_pagination(callback: CallbackQuery, callback_data: calls.BankCardsPagination, state: FSMContext):
    await state.set_state(None)
    
    page = callback_data.page
    await state.update_data(last_page=page)
    
    data = await state.get_data()
    bank_cards = data.get("bank_cards", [])
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.withdrawal_cards_text(bank_cards),
        reply_markup=templ.withdrawal_cards_kb(bank_cards, page),
        callback=callback
    )


@router.callback_query(calls.SbpBanksPagination.filter())
async def callback_sbp_banks_pagination(callback: CallbackQuery, callback_data: calls.SbpBanksPagination, state: FSMContext):
    await state.set_state(None)
    
    page = callback_data.page
    await state.update_data(last_page=page)
    
    data = await state.get_data()
    sbp_banks = data.get("sbp_banks", [])
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.withdrawal_sbp_text(sbp_banks),
        reply_markup=templ.withdrawal_sbp_kb(sbp_banks, page),
        callback=callback
    )


@router.callback_query(calls.ChatsPagination.filter())
async def callback_chats_pagination(callback: CallbackQuery, callback_data: calls.ChatsPagination, state: FSMContext):
    try:
        await state.set_state(None)
        
        page = callback_data.page
        upd = callback_data.upd
        await state.update_data(last_page=page)

        data = await state.get_data()
        chats = data.get("chats") or []
        end_cursor = data.get("chats_end_cursor")
        is_all_chats_loaded = data.get("is_all_chats_loaded") or False

        next_page_start = (page + 1) * 12
        need_more = len(chats) < next_page_start + 1

        if upd:
            end_cursor = None

        if (not is_all_chats_loaded and need_more) or upd:
            await throw_float_message(state, callback.message, "⌛️")
            from plbot.playerokbot import get_playerok_bot as plbot
            
            chat_lst = plbot().account.get_chats(
                count=24, 
                after_cursor=end_cursor
            ) 
            
            if upd:
                chats = chat_lst.chats
            else:
                chats.extend(chat_lst.chats or [])

            if len(chat_lst.chats or []) < 24:
                is_all_chats_loaded = True

            await state.update_data(
                is_all_chats_loaded=is_all_chats_loaded,
                chats_end_cursor=chat_lst.page_info.end_cursor,
                chats=chats
            )
        
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.chats_text(chats, page),
            reply_markup=templ.chats_kb(chats, page),
            callback=callback
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.chats_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="default").pack()),
            callback=callback
        )


@router.callback_query(calls.DealsPagination.filter())
async def callback_deals_pagination(callback: CallbackQuery, callback_data: calls.DealsPagination, state: FSMContext):
    try:
        await state.set_state(None)
        
        page = callback_data.page
        upd = callback_data.upd
        await state.update_data(last_page=page)

        data = await state.get_data()
        deals = data.get("deals") or []
        end_cursor = data.get("deals_end_cursor")
        is_all_deals_loaded = data.get("is_all_deals_loaded") or False
        
        deals_filter = data.get("deals_filter")
        last_deals_filter = data.get("last_deals_filter")

        if not deals_filter:
            deals_filter = {"direction": None, "statuses": []}
            await state.update_data(deals_filter=deals_filter)

        await state.update_data(last_deals_filter=copy.deepcopy(deals_filter))

        next_page_start = (page + 1) * 12
        need_more = len(deals) < next_page_start + 1
        filter_updated = deals_filter != last_deals_filter

        if upd:
            end_cursor = None

        if (not is_all_deals_loaded and need_more) or filter_updated or upd:
            await throw_float_message(state, callback.message, "⌛️")
            from plbot.playerokbot import get_playerok_bot as plbot
            
            deal_lst = plbot().account.get_deals(
                count=24, 
                direction=deals_filter["direction"],
                statuses=deals_filter["statuses"] or None,
                after_cursor=end_cursor
            )

            if filter_updated or upd:
                deals = deal_lst.deals
            else:
                deals.extend(deal_lst.deals or [])

            if len(deal_lst.deals or []) < 24:
                is_all_deals_loaded = True

            await state.update_data(
                is_all_deals_loaded=is_all_deals_loaded,
                deals_end_cursor=deal_lst.page_info.end_cursor,
                deals=deals
            )
        
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.deals_text(deals, page),
            reply_markup=templ.deals_kb(deals, page),
            callback=callback
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.deals_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="default").pack()),
            callback=callback
        )


@router.callback_query(calls.SelMessageTemplatePagination.filter())
async def callback_sel_message_template_pagination(callback: CallbackQuery, callback_data: calls.SelMessageTemplatePagination, state: FSMContext):
    try:
        await state.set_state(None)
        data = await state.get_data()
        
        from plbot.playerokbot import get_playerok_bot as plbot
        acc = plbot().account
        
        deal_id = callback_data.id
        type_int = callback_data.type
        page = callback_data.page
        await state.update_data(deal_id=deal_id, last_page=page)

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
            await throw_float_message(state, callback.message, "⌛️")
            mt_list = acc.get_message_templates(count=24, type=type)
            mt = mt_list.message_templates
            await state.update_data(mts=mt)
        
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.deal_float_text("🗂️ Выберите <b>категорию проблемы</b>:"),
            reply_markup=templ.sel_message_template_kb(mt, deal_id, page),
            callback=callback
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.deal_float_text(e),
            reply_markup=templ.back_kb(calls.DealPage(id=deal_id).pack()),
            callback=callback
        )


@router.callback_query(calls.FastSelMessageTemplatePagination.filter())
async def callback_fast_sel_message_template_pagination(callback: CallbackQuery, callback_data: calls.FastSelMessageTemplatePagination, state: FSMContext):
    try:
        await state.set_state(None)
        data = await state.get_data()
        
        from plbot.playerokbot import get_playerok_bot as plbot
        acc = plbot().account
        
        deal_id = callback_data.id
        type_int = callback_data.type
        page = callback_data.page
        await state.update_data(deal_id=deal_id, last_page=page)

        if type_int == 0:
            type = MessageTemplateTypes.ACTIVE_DEAL_PROBLEM
        else:
            type = MessageTemplateTypes.FINISHED_DEAL_PROBLEM

        data = await state.get_data()
        mt = data.get("mts") or []

        if not mt:
            await throw_float_message(state, callback.message, "⌛️")
            mt_list = acc.get_message_templates(count=24, type=type)
            mt = mt_list.message_templates
            await state.update_data(mts=mt)
        
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.deal_float_text("🗂️ Выберите <b>категорию проблемы</b>:"),
            reply_markup=templ.fast_sel_message_template_kb(mt, page),
            callback=callback
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.deal_float_text(e),
            reply_markup=templ.back_kb(calls.DealPage(id=deal_id).pack()),
            callback=callback
        )


@router.callback_query(calls.ItemsPagination.filter())
async def callback_items_pagination(callback: CallbackQuery, callback_data: calls.ItemsPagination, state: FSMContext):
    try:
        await state.set_state(None)
        
        page = callback_data.page
        upd = callback_data.upd
        await state.update_data(last_page=page)

        data = await state.get_data()
        items = data.get("items") or []
        end_cursor = data.get("items_end_cursor")
        is_all_items_loaded = data.get("is_all_items_loaded") or False
        
        items_filter = data.get("items_filter")
        last_items_filter = data.get("last_items_filter")

        if not items_filter:
            items_filter = {"statuses": [], "game_id": None, "game_name": None, "category_id": None, "category_name": None}
            await state.update_data(items_filter=items_filter)

        await state.update_data(last_items_filter=copy.deepcopy(items_filter))

        next_page_start = (page + 1) * 12
        need_more = len(items) < next_page_start + 1
        filter_updated = items_filter != last_items_filter

        if upd:
            end_cursor = None

        if (not is_all_items_loaded and need_more) or filter_updated or upd:
            await throw_float_message(state, callback.message, "⌛️")
            from plbot.playerokbot import get_playerok_bot as plbot
            
            item_lst = plbot().account.get_my_items(
                game_id=items_filter["game_id"],
                category_id=items_filter["category_id"],
                statuses=items_filter["statuses"] or None,
                count=24, 
                after_cursor=end_cursor
            )

            if filter_updated or upd:
                items = item_lst.items
            else:
                items.extend(item_lst.items or [])

            if len(item_lst.items or []) < 24:
                is_all_items_loaded = True

            await state.update_data(
                is_all_items_loaded=is_all_items_loaded,
                items_end_cursor=item_lst.page_info.end_cursor,
                items=items
            )
        
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.items_text(items, page),
            reply_markup=templ.items_kb(items, page),
            callback=callback
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.items_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="default").pack()),
            callback=callback
        )


@router.callback_query(calls.TransactionsPagination.filter())
async def callback_transactions_pagination(callback: CallbackQuery, callback_data: calls.TransactionsPagination, state: FSMContext):
    try:
        await state.set_state(None)
        
        page = callback_data.page
        upd = callback_data.upd
        await state.update_data(last_page=page)

        data = await state.get_data()
        transactions = data.get("transactions") or []
        end_cursor = data.get("transactions_end_cursor")
        is_all_transactions_loaded = data.get("is_all_transactions_loaded") or False
        
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

        next_page_start = (page + 1) * 12
        need_more = len(transactions) < next_page_start + 1
        filter_updated = transactions_filter != last_transactions_filter

        if upd:
            end_cursor = None

        if (not is_all_transactions_loaded and need_more) or filter_updated or upd:
            await throw_float_message(state, callback.message, "⌛️")
            from plbot.playerokbot import get_playerok_bot as plbot
            
            transaction_lst = plbot().account.get_transactions(
                status=transactions_filter["status"],
                operation=transactions_filter["operation"],
                provider_id=transactions_filter["provider_id"],
                min_value=transactions_filter["min_value"],
                max_value=transactions_filter["max_value"],
                from_date=transactions_filter["from_date"],
                to_date=transactions_filter["to_date"],
                count=24, 
                after_cursor=end_cursor
            )

            if filter_updated or upd:
                transactions = transaction_lst.transactions
            else:
                transactions.extend(transaction_lst.transactions or [])

            if len(transaction_lst.transactions or []) < 24:
                is_all_transactions_loaded = True

            await state.update_data(
                is_all_transactions_loaded=is_all_transactions_loaded,
                transactions_end_cursor=transaction_lst.page_info.end_cursor,
                transactions=transactions
            )
        
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.transactions_text(transactions, page),
            reply_markup=templ.transactions_kb(transactions, page),
            callback=callback
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.transactions_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="default").pack()),
            callback=callback
        )


@router.callback_query(calls.ReviewsPagination.filter())
async def callback_reviews_pagination(callback: CallbackQuery, callback_data: calls.ReviewsPagination, state: FSMContext):
    try:
        await state.set_state(None)
        
        page = callback_data.page
        upd = callback_data.upd
        await state.update_data(last_page=page)

        data = await state.get_data()
        reviews = data.get("reviews") or []
        end_cursor = data.get("reviews_end_cursor")
        is_all_reviews_loaded = data.get("is_all_reviews_loaded") or False
        
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

        next_page_start = (page + 1) * 12
        need_more = len(reviews) < next_page_start + 1
        filter_updated = reviews_filter != last_reviews_filter

        if upd:
            end_cursor = None

        if (not is_all_reviews_loaded and need_more) or filter_updated or upd:
            await throw_float_message(state, callback.message, "⌛️")
            from plbot.playerokbot import get_playerok_bot as plbot
            
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
                after_cursor=end_cursor
            )

            if filter_updated or upd:
                reviews = review_lst.reviews
            else:
                reviews.extend(review_lst.reviews or [])

            if len(review_lst.reviews or []) < 24:
                is_all_reviews_loaded = True

            await state.update_data(
                is_all_reviews_loaded=is_all_reviews_loaded,
                reviews_end_cursor=review_lst.page_info.end_cursor,
                reviews=reviews
            )
        
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.reviews_text(reviews, page),
            reply_markup=templ.reviews_kb(reviews, page),
            callback=callback
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.reviews_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="default").pack()),
            callback=callback
        )