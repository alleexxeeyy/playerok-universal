from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from settings import Settings as sett
from utils import escape_html

from .. import templates as templ
from .. import callback_datas as calls
from .. import states
from ..helpful import throw_float_message, extract_lines, parse_keyphrases_lines


router = Router()


@router.message(
    states.RestoreItemsStates.waiting_for_new_included_restore_item_keyphrases,
    F.text | F.document
)
async def handler_waiting_for_new_included_restore_item_keyphrases(message: types.Message, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    try:
        await state.set_state(None)

        keyphrases_list = parse_keyphrases_lines(await extract_lines(message))

        auto_restore_items = sett.get("auto_restore_items")
        auto_restore_items["included"].extend(keyphrases_list)
        sett.set("auto_restore_items", auto_restore_items)

        if len(keyphrases_list) > 1:
            text = f"✅ Успешно включено <b>{len(keyphrases_list)}</b> товаров в восстановление"
        else:
            phrases = "</code>, <code>".join(escape_html(p) for p in keyphrases_list[0])
            text = f"✅ Товар с ключевыми фразами <code>{phrases}</code> успешно включён в восстановление"

        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_restore_included_float_text(text),
            reply_markup=templ.back_kb(calls.IncludedRestoreItemsPagination(page=last_page).pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_restore_included_float_text(e),
            reply_markup=templ.back_kb(calls.IncludedRestoreItemsPagination(page=last_page).pack())
        )


@router.message(
    states.RestoreItemsStates.waiting_for_new_excluded_restore_item_keyphrases,
    F.text | F.document
)
async def handler_waiting_for_new_excluded_restore_item_keyphrases(message: types.Message, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    try:
        await state.set_state(None)

        keyphrases_list = parse_keyphrases_lines(await extract_lines(message))

        auto_restore_items = sett.get("auto_restore_items")
        auto_restore_items["excluded"].extend(keyphrases_list)
        sett.set("auto_restore_items", auto_restore_items)

        if len(keyphrases_list) > 1:
            text = f"✅ Успешно добавлено <b>{len(keyphrases_list)}</b> товаров в исключения для восстановления"
        else:
            phrases = "</code>, <code>".join(escape_html(p) for p in keyphrases_list[0])
            text = f"✅ Товар с ключевыми фразами <code>{phrases}</code> успешно добавлен в исключения для восстановления"

        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_restore_excluded_float_text(text),
            reply_markup=templ.back_kb(calls.ExcludedRestoreItemsPagination(page=last_page).pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_restore_excluded_float_text(e),
            reply_markup=templ.back_kb(calls.ExcludedRestoreItemsPagination(page=last_page).pack())
        )
