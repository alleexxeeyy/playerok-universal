from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from settings import Settings as sett

from .. import templates as templ
from .. import callback_datas as calls
from ..helpful import throw_float_message, do_auth


router = Router()


async def _load_withdrawal_info(state: FSMContext):
    from plbot.playerokbot import get_playerok_bot
    acc = get_playerok_bot().account

    config = sett.get("config")
    credentials_type = config["playerok"]["auto_withdrawal"]["credentials_type"]
    card_id = config["playerok"]["auto_withdrawal"]["card_id"]
    sbp_bank_id = config["playerok"]["auto_withdrawal"]["sbp_bank_id"]
    
    card = None
    sbp_bank = None

    try: 
        crsr = None
        while True:
            card_list = acc.get_verified_cards(after_cursor=crsr)
            if not card_list.page_info.has_next_page: break
            crsr = card_list.page_info.end_cursor
        
        await state.update_data(bank_cards=card_list.bank_cards)
        if credentials_type == "card":
            card = [card for card in card_list.bank_cards if card.id == card_id][0]
    except: 
        pass

    try: 
        sbp_banks = acc.get_sbp_bank_members()
        await state.update_data(sbp_banks=sbp_banks)
        if credentials_type == "sbp":
            sbp_bank = [bank for bank in sbp_banks if bank.id == sbp_bank_id][0]
    except: 
        pass

    return card, sbp_bank


@router.callback_query(calls.MenuNavigation.filter())
async def callback_menu_navigation(callback: CallbackQuery, callback_data: calls.MenuNavigation, state: FSMContext):
    await state.set_state(None)
    to = callback_data.to

    config = sett.get("config")
    if callback.from_user.id not in config["telegram"]["bot"]["signed_users"]:
        return await do_auth(callback.message, state)
    
    if to == "default":
        await throw_float_message(
            state, callback.message, templ.menu_text(), templ.menu_kb(), callback
        )
    elif to == "profile":
        await throw_float_message(
            state, callback.message, templ.profile_text(), templ.profile_kb(), callback
        )
    elif to == "logs":
        await throw_float_message(
            state, callback.message, templ.logs_text(), templ.logs_kb(), callback
        )
    elif to == "updates":
        await throw_float_message(
            state, callback.message, templ.updates_text(), templ.updates_kb(), callback
        )

    elif to == "auth":
        await throw_float_message(
            state, callback.message, templ.auth_text(), templ.auth_kb(), callback
        )
    elif to == "conn":
        await throw_float_message(
            state, callback.message, templ.conn_text(), templ.conn_kb(), callback
        )
    elif to == "restore":
        await throw_float_message(
            state, callback.message, templ.restore_text(), templ.restore_kb(), callback
        )
    elif to == "complete":
        await throw_float_message(
            state, callback.message, templ.complete_text(), templ.complete_kb(), callback
        )
    elif to == "withdrawal":
        card, sbp_bank = await _load_withdrawal_info(state)
        await throw_float_message(
            state, callback.message, templ.withdrawal_text(card, sbp_bank), templ.withdrawal_kb(card, sbp_bank), callback
        )
    elif to == "bump":
        await throw_float_message(
            state, callback.message, templ.bump_text(), templ.bump_kb(), callback
        )
    elif to == "notifications":
        await throw_float_message(
            state, callback.message, templ.notifications_text(), templ.notifications_kb(), callback
        )
    elif to == "other":
        await throw_float_message(
            state, callback.message, templ.other_text(), templ.other_kb(), callback
        )

@router.callback_query(calls.PlaceholdersNavigation.filter())
async def callback_placeholders_navigation(callback: CallbackQuery, callback_data: calls.PlaceholdersNavigation, state: FSMContext):
    await state.set_state(None)
    
    to = callback_data.to
    by = callback_data.by

    data = await state.get_data()
    last_page = data.get("last_page", 0)
    
    await throw_float_message(
        state, callback.message, templ.plholders_text(to), templ.plholders_kb(to, by, last_page), callback
    )


@router.callback_query(calls.StatsNavigation.filter())
async def callback_stats_navigation(callback: CallbackQuery, callback_data: calls.StatsNavigation, state: FSMContext):
    await state.set_state(None)
    to = callback_data.to
    
    if to == "day":
        await throw_float_message(
            state, callback.message, templ.stats_day_text(), templ.stats_day_kb(), callback
        )
    elif to == "week":
        await throw_float_message(
            state, callback.message, templ.stats_week_text(), templ.stats_week_kb(), callback
        )
    elif to == "month":
        await throw_float_message(
            state, callback.message, templ.stats_month_text(), templ.stats_month_kb(), callback
        )
    elif to == "all":
        await throw_float_message(
            state, callback.message, templ.stats_all_text(), templ.stats_all_kb(), callback
        )