from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from settings import Settings as sett
from utils import escape_html, parse_day_time

from .. import templates as templ
from .. import callback_datas as calls
from .. import states
from ..helpful import throw_float_message, extract_lines, parse_keyphrases_lines


router = Router()

MAX_INTERVAL = 31536000
MAX_POSITION = 10000


@router.message(states.BumpItemsStates.waiting_for_bump_items_interval, F.text)
async def handler_waiting_for_bump_items_interval(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)

        if not message.text.isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")
        if int(message.text) <= 0:
            raise Exception("❌ Слишком низкое значение")
        if int(message.text) > MAX_INTERVAL:
            raise Exception("❌ Слишком высокое значение")

        interval = int(message.text)

        config = sett.get("config")
        config["playerok"]["auto_bump_items"]["interval"] = interval
        sett.set("config", config)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.bump_float_text(f"✅ <b>Интервал поднятия товаров</b> был успешно изменён на <b>{interval}</b>"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="bump").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.bump_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="bump").pack())
        )


@router.message(states.BumpItemsStates.waiting_for_bump_items_position, F.text)
async def handler_waiting_for_bump_items_position(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)

        if not message.text.isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")
        if int(message.text) <= 0:
            raise Exception("❌ Слишком низкое значение")
        if int(message.text) > MAX_POSITION:
            raise Exception("❌ Слишком высокое значение")

        position = int(message.text)

        config = sett.get("config")
        config["playerok"]["auto_bump_items"]["position"] = position
        sett.set("config", config)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.bump_float_text(f"✅ <b>Позиция поднятия товаров</b> была успешно изменена на <b>{position}</b>"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="bump").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.bump_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="bump").pack())
        )


@router.message(states.BumpItemsStates.waiting_for_bump_items_cooldown, F.text)
async def handler_waiting_for_bump_items_cooldown(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)

        if not message.text.isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")
        if int(message.text) <= 0:
            raise Exception("❌ Слишком низкое значение")
        if int(message.text) > MAX_INTERVAL:
            raise Exception("❌ Слишком высокое значение")

        cooldown = int(message.text)

        config = sett.get("config")
        config["playerok"]["auto_bump_items"]["cooldown"] = cooldown
        sett.set("config", config)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.bump_float_text(f"✅ <b>Кулдаун поднятия товара</b> был успешно изменён на <b>{cooldown}</b>"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="bump").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.bump_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="bump").pack())
        )


@router.message(states.BumpItemsStates.waiting_for_bump_items_night_interval, F.text)
async def handler_waiting_for_bump_items_night_interval(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)

        if not message.text.isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")
        if int(message.text) <= 0:
            raise Exception("❌ Слишком низкое значение")
        if int(message.text) > MAX_INTERVAL:
            raise Exception("❌ Слишком высокое значение")

        interval = int(message.text)

        config = sett.get("config")
        config["playerok"]["auto_bump_items"]["night"]["interval"] = interval
        sett.set("config", config)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.bump_float_text(f"✅ <b>Ночной интервал поднятия товаров</b> был успешно изменён на <b>{interval}</b>"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="bump").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.bump_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="bump").pack())
        )


@router.message(states.BumpItemsStates.waiting_for_bump_items_night_position, F.text)
async def handler_waiting_for_bump_items_night_position(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)

        if not message.text.isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")
        if int(message.text) <= 0:
            raise Exception("❌ Слишком низкое значение")
        if int(message.text) > MAX_POSITION:
            raise Exception("❌ Слишком высокое значение")

        position = int(message.text)

        config = sett.get("config")
        config["playerok"]["auto_bump_items"]["night"]["position"] = position
        sett.set("config", config)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.bump_float_text(f"✅ <b>Ночная позиция поднятия товаров</b> была успешно изменена на <b>{position}</b>"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="bump").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.bump_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="bump").pack())
        )


@router.message(states.BumpItemsStates.waiting_for_bump_items_night_time_from, F.text)
async def handler_waiting_for_bump_items_night_time_from(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)

        time_from = parse_day_time(message.text)
        if not time_from:
            raise Exception("❌ Неверный формат времени. Укажите его в формате <code>ЧЧ:ММ</code>, например, <code>23:00</code>")

        config = sett.get("config")
        if time_from == config["playerok"]["auto_bump_items"]["night"]["time_to"]:
            raise Exception("❌ Начало ночи не может совпадать с её концом")
        config["playerok"]["auto_bump_items"]["night"]["time_from"] = time_from
        sett.set("config", config)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.bump_float_text(f"✅ <b>Начало ночи</b> было успешно изменено на <b>{time_from}</b>"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="bump").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.bump_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="bump").pack())
        )


@router.message(states.BumpItemsStates.waiting_for_bump_items_night_time_to, F.text)
async def handler_waiting_for_bump_items_night_time_to(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)

        time_to = parse_day_time(message.text)
        if not time_to:
            raise Exception("❌ Неверный формат времени. Укажите его в формате <code>ЧЧ:ММ</code>, например, <code>08:00</code>")

        config = sett.get("config")
        if time_to == config["playerok"]["auto_bump_items"]["night"]["time_from"]:
            raise Exception("❌ Конец ночи не может совпадать с её началом")
        config["playerok"]["auto_bump_items"]["night"]["time_to"] = time_to
        sett.set("config", config)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.bump_float_text(f"✅ <b>Конец ночи</b> был успешно изменён на <b>{time_to}</b>"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="bump").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.bump_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="bump").pack())
        )


@router.message(states.BumpItemsStates.waiting_for_new_included_bump_item_keyphrases, F.text | F.document)
async def handler_waiting_for_new_included_bump_item_keyphrases(message: types.Message, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    try:
        await state.set_state(None)

        keyphrases_list = parse_keyphrases_lines(await extract_lines(message))

        auto_bump_items = sett.get("auto_bump_items")
        auto_bump_items["included"].extend(keyphrases_list)
        sett.set("auto_bump_items", auto_bump_items)

        if len(keyphrases_list) == 1:
            phrases = "</code>, <code>".join(escape_html(p) for p in keyphrases_list[0])
            text = f"✅ Товар с ключевыми фразами <code>{phrases}</code> успешно включён в поднятие"
        else:
            text = f"✅ Успешно включено <b>{len(keyphrases_list)}</b> товаров в поднятие"

        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_bump_included_float_text(text),
            reply_markup=templ.back_kb(calls.IncludedBumpItemsPagination(page=last_page).pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_bump_included_float_text(e),
            reply_markup=templ.back_kb(calls.IncludedBumpItemsPagination(page=last_page).pack())
        )


@router.message(states.BumpItemsStates.waiting_for_new_excluded_bump_item_keyphrases, F.text | F.document)
async def handler_waiting_for_new_excluded_bump_item_keyphrases(message: types.Message, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    try:
        await state.set_state(None)

        keyphrases_list = parse_keyphrases_lines(await extract_lines(message))

        auto_bump_items = sett.get("auto_bump_items")
        auto_bump_items["excluded"].extend(keyphrases_list)
        sett.set("auto_bump_items", auto_bump_items)

        if len(keyphrases_list) == 1:
            phrases = "</code>, <code>".join(escape_html(p) for p in keyphrases_list[0])
            text = f"✅ Товар с ключевыми фразами <code>{phrases}</code> успешно исключён из поднятия"
        else:
            text = f"✅ Успешно исключено <b>{len(keyphrases_list)}</b> товаров из поднятия"

        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_bump_excluded_float_text(text),
            reply_markup=templ.back_kb(calls.ExcludedBumpItemsPagination(page=last_page).pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_bump_excluded_float_text(e),
            reply_markup=templ.back_kb(calls.ExcludedBumpItemsPagination(page=last_page).pack())
        )
