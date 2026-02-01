import re
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from settings import Settings as sett

from .. import templates as templ
from .. import states
from .. import callback_datas as calls
from ..helpful import throw_float_message


router = Router()


def is_eng_str(str: str):
    pattern = r'^[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};:\'",.<>/?\\|`~ ]+$'
    return bool(re.match(pattern, str))


@router.message(states.SettingsStates.waiting_for_token, F.text)
async def handler_waiting_for_token(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if len(message.text.strip()) <= 3 or len(message.text.strip()) >= 500:
            raise Exception("❌ Слишком короткое или длинное значение")

        config = sett.get("config")
        config["playerok"]["api"]["token"] = message.text.strip()
        sett.set("config", config)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_auth_float_text(f"✅ <b>Токен</b> был успешно изменён на <b>{message.text.strip()}</b>"),
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
        if len(message.text.strip()) <= 3:
            raise Exception("❌ Слишком короткое значение")

        config = sett.get("config")
        config["playerok"]["api"]["user_agent"] = message.text.strip()
        sett.set("config", config)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_auth_float_text(f"✅ <b>User Agent</b> был успешно изменён на <b>{message.text.strip()}</b>"),
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="auth").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_auth_float_text(e), 
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="auth").pack())
        )


@router.message(states.SettingsStates.waiting_for_proxy, F.text)
async def handler_waiting_for_proxy(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if len(message.text.strip()) <= 3:
            raise Exception("❌ Слишком короткое значение")
        if not is_eng_str(message.text.strip()):
            raise Exception("❌ Некорректный прокси")

        config = sett.get("config")
        config["playerok"]["api"]["proxy"] = message.text.strip()
        sett.set("config", config)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_auth_float_text(f"✅ <b>Прокси</b> был успешно изменён на <b>{message.text.strip()}</b>"),
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
        if not message.text.strip().isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")       
        if int(message.text.strip()) < 0:
            raise Exception("❌ Слишком низкое значение")

        config = sett.get("config")
        config["playerok"]["api"]["requests_timeout"] = int(message.text.strip())
        sett.set("config", config)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_conn_float_text(f"✅ <b>Таймаут запросов</b> был успешно изменён на <b>{message.text.strip()}</b>"),
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
        if not message.text.strip().isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")
        if int(message.text.strip()) < 0:
            raise Exception("❌ Слишком низкое значение")

        config = sett.get("config")
        config["playerok"]["api"]["listener_requests_delay"] = int(message.text.strip())
        sett.set("config", config)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_conn_float_text(f"✅ <b>Периодичность запросов</b> была успешна изменена на <b>{message.text.strip()}</b>"),
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
        if len(message.text.strip()) < 0:
            raise Exception("❌ Слишком низкое значение")
        
        if message.text.strip().isdigit(): 
            chat_id = "-100" + str(message.text.strip()).replace("-100", "")
        else: 
            chat_id = "@" + str(message.text.strip()).replace("@", "")
        
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

        intreval = message.text.strip()
        if not intreval.isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")
        if int(intreval) <= 1:
            raise Exception("❌ Слишком низкое значение")
        intreval = int(intreval)

        config = sett.get("config")
        config["playerok"]["auto_withdrawal"]["interval"] = intreval
        sett.set("config", config)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_withdrawal_float_text(f"✅ <b>Интервал вывода</b> был успешно изменён на <b>{intreval}</b>"),
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

        phone_number = message.text.strip()
        if not phone_number.isdigit():
            raise Exception("❌ Вы указали некорректный номер телефона")
        if len(phone_number) < 4:
            raise Exception("❌ Слишком короткое значение")
        
        if phone_number.startswith("8"):
            phone_number = phone_number.replace("8", "+7", 1)
        
        data = await state.get_data()
        sbp_bank_id = data.get("sbp_bank_id")

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

        address = message.text.strip()
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

        if len(message.text.strip()) <= 0 or len(message.text.strip()) >= 150:
            raise Exception("❌ Слишком короткое или длинное значение")

        config = sett.get("config")
        config["playerok"]["watermark"]["value"] = message.text.strip()
        sett.set("config", config)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.settings_other_float_text(f"✅ <b>Водяной знак сообщений</b> был успешно изменён на <b>{message.text.strip()}</b>"),
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

        max_size = message.text.strip()
        if not message.text.strip().isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")
        if int(message.text.strip()) <= 0:
            raise Exception("❌ Слишком низкое значение")
        max_size = int(max_size)

        config = sett.get("config")
        config["logs"]["max_file_size"] = max_size
        sett.set("config", config)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.logs_float_text(f"✅ <b>Максимальный размер файла логов</b> был успешно изменён на <b>{max_size} MB</b>"),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="logs").pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.logs_float_text(e), 
            reply_markup=templ.back_kb(calls.MenuNavigation(to="logs").pack())
        )