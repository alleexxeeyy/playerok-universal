from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from settings import Settings as sett
from utils import split_new_items

from .. import templates as templ
from .. import callback_datas as calls
from .. import states
from ..helpful import (
    throw_float_message,
    extract_lines,
    resolve_item_lines,
    item_refs_report
)


router = Router()


@router.message(states.CompleteDealsStates.waiting_for_new_included_complete_deal_items, F.text | F.document)
async def handler_waiting_for_new_included_complete_deal_items(message: types.Message, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    try:
        await state.set_state(None)

        items, errors = await resolve_item_lines(await extract_lines(message))

        auto_complete_deals = sett.get("auto_complete_deals")
        items, dupes = split_new_items(items, auto_complete_deals["included"])
        text = item_refs_report(
            items, errors + dupes,
            "✅ Товар <b>{name}</b> успешно включён в авто-подтверждение",
            "✅ Успешно включено <b>{count}</b> товаров в авто-подтверждение"
        )

        auto_complete_deals["included"].extend({"items": [item]} for item in items)
        sett.set("auto_complete_deals", auto_complete_deals)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_complete_included_float_text(text),
            reply_markup=templ.back_kb(calls.IncludedCompleteDealsPagination(page=last_page).pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_complete_included_float_text(e),
            reply_markup=templ.back_kb(calls.IncludedCompleteDealsPagination(page=last_page).pack())
        )


@router.message(states.CompleteDealsStates.waiting_for_new_excluded_complete_deal_items, F.text | F.document)
async def handler_waiting_for_new_excluded_complete_deal_items(message: types.Message, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    try:
        await state.set_state(None)

        items, errors = await resolve_item_lines(await extract_lines(message))

        auto_complete_deals = sett.get("auto_complete_deals")
        items, dupes = split_new_items(items, auto_complete_deals["excluded"])
        text = item_refs_report(
            items, errors + dupes,
            "✅ Товар <b>{name}</b> успешно исключён из авто-подтверждения",
            "✅ Успешно исключено <b>{count}</b> товаров из авто-подтверждения"
        )

        auto_complete_deals["excluded"].extend({"items": [item]} for item in items)
        sett.set("auto_complete_deals", auto_complete_deals)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_complete_excluded_float_text(text),
            reply_markup=templ.back_kb(calls.ExcludedCompleteDealsPagination(page=last_page).pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_complete_excluded_float_text(e),
            reply_markup=templ.back_kb(calls.ExcludedCompleteDealsPagination(page=last_page).pack())
        )
