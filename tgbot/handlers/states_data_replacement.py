from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from settings import Settings as sett
from utils import escape_html

from .. import templates as templ
from .. import states
from .. import callback_datas as calls
from ..helpful import throw_float_message, extract_lines


router = Router()


@router.message(states.DataReplacementStates.waiting_for_page, F.text)
async def handler_waiting_for_data_replacements_page(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)

        if not message.text.isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")

        page = int(message.text) - 1
        await state.update_data(last_page=page)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.data_replacements_text(),
            reply_markup=templ.data_replacements_kb(page)
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.data_replacements_float_text(e),
            reply_markup=templ.back_kb(calls.DataReplacementsPagination(page=last_page).pack())
        )


@router.message(states.DataReplacementStates.waiting_for_new_data_replacement_keyphrases, F.text)
async def handler_waiting_for_new_data_replacement_keyphrases(message: types.Message, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    try:
        await state.set_state(None)

        keyphrases = [phrase.strip() for phrase in message.text.split(",") if phrase.strip()]
        if not keyphrases:
            raise Exception("❌ Не удалось извлечь ключевые фразы")

        await state.update_data(new_data_replacement_keyphrases=keyphrases)
        await state.set_state(states.DataReplacementStates.waiting_for_new_data_replacement_values)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_data_replacement_float_text(
                f"💽 Отправьте <b>данные</b> для замены (1 строка = 1 набор данных для одного товара, "
                f"значения разделяются двоеточием, например, \"login:password:mail\"):"
                f"\n\n📄 Можно прислать <b>.txt файл</b>"
            ),
            reply_markup=templ.back_kb(calls.DataReplacementsPagination(page=last_page).pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_data_replacement_float_text(e),
            reply_markup=templ.back_kb(calls.DataReplacementsPagination(page=last_page).pack())
        )


@router.message(states.DataReplacementStates.waiting_for_new_data_replacement_values, F.text | F.document)
async def handler_waiting_for_new_data_replacement_values(message: types.Message, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    try:
        await state.set_state(None)

        values = await extract_lines(message)
        await state.update_data(new_data_replacement_values=values)

        keyphrases = data.get("new_data_replacement_keyphrases") or []
        phrases = "</code>, <code>".join(escape_html(p) for p in keyphrases)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_data_replacement_float_text(
                f"✔️ Подтвердите <b>добавление замены данных</b>:"
                f"\n\n<b>· Ключевые фразы:</b> <code>{phrases}</code>"
                f"\n<b>· Разделитель:</b> <code>:</code>"
                f"\n<b>· Данные:</b> {len(values)} шт."
            ),
            reply_markup=templ.confirm_kb(
                confirm_cb="add_new_data_replacement",
                cancel_cb=calls.DataReplacementsPagination(page=last_page).pack()
            )
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_data_replacement_float_text(e),
            reply_markup=templ.back_kb(calls.DataReplacementsPagination(page=last_page).pack())
        )


@router.message(states.DataReplacementStates.waiting_for_data_replacement_keyphrases, F.text)
async def handler_waiting_for_data_replacement_keyphrases(message: types.Message, state: FSMContext):
    data = await state.get_data()
    index = data.get("data_replacement_index")
    try:
        await state.set_state(None)

        keyphrases = [phrase.strip() for phrase in message.text.split(",") if phrase.strip()]
        if not keyphrases:
            raise Exception("❌ Не удалось извлечь ключевые фразы")

        data_replacement = sett.get("data_replacement")
        data_replacement[index]["keyphrases"] = keyphrases
        sett.set("data_replacement", data_replacement)

        keyphrases_str = "</code>, <code>".join(escape_html(p) for p in keyphrases)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.data_replacement_float_text(f"✅ <b>Ключевые фразы</b> были успешно изменены на: <code>{keyphrases_str}</code>"),
            reply_markup=templ.back_kb(calls.DataReplacementPage(index=index).pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.data_replacement_float_text(e),
            reply_markup=templ.back_kb(calls.DataReplacementPage(index=index).pack())
        )


@router.message(states.DataReplacementStates.waiting_for_data_replacement_separator, F.text)
async def handler_waiting_for_data_replacement_separator(message: types.Message, state: FSMContext):
    data = await state.get_data()
    index = data.get("data_replacement_index")
    try:
        await state.set_state(None)

        separator = message.text.strip()
        if not separator:
            raise Exception("❌ Разделитель не может быть пустым")

        data_replacement = sett.get("data_replacement")
        data_replacement[index]["separator"] = separator
        sett.set("data_replacement", data_replacement)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.data_replacement_float_text(f"✅ <b>Разделитель</b> был успешно изменён на: <code>{escape_html(separator)}</code>"),
            reply_markup=templ.back_kb(calls.DataReplacementPage(index=index).pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.data_replacement_float_text(e),
            reply_markup=templ.back_kb(calls.DataReplacementPage(index=index).pack())
        )


@router.message(states.DataReplacementStates.waiting_for_data_replacement_values_add, F.text | F.document)
async def handler_waiting_for_data_replacement_values_add(message: types.Message, state: FSMContext):
    data = await state.get_data()
    values_page = data.get("data_replacement_values_page", 0)
    index = data.get("data_replacement_index")
    try:
        await state.set_state(None)

        values = await extract_lines(message)

        data_replacement = sett.get("data_replacement")
        data_replacement[index].setdefault("data", []).extend(values)
        sett.set("data_replacement", data_replacement)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_data_replacement_values_float_text(
                f"✅ <b>{len(values)} строк данных</b> успешно добавлено в замену"
            ),
            reply_markup=templ.back_kb(calls.DataReplacementValuesPagination(page=values_page).pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_data_replacement_values_float_text(e),
            reply_markup=templ.back_kb(calls.DataReplacementValuesPagination(page=values_page).pack())
        )
