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
        
        if not message.text.isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")
        
        page = int(message.text) - 1
        await state.update_data(last_page=page)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_delivs_float_text(f"📃 Введите номер страницы для перехода:"),
            reply_markup=templ.settings_delivs_kb(page)
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_delivs_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
        )


@router.message(states.AutoDeliveriesStates.waiting_for_new_auto_delivery_keyphrases, F.text)
async def handler_waiting_for_new_auto_delivery_keyphrases(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        
        if len(message.text) <= 0:
            raise Exception("❌ Слишком короткое значение")
        
        keyphrases = [phrase.strip() for phrase in message.text.split(",")]
        
        await state.update_data(new_auto_delivery_keyphrases=keyphrases)
        await state.set_state(states.AutoDeliveriesStates.waiting_for_auto_delivery_piece)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_deliv_float_text(f"🛒 Выберите <b>тип авто-выдачи</b>:"),
            reply_markup=templ.settings_new_deliv_piece_kb(last_page)
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_deliv_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
        )
        

@router.message(states.AutoDeliveriesStates.waiting_for_new_auto_delivery_message, F.text)
async def handler_waiting_for_new_auto_delivery_message(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        
        if len(message.text) <= 0:
            raise Exception("❌ Слишком короткое значение")

        await state.update_data(new_auto_delivery_message=message.text)
        
        keyphrases = data.get("new_auto_delivery_keyphrases")
        phrases = "</code>, <code>".join(keyphrases)
        msg = message.text
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_deliv_float_text(
                f"✔️ Подтвердите <b>добавление авто-выдачи</b>:"
                f"\n<b>· Ключевые фразы:</b> <code>{phrases}</code>"
                f"\n<b>· Тип выдачи:</b> Сообщением"
                f"\n<b>· Сообщение:</b> {msg}"
            ),
            reply_markup=templ.confirm_kb(
                confirm_cb="add_new_auto_delivery", 
                cancel_cb=calls.AutoDeliveriesPagination(page=last_page).pack()
            )
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_deliv_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
        )
        

@router.message(states.AutoDeliveriesStates.waiting_for_new_auto_delivery_goods, F.text | F.document)
async def handler_waiting_for_new_auto_delivery_goods(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        
        if message.text:
            if len(message.text.strip()) == 0:
                raise Exception("❌ Слишком короткое значение")

            goods = [g.strip() for g in message.text.splitlines() if g.strip()]
        elif message.document:
            file = await message.bot.get_file(message.document.file_id)
            file_bytes = await message.bot.download_file(file.file_path)
            content = file_bytes.read().decode("utf-8", errors="ignore")

            if len(content.strip()) == 0:
                raise Exception("❌ Файл пустой")

            goods = [g.strip() for g in content.splitlines() if g.strip()]
        else:
            raise Exception("❌ Отправьте текст или файл")
        
        if not goods:
            raise Exception("❌ Не удалось извлечь товары")
        
        await state.update_data(new_auto_delivery_goods=goods)
        
        keyphrases = data.get("new_auto_delivery_keyphrases")
        phrases = "</code>, <code>".join(keyphrases)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_deliv_float_text(
                f"✔️ Подтвердите <b>добавление авто-выдачи</b>:"
                f"\n<b>· Ключевые фразы:</b> <code>{phrases}</code>"
                f"\n<b>· Тип выдачи:</b> Поштучно"
                f"\n<b>· Товары:</b> {len(goods)} шт."
            ),
            reply_markup=templ.confirm_kb(
                confirm_cb="add_new_auto_delivery", 
                cancel_cb=calls.AutoDeliveriesPagination(page=last_page).pack()
            )
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_deliv_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
        )


@router.message(states.AutoDeliveriesStates.waiting_for_auto_delivery_keyphrases, F.text)
async def handler_waiting_for_auto_delivery_keyphrases(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        
        data = await state.get_data()
        index = data.get("auto_delivery_index")

        if len(message.text) <= 0:
            raise Exception("❌ Слишком короткое значение")
        
        auto_deliveries = sett.get("auto_deliveries")
        keyphrases = [phrase.strip() for phrase in message.text.split(",")]
        auto_deliveries[index]["keyphrases"] = keyphrases
        sett.set("auto_deliveries", auto_deliveries)
        
        keyphrases_str = "</code>, <code>".join(keyphrases)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_deliv_page_float_text(f"✅ <b>Ключевые фразы</b> были успешно изменены на: <code>{keyphrases_str}</code>"),
            reply_markup=templ.back_kb(calls.AutoDeliveryPage(index=index).pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_deliv_page_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveryPage(index=index).pack())
        )


@router.message(states.AutoDeliveriesStates.waiting_for_auto_delivery_message, F.text)
async def handler_waiting_for_auto_delivery_message(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        
        data = await state.get_data()
        index = data.get("auto_delivery_index")
        
        if len(message.text) <= 0:
            raise Exception("❌ Слишком короткий текст")
        
        auto_deliveries = sett.get("auto_deliveries")
        auto_deliveries[index]["message"] = message.text.splitlines()
        sett.set("auto_deliveries", auto_deliveries)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_deliv_page_float_text(f"✅ <b>Сообщение авто-выдачи</b> было успешно изменено на: <blockquote>{message.text}</blockquote>"),
            reply_markup=templ.back_kb(calls.AutoDeliveryPage(index=index).pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_deliv_page_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveryPage(index=index).pack())
        )


@router.message(states.AutoDeliveriesStates.waiting_for_auto_delivery_goods_add, F.text | F.document)
async def handler_waiting_for_auto_delivery_goods_add(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        index = data.get("auto_delivery_index")
        
        if message.text:
            if len(message.text.strip()) == 0:
                raise Exception("❌ Слишком короткое значение")

            goods = [g.strip() for g in message.text.splitlines() if g.strip()]
        elif message.document:
            file = await message.bot.get_file(message.document.file_id)
            file_bytes = await message.bot.download_file(file.file_path)
            content = file_bytes.read().decode("utf-8", errors="ignore")

            if len(content.strip()) == 0:
                raise Exception("❌ Файл пустой")

            goods = [g.strip() for g in content.splitlines() if g.strip()]
        else:
            raise Exception("❌ Отправьте текст или файл")
        
        if not goods:
            raise Exception("❌ Не удалось извлечь товары")
        
        auto_deliveries = sett.get("auto_deliveries")
        auto_deliveries[index]["goods"].extend(goods)
        sett.set("auto_deliveries", auto_deliveries)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_deliv_goods_float_text(
                f"✅ <b>{len(goods)} товаров</b> успешно добавлено в авто-выдачу"
            ),
            reply_markup=templ.back_kb(calls.DelivGoodsPagination(page=last_page).pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_new_deliv_goods_float_text(e), 
            reply_markup=templ.back_kb(calls.DelivGoodsPagination(page=last_page).pack())
        )