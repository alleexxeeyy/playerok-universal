from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from settings import Settings as sett

from .. import templates as templ
from .. import callback_datas as calls
from .. import states
from ..helpful import throw_float_message


router = Router()


@router.message(states.BumpItemsStates.waiting_for_day_max_sequence, F.text)
async def handler_waiting_for_day_max_sequence(message: types.Message, state: FSMContext):
    try: 
        await state.set_state(None)
        if not message.text.strip().isdigit():
            raise Exception("❌ Слишком короткое значение")

        day_max_sequence = int(message.text.strip())
        config = sett.get("config")
        config["playerok"]["auto_bump_items"]["day_max_sequence"] = day_max_sequence
        sett.set("config", config)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_bump_float_text(f"✅ <b>Максимальная позиция товара днём</b> была успешно изменена на <b>{day_max_sequence}</b>"),
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="bump").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_bump_float_text(e), 
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="bump").pack())
        )


@router.message(states.BumpItemsStates.waiting_for_night_max_sequence, F.text)
async def handler_waiting_for_night_max_sequence(message: types.Message, state: FSMContext):
    try: 
        await state.set_state(None)
        if not message.text.strip().isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")

        night_max_sequence = int(message.text.strip())
        config = sett.get("config")
        config["playerok"]["auto_bump_items"]["night_max_sequence"] = night_max_sequence
        sett.set("config", config)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_bump_float_text(f"✅ <b>Максимальная позиция товара ночью</b> была успешно изменена на <b>{night_max_sequence}</b>"),
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="bump").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_bump_float_text(e), 
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="bump").pack())
        )


@router.message(states.BumpItemsStates.waiting_for_new_included_bump_item_keyphrases, F.text)
async def handler_waiting_for_new_included_bump_item_keyphrases(message: types.Message, state: FSMContext):
    try: 
        await state.set_state(None)
        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком короткое значение")
        
        keyphrases = [phrase.strip() for phrase in message.text.strip().split(",") if len(phrase.strip()) > 0]
        auto_bump_items = sett.get("auto_bump_items")
        auto_bump_items["included"].append(keyphrases)
        sett.set("auto_bump_items", auto_bump_items)

        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_bump_included_float_text(f"✅ Предмет с ключевыми фразами <code>{'</code>, <code>'.join(keyphrases)}</code> успешно включён в поднятие"),
            reply_markup=templ.back_kb(calls.IncludedBumpItemsPagination(page=last_page).pack())
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_bump_included_float_text(e), 
            reply_markup=templ.back_kb(calls.IncludedBumpItemsPagination(page=last_page).pack())
        )


@router.message(
    states.BumpItemsStates.waiting_for_new_included_bump_items_keyphrases_file, 
    F.document.file_name.lower().endswith('.txt')
)
async def handler_waiting_for_new_included_bump_items_keyphrases_file(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        file = await message.bot.get_file(message.document.file_id)
        downloaded_file = await message.bot.download_file(file.file_path)
        file_content = downloaded_file.read().decode('utf-8')

        keyphrases_list = []
        for line in file_content.splitlines():
            line = line.strip()
            if len(line) > 0:
                keyphrases = [phrase.strip() for phrase in line.split(",") if len(phrase.strip()) > 0]
                if len(keyphrases) > 0:
                    keyphrases_list.append(keyphrases)

        if len(keyphrases_list) <= 0:
            raise Exception("❌ Файл не содержит валидных ключевых фраз")

        auto_bump_items = sett.get("auto_bump_items")
        auto_bump_items["included"].extend(keyphrases_list)
        sett.set("auto_bump_items", auto_bump_items)

        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_bump_included_float_text(f"✅ Успешно включено <b>{len(keyphrases_list)}</b> предметов из файла в поднятие"),
            reply_markup=templ.back_kb(calls.IncludedBumpItemsPagination(page=last_page).pack())
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_bump_included_float_text(e), 
            reply_markup=templ.back_kb(calls.IncludedBumpItemsPagination(page=last_page).pack())
        )


@router.message(states.BumpItemsStates.waiting_for_new_excluded_bump_item_keyphrases, F.text)
async def handler_waiting_for_new_excluded_bump_item_keyphrases(message: types.Message, state: FSMContext):
    try: 
        await state.set_state(None)
        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком короткое значение")
        
        keyphrases = [phrase.strip() for phrase in message.text.strip().split(",") if len(phrase.strip()) > 0]
        auto_bump_items = sett.get("auto_bump_items")
        auto_bump_items["excluded"].append(keyphrases)
        sett.set("auto_bump_items", auto_bump_items)

        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_bump_excluded_float_text(f"✅ Предмет с ключевыми фразами <code>{'</code>, <code>'.join(keyphrases)}</code> успешно добавлен в исключения для поднятия"),
            reply_markup=templ.back_kb(calls.ExcludedBumpItemsPagination(page=last_page).pack())
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_bump_excluded_float_text(e), 
            reply_markup=templ.back_kb(calls.ExcludedBumpItemsPagination(page=last_page).pack())
        )


@router.message(
    states.BumpItemsStates.waiting_for_new_excluded_bump_items_keyphrases_file, 
    F.document.file_name.lower().endswith('.txt')
)
async def handler_waiting_for_new_excluded_bump_items_keyphrases_file(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        file = await message.bot.get_file(message.document.file_id)
        downloaded_file = await message.bot.download_file(file.file_path)
        file_content = downloaded_file.read().decode('utf-8')

        keyphrases_list = []
        for line in file_content.splitlines():
            line = line.strip()
            if len(line) > 0:
                keyphrases = [phrase.strip() for phrase in line.split(",") if len(phrase.strip()) > 0]
                if len(keyphrases) > 0:
                    keyphrases_list.append(keyphrases)

        if len(keyphrases_list) <= 0:
            raise Exception("❌ Файл не содержит валидных ключевых фраз")

        auto_bump_items = sett.get("auto_bump_items")
        auto_bump_items["excluded"].extend(keyphrases_list)
        sett.set("auto_bump_items", auto_bump_items)

        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_bump_excluded_float_text(f"✅ Успешно добавлено <b>{len(keyphrases_list)}</b> предметов из файла в исключения для поднятия"),
            reply_markup=templ.back_kb(calls.ExcludedBumpItemsPagination(page=last_page).pack())
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_bump_excluded_float_text(e), 
            reply_markup=templ.back_kb(calls.ExcludedBumpItemsPagination(page=last_page).pack())
        )