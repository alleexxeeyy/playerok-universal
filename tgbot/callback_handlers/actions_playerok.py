from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from playerokapi.enums import ItemDealStatuses
from settings import Settings as sett

from .. import templates as templ
from .. import callback_datas as calls
from .. import states
from ..helpful import throw_float_message

from .navigation import *
from .pagination import *
from .page import *


router = Router()


@router.callback_query(calls.FastSendFastReply.filter())
async def callback_fast_send_fast_reply(callback: CallbackQuery, callback_data: calls.FastSendFastReply, state: FSMContext):
    try:
        await state.set_state(None)

        chat_id = callback_data.id
        index = callback_data.index

        fast_replies = sett.get("fast_replies")
        reply_text = fast_replies[index]

        from plbot.playerokbot import get_playerok_bot as plbot
        acc = plbot().account

        acc.send_message(chat_id, reply_text)
        
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.do_action_text(
                f"✅ Быстрое сообщение <b>успешно отправлено</b>: <blockquote>{reply_text}</blockquote>"
            ),
            reply_markup=templ.destroy_kb()
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.do_action_text(e),
            reply_markup=templ.destroy_kb()
        )


@router.callback_query(calls.SendFastReply.filter())
async def callback_send_fast_reply(callback: CallbackQuery, callback_data: calls.SendFastReply, state: FSMContext):
    try:
        await state.set_state(None)
        data = await state.get_data()

        from plbot.playerokbot import get_playerok_bot as plbot
        acc = plbot().account

        chat_id = callback_data.id
        index = callback_data.index
        
        chat = data.get("chat")
        if not chat:
            chat = acc.get_chat(chat_id)

        fast_replies = sett.get("fast_replies")
        reply_text = fast_replies[index]

        acc.send_message(chat_id, reply_text)
        
        await callback_chat_page(callback, calls.ChatPage(id=chat_id), state)
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.chat_float_text(chat, e),
            reply_markup=templ.back_kb(calls.ChatPage(id=chat_id).pack())
        )


@router.callback_query(calls.FastChangeDealStatus.filter())
async def callback_fast_change_deal_status(callback: CallbackQuery, callback_data: calls.FastChangeDealStatus, state: FSMContext):
    try:
        await state.set_state(None)
        
        deal_id = callback_data.id
        status_str = callback_data.st

        from plbot.playerokbot import get_playerok_bot as plbot
        acc = plbot().account

        status = ItemDealStatuses.__members__.get(status_str)
        acc.update_deal(deal_id, status)

        if status == ItemDealStatuses.CONFIRMED:
            text = "✅ Сделка <b>успешно подтверждена</b>"
        elif status == ItemDealStatuses.ROLLED_BACK:
            text = "✅ По сделке <b>успешно оформлен возврат</b>"

        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.do_action_text(text),
            reply_markup=templ.destroy_kb(),
            reply_to=callback.message.message_id
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.do_action_text(e),
            reply_markup=templ.destroy_kb(),
            reply_to=callback.message.message_id
        )


@router.callback_query(calls.ChangeDealStatus.filter())
async def callback_change_deal_status(callback: CallbackQuery, callback_data: calls.ChangeDealStatus, state: FSMContext):
    try:
        await state.set_state(None)
        data = await state.get_data()

        from plbot.playerokbot import get_playerok_bot as plbot
        acc = plbot().account
        
        deal_id = callback_data.id
        status_str = callback_data.st

        deal = data.get("deal")
        if not deal:
            deal = acc.get_deal(deal_id)
    
        status = ItemDealStatuses.__members__.get(status_str)
        acc.update_deal(deal_id, status)

        await callback_deal_page(callback, calls.DealPage(id=deal_id), state)
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.deal_float_text(e),
            reply_markup=templ.destroy_kb()
        )


@router.callback_query(calls.FastSelMessageTemplate.filter())
async def callback_fast_sel_message_template(callback: CallbackQuery, callback_data: calls.FastSelMessageTemplate, state: FSMContext):
    await state.set_state(states.ActionsStates.waiting_for_fast_problem_description)
    data = await state.get_data()

    mts = data.get("mts")
    mt_id = callback_data.id
    await state.update_data(mt_id=mt_id)

    mt = next((mt for mt in mts if mt.id == mt_id), None)
    mt_str = f"<b>{mt.title}</b>\n{mt.text}"
    await state.update_data(mt_str=mt_str)

    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.do_action_text(
            f"<b>🗂️ Категория:</b>"
            f"<blockquote>{mt_str}</blockquote>"
            f"\n\n💬 Введите <b>описание проблемы</b>:"
        ),
        reply_markup=templ.destroy_kb()
    )


@router.callback_query(calls.SelMessageTemplate.filter())
async def callback_sel_message_template(callback: CallbackQuery, callback_data: calls.SelMessageTemplate, state: FSMContext):
    await state.set_state(states.ActionsStates.waiting_for_deal_problem_description)
    data = await state.get_data()

    from plbot.playerokbot import get_playerok_bot as plbot
    acc = plbot().account

    mts = data.get("mts")
    deal_id = data.get("deal_id")
    mt_id = callback_data.id
    await state.update_data(mt_id=mt_id)

    deal = data.get("deal")
    if not deal:
        deal = acc.get_deal(deal_id)

    mt = next((mt for mt in mts if mt.id == mt_id), None)
    mt_str = f"<b>{mt.title}</b>\n{mt.text}"
    await state.update_data(mt_str=mt_str)

    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.deal_float_text(
            f"<b>🗂️ Категория:</b>"
            f"<blockquote>{mt_str}</blockquote>"
            f"\n\n💬 Введите <b>описание проблемы</b>:"
        ),
        reply_markup=templ.back_kb(calls.DealPage(id=deal_id).pack())
    )


@router.callback_query(calls.FastReportDealProblem.filter())
async def callback_fast_report_deal_problem(callback: CallbackQuery, callback_data: calls.FastReportDealProblem, state: FSMContext):
    try:
        await state.set_state(None)
        data = await state.get_data()

        from plbot.playerokbot import get_playerok_bot as plbot
        acc = plbot().account

        deal_id = callback_data.id
        mt_id = data.get("mt_id")
        problem_desc = data.get("problem_desc")

        acc.report_deal_problem(deal_id, problem_desc, mt_id)

        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.do_action_text(
                f"✅ Проблема <b>успешно создана</b>"
            ),
            reply_markup=templ.destroy_kb()
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.do_action_text(e),
            reply_markup=templ.destroy_kb()
        )


@router.callback_query(calls.ReportDealProblem.filter())
async def callback_report_deal_problem(callback: CallbackQuery, callback_data: calls.ReportDealProblem, state: FSMContext):
    try:
        await state.set_state(None)
        data = await state.get_data()

        from plbot.playerokbot import get_playerok_bot as plbot
        acc = plbot().account

        deal_id = callback_data.id
        mt_id = data.get("mt_id")
        problem_desc = data.get("problem_desc")

        acc.report_deal_problem(deal_id, problem_desc, mt_id)

        await callback_deal_page(
            callback, calls.DealPage(id=deal_id), state
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.deal_float_text(e),
            reply_markup=templ.back_kb(calls.DealPage(id=deal_id).pack())
        )


@router.callback_query(calls.PublishItem.filter())
async def callback_publish_item(callback: CallbackQuery, callback_data: calls.PublishItem, state: FSMContext):
    try:
        await state.set_state(None)
        data = await state.get_data()

        item_id = callback_data.id
        status_id = data.get("item_pr_status_id")

        from plbot.playerokbot import get_playerok_bot as plbot
        plbot().account.publish_item(item_id, status_id)

        await callback_item_page(
            callback, calls.ItemPage(id=item_id), state
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.item_float_text(e),
            reply_markup=templ.back_kb(calls.ItemPage(id=item_id).pack())
        )


@router.callback_query(calls.IncreaseItemPriority.filter())
async def callback_increase_item_priority(callback: CallbackQuery, callback_data: calls.IncreaseItemPriority, state: FSMContext):
    try:
        await state.set_state(None)
        data = await state.get_data()

        item_id = callback_data.id
        status_id = data.get("item_pr_status_id")

        from plbot.playerokbot import get_playerok_bot as plbot
        plbot().account.increase_item_priority_status(item_id, status_id)

        await callback_item_page(
            callback, calls.ItemPage(id=item_id), state
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.item_float_text(e),
            reply_markup=templ.back_kb(calls.ItemPage(id=item_id).pack())
        )


@router.callback_query(calls.DeleteItem.filter())
async def callback_delete_item(callback: CallbackQuery, callback_data: calls.DeleteItem, state: FSMContext):
    try:
        await state.set_state(None)
        data = await state.get_data()

        item_id = callback_data.id
        item = data.get("item")
        last_page = data.get("last_page", 0)

        from plbot.playerokbot import get_playerok_bot as plbot
        plbot().account.remove_item(item_id)

        items = data.get("items")
        items.remove(item)
        await state.update_data(items=items)

        await callback_items_pagination(
            callback, calls.ItemsPagination(page=last_page), state
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.item_float_text(e),
            reply_markup=templ.back_kb(calls.ItemPage(id=item_id).pack())
        )