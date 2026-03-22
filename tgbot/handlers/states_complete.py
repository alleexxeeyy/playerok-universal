from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from settings import Settings as sett

from .. import templates as templ
from .. import callback_datas as calls
from .. import states
from ..helpful import throw_float_message


router = Router()


@router.message(states.CompleteDealsStates.waiting_for_new_included_complete_deal_keyphrases, F.text)
async def handler_waiting_for_new_included_complete_deal_keyphrases(message: types.Message, state: FSMContext):
    try: 
        await state.set_state(None)
        
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        
        if len(message.text) <= 0:
            raise Exception("❌ Слишком короткое значение")
        
        keyphrases = [phrase.strip() for phrase in message.text.split(",") if phrase.strip()]
        
        auto_complete_deals = sett.get("auto_complete_deals")
        auto_complete_deals["included"].append(keyphrases)
        sett.set("auto_complete_deals", auto_complete_deals)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_complete_included_float_text(
                "✅ Предмет успешно включён в подтверждение"
            ),
            reply_markup=templ.back_kb(calls.IncludedCompleteDealsPagination(page=last_page).pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_complete_included_float_text(e), 
            reply_markup=templ.back_kb(calls.IncludedCompleteDealsPagination(page=last_page).pack())
        )


@router.message(
    states.CompleteDealsStates.waiting_for_new_included_complete_deals_keyphrases_file, 
    F.document.file_name.lower().endswith('.txt')
)
async def handler_waiting_for_new_included_complete_deals_keyphrases_file(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        
        file = await message.bot.get_file(message.document.file_id)
        downloaded_file = await message.bot.download_file(file.file_path)
        file_content = downloaded_file.read().decode('utf-8')

        keyphrases_list = []
        for line in file_content.splitlines():
            line = line.strip()
            if len(line) > 0:
                keyphrases = [phrase.strip() for phrase in line.split(",") if phrase.strip()]
                if len(keyphrases) > 0:
                    keyphrases_list.append(keyphrases)

        if len(keyphrases_list) <= 0:
            raise Exception("❌ Файл не содержит валидных ключевых фраз")

        auto_complete_deals = sett.get("auto_complete_deals")
        auto_complete_deals["included"].extend(keyphrases_list)
        sett.set("auto_complete_deals", auto_complete_deals)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_complete_included_float_text(
                f"✅ Успешно включено <b>{len(keyphrases_list)} предметов</b> из файла в подтверждение"
            ),
            reply_markup=templ.back_kb(calls.IncludedCompleteDealsPagination(page=last_page).pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_complete_included_float_text(e), 
            reply_markup=templ.back_kb(calls.IncludedCompleteDealsPagination(page=last_page).pack())
        )


@router.message(states.CompleteDealsStates.waiting_for_new_excluded_complete_deal_keyphrases, F.text)
async def handler_waiting_for_new_excluded_complete_deal_keyphrases(message: types.Message, state: FSMContext):
    try: 
        await state.set_state(None)
        
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        
        if len(message.text) <= 0:
            raise Exception("❌ Слишком короткое значение")
        
        keyphrases = [phrase.strip() for phrase in message.text.split(",") if phrase.strip()]
        
        auto_complete_deals = sett.get("auto_complete_deals")
        auto_complete_deals["excluded"].append(keyphrases)
        sett.set("auto_complete_deals", auto_complete_deals)
    
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_complete_excluded_float_text(
                "✅ Предмет успешно добавлен в исключения для подтверждения"
            ),
            reply_markup=templ.back_kb(calls.ExcludedCompleteDealsPagination(page=last_page).pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_complete_excluded_float_text(e), 
            reply_markup=templ.back_kb(calls.ExcludedCompleteDealsPagination(page=last_page).pack())
        )


@router.message(
    states.CompleteDealsStates.waiting_for_new_excluded_complete_deals_keyphrases_file, 
    F.document.file_name.lower().endswith('.txt')
)
async def handler_waiting_for_new_excluded_complete_deals_keyphrases_file(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        
        file = await message.bot.get_file(message.document.file_id)
        downloaded_file = await message.bot.download_file(file.file_path)
        file_content = downloaded_file.read().decode('utf-8')

        keyphrases_list = []
        for line in file_content.splitlines():
            line = line.strip()
            if len(line) > 0:
                keyphrases = [phrase.strip() for phrase in line.split(",") if phrase.strip()]
                if len(keyphrases) > 0:
                    keyphrases_list.append(keyphrases)

        if len(keyphrases_list) <= 0:
            raise Exception("❌ Файл не содержит валидных ключевых фраз")

        auto_complete_deals = sett.get("auto_complete_deals")
        auto_complete_deals["excluded"].extend(keyphrases_list)
        sett.set("auto_complete_deals", auto_complete_deals)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_complete_excluded_float_text(
                f"✅ Успешно добавлено <b>{len(keyphrases_list)} предметов</b> из файла в исключения для подтверждения"
            ),
            reply_markup=templ.back_kb(calls.ExcludedCompleteDealsPagination(page=last_page).pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_complete_excluded_float_text(e), 
            reply_markup=templ.back_kb(calls.ExcludedCompleteDealsPagination(page=last_page).pack())
        )