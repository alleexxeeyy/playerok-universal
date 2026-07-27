from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from settings import Settings as sett
from utils import escape_html

from .. import templates as templ
from .. import callback_datas as calls
from .. import states
from ..helpful import throw_float_message, extract_lines, parse_keyphrases_lines


router = Router()


@router.message(states.CompleteDealsStates.waiting_for_new_included_complete_deal_keyphrases, F.text | F.document)
async def handler_waiting_for_new_included_complete_deal_keyphrases(message: types.Message, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    try:
        await state.set_state(None)

        keyphrases_list = parse_keyphrases_lines(await extract_lines(message))

        auto_complete_deals = sett.get("auto_complete_deals")
        auto_complete_deals["included"].extend(keyphrases_list)
        sett.set("auto_complete_deals", auto_complete_deals)

        if len(keyphrases_list) == 1:
            phrases = "</code>, <code>".join(escape_html(p) for p in keyphrases_list[0])
            text = f"✅ Товар с ключевыми фразами <code>{phrases}</code> успешно включён в авто-подтверждение"
        else:
            text = f"✅ Успешно включено <b>{len(keyphrases_list)}</b> товаров в авто-подтверждение"

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


@router.message(states.CompleteDealsStates.waiting_for_new_excluded_complete_deal_keyphrases, F.text | F.document)
async def handler_waiting_for_new_excluded_complete_deal_keyphrases(message: types.Message, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    try:
        await state.set_state(None)

        keyphrases_list = parse_keyphrases_lines(await extract_lines(message))

        auto_complete_deals = sett.get("auto_complete_deals")
        auto_complete_deals["excluded"].extend(keyphrases_list)
        sett.set("auto_complete_deals", auto_complete_deals)

        if len(keyphrases_list) == 1:
            phrases = "</code>, <code>".join(escape_html(p) for p in keyphrases_list[0])
            text = f"✅ Товар с ключевыми фразами <code>{phrases}</code> успешно исключён из авто-подтверждения"
        else:
            text = f"✅ Успешно исключено <b>{len(keyphrases_list)}</b> товаров из авто-подтверждения"

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
