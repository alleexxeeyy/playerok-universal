from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from settings import Settings as sett

from .. import templates as templ
from .. import callback_datas as calls
from .. import states
from ..helpful import throw_float_message


router = Router()


@router.message(states.RestoreItemsStates.waiting_for_new_included_restore_item_keyphrases, F.text)
async def handler_waiting_for_new_included_restore_item_keyphrases(message: types.Message, state: FSMContext):
    try: 
        await state.set_state(None)
        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком короткое значение")
        
        keyphrases = [phrase.strip() for phrase in message.text.strip().split(",") if len(phrase.strip()) > 0]
        auto_restore_items = sett.get("auto_restore_items")
        auto_restore_items["included"].append(keyphrases)
        sett.set("auto_restore_items", auto_restore_items)

        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_restore_included_float_text(f"✅ Предмет с ключевыми фразами <code>{'</code>, <code>'.join(keyphrases)}</code> успешно включён в восстановление"),
            reply_markup=templ.back_kb(calls.IncludedRestoreItemsPagination(page=last_page).pack())
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_restore_included_float_text(e), 
            reply_markup=templ.back_kb(calls.IncludedRestoreItemsPagination(page=last_page).pack())
        )


@router.message(
    states.RestoreItemsStates.waiting_for_new_included_restore_items_keyphrases_file, 
    F.document.file_name.lower().endswith('.txt')
)
async def handler_waiting_for_new_included_restore_items_keyphrases_file(message: types.Message, state: FSMContext):
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

        auto_restore_items = sett.get("auto_restore_items")
        auto_restore_items["included"].extend(keyphrases_list)
        sett.set("auto_restore_items", auto_restore_items)

        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_restore_included_float_text(f"✅ Успешно включено <b>{len(keyphrases_list)}</b> предметов из файла в восстановление"),
            reply_markup=templ.back_kb(calls.IncludedRestoreItemsPagination(page=last_page).pack())
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_restore_included_float_text(e), 
            reply_markup=templ.back_kb(calls.IncludedRestoreItemsPagination(page=last_page).pack())
        )


@router.message(states.RestoreItemsStates.waiting_for_new_excluded_restore_item_keyphrases, F.text)
async def handler_waiting_for_new_excluded_restore_item_keyphrases(message: types.Message, state: FSMContext):
    try: 
        await state.set_state(None)
        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком короткое значение")
        
        keyphrases = [phrase.strip() for phrase in message.text.strip().split(",") if len(phrase.strip()) > 0]
        auto_restore_items = sett.get("auto_restore_items")
        auto_restore_items["excluded"].append(keyphrases)
        sett.set("auto_restore_items", auto_restore_items)
    
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_restore_excluded_float_text(f"✅ Предмет с ключевыми фразами <code>{'</code>, <code>'.join(keyphrases)}</code> успешно добавлен в исключения для восстановления"),
            reply_markup=templ.back_kb(calls.ExcludedRestoreItemsPagination(page=last_page).pack())
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_restore_excluded_float_text(e), 
            reply_markup=templ.back_kb(calls.ExcludedRestoreItemsPagination(page=last_page).pack())
        )


@router.message(
    states.RestoreItemsStates.waiting_for_new_excluded_restore_items_keyphrases_file, 
    F.document.file_name.lower().endswith('.txt')
)
async def handler_waiting_for_new_excluded_restore_items_keyphrases_file(message: types.Message, state: FSMContext):
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

        auto_restore_items = sett.get("auto_restore_items")
        auto_restore_items["excluded"].extend(keyphrases_list)
        sett.set("auto_restore_items", auto_restore_items)

        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_restore_excluded_float_text(f"✅ Успешно добавлено <b>{len(keyphrases_list)}</b> предметов из файла в исключения для восстановления"),
            reply_markup=templ.back_kb(calls.ExcludedRestoreItemsPagination(page=last_page).pack())
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_restore_excluded_float_text(e), 
            reply_markup=templ.back_kb(calls.ExcludedRestoreItemsPagination(page=last_page).pack())
        )