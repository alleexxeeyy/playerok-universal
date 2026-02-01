from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from settings import Settings as sett

from .. import templates as templ
from .. import callback_datas as calls
from ..helpful import throw_float_message


router = Router()


@router.callback_query(calls.MenuNavigation.filter())
async def callback_menu_navigation(callback: CallbackQuery, callback_data: calls.MenuNavigation, state: FSMContext):
    await state.set_state(None)
    to = callback_data.to
    if to == "default":
        await throw_float_message(state, callback.message, templ.menu_text(), templ.menu_kb(), callback)
    elif to == "stats":
        await throw_float_message(state, callback.message, templ.stats_text(), templ.stats_kb(), callback)
    elif to == "profile":
        await throw_float_message(state, callback.message, templ.profile_text(), templ.profile_kb(), callback)
    elif to == "events":
        await throw_float_message(state, callback.message, templ.events_text(), templ.events_kb(), callback)
    elif to == "logs":
        await throw_float_message(state, callback.message, templ.logs_text(), templ.logs_kb(), callback)


@router.callback_query(calls.InstructionNavigation.filter())
async def callback_instruction_navgiation(callback: CallbackQuery, callback_data: calls.InstructionNavigation, state: FSMContext):
    await state.set_state(None)
    to = callback_data.to
    if to == "default":
        await throw_float_message(state, callback.message, templ.instruction_text(), templ.instruction_kb(), callback)
    elif to == "commands":
        await throw_float_message(state, callback.message, templ.instruction_comms_text(), templ.instruction_comms_kb(), callback)


@router.callback_query(calls.SettingsNavigation.filter())
async def callback_settings_navigation(callback: CallbackQuery, callback_data: calls.SettingsNavigation, state: FSMContext):
    await state.set_state(None)
    to = callback_data.to
    if to == "default":
        await throw_float_message(state, callback.message, templ.settings_text(), templ.settings_kb(), callback)
    elif to == "auth":
        await throw_float_message(state, callback.message, templ.settings_auth_text(), templ.settings_auth_kb(), callback)
    elif to == "conn":
        await throw_float_message(state, callback.message, templ.settings_conn_text(), templ.settings_conn_kb(), callback)
    elif to == "restore":
        await throw_float_message(state, callback.message, templ.settings_restore_text(), templ.settings_restore_kb(), callback)
    elif to == "withdrawal":
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

        await throw_float_message(state, callback.message, templ.settings_withdrawal_text(card, sbp_bank), templ.settings_withdrawal_kb(card, sbp_bank), callback)
    elif to == "bump":
        await throw_float_message(state, callback.message, templ.settings_bump_text(), templ.settings_bump_kb(), callback)
    elif to == "logger":
        await throw_float_message(state, callback.message, templ.settings_logger_text(), templ.settings_logger_kb(), callback)
    elif to == "other":
        await throw_float_message(state, callback.message, templ.settings_other_text(), templ.settings_other_kb(), callback)