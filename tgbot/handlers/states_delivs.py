from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from settings import Settings as sett

from .. import templates as templ
from .. import states
from .. import callback_datas as calls
from ..helpful import throw_float_message


router = Router()


@router.message(states.AutoDeliveriesStates.waiting_for_page, F.text)
async def handler_waiting_for_auto_deliveries_page(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if not message.text.strip().isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")
        
        await state.update_data(last_page=int(message.text.strip())-1)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_delivs_float_text(f"📃 Введите номер страницы для перехода ↓"),
            reply_markup=templ.settings_delivs_kb(int(message.text)-1)
        )
    except Exception as e:
        data = await state.get_data()
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_delivs_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=data.get("last_page", 0)).pack())
        )


@router.message(states.AutoDeliveriesStates.waiting_for_new_auto_delivery_keyphrases, F.text)
async def handler_waiting_for_new_auto_delivery_keyphrases(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком короткое значение")
        
        data = await state.get_data()
        keyphrases = [phrase.strip() for phrase in message.text.strip().split(",")]
        await state.update_data(new_auto_delivery_keyphrases=keyphrases)

        await state.set_state(states.AutoDeliveriesStates.waiting_for_new_auto_delivery_message)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_deliv_float_text(f"💬 Введите <b>сообщение авто-выдачи</b>, которое будет писаться после покупки лота ↓"),
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=data.get("last_page", 0)).pack())
        )
    except Exception as e:
        data = await state.get_data()
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_deliv_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=data.get("last_page", 0)).pack())
        )
        

@router.message(states.AutoDeliveriesStates.waiting_for_new_auto_delivery_message, F.text)
async def handler_waiting_for_new_auto_delivery_message(message: types.Message, state: FSMContext):
    try:
        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком короткое значение")

        data = await state.get_data()
        await state.update_data(new_auto_delivery_message=message.text.strip())

        keyphrases = "</code>, <code>".join(data.get("new_auto_delivery_keyphrases"))
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_deliv_float_text(f"➕ Подтвердите <b>добавление авто-выдачи</b> с ключевыми фразами <code>{keyphrases}</code>"),
            reply_markup=templ.confirm_kb(confirm_cb="add_new_auto_delivery", cancel_cb=calls.AutoDeliveriesPagination(page=data.get("last_page", 0)).pack())
        )
    except Exception as e:
        data = await state.get_data()
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_deliv_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=data.get("last_page", 0)).pack())
        )


@router.message(states.AutoDeliveriesStates.waiting_for_auto_delivery_keyphrases, F.text)
async def handler_waiting_for_auto_delivery_keyphrases(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком короткое значение")

        data = await state.get_data()
        auto_deliveries = sett.get("auto_deliveries")
        keyphrases = [phrase.strip() for phrase in message.text.strip().split(",")]
        auto_deliveries[data.get("auto_delivery_index")]["keyphrases"] = keyphrases
        sett.set("auto_deliveries", auto_deliveries)
        
        keyphrases = "</code>, <code>".join(keyphrases)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_deliv_page_float_text(f"✅ <b>Ключевые фразы</b> были успешно изменены на: <code>{keyphrases}</code>"),
            reply_markup=templ.back_kb(calls.AutoDeliveryPage(index=data.get("auto_delivery_index")).pack())
        )
    except Exception as e:
        data = await state.get_data()
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_deliv_page_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveryPage(index=data.get("auto_delivery_index")).pack())
        )


@router.message(states.AutoDeliveriesStates.waiting_for_auto_delivery_message, F.text)
async def handler_waiting_for_auto_delivery_message(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком короткий текст")

        data = await state.get_data()
        auto_deliveries = sett.get("auto_deliveries")
        auto_deliveries[data.get("auto_delivery_index")]["message"] = message.text.strip().splitlines()
        sett.set("auto_deliveries", auto_deliveries)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_deliv_page_float_text(f"✅ <b>Сообщение авто-выдачи</b> было успешно изменено на: <blockquote>{message.text.strip()}</blockquote>"),
            reply_markup=templ.back_kb(calls.AutoDeliveryPage(index=data.get("auto_delivery_index")).pack())
        )
    except Exception as e:
        data = await state.get_data()
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_deliv_page_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveryPage(index=data.get("auto_delivery_index")).pack())
        )