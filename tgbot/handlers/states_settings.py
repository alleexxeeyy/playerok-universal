import re
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from settings import Settings as sett

from .. import templates as templ
from .. import states
from .. import callback_datas as calls
from ..helpful import throw_float_message

from utils import (
    is_cookies_valid,
    is_token_valid,
    is_user_agent_valid,
    is_proxy_valid, 
    is_proxy_working
)


router = Router()


@router.message(states.SettingsStates.waiting_for_cookies, F.text)
async def handler_waiting_for_cookies(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        
        str_cookies = message.text
        cookies = {
            c.split("=")[0].strip(): c.split("=")[1].strip() for c
            in str_cookies.split(";") if c.strip() and "=" in c
        }
        
        if not is_cookies_valid(str_cookies) or not is_token_valid(cookies["token"]):
            raise Exception("❌ Неверные Cookie-данные. Убедитесь, что они указаны в формате Header String")

        config = sett.get("config")
        config["playerok"]["api"]["cookies"] = str_cookies
        sett.set("config", config)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_auth_float_text(f"🍪 <b>Cookie-данные</b> были успешно изменены на: <blockquote>{str_cookies}</blockquote>"),
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="auth").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_auth_float_text(e), 
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="auth").pack())
        )


@router.message(states.SettingsStates.waiting_for_user_agent, F.text)
async def handler_waiting_for_user_agent(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        
        user_agent = message.text
        
        if not is_user_agent_valid(user_agent):
            raise Exception("❌ Неверный формат User Agent. Пример: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36")

        config = sett.get("config")
        config["playerok"]["api"]["user_agent"] = user_agent
        sett.set("config", config)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_auth_float_text(f"✅ <b>User Agent</b> был успешно изменён на <b>{user_agent}</b>"),
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="auth").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_auth_float_text(e), 
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="auth").pack())
        )


@router.message(states.SettingsStates.waiting_for_pl_proxy, F.text)
async def handler_waiting_for_pl_proxy(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        
        proxy = message.text
        
        if len(proxy) <= 3:
            raise Exception("❌ Слишком короткое значение")
        if not is_proxy_valid(proxy):
            raise Exception("❌ Неверный формат прокси. Правильный формат: user:pass@ip:port или ip:port")
        if not is_proxy_working(proxy):
            raise Exception("❌ Указанный вами прокси не работает. Нет подключения к playerok.com")

        config = sett.get("config")
        config["playerok"]["api"]["proxy"] = proxy
        sett.set("config", config)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_auth_float_text(f"✅ <b>Прокси для Playerok</b> был успешно изменён на <b>{proxy}</b>"),
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="conn").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_auth_float_text(e), 
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="conn").pack())
        )


@router.message(states.SettingsStates.waiting_for_tg_proxy, F.text)
async def handler_waiting_for_tg_proxy(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        
        proxy = message.text
        
        if len(proxy) <= 3:
            raise Exception("❌ Слишком короткое значение")
        if not is_proxy_valid(proxy):
            raise Exception("❌ Неверный формат прокси. Правильный формат: user:pass@ip:port или ip:port")
        if not is_proxy_working(proxy, "https://api.telegram.org/"):
            raise Exception("❌ Указанный вами прокси не работает. Нет подключения к api.telegram.org")

        config = sett.get("config")
        config["telegram"]["api"]["proxy"] = proxy
        sett.set("config", config)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_auth_float_text(f"✅ <b>Прокси для Telegram</b> был успешно изменён на <b>{proxy}</b>"),
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="conn").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_auth_float_text(e), 
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="conn").pack())
        )


@router.message(states.SettingsStates.waiting_for_requests_timeout, F.text)
async def handler_waiting_for_requests_timeout(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        
        timeout = message.text
        
        if not timeout.isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")       
        if int(timeout) < 0:
            raise Exception("❌ Слишком низкое значение")

        config = sett.get("config")
        config["playerok"]["api"]["requests_timeout"] = int(timeout)
        sett.set("config", config)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_conn_float_text(f"✅ <b>Таймаут запросов</b> был успешно изменён на <b>{timeout}</b>"),
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="conn").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_conn_float_text(e), 
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="conn").pack())
        )


@router.message(states.SettingsStates.waiting_for_listener_requests_delay, F.text)
async def handler_waiting_for_listener_requests_delay(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        
        delay = message.text
        
        if not delay.isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")
        if int(delay) < 0:
            raise Exception("❌ Слишком низкое значение")

        config = sett.get("config")
        config["playerok"]["api"]["listener_requests_delay"] = int(delay)
        sett.set("config", config)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_conn_float_text(f"✅ <b>Периодичность запросов</b> была успешна изменена на <b>{delay}</b>"),
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="conn").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_conn_float_text(e), 
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="conn").pack())
        )


@router.message(states.SettingsStates.waiting_for_tg_logging_chat_id, F.text)
async def handler_waiting_for_tg_logging_chat_id(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        
        chat_input = message.text
        
        if len(chat_input) < 0:
            raise Exception("❌ Слишком низкое значение")
        
        if chat_input.isdigit(): 
            chat_id = "-100" + str(chat_input).replace("-100", "")
        else: 
            chat_id = "@" + str(chat_input).replace("@", "")
        
        config = sett.get("config")
        config["playerok"]["tg_logging"]["chat_id"] = chat_id
        sett.set("config", config)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_logger_float_text(f"✅ <b>ID чата для логов</b> было успешно изменено на <b>{chat_id}</b>"),
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="logger").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_logger_float_text(e), 
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="logger").pack())
        )


@router.message(states.SettingsStates.waiting_for_auto_withdrawal_interval, F.text)
async def handler_waiting_for_auto_withdrawal_interval(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        
        interval = message.text
        
        if not interval.isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")
        if int(interval) <= 1:
            raise Exception("❌ Слишком низкое значение")
        
        interval_int = int(interval)

        config = sett.get("config")
        config["playerok"]["auto_withdrawal"]["interval"] = interval_int
        sett.set("config", config)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_withdrawal_float_text(f"✅ <b>Интервал вывода</b> был успешно изменён на <b>{interval_int}</b>"),
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="withdrawal").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_withdrawal_float_text(e), 
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="withdrawal").pack())
        )


@router.message(states.SettingsStates.waiting_for_sbp_bank_phone_number, F.text)
async def handler_waiting_for_sbp_bank_phone_number(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        
        data = await state.get_data()
        sbp_bank_id = data.get("sbp_bank_id")
        
        phone_number = message.text
        
        if not phone_number.isdigit():
            raise Exception("❌ Вы указали некорректный номер телефона")
        if len(phone_number) < 4:
            raise Exception("❌ Слишком короткое значение")
        
        if phone_number.startswith("8"):
            phone_number = phone_number.replace("8", "+7", 1)

        config = sett.get("config")
        config["playerok"]["auto_withdrawal"]["credentials_type"] = "sbp"
        config["playerok"]["auto_withdrawal"]["sbp_bank_id"] = sbp_bank_id
        config["playerok"]["auto_withdrawal"]["sbp_phone_number"] = phone_number.strip()
        sett.set("config", config)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_withdrawal_sbp_float_text(f"✅ <b>Данные вывода</b> были успешно изменены на <b>{phone_number} (СБП)</b>"),
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="withdrawal").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_withdrawal_sbp_float_text(e), 
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="withdrawal").pack())
        )


@router.message(states.SettingsStates.waiting_for_usdt_address, F.text)
async def handler_waiting_for_usdt_address(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        
        address = message.text
        
        if len(address) <= 10:
            raise Exception("❌ Слишком короткое значение")

        config = sett.get("config")
        config["playerok"]["auto_withdrawal"]["credentials_type"] = "usdt"
        config["playerok"]["auto_withdrawal"]["usdt_address"] = address
        sett.set("config", config)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_withdrawal_float_text(f"✅ <b>Данные вывода</b> были успешно изменены на <b>{address} (USDT TRC20)</b>"),
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="withdrawal").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_withdrawal_float_text(e), 
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="withdrawal").pack())
        )
            

@router.message(states.SettingsStates.waiting_for_watermark_value, F.text)
async def handler_waiting_for_watermark_value(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        
        watermark = message.text

        if len(watermark) <= 0 or len(watermark) >= 150:
            raise Exception("❌ Слишком короткое или длинное значение")

        config = sett.get("config")
        config["playerok"]["watermark"]["value"] = watermark
        sett.set("config", config)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_other_float_text(f"✅ <b>Водяной знак сообщений</b> был успешно изменён на <b>{watermark}</b>"),
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="other").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_other_float_text(e), 
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="other").pack())
        )
            

@router.message(states.SettingsStates.waiting_for_logs_max_file_size, F.text)
async def handler_waiting_for_logs_max_file_size(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        
        max_size = message.text
        
        if not max_size.isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")
        if int(max_size) <= 0:
            raise Exception("❌ Слишком низкое значение")
        
        max_size_int = int(max_size)

        config = sett.get("config")
        config["logs"]["max_file_size"] = max_size_int
        sett.set("config", config)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.logs_float_text(f"✅ <b>Максимальный размер файла логов</b> был успешно изменён на <b>{max_size_int} MB</b>"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="logs").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.logs_float_text(e), 
            reply_markup=templ.back_kb(calls.MenuNavigation(to="logs").pack())
        )