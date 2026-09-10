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


@router.message(
    states.RestoreItemsStates.waiting_for_new_included_restore_items,
    F.text | F.document
)
async def handler_waiting_for_new_included_restore_items(message: types.Message, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    try:
        await state.set_state(None)

        items, errors = await resolve_item_lines(await extract_lines(message))

        auto_restore_items = sett.get("auto_restore_items")
        items, dupes = split_new_items(items, auto_restore_items["included"])
        text = item_refs_report(
            items, errors + dupes,
            "✅ Товар <b>{name}</b> успешно включён в восстановление",
            "✅ Успешно включено <b>{count}</b> товаров в восстановление"
        )

        auto_restore_items["included"].extend({"items": [item]} for item in items)
        sett.set("auto_restore_items", auto_restore_items)

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
    states.RestoreItemsStates.waiting_for_new_excluded_restore_items,
    F.text | F.document
)
async def handler_waiting_for_new_excluded_restore_items(message: types.Message, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    try:
        await state.set_state(None)

        items, errors = await resolve_item_lines(await extract_lines(message))

        auto_restore_items = sett.get("auto_restore_items")
        items, dupes = split_new_items(items, auto_restore_items["excluded"])
        text = item_refs_report(
            items, errors + dupes,
            "✅ Товар <b>{name}</b> успешно добавлен в исключения для восстановления",
            "✅ Успешно добавлено <b>{count}</b> товаров в исключения для восстановления"
        )

        auto_restore_items["excluded"].extend({"items": [item]} for item in items)
        sett.set("auto_restore_items", auto_restore_items)

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
