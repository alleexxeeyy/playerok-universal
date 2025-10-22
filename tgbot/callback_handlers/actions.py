from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramAPIError

from core.modules import get_module_by_uuid, enable_module, disable_module
from playerokapi.enums import ItemDealStatuses

from settings import Settings as sett
from .. import templates as templ
from .. import callback_datas as calls
from .. import states as states
from ..helpful import throw_float_message
from .navigation import *

router = Router()



@router.callback_query(F.data == "destroy")
async def callback_back(callback: CallbackQuery):
    await callback.message.delete()


@router.callback_query(calls.RememberUsername.filter())
async def callback_remember_username(callback: CallbackQuery, callback_data: calls.RememberUsername, state: FSMContext):
    await state.set_state(None)
    username = callback_data.name
    do = callback_data.do
    await state.update_data(username=username)
    if do == "send_mess":
        await state.set_state(states.ActionsStates.entering_message_text)
        await throw_float_message(state=state, 
                                    message=callback.message, 
                                    text=templ.do_action_text(f"💬 Введите <b>сообщение</b> для отправки <b>{username}</b> ↓"), 
                                    reply_markup=templ.destroy_kb(),
                                    callback=callback,
                                    send=True)

@router.callback_query(calls.RememberDealId.filter())
async def callback_remember_deal_id(callback: CallbackQuery, callback_data: calls.RememberDealId, state: FSMContext):
    await state.set_state(None)
    deal_id = callback_data.de_id
    do = callback_data.do
    await state.update_data(deal_id=deal_id)
    if do == "refund":
        await throw_float_message(state=state, 
                                  message=callback.message, 
                                  text=templ.do_action_text(f'📦✔️ Подтвердите <b>возврат</b> <a href="https://playerok.com/deal/{deal_id}">сделки</a> ↓'), 
                                  reply_markup=templ.confirm_kb(confirm_cb="refund_deal", cancel_cb="destroy"),
                                  callback=callback,
                                  send=True)
    if do == "complete":
        await throw_float_message(state=state, 
                                  message=callback.message, 
                                  text=templ.do_action_text(f'☑️✔️ Подтвердите <b>выполнение</b> <a href="https://playerok.com/deal/{deal_id}">сделки</a> ↓'), 
                                  reply_markup=templ.confirm_kb(confirm_cb="complete_deal", cancel_cb="destroy"),
                                  callback=callback,
                                  send=True)
        
@router.callback_query(F.data == "refund_deal")
async def callback_refund_deal(callback: CallbackQuery, state: FSMContext):
    from plbot.playerokbot import get_playerok_bot
    await state.set_state(None)
    plbot = get_playerok_bot()
    data = await state.get_data()
    deal_id = data.get("deal_id")
    plbot.playerok_account.update_deal(deal_id, ItemDealStatuses.ROLLED_BACK)
    await throw_float_message(state=state, 
                              message=callback.message, 
                              text=templ.do_action_text(f"✅ По сделке <b>https://playerok.com/deal/{deal_id}</b> был оформлен возврат"), 
                              reply_markup=templ.destroy_kb())
        
@router.callback_query(F.data == "complete_deal")
async def callback_complete_deal(callback: CallbackQuery, state: FSMContext):
    from plbot.playerokbot import get_playerok_bot
    await state.set_state(None)
    plbot = get_playerok_bot()
    data = await state.get_data()
    deal_id = data.get("deal_id")
    plbot.playerok_account.update_deal(deal_id, ItemDealStatuses.SENT)
    await throw_float_message(state=state, 
                              message=callback.message, 
                              text=templ.do_action_text(f"✅ Сделка <b>https://playerok.com/deal/{deal_id}</b> была помечена вами, как выполненная"), 
                              reply_markup=templ.destroy_kb())


@router.callback_query(F.data == "enter_token")
async def callback_enter_token(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.entering_token)
    config = sett.get("config")
    golden_key = config["playerok"]["api"]["token"] or "❌ Не задано"
    await throw_float_message(state=state, 
                              message=callback.message, 
                              text=templ.settings_auth_float_text(f"🔐 Введите новый <b>токен</b> вашего аккаунта ↓\n┗ Текущее: <code>{golden_key}</code>"), 
                              reply_markup=templ.back_kb(calls.SettingsNavigation(to="auth").pack()))

@router.callback_query(F.data == "enter_user_agent")
async def callback_enter_user_agent(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.entering_user_agent)
    config = sett.get("config")
    user_agent = config["playerok"]["api"]["user_agent"] or "❌ Не задано"
    await throw_float_message(state=state, 
                              message=callback.message, 
                              text=templ.settings_auth_float_text(f"🎩 Введите новый <b>user_agent</b> вашего браузера ↓\n┗ Текущее: <code>{user_agent}</code>"), 
                              reply_markup=templ.back_kb(calls.SettingsNavigation(to="auth").pack()))
    

@router.callback_query(F.data == "remove_proxy")
async def callback_remove_proxy(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    config = sett.get("config")
    proxy = config["playerok"]["api"]["proxy"] = ""
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="conn"), state)

@router.callback_query(F.data == "enter_proxy")
async def callback_enter_proxy(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.entering_proxy)
    config = sett.get("config")
    proxy = config["playerok"]["api"]["proxy"] or "❌ Не задано"
    await throw_float_message(state=state, 
                              message=callback.message, 
                              text=templ.settings_conn_float_text(f"🌐 Введите новый <b>прокси-сервер</b> (формат: user:pass@ip:port или ip:port) ↓\n┗ Текущее: <code>{proxy}</code>"), 
                              reply_markup=templ.back_kb(calls.SettingsNavigation(to="conn").pack()))

@router.callback_query(F.data == "enter_requests_timeout")
async def callback_enter_requests_timeout(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.entering_requests_timeout)
    config = sett.get("config")
    requests_timeout = config["playerok"]["api"]["requests_timeout"] or "❌ Не задано"
    await throw_float_message(state=state, 
                              message=callback.message, 
                              text=templ.settings_conn_float_text(f"🛜 Введите новый <b>таймаут подключения</b> (в секундах) ↓\n┗ Текущее: <code>{requests_timeout}</code>"), 
                              reply_markup=templ.back_kb(calls.SettingsNavigation(to="conn").pack()))

@router.callback_query(F.data == "enter_listener_requests_delay")
async def callback_enter_listener_requests_delay(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.entering_listener_requests_delay)
    config = sett.get("config")
    requests_timeout = config["playerok"]["api"]["listener_requests_delay"] or "❌ Не задано"
    await throw_float_message(state=state, 
                                message=callback.message, 
                                text=templ.settings_conn_float_text(f"⏱️ Введите новую <b>периодичность запросов</b> (в секундах) ↓\n┗ Текущее: <code>{requests_timeout}</code>"), 
                                reply_markup=templ.back_kb(calls.SettingsNavigation(to="conn").pack()))


@router.callback_query(F.data == "switch_auto_restore_items_enabled")
async def callback_switch_auto_restore_items_enabled(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["bot"]["auto_restore_items_enabled"] = not config["playerok"]["bot"]["auto_restore_items_enabled"]
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="items"), state)

@router.callback_query(F.data == "switch_read_chat_before_sending_message_enabled")
async def callback_switch_read_chat_before_sending_message_enabled(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["bot"]["read_chat_before_sending_message_enabled"] = not config["playerok"]["bot"]["read_chat_before_sending_message_enabled"]
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="other"), state)

@router.callback_query(F.data == "switch_auto_complete_deals_enabled")
async def callback_switch_auto_complete_deals_enabled(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["bot"]["auto_complete_deals_enabled"] = not config["playerok"]["bot"]["auto_complete_deals_enabled"]
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="other"), state)

@router.callback_query(F.data == "switch_custom_commands_enabled")
async def callback_switch_custom_commands_enabled(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["bot"]["custom_commands_enabled"] = False if config["playerok"]["bot"]["custom_commands_enabled"] else True
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="other"), state)

@router.callback_query(F.data == "switch_auto_deliveries_enabled")
async def callback_switch_auto_deliveries_enabled(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["bot"]["auto_deliveries_enabled"] = False if config["playerok"]["bot"]["auto_deliveries_enabled"] else True
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="other"), state)

@router.callback_query(F.data == "switch_messages_watermark_enabled")
async def callback_switch_messages_watermark_enabled(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["bot"]["messages_watermark_enabled"] = False if config["playerok"]["bot"]["messages_watermark_enabled"] else True
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="other"), state)

@router.callback_query(F.data == "enter_messages_watermark")
async def callback_enter_messages_watermark(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.entering_messages_watermark)
    config = sett.get("config")
    messages_watermark = config["playerok"]["bot"]["messages_watermark"] or "❌ Не задано"
    await throw_float_message(state=state, 
                              message=callback.message, 
                              text=templ.settings_other_float_text(f"✍️©️ Введите новый <b>водяной знак</b> под сообщениями ↓\n┗ Текущее: <code>{messages_watermark}</code>"), 
                              reply_markup=templ.back_kb(calls.SettingsNavigation(to="other").pack()))
        


@router.callback_query(F.data == "enter_custom_commands_page")
async def callback_enter_custom_commands_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page") or 0
    await state.set_state(states.CustomCommandsStates.entering_page)
    await throw_float_message(state=state, 
                              message=callback.message, 
                              text=templ.settings_comm_float_text(f"📃 Введите номер страницы для перехода ↓"), 
                              reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack()))

@router.callback_query(F.data == "enter_new_custom_command")
async def callback_enter_new_custom_command(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page") or 0
    await state.set_state(states.CustomCommandsStates.entering_new_custom_command)
    await throw_float_message(state=state, 
                              message=callback.message, 
                              text=templ.adding_new_comm_float_text(f"⌨️ Введите <b>новую команду</b> (например, <code>!тест</code>) ↓"), 
                              reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack()))

@router.callback_query(F.data == "add_new_custom_command")
async def callback_add_new_custom_command(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        last_page = data.get("last_page") or 0
        custom_commands = sett.get("custom_commands")
        new_custom_command = data.get("new_custom_command")
        new_custom_command_answer = data.get("new_custom_command_answer")
        if not new_custom_command:
            raise Exception("❌ Новая пользовательская команда не была найдена, повторите процесс с самого начала")
        if not new_custom_command_answer:
            raise Exception("❌ Ответ на новую пользовательскую команду не был найден, повторите процесс с самого начала")

        custom_commands[new_custom_command] = new_custom_command_answer.splitlines()
        sett.set("custom_commands", custom_commands)
        last_page = data.get("last_page") or 0
        await throw_float_message(state=state, 
                                  message=callback.message, 
                                  text=templ.adding_new_comm_float_text(f"✅ <b>Пользовательская команда</b> <code>{new_custom_command}</code> была добавлена"), 
                                  reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            data = await state.get_data()
            last_page = data.get("last_page") or 0
            await throw_float_message(state=state, 
                                      message=callback.message, 
                                      text=templ.adding_new_comm_float_text(e), 
                                      reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack()))

@router.callback_query(F.data == "enter_custom_command_answer")
async def callback_enter_custom_command_answer(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        custom_commands = sett.get("custom_commands")
        custom_command = data.get("custom_command")
        if not custom_command:
            raise Exception("❌ Пользовательская команда не была найдена, повторите процесс с самого начала")
        
        await state.set_state(states.CustomCommandPageStates.entering_custom_command_answer)
        custom_command_answer = "\n".join(custom_commands[custom_command]) or "❌ Не задано"
        await throw_float_message(state=state, 
                                  message=callback.message, 
                                  text=templ.settings_comm_page_float_text(f"💬 Введите новый <b>текст ответа</b> команды <code>{custom_command}</code> ↓\n┗ Текущее: <blockquote>{custom_command_answer}</blockquote>"), 
                                  reply_markup=templ.back_kb(calls.CustomCommandPage(command=custom_command).pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            data = await state.get_data()
            last_page = data.get("last_page") or 0
            await throw_float_message(state=state, 
                                      message=callback.message, 
                                      text=templ.settings_comm_page_float_text(e), 
                                      reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack()))

@router.callback_query(F.data == "confirm_deleting_custom_command")
async def callback_confirm_deleting_custom_command(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        custom_command = data.get("custom_command")
        if not custom_command:
            raise Exception("❌ Пользовательская команда не была найдена, повторите процесс с самого начала")
        
        await throw_float_message(state=state, 
                                  message=callback.message, 
                                  text=templ.settings_comm_page_float_text(f"🗑️ Подтвердите <b>удаление пользовательской команды</b> <code>{custom_command}</code>"), 
                                  reply_markup=templ.confirm_kb(confirm_cb="delete_custom_command", cancel_cb=calls.CustomCommandPage(command=custom_command).pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            data = await state.get_data()
            last_page = data.get("last_page") or 0
            await throw_float_message(state=state, 
                                      message=callback.message, 
                                      text=templ.settings_comm_page_float_text(e), 
                                      reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack()))

@router.callback_query(F.data == "delete_custom_command")
async def callback_delete_custom_command(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        last_page = data.get("last_page") or 0
        custom_commands = sett.get("custom_commands")
        custom_command = data.get("custom_command")
        if not custom_command:
            raise Exception("❌ Пользовательская команда не была найдена, повторите процесс с самого начала")
        
        del custom_commands[custom_command]
        sett.set("custom_commands", custom_commands)
        await throw_float_message(state=state, 
                                  message=callback.message, 
                                  text=templ.settings_comm_page_float_text(f"✅ <b>Пользовательская команда</b> <code>{custom_command}</code> была удалена"), 
                                  reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            data = await state.get_data()
            last_page = data.get("last_page") or 0
            await throw_float_message(state=state, 
                                      message=callback.message, 
                                      text=templ.settings_comm_page_float_text(e), 
                                      reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack()))


@router.callback_query(F.data == "enter_auto_deliveries_page")
async def callback_enter_auto_deliveries_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page") or 0
    await state.set_state(states.AutoDeliveriesStates.entering_page)
    await throw_float_message(state=state, 
                              message=callback.message, 
                              text=templ.settings_deliv_float_text(f"📃 Введите номер страницы для перехода ↓"), 
                              reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack()))

@router.callback_query(F.data == "enter_new_auto_delivery_keyphrases")
async def callback_enter_new_auto_delivery_keyphrases(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page") or 0
    await state.set_state(states.AutoDeliveriesStates.entering_new_auto_delivery_keyphrases)
    await throw_float_message(state=state, 
                              message=callback.message, 
                              text=templ.adding_new_deliv_float_text(f"🔑 Введите <b>ключевые фразы</b> названия товара, на который нужно добавить авто-выдачу (указываются через запятую, например, \"telegram подписчики, авто-выдача\") ↓"), 
                              reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack()))

@router.callback_query(F.data == "add_new_auto_delivery")
async def callback_add_new_auto_delivery(callback: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(None)
        data = await state.get_data()
        last_page = data.get("last_page") or 0
        auto_deliveries = sett.get("auto_deliveries")
        new_auto_delivery_keyphrases = data.get("new_auto_delivery_keyphrases")
        new_auto_delivery_message = data.get("new_auto_delivery_message")
        if not new_auto_delivery_keyphrases:
            raise Exception("❌ Ключевые фразы авто-выдачи не были найдены, повторите процесс с самого начала")
        if not new_auto_delivery_message:
            raise Exception("❌ Сообщение авто-выдачи не было найдено, повторите процесс с самого начала")
        
        auto_deliveries.append({"keyphrases": new_auto_delivery_keyphrases, "message": new_auto_delivery_message.splitlines()})
        sett.set("auto_deliveries", auto_deliveries)
        await throw_float_message(state=state, 
                                  message=callback.message, 
                                  text=templ.adding_new_deliv_float_text(f"✅ <b>Авто-выдача</b> была добавлена"), 
                                  reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            data = await state.get_data()
            last_page = data.get("last_page") or 0
            await throw_float_message(state=state, 
                                      message=callback.message, 
                                      text=templ.adding_new_deliv_float_text(e), 
                                      reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack()))

@router.callback_query(F.data == "enter_auto_delivery_keyphrases")
async def callback_enter_auto_delivery_keyphrases(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        auto_delivery_index = data.get("auto_delivery_index")
        if auto_delivery_index is None:
            raise Exception("❌ Авто-выдача не была найдена, повторите процесс с самого начала")
        
        await state.set_state(states.AutoDeliveryPageStates.entering_auto_delivery_keyphrases)
        auto_deliveries = sett.get("auto_deliveries")
        auto_delivery_message = "</code>, <code>".join(auto_deliveries[auto_delivery_index]["keyphrases"]) or "❌ Не задано"
        await throw_float_message(state=state, 
                                  message=callback.message, 
                                  text=templ.settings_deliv_page_float_text(f"🔑 Введите новые <b>ключевые фразы</b> названия товара, на который авто-выдачи (указываются через запятую)\n┗ Текущее: <code>{auto_delivery_message}</code>"), 
                                  reply_markup=templ.back_kb(calls.AutoDeliveryPage(index=auto_delivery_index).pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            data = await state.get_data()
            last_page = data.get("last_page") or 0
            await throw_float_message(state=state, 
                                      message=callback.message, 
                                      text=templ.settings_deliv_page_float_text(e), 
                                      reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack()))

@router.callback_query(F.data == "enter_auto_delivery_message")
async def callback_enter_auto_delivery_message(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        auto_delivery_index = data.get("auto_delivery_index")
        if auto_delivery_index is None:
            raise Exception("❌ Авто-выдача не была найдена, повторите процесс с самого начала")
        
        await state.set_state(states.AutoDeliveryPageStates.entering_auto_delivery_message)
        auto_deliveries = sett.get("auto_deliveries")
        auto_delivery_message = "\n".join(auto_deliveries[auto_delivery_index]["message"]) or "❌ Не задано"
        await throw_float_message(state=state, 
                                  message=callback.message, 
                                  text=templ.settings_deliv_page_float_text(f"💬 Введите новое <b>сообщение</b> после покупки\n┗ Текущее: <blockquote>{auto_delivery_message}</blockquote>"), 
                                  reply_markup=templ.back_kb(calls.AutoDeliveryPage(index=auto_delivery_index).pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            data = await state.get_data()
            last_page = data.get("last_page") or 0
            await throw_float_message(state=state, 
                                      message=callback.message, 
                                      text=templ.settings_deliv_page_float_text(e), 
                                      reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack()))

@router.callback_query(F.data == "confirm_deleting_auto_delivery")
async def callback_confirm_deleting_auto_delivery(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        auto_delivery_index = data.get("auto_delivery_index")
        if auto_delivery_index is None:
            raise Exception("❌ Авто-выдача не была найдена, повторите процесс с самого начала")
        

        auto_deliveries = sett.get("auto_deliveries")
        auto_delivery_keyphrases = "</code>, <code>".join(auto_deliveries[auto_delivery_index]["keyphrases"]) or "❌ Не задано"
        await throw_float_message(state=state, 
                                  message=callback.message, 
                                  text=templ.settings_deliv_page_float_text(f"🗑️ Подтвердите <b>удаление пользовательской авто-выдачи</b> для ключевых фраз <code>{auto_delivery_keyphrases}</code>"), 
                                  reply_markup=templ.confirm_kb(confirm_cb="delete_auto_delivery", cancel_cb=calls.AutoDeliveryPage(index=auto_delivery_index).pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            data = await state.get_data()
            last_page = data.get("last_page") or 0
            await throw_float_message(state=state, 
                                      message=callback.message, 
                                      text=templ.settings_deliv_page_float_text(e), 
                                      reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack()))

@router.callback_query(F.data == "delete_auto_delivery")
async def callback_delete_auto_delivery(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        auto_delivery_index = data.get("auto_delivery_index")
        if auto_delivery_index is None:
            raise Exception("❌ Авто-выдача не была найдена, повторите процесс с самого начала")
        
        auto_deliveries = sett.get("auto_deliveries")
        del auto_deliveries[auto_delivery_index]
        sett.set("auto_deliveries", auto_deliveries)
        last_page = data.get("last_page") or 0
        await throw_float_message(state=state, 
                                  message=callback.message, 
                                  text=templ.settings_deliv_page_float_text(f"✅ <b>Авто-выдача</b> была удалена"), 
                                  reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            data = await state.get_data()
            last_page = data.get("last_page") or 0
            await throw_float_message(state=state, 
                                      message=callback.message, 
                                      text=templ.settings_deliv_page_float_text(e), 
                                      reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack()))

        
@router.callback_query(F.data == "enter_messages_page")
async def callback_enter_messages_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page") or 0
    await state.set_state(states.MessagesStates.entering_page)
    await throw_float_message(state=state, 
                              message=callback.message, 
                              text=templ.settings_mess_float_text(f"📃 Введите номер страницы для перехода ↓"), 
                              reply_markup=templ.back_kb(calls.MessagesPagination(page=last_page).pack()))

@router.callback_query(F.data == "switch_message_enabled")
async def callback_switch_message_enabled(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        last_page = data.get("last_page") or 0
        message_id = data.get("message_id")
        if not message_id:
            raise Exception("❌ ID сообщения не был найден, повторите процесс с самого начала")
        
        messages = sett.get("messages")
        messages[message_id]["enabled"] = not messages[message_id]["enabled"]
        sett.set("messages", messages)
        return await callback_message_page(callback, calls.MessagePage(message_id=message_id), state)
    except Exception as e:
        if e is not TelegramAPIError:
            data = await state.get_data()
            last_page = data.get("last_page") or 0
            await throw_float_message(state=state, 
                                      message=callback.message, 
                                      text=templ.settings_mess_float_text(e), 
                                      reply_markup=templ.back_kb(calls.MessagesPagination(page=last_page).pack()))

@router.callback_query(F.data == "enter_message_text")
async def callback_enter_message_text(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        last_page = data.get("last_page") or 0
        message_id = data.get("message_id")
        if not message_id:
            raise Exception("❌ ID сообщения не был найден, повторите процесс с самого начала")
        
        await state.set_state(states.MessagePageStates.entering_message_text)
        messages = sett.get("messages")
        mess_text = "\n".join(messages[message_id]["text"]) or "❌ Не задано"
        await throw_float_message(state=state, 
                                  message=callback.message, 
                                  text=templ.settings_mess_float_text(f"💬 Введите новый <b>текст сообщения</b> <code>{message_id}</code> ↓\n┗ Текущее: <blockquote>{mess_text}</blockquote>"), 
                                  reply_markup=templ.back_kb(calls.MessagesPagination(page=last_page).pack()))
    except Exception as e:
        if e is not TelegramAPIError:
            data = await state.get_data()
            last_page = data.get("last_page") or 0
            await throw_float_message(state=state, 
                                      message=callback.message, 
                                      text=templ.settings_mess_float_text(e), 
                                      reply_markup=templ.back_kb(calls.MessagesPagination(page=last_page).pack()))


@router.callback_query(F.data == "switch_tg_logging_enabled")
async def callback_switch_tg_logging_enabled(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["bot"]["tg_logging_enabled"] = not config["playerok"]["bot"]["tg_logging_enabled"]
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="logger"), state)

@router.callback_query(F.data == "enter_tg_logging_chat_id")
async def callback_enter_tg_logging_chat_id(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.entering_tg_logging_chat_id)
    config = sett.get("config")
    tg_logging_chat_id = config["playerok"]["bot"]["tg_logging_chat_id"] or "✔️ Ваш чат с ботом"
    await throw_float_message(state=state, 
                              message=callback.message, 
                              text=templ.settings_logger_float_text(f"💬 Введите новый <b>ID чата для логов</b> (вы можете указать как цифровой ID, так и юзернейм чата) ↓\n┗ Текущее: <code>{tg_logging_chat_id}</code>"), 
                              reply_markup=templ.back_kb(calls.SettingsNavigation(to="logger").pack()))

@router.callback_query(F.data == "switch_tg_logging_event_new_user_message")
async def callback_switch_tg_logging_event_new_user_message(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["bot"]["tg_logging_events"]["new_user_message"] = not config["playerok"]["bot"]["tg_logging_events"]["new_user_message"]
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="logger"), state)

@router.callback_query(F.data == "switch_tg_logging_event_new_system_message")
async def callback_switch_tg_logging_event_new_system_message(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["bot"]["tg_logging_events"]["new_system_message"] = not config["playerok"]["bot"]["tg_logging_events"]["new_system_message"]
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="logger"), state)

@router.callback_query(F.data == "switch_tg_logging_event_new_deal")
async def callback_switch_tg_logging_event_new_deal(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["bot"]["tg_logging_events"]["new_deal"] = not config["playerok"]["bot"]["tg_logging_events"]["new_deal"]
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="logger"), state)

@router.callback_query(F.data == "switch_tg_logging_event_new_review")
async def callback_switch_tg_logging_event_new_review(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["bot"]["tg_logging_events"]["new_review"] = not config["playerok"]["bot"]["tg_logging_events"]["new_review"]
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="logger"), state)

@router.callback_query(F.data == "switch_tg_logging_event_new_problem")
async def callback_switch_tg_logging_event_new_problem(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["bot"]["tg_logging_events"]["new_problem"] = not config["playerok"]["bot"]["tg_logging_events"]["new_problem"]
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="logger"), state)

@router.callback_query(F.data == "switch_tg_logging_event_deal_status_changed")
async def callback_switch_tg_logging_event_deal_status_changed(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["bot"]["tg_logging_events"]["deal_status_changed"] = not config["playerok"]["bot"]["tg_logging_events"]["deal_status_changed"]
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="logger"), state)

@router.callback_query(F.data == "clean_tg_logging_chat_id")
async def callback_clean_tg_logging_chat_id(callback: CallbackQuery, state: FSMContext):
    config = sett.get("config")
    config["playerok"]["bot"]["tg_logging_chat_id"] = ""
    sett.set("config", config)
    return await callback_settings_navigation(callback, calls.SettingsNavigation(to="logger"), state)


@router.callback_query(F.data == "switch_module_enabled")
async def callback_disable_module(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        last_page = data.get("last_page") or 0
        module_uuid = data.get("module_uuid")
        if not module_uuid:
            raise Exception("❌ UUID модуля не был найден, повторите процесс с самого начала")

        module = get_module_by_uuid(module_uuid)
        disable_module(module_uuid) if module.enabled else enable_module(module_uuid)
        return await callback_module_page(callback, calls.ModulePage(uuid=module_uuid), state)
    except Exception as e:
        if e is not TelegramAPIError:
            data = await state.get_data()
            last_page = data.get("last_page") or 0
            await throw_float_message(state=state, 
                                      message=callback.message, 
                                      text=templ.module_page_float_text(e), 
                                      reply_markup=templ.back_kb(calls.ModulesPagination(page=last_page).pack()))