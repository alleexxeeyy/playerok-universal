from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from settings import Settings as sett
from utils import escape_html, binding_title

from .. import templates as templ
from .. import states
from .. import callback_datas as calls
from ..helpful import (
    throw_float_message,
    extract_lines,
    resolve_item_lines,
    item_refs_report
)


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
            text=templ.delivs_float_text(f"📃 Введите номер страницы для перехода:"),
            reply_markup=templ.delivs_kb(page)
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.delivs_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
        )


@router.message(states.AutoDeliveriesStates.waiting_for_new_auto_delivery_items, F.text | F.document)
async def handler_waiting_for_new_auto_delivery_items(message: types.Message, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    try:
        await state.set_state(None)

        items, errors = await resolve_item_lines(await extract_lines(message))
        report = item_refs_report(
            items, errors,
            "🛍️ Выбран товар <b>{name}</b>",
            "🛍️ Выбрано товаров: <b>{count}</b>"
        )

        await state.update_data(new_auto_delivery_items=items)
        await state.set_state(states.AutoDeliveriesStates.waiting_for_auto_delivery_piece)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_deliv_float_text(f"{report}\n\n🛒 Выберите <b>тип авто-выдачи</b>:"),
            reply_markup=templ.new_deliv_piece_kb(last_page)
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_deliv_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
        )
        

@router.message(states.AutoDeliveriesStates.waiting_for_new_auto_delivery_message, F.text)
async def handler_waiting_for_new_auto_delivery_message(message: types.Message, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    try:
        await state.set_state(None)
        
        if len(message.text) <= 0:
            raise Exception("❌ Слишком короткое значение")

        await state.update_data(new_auto_delivery_message=message.text)
        
        items_frmtd = escape_html(binding_title({"items": data.get("new_auto_delivery_items") or []}))
        msg = message.text
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_deliv_float_text(
                f"✔️ Подтвердите <b>добавление авто-выдачи</b>:"
                f"\n\n<b>· Товары:</b> {items_frmtd}"
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
            text=templ.new_deliv_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
        )
        

@router.message(states.AutoDeliveriesStates.waiting_for_new_auto_delivery_goods, F.text | F.document)
async def handler_waiting_for_new_auto_delivery_goods(message: types.Message, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    try:
        await state.set_state(None)
        
        goods = await extract_lines(message)
        await state.update_data(new_auto_delivery_goods=goods)
        
        items_frmtd = escape_html(binding_title({"items": data.get("new_auto_delivery_items") or []}))
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_deliv_float_text(
                f"✔️ Подтвердите <b>добавление авто-выдачи</b>:"
                f"\n\n<b>· Товары:</b> {items_frmtd}"
                f"\n<b>· Тип выдачи:</b> Поштучно"
                f"\n<b>· Позиции:</b> {len(goods)} шт."
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
            text=templ.new_deliv_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
        )


@router.message(states.AutoDeliveriesStates.waiting_for_auto_delivery_items, F.text | F.document)
async def handler_waiting_for_auto_delivery_items(message: types.Message, state: FSMContext):
    data = await state.get_data()
    index = data.get("auto_delivery_index")
    try:
        await state.set_state(None)

        items, errors = await resolve_item_lines(await extract_lines(message))
        report = item_refs_report(
            items, errors,
            "✅ <b>Товары</b> авто-выдачи изменены на: <b>{name}</b>",
            "✅ <b>Товары</b> авто-выдачи изменены (выбрано: <b>{count}</b>)"
        )

        auto_deliveries = sett.get("auto_deliveries")
        auto_deliveries[index]["items"] = items
        auto_deliveries[index].pop("keyphrases", None)
        sett.set("auto_deliveries", auto_deliveries)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.deliv_page_float_text(report),
            reply_markup=templ.back_kb(calls.AutoDeliveryPage(index=index).pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.deliv_page_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveryPage(index=index).pack())
        )


@router.message(states.AutoDeliveriesStates.waiting_for_auto_delivery_message, F.text)
async def handler_waiting_for_auto_delivery_message(message: types.Message, state: FSMContext):
    data = await state.get_data()
    index = data.get("auto_delivery_index")
    try:
        await state.set_state(None)
        
        if len(message.text) <= 0:
            raise Exception("❌ Слишком короткий текст")
        
        auto_deliveries = sett.get("auto_deliveries")
        auto_deliveries[index]["message"] = message.text.splitlines()
        sett.set("auto_deliveries", auto_deliveries)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.deliv_page_float_text(f"✅ <b>Сообщение авто-выдачи</b> было успешно изменено на: <blockquote>{message.text}</blockquote>"),
            reply_markup=templ.back_kb(calls.AutoDeliveryPage(index=index).pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.deliv_page_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveryPage(index=index).pack())
        )


@router.message(states.AutoDeliveriesStates.waiting_for_auto_delivery_goods_add, F.text | F.document)
async def handler_waiting_for_auto_delivery_goods_add(message: types.Message, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    index = data.get("auto_delivery_index")
    try:
        await state.set_state(None)

        goods = await extract_lines(message)

        auto_deliveries = sett.get("auto_deliveries")
        auto_deliveries[index]["goods"].extend(goods)
        sett.set("auto_deliveries", auto_deliveries)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_deliv_goods_float_text(
                f"✅ <b>{len(goods)} товаров</b> успешно добавлено в авто-выдачу"
            ),
            reply_markup=templ.back_kb(calls.DelivGoodsPagination(page=last_page).pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_deliv_goods_float_text(e), 
            reply_markup=templ.back_kb(calls.DelivGoodsPagination(page=last_page).pack())
        )