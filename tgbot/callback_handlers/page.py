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
    await state.update_data(custom_command=command)
    
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.comm_page_text(command),
        reply_markup=templ.comm_page_kb(command, last_page),
        callback=callback
    )


@router.callback_query(calls.AutoDeliveryPage.filter())
async def callback_auto_delivery_page(callback: CallbackQuery, callback_data: calls.AutoDeliveryPage, state: FSMContext):
    await state.set_state(None)
    
    index = callback_data.index
    await state.update_data(auto_delivery_index=index)
    
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.deliv_page_text(index),
        reply_markup=templ.deliv_page_kb(index, last_page),
        callback=callback
    )
    

@router.callback_query(calls.MessagePage.filter())
async def callback_message_page(callback: CallbackQuery, callback_data: calls.MessagePage, state: FSMContext):
    await state.set_state(None)
    
    message_id = callback_data.message_id
    await state.update_data(message_id=message_id)
    
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.mess_page_text(message_id),
        reply_markup=templ.mess_page_kb(message_id, last_page),
        callback=callback
    )


@router.callback_query(calls.ModulePage.filter())
async def callback_module_page(callback: CallbackQuery, callback_data: calls.ModulePage, state: FSMContext):
    await state.set_state(None)
    
    module_uuid = callback_data.uuid
    await state.update_data(module_uuid=module_uuid)
    
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.module_page_text(module_uuid),
        reply_markup=templ.module_page_kb(module_uuid, last_page),
        callback=callback
    )


@router.callback_query(calls.ChatPage.filter())
async def callback_chat_page(callback: CallbackQuery, callback_data: calls.ChatPage, state: FSMContext):
    try:
        await state.set_state(None)
        await throw_float_message(state, callback.message, "⌛️")

        chat_id = callback_data.id
        await state.update_data(chat_id=chat_id)
        
        data = await state.get_data()
        last_page = data.get("last_page", 0)

        chats = data.get("chats") or []
        _chat = next((c for c in chats if c.id == chat_id), None)

        from plbot.playerokbot import get_playerok_bot as plbot
        acc = plbot().account
        
        chat = acc.get_chat(chat_id)
        msg_lst = acc.get_chat_messages(chat.id, count=12) or []
        msgs = [msg for msg in msg_lst.messages if msg][::-1]
        
        chat.last_message = msgs[-1]
        if _chat:
            chats[chats.index(_chat)] = chat

        await state.update_data(chats=chats, chat=chat)
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.chat_text(chat, msgs),
            reply_markup=templ.chat_kb(chat, last_page),
            callback=callback
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.chat_float_text(e),
            reply_markup=templ.back_kb(calls.ChatsPagination(page=last_page).pack()),
            callback=callback
        )


@router.callback_query(calls.DealPage.filter())
async def callback_deal_page(callback: CallbackQuery, callback_data: calls.DealPage, state: FSMContext):
    try:
        await state.set_state(None)
        await throw_float_message(state, callback.message, "⌛️")
        
        deal_id = callback_data.id
        await state.update_data(deal_id=deal_id)
        
        data = await state.get_data()
        last_page = data.get("last_page", 0)

        deals = data.get("deals") or []
        _deal = next((c for c in deals if c.id == deal_id), None)

        from plbot.playerokbot import get_playerok_bot as plbot
        acc = plbot().account
        
        deal = acc.get_deal(deal_id)
        if _deal:
            deals[deals.index(_deal)] = deal

        await state.update_data(deals=deals, deal=deal)
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.deal_text(deal),
            reply_markup=templ.deal_kb(deal, last_page),
            callback=callback
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.deal_float_text(e),
            reply_markup=templ.back_kb(calls.DealsPagination(page=last_page).pack()),
            callback=callback
        )


@router.callback_query(calls.ItemPage.filter())
async def callback_item_page(callback: CallbackQuery, callback_data: calls.ItemPage, state: FSMContext):
    try:
        await state.set_state(None)
        await throw_float_message(state, callback.message, "⌛️")
        
        item_id = callback_data.id
        await state.update_data(item_id=item_id)
        
        data = await state.get_data()
        last_page = data.get("last_page", 0)

        items = data.get("items") or []
        _item = next((c for c in items if c.id == item_id), None)

        from plbot.playerokbot import get_playerok_bot as plbot
        acc = plbot().account
        
        item = acc.get_item(item_id)
        if _item:
            items[items.index(_item)] = item

        await state.update_data(items=items, item=item)
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.item_text(item),
            reply_markup=templ.item_kb(item, last_page),
            callback=callback
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.item_float_text(e),
            reply_markup=templ.back_kb(calls.ItemsPagination(page=last_page).pack()),
            callback=callback
        )


@router.callback_query(calls.TransactionPage.filter())
async def callback_transaction_page(callback: CallbackQuery, callback_data: calls.TransactionPage, state: FSMContext):
    try:
        await state.set_state(None)
        await throw_float_message(state, callback.message, "⌛️")
        
        trans_id = callback_data.id
        await state.update_data(transaction_id=trans_id)
        
        data = await state.get_data()
        last_page = data.get("last_page", 0)

        transes = data.get("transactions") or []
        if not transes:
            from plbot.playerokbot import get_playerok_bot as plbot
            transes = plbot().account.get_transactions()
            await state.update_data(transactions=transes)

        trans = next((c for c in transes if c.id == trans_id), None)

        await state.update_data(transaction=trans)
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.transaction_text(trans),
            reply_markup=templ.transaction_kb(trans, last_page),
            callback=callback
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.transaction_float_text(e),
            reply_markup=templ.back_kb(calls.TransactionsPagination(page=last_page).pack()),
            callback=callback
        )


@router.callback_query(calls.ReviewPage.filter())
async def callback_review_page(callback: CallbackQuery, callback_data: calls.ReviewPage, state: FSMContext):
    try:
        await state.set_state(None)
        await throw_float_message(state, callback.message, "⌛️")
        
        review_id = callback_data.id
        await state.update_data(review_id=review_id)
        
        data = await state.get_data()
        last_page = data.get("last_page", 0)

        reviews = data.get("reviews") or []
        if not reviews:
            from plbot.playerokbot import get_playerok_bot as plbot
            reviews = plbot().account.get_my_reviews()
            await state.update_data(reviews=reviews)

        review = next((c for c in reviews if c.id == review_id), None)

        await state.update_data(review=review)
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.review_text(review),
            reply_markup=templ.review_kb(review, last_page),
            callback=callback
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.review_float_text(e),
            reply_markup=templ.back_kb(calls.ReviewsPagination(page=last_page).pack()),
            callback=callback
        )