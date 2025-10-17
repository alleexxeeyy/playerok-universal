import re
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramAPIError

from settings import Settings as sett

from .. import templates as templ
from .. import states
from .. import callback_datas as calls
from ..helpful import throw_float_message


router = Router()
    
    
def is_eng_str(str: str):
    pattern = r'^[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};:\'",.<>/?\\|`~ ]+$'
    return bool(re.match(pattern, str))


@router.message(states.ActionsStates.entering_message_text, F.text)
async def handler_entering_password(message: types.Message, state: FSMContext):
    try: 
        from plbot.playerokbot import get_playerok_bot
        await state.set_state(None)
        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком короткий текст")

        data = await state.get_data()
        plbot = get_playerok_bot()
        username = data.get("username")
        chat = plbot.get_chat_by_username(username)
        plbot.send_message(chat_id=chat.id, text=message.text.strip())

        await throw_float_message(state=state,
                                  message=message,
                                  text=templ.do_action_text(f"✅ Пользователю <b>{username}</b> было отправлено сообщение: <blockquote>{message.text.strip()}</blockquote>"),
                                  reply_markup=templ.destroy_kb())
    except Exception as e:
        if e is not TelegramAPIError:
            await throw_float_message(state=state,
                                      message=message,
                                      text=templ.do_action_text(e), 
                                      reply_markup=templ.destroy_kb())


@router.message(states.SystemStates.entering_password, F.text)
async def handler_entering_password(message: types.Message, state: FSMContext):
    try: 
        await state.set_state(None)
        config = sett.get("config")
        if message.text.strip() != config["telegram"]["bot"]["password"]:
            raise Exception("❌ Неверный ключ-пароль.")
        
        config["telegram"]["bot"]["signed_users"].append(message.from_user.id)
        sett.set("config", config)

        await throw_float_message(state=state,
                                  message=message,
                                  text=templ.menu_text(),
                                  reply_markup=templ.menu_kb())
    except Exception as e:
        if e is not TelegramAPIError:
            await throw_float_message(state=state,
                                      message=message,
                                      text=templ.sign_text(e), 
                                      reply_markup=templ.destroy_kb())

@router.message(states.MessagesStates.entering_page, F.text)
async def handler_entering_messages_page(message: types.Message, state: FSMContext):
    try: 
        await state.set_state(None)
        if not message.text.strip().isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")
        
        await state.update_data(last_page=int(message.text.strip())-1)
        await throw_float_message(state=state,
                                  message=message,
                                  text=templ.settings_mess_text(),
                                  reply_markup=templ.settings_mess_kb(int(message.text)-1))
    except Exception as e:
        if e is not TelegramAPIError:
            data = await state.get_data()
            await throw_float_message(state=state,
                                      message=message,
                                      text=templ.settings_mess_float_text(e),
                                      reply_markup=templ.back_kb(calls.MessagesPagination(page=data.get("last_page") or 0).pack()))
        
@router.message(states.MessagePageStates.entering_message_text, F.text)
async def handler_entering_message_text(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком короткий текст")

        data = await state.get_data()
        messages = sett.get("messages")
        message_split_lines = message.text.strip().split('\n')
        messages[data["message_id"]]["text"] = message_split_lines
        sett.set("messages", messages)
        await throw_float_message(state=state,
                                  message=message,
                                  text=templ.settings_mess_page_float_text(f"✅ <b>Текст сообщения</b> <code>{data['message_id']}</code> был успешно изменён на <blockquote>{message.text.strip()}</blockquote>"),
                                  reply_markup=templ.back_kb(calls.MessagePage(message_id=data.get("message_id")).pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            data = await state.get_data()
            await throw_float_message(state=state,
                                      message=message,
                                      text=templ.settings_mess_page_float_text(e), 
                                      reply_markup=templ.back_kb(calls.MessagePage(message_id=data.get("message_id")).pack()))
            
@router.message(states.SettingsStates.entering_token, F.text)
async def handler_entering_token(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if len(message.text.strip()) <= 3 or len(message.text.strip()) >= 500:
            raise Exception("❌ Слишком короткое или длинное значение")

        config = sett.get("config")
        config["playerok"]["api"]["token"] = message.text.strip()
        sett.set("config", config)
        await throw_float_message(state=state,
                                  message=message,
                                  text=templ.settings_auth_float_text(f"✅ <b>Токен</b> был успешно изменён на <b>{message.text.strip()}</b>"),
                                  reply_markup=templ.back_kb(calls.SettingsNavigation(to="auth").pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            await throw_float_message(state=state,
                                      message=message,
                                      text=templ.settings_auth_float_text(e), 
                                      reply_markup=templ.back_kb(calls.SettingsNavigation(to="auth").pack()))

@router.message(states.SettingsStates.entering_user_agent, F.text)
async def handler_entering_user_agent(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if len(message.text.strip()) <= 3:
            raise Exception("❌ Слишком короткое значение")

        config = sett.get("config")
        config["playerok"]["api"]["user_agent"] = message.text.strip()
        sett.set("config", config)
        await throw_float_message(state=state,
                                  message=message,
                                  text=templ.settings_auth_float_text(f"✅ <b>user_agent</b> был успешно изменён на <b>{message.text.strip()}</b>"),
                                  reply_markup=templ.back_kb(calls.SettingsNavigation(to="auth").pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            await throw_float_message(state=state,
                                      message=message,
                                      text=templ.settings_auth_float_text(e), 
                                      reply_markup=templ.back_kb(calls.SettingsNavigation(to="auth").pack()))

@router.message(states.SettingsStates.entering_proxy, F.text)
async def handler_entering_proxy(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if len(message.text.strip()) <= 3:
            raise Exception("❌ Слишком короткое значение")
        if not is_eng_str(message.text.strip()):
            raise Exception("❌ Некорректный прокси")

        config = sett.get("config")
        config["playerok"]["api"]["proxy"] = message.text.strip()
        sett.set("config", config)
        await throw_float_message(state=state,
                                  message=message,
                                  text=templ.settings_auth_float_text(f"✅ <b>Прокси</b> был успешно изменён на <b>{message.text.strip()}</b>"),
                                  reply_markup=templ.back_kb(calls.SettingsNavigation(to="conn").pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            await throw_float_message(state=state,
                                      message=message,
                                      text=templ.settings_auth_float_text(e), 
                                      reply_markup=templ.back_kb(calls.SettingsNavigation(to="conn").pack()))

@router.message(states.SettingsStates.entering_requests_timeout, F.text)
async def handler_entering_requests_timeout(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if not message.text.strip().isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")       
        if int(message.text.strip()) < 0:
            raise Exception("❌ Слишком низкое значение")

        config = sett.get("config")
        config["playerok"]["api"]["requests_timeout"] = int(message.text.strip())
        sett.set("config", config)
        await throw_float_message(state=state,
                                  message=message,
                                  text=templ.settings_conn_float_text(f"✅ <b>Таймаут запросов</b> был успешно изменён на <b>{message.text.strip()}</b>"),
                                  reply_markup=templ.back_kb(calls.SettingsNavigation(to="conn").pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            await throw_float_message(state=state,
                                      message=message,
                                      text=templ.settings_conn_float_text(e), 
                                      reply_markup=templ.back_kb(calls.SettingsNavigation(to="conn").pack()))

@router.message(states.SettingsStates.entering_listener_requests_delay, F.text)
async def handler_entering_listener_requests_delay(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if not message.text.strip().isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")
        if int(message.text.strip()) < 0:
            raise Exception("❌ Слишком низкое значение")

        config = sett.get("config")
        config["playerok"]["api"]["listener_requests_delay"] = int(message.text.strip())
        sett.set("config", config)
        await throw_float_message(state=state,
                                  message=message,
                                  text=templ.settings_conn_float_text(f"✅ <b>Периодичность запросов</b> была успешна изменена на <b>{message.text.strip()}</b>"),
                                  reply_markup=templ.back_kb(calls.SettingsNavigation(to="conn").pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            await throw_float_message(state=state,
                                      message=message,
                                      text=templ.settings_conn_float_text(e), 
                                      reply_markup=templ.back_kb(calls.SettingsNavigation(to="conn").pack()))


@router.message(states.SettingsStates.entering_tg_logging_chat_id, F.text)
async def handler_entering_tg_logging_chat_id(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None) 
        if len(message.text.strip()) < 0:
            raise Exception("❌ Слишком низкое значение")
        
        if message.text.strip().isdigit(): chat_id = "-100" + str(message.text.strip()).replace("-100", "")
        else: chat_id = "@" + str(message.text.strip()).replace("@", "")

        config = sett.get("config")
        config["playerok"]["bot"]["tg_logging_chat_id"] = chat_id
        sett.set("config", config)
        await throw_float_message(state=state,
                                  message=message,
                                  text=templ.settings_logger_float_text(f"✅ <b>ID чата для логов</b> было успешно изменено на <b>{chat_id}</b>"),
                                  reply_markup=templ.back_kb(calls.SettingsNavigation(to="logger").pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            await throw_float_message(state=state,
                                      message=message,
                                      text=templ.settings_logger_float_text(e), 
                                      reply_markup=templ.back_kb(calls.SettingsNavigation(to="logger").pack()))
            

@router.message(states.CustomCommandsStates.entering_page, F.text)
async def handler_entering_custom_commands_page(message: types.Message, state: FSMContext):
    try: 
        await state.set_state(None)
        if not message.text.strip().isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")
        
        await state.update_data(last_page=int(message.text.strip())-1)
        await throw_float_message(state=state,
                                  message=message,
                                  text=templ.settings_comm_text(),
                                  reply_markup=templ.settings_comm_kb(page=int(message.text)-1))
    except Exception as e:
        if e is not TelegramAPIError:
            data = await state.get_data()
            await throw_float_message(state=state,
                                      message=message,
                                      text=templ.settings_comm_float_text(e), 
                                      reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=data.get("last_page") or 0).pack()))
        
@router.message(states.CustomCommandsStates.entering_new_custom_command, F.text)
async def handler_entering_custom_command(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if len(message.text.strip()) <= 0 or len(message.text.strip()) >= 32:
            raise Exception("❌ Слишком короткая или длинная команда")

        data = await state.get_data()
        await state.update_data(new_custom_command=message.text.strip())
        await state.set_state(states.CustomCommandsStates.entering_new_custom_command_answer)
        await throw_float_message(state=state,
                                  message=message,
                                  text=templ.adding_new_comm_float_text(f"💬 Введите <b>ответ для команды</b> <code>{message.text.strip()}</code> ↓"),
                                  reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=data.get("last_page") or 0).pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            data = await state.get_data()
            await throw_float_message(state=state,
                                      message=message,
                                      text=templ.adding_new_comm_float_text(e), 
                                      reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=data.get("last_page") or 0).pack()))
        
@router.message(states.CustomCommandsStates.entering_new_custom_command_answer, F.text)
async def handler_entering_new_custom_command_answer(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком короткий ответ")

        data = await state.get_data()
        await state.update_data(new_custom_command_answer=message.text.strip())
        await throw_float_message(state=state,
                                  message=message,
                                  text=templ.adding_new_comm_float_text(f"➕ Подтвердите <b>добавление новой команды</b> <code>{data['new_custom_command']}</code> ↓"),
                                  reply_markup=templ.confirm_kb(confirm_cb="add_new_custom_command", cancel_cb=calls.CustomCommandsPagination(page=data.get("last_page") or 0).pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            data = await state.get_data()
            await throw_float_message(state=state,
                                      message=message,
                                      text=templ.adding_new_comm_float_text(e), 
                                      reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=data.get("last_page") or 0).pack()))

@router.message(states.CustomCommandPageStates.entering_custom_command_answer, F.text)
async def handler_entering_custom_command_answer(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком короткий текст")

        data = await state.get_data()
        custom_commands = sett.get("custom_commands")
        custom_commands[data["custom_command"]] = message.text.strip().split('\n')
        sett.set("custom_commands", custom_commands)
        await throw_float_message(state=state,
                                  message=message,
                                  text=templ.settings_comm_float_text(f"✅ <b>Текст ответа</b> команды <code>{data['custom_command']}</code> был успешно изменён на: <blockquote>{message.text.strip()}</blockquote>"),
                                  reply_markup=templ.back_kb(calls.CustomCommandPage(command=data["custom_command"]).pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            data = await state.get_data()
            await throw_float_message(state=state,
                                      message=message,
                                      text=templ.settings_comm_float_text(e), 
                                      reply_markup=templ.back_kb(calls.CustomCommandPage(command=data["custom_command"]).pack()))


@router.message(states.AutoDeliveriesStates.entering_page, F.text)
async def handler_entering_auto_deliveries_page(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if not message.text.strip().isdigit():
            raise Exception("❌ Вы должны ввести числовое значение")
        
        await state.update_data(last_page=int(message.text.strip())-1)
        await throw_float_message(state=state,
                                  message=message,
                                  text=templ.settings_deliv_float_text(f"📃 Введите номер страницы для перехода ↓"),
                                  reply_markup=templ.settings_deliv_kb(int(message.text)-1))
    except Exception as e:
        if e is not TelegramAPIError:
            data = await state.get_data()
            await throw_float_message(state=state,
                                      message=message,
                                      text=templ.settings_deliv_float_text(e), 
                                      reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=data.get("last_page") or 0).pack()))

@router.message(states.AutoDeliveriesStates.entering_new_auto_delivery_keyphrases, F.text)
async def handler_entering_new_auto_delivery_keyphrases(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком короткое значение")
        
        data = await state.get_data()
        keyphrases = [phrase.strip() for phrase in message.text.strip().split(",")]
        await state.update_data(new_auto_delivery_keyphrases=keyphrases)

        await state.set_state(states.AutoDeliveriesStates.entering_new_auto_delivery_message)
        await throw_float_message(state=state,
                                  message=message,
                                  text=templ.adding_new_deliv_float_text(f"💬 Введите <b>сообщение авто-выдачи</b>, которое будет писаться после покупки лота ↓"),
                                  reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=data.get("last_page") or 0).pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            data = await state.get_data()
            await throw_float_message(state=state,
                                      message=message,
                                      text=templ.settings_new_deliv_float_text(e), 
                                      reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=data.get("last_page") or 0).pack()))
        
@router.message(states.AutoDeliveriesStates.entering_new_auto_delivery_message, F.text)
async def handler_entering_new_auto_delivery_message(message: types.Message, state: FSMContext):
    try:
        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком короткое значение")

        data = await state.get_data()
        await state.update_data(new_auto_delivery_message=message.text.strip())
        keyphrases = "</code>, <code>".join(data.get("new_auto_delivery_keyphrases"))
        await throw_float_message(state=state,
                                  message=message,
                                  text=templ.adding_new_deliv_float_text(f"➕ Подтвердите <b>добавление авто-выдачи</b> с ключевыми фразами <code>{keyphrases}</code>"),
                                  reply_markup=templ.confirm_kb(confirm_cb="add_new_auto_delivery", cancel_cb=calls.AutoDeliveriesPagination(page=data.get("last_page") or 0).pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            data = await state.get_data()
            await throw_float_message(state=state,
                                      message=message,
                                      text=templ.settings_new_deliv_float_text(e), 
                                      reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=data.get("last_page") or 0).pack()))

@router.message(states.AutoDeliveryPageStates.entering_auto_delivery_keyphrases, F.text)
async def handler_entering_auto_delivery_keyphrases(message: types.Message, state: FSMContext):
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
        await throw_float_message(state=state,
                                  message=message,
                                  text=templ.settings_deliv_page_float_text(f"✅ <b>Ключевые фразы</b> были успешно изменены на: <code>{keyphrases}</code>"),
                                  reply_markup=templ.back_kb(calls.AutoDeliveryPage(index=data.get("auto_delivery_index")).pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            data = await state.get_data()
            await throw_float_message(state=state,
                                      message=message,
                                      text=templ.settings_deliv_page_float_text(e), 
                                      reply_markup=templ.back_kb(calls.AutoDeliveryPage(index=data.get("auto_delivery_index")).pack()))

@router.message(states.AutoDeliveryPageStates.entering_auto_delivery_message, F.text)
async def handler_entering_auto_delivery_message(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        if len(message.text.strip()) <= 0:
            raise Exception("❌ Слишком короткий текст")

        data = await state.get_data()
        auto_deliveries = sett.get("auto_deliveries")
        auto_deliveries[data.get("auto_delivery_index")]["message"] = message.text.strip().splitlines()
        sett.set("auto_deliveries", auto_deliveries)
        
        await throw_float_message(state=state,
                                  message=message,
                                  text=templ.settings_deliv_page_float_text(f"✅ <b>Сообщение авто-выдачи</b> было успешно изменено на: <blockquote>{message.text.strip()}</blockquote>"),
                                  reply_markup=templ.back_kb(calls.AutoDeliveryPage(index=data.get("auto_delivery_index")).pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            data = await state.get_data()
            await throw_float_message(state=state,
                                      message=message,
                                      text=templ.settings_deliv_page_float_text(e), 
                                      reply_markup=templ.back_kb(calls.AutoDeliveryPage(index=data.get("auto_delivery_index")).pack()))
            

@router.message(states.SettingsStates.entering_messages_watermark, F.text)
async def handler_entering_messages_watermark(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        data = await state.get_data()
        if len(message.text.strip()) <= 0 or len(message.text.strip()) >= 150:
            raise Exception("❌ Слишком короткое или длинное значение")

        config = sett.get("config")
        config["playerok"]["bot"]["messages_watermark"] = message.text.strip()
        sett.set("config", config)
        await throw_float_message(state=state,
                                  message=message,
                                  text=templ.settings_other_float_text(f"✅ <b>Водяной знак сообщений</b> был успешно изменён на <b>{message.text.strip()}</b>"),
                                  reply_markup=templ.back_kb(calls.SettingsNavigation(to="other").pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            await throw_float_message(state=state,
                                      message=message,
                                      text=templ.settings_other_float_text(e), 
                                      reply_markup=templ.back_kb(calls.SettingsNavigation(to="other").pack()))