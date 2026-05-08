from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from playerokapi.enums import PriorityTypes
from settings import Settings as sett

from .. import templates as templ
from .. import callback_datas as calls
from .. import states as states
from ..helpful import throw_float_message
from .navigation import *


router = Router()


@router.callback_query(F.data == "confirm_bump_items")
async def callback_confirm_bump_items(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    await throw_float_message(
        state=state,
        message=callback.message, 
        text=templ.bump_float_text("✔️ Подтвердите <b>поднятие товаров</b>:"), 
        reply_markup=templ.confirm_kb("bump_items", calls.MenuNavigation(to="bump").pack())
    )


@router.callback_query(F.data == "confirm_withdrawal")
async def callback_confirm_withdrawal(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    await throw_float_message(
        state=state,
        message=callback.message, 
        text=templ.withdrawal_float_text("✔️ Подтвердите <b>вывод средств</b>:"), 
        reply_markup=templ.confirm_kb("request_withdrawal", calls.MenuNavigation(to="withdrawal").pack())
    )


@router.callback_query(calls.ConfirmPublishItem.filter())
async def callback_confirm_publish_item(callback: CallbackQuery, callback_data: calls.ConfirmPublishItem, state: FSMContext):
    await state.set_state(None)

    data = await state.get_data()
    item = data.get("item")
    statuses = data.get("item_pr_statuses")

    status_id = callback_data.st_id
    await state.update_data(item_pr_status_id=status_id)

    status = next((st for st in statuses if st.id == status_id), None)
    status_str = "Бесплатный" if status.price == 0 else "Премиум"

    await throw_float_message(
        state=state,
        message=callback.message, 
        text=templ.item_float_text(
            "✔️ Подтвердите <b>публикацию товара</b>:"
            f"\n\n・ <b>Товар:</b> {item.name}"
            f"\n・ <b>Приоритет:</b> {status_str}"
        ), 
        reply_markup=templ.confirm_kb(
            confirm_cb=calls.PublishItem(id=item.id).pack(), 
            cancel_cb=calls.ItemPage(id=item.id).pack()
        )
    )


@router.callback_query(F.data == "confirm_raise_item")
async def callback_confirm_raise_item(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)

    data = await state.get_data()
    item = data.get("item")

    from plbot.playerokbot import get_playerok_bot as plbot
    pr_statuses = plbot().account.get_item_priority_statuses(item.id, item.raw_price)
    
    prem_st = next((st for st in pr_statuses if st.price > 0), None)
    await state.update_data(item_pr_status_id=prem_st.id)

    if item.priority == PriorityTypes.DEFAULT:
        text = (
            "✔️ Подтвердите <b>повышение приоритета</b>:"
            f"\n\n・ <b>Товар:</b> {item.name}"
            f"\n・ <b>Приоритет:</b> Премиум ({prem_st.price}₽)"
        )
    else:
        text = (
            "✔️ Подтвердите <b>поднятие товара</b>:"
            f"\n\n・ <b>Товар:</b> {item.name}"
            f"\n・ <b>Стоимость:</b> {prem_st.price}₽"
        )

    await throw_float_message(
        state=state,
        message=callback.message, 
        text=templ.item_float_text(text), 
        reply_markup=templ.confirm_kb(
            calls.IncreaseItemPriority(id=item.id).pack(), 
            calls.ItemPage(id=item.id).pack()
        )
    )

@router.callback_query(F.data == "confirm_delete_item")
async def callback_confirm_delete_item(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)

    data = await state.get_data()
    item = data.get("item")

    await throw_float_message(
        state=state,
        message=callback.message, 
        text=templ.item_float_text(
            "✔️ Подтвердите <b>удаление товара</b>:"
            f"\n\n・ <b>Товар:</b> {item.name}"
        ), 
        reply_markup=templ.confirm_kb(
            confirm_cb=calls.DeleteItem(id=item.id).pack(), 
            cancel_cb=calls.ItemPage(id=item.id).pack()
        )
    )