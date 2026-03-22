from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from .. import templates as templ
from .. import callback_datas as calls
from ..helpful import throw_float_message


router = Router()


@router.callback_query(calls.IncludedRestoreItemsPagination.filter())
async def callback_included_restore_items_pagination(callback: CallbackQuery, callback_data: calls.IncludedRestoreItemsPagination, state: FSMContext):
    await state.set_state(None)
    
    page = callback_data.page
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.settings_restore_included_text(),
        reply_markup=templ.settings_restore_included_kb(page),
        callback=callback
    )


@router.callback_query(calls.ExcludedRestoreItemsPagination.filter())
async def callback_excluded_restore_items_pagination(callback: CallbackQuery, callback_data: calls.ExcludedRestoreItemsPagination, state: FSMContext):
    await state.set_state(None)
    
    page = callback_data.page
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.settings_restore_excluded_text(),
        reply_markup=templ.settings_restore_excluded_kb(page),
        callback=callback
    )


@router.callback_query(calls.IncludedCompleteDealsPagination.filter())
async def callback_included_complete_deals_pagination(callback: CallbackQuery, callback_data: calls.IncludedCompleteDealsPagination, state: FSMContext):
    await state.set_state(None)
    
    page = callback_data.page
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.settings_complete_included_text(),
        reply_markup=templ.settings_complete_included_kb(page),
        callback=callback
    )


@router.callback_query(calls.ExcludedCompleteDealsPagination.filter())
async def callback_excluded_complete_deals_pagination(callback: CallbackQuery, callback_data: calls.ExcludedCompleteDealsPagination, state: FSMContext):
    await state.set_state(None)
    
    page = callback_data.page
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.settings_complete_excluded_text(),
        reply_markup=templ.settings_complete_excluded_kb(page),
        callback=callback
    )


@router.callback_query(calls.IncludedBumpItemsPagination.filter())
async def callback_included_bump_items_pagination(callback: CallbackQuery, callback_data: calls.IncludedBumpItemsPagination, state: FSMContext):
    await state.set_state(None)
    
    page = callback_data.page
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.settings_bump_included_text(),
        reply_markup=templ.settings_bump_included_kb(page),
        callback=callback
    )


@router.callback_query(calls.ExcludedBumpItemsPagination.filter())
async def callback_excluded_bump_items_pagination(callback: CallbackQuery, callback_data: calls.ExcludedBumpItemsPagination, state: FSMContext):
    await state.set_state(None)
    
    page = callback_data.page
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.settings_bump_excluded_text(),
        reply_markup=templ.settings_bump_excluded_kb(page),
        callback=callback
    )


@router.callback_query(calls.CustomCommandsPagination.filter())
async def callback_custom_commands_pagination(callback: CallbackQuery, callback_data: calls.CustomCommandsPagination, state: FSMContext):
    await state.set_state(None)
    
    page = callback_data.page
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.settings_comms_text(),
        reply_markup=templ.settings_comms_kb(page),
        callback=callback
    )


@router.callback_query(calls.AutoDeliveriesPagination.filter())
async def callback_auto_deliveries_pagination(callback: CallbackQuery, callback_data: calls.AutoDeliveriesPagination, state: FSMContext):
    await state.set_state(None)
    
    page = callback_data.page
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.settings_delivs_text(),
        reply_markup=templ.settings_delivs_kb(page),
        callback=callback
        )


@router.callback_query(calls.DelivGoodsPagination.filter())
async def callback_deliv_goods_pagination(callback: CallbackQuery, callback_data: calls.DelivGoodsPagination, state: FSMContext):
    await state.set_state(None)

    data = await state.get_data()
    index = data.get("auto_delivery_index")
    
    page = callback_data.page
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.settings_deliv_goods_text(index),
        reply_markup=templ.settings_deliv_goods_kb(index, page),
        callback=callback
    )


@router.callback_query(calls.MessagesPagination.filter())
async def callback_messages_pagination(callback: CallbackQuery, callback_data: calls.MessagesPagination, state: FSMContext):
    await state.set_state(None)
    
    page = callback_data.page
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.settings_mess_text(),
        reply_markup=templ.settings_mess_kb(page),
        callback=callback
    )


@router.callback_query(calls.ModulesPagination.filter())
async def callback_modules_pagination(callback: CallbackQuery, callback_data: calls.ModulesPagination, state: FSMContext):
    await state.set_state(None)
    
    page = callback_data.page
    await state.update_data(last_page=page)
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.modules_text(),
        reply_markup=templ.modules_kb(page),
        callback=callback
    )


@router.callback_query(calls.BankCardsPagination.filter())
async def callback_bank_cards_pagination(callback: CallbackQuery, callback_data: calls.BankCardsPagination, state: FSMContext):
    await state.set_state(None)
    
    page = callback_data.page
    await state.update_data(last_page=page)
    
    data = await state.get_data()
    bank_cards = data.get("bank_cards", [])
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.settings_withdrawal_cards_text(bank_cards),
        reply_markup=templ.settings_withdrawal_cards_kb(bank_cards, page),
        callback=callback
    )


@router.callback_query(calls.SbpBanksPagination.filter())
async def callback_sbp_banks_pagination(callback: CallbackQuery, callback_data: calls.SbpBanksPagination, state: FSMContext):
    await state.set_state(None)
    
    page = callback_data.page
    await state.update_data(last_page=page)
    
    data = await state.get_data()
    sbp_banks = data.get("sbp_banks", [])
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.settings_withdrawal_sbp_text(sbp_banks),
        reply_markup=templ.settings_withdrawal_sbp_kb(sbp_banks, page),
        callback=callback
    )