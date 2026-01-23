from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from settings import Settings as sett

from .. import templates as templ
from .. import callback_datas as calls
from .. import states as states
from ..helpful import throw_float_message
from .navigation import *


router = Router()


@router.callback_query(F.data == "enter_token")
async def callback_enter_token(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.waiting_for_token)
    config = sett.get("config")
    golden_key = config["playerok"]["api"]["token"] or "❌ Не задано"
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_auth_float_text(f"🔐 Введите новый <b>токен</b> вашего аккаунта ↓\n・ Текущее: <code>{golden_key}</code>"), 
        reply_markup=templ.back_kb(calls.SettingsNavigation(to="auth").pack())
    )


@router.callback_query(F.data == "enter_user_agent")
async def callback_enter_user_agent(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.waiting_for_user_agent)
    config = sett.get("config")
    user_agent = config["playerok"]["api"]["user_agent"] or "❌ Не задано"
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_auth_float_text(f"🎩 Введите новый <b>user_agent</b> вашего браузера ↓\n・ Текущее: <code>{user_agent}</code>"), 
        reply_markup=templ.back_kb(calls.SettingsNavigation(to="auth").pack())
    )


@router.callback_query(F.data == "enter_proxy")
async def callback_enter_proxy(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.waiting_for_proxy)
    config = sett.get("config")
    proxy = config["playerok"]["api"]["proxy"] or "❌ Не задано"
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_conn_float_text(f"🌐 Введите новый <b>прокси-сервер</b> (формат: user:pass@ip:port или ip:port) ↓\n・ Текущее: <code>{proxy}</code>"), 
        reply_markup=templ.back_kb(calls.SettingsNavigation(to="conn").pack())
    )


@router.callback_query(F.data == "enter_requests_timeout")
async def callback_enter_requests_timeout(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.waiting_for_requests_timeout)
    config = sett.get("config")
    requests_timeout = config["playerok"]["api"]["requests_timeout"] or "❌ Не задано"
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_conn_float_text(f"🛜 Введите новый <b>таймаут подключения</b> (в секундах) ↓\n・ Текущее: <code>{requests_timeout}</code>"), 
        reply_markup=templ.back_kb(calls.SettingsNavigation(to="conn").pack())
    )


@router.callback_query(F.data == "enter_watermark_value")
async def callback_enter_watermark_value(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.waiting_for_watermark_value)
    config = sett.get("config")
    watermark_value = config["playerok"]["watermark"]["value"] or "❌ Не задано"
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_other_float_text(f"✍️©️ Введите новый <b>водяной знак</b> под сообщениями ↓\n・ Текущее: <code>{watermark_value}</code>"), 
        reply_markup=templ.back_kb(calls.SettingsNavigation(to="other").pack())
    )


@router.callback_query(F.data == "enter_new_included_restore_item_keyphrases")
async def callback_enter_new_included_restore_item_keyphrases(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    await state.set_state(states.RestoreItemsStates.waiting_for_new_included_restore_item_keyphrases)
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_new_restore_included_float_text(f"🔑 Введите <b>ключевые фразы</b> названия товара, который нужно включить в авто-восстановление (указываются через запятую, например, \"samp аккаунт, со всеми данными\") ↓"), 
        reply_markup=templ.back_kb(calls.IncludedRestoreItemsPagination(page=last_page).pack())
    )


@router.callback_query(F.data == "enter_new_excluded_restore_item_keyphrases")
async def callback_enter_new_excluded_restore_item_keyphrases(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    await state.set_state(states.RestoreItemsStates.waiting_for_new_excluded_restore_item_keyphrases)
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_new_restore_excluded_float_text(f"🔑 Введите <b>ключевые фразы</b> названия товара, который нужно исключить из авто-восстановления (указываются через запятую, например, \"samp аккаунт, со всеми данными\") ↓"), 
        reply_markup=templ.back_kb(calls.ExcludedRestoreItemsPagination(page=last_page).pack())
    )


@router.callback_query(F.data == "enter_auto_bump_items_interval")
async def callback_enter_auto_bump_items_interval(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.set_state(states.BumpItemsStates.waiting_for_bump_items_interval)
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_bump_float_text(f"⏲️ Введите <b>интервал поднятия предметов</b> ↓"), 
        reply_markup=templ.back_kb(calls.SettingsNavigation(to="bump").pack())
    )


@router.callback_query(F.data == "enter_new_included_bump_item_keyphrases")
async def callback_enter_new_included_bump_item_keyphrases(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    await state.set_state(states.BumpItemsStates.waiting_for_new_included_bump_item_keyphrases)
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_new_bump_included_float_text(f"🔑 Введите <b>ключевые фразы</b> названия товара, который нужно включить в авто-поднятие (указываются через запятую, например, \"samp аккаунт, со всеми данными\") ↓"), 
        reply_markup=templ.back_kb(calls.IncludedBumpItemsPagination(page=last_page).pack())
    )


@router.callback_query(F.data == "enter_new_excluded_bump_item_keyphrases")
async def callback_enter_new_excluded_bump_item_keyphrases(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    await state.set_state(states.BumpItemsStates.waiting_for_new_excluded_bump_item_keyphrases)
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_new_bump_excluded_float_text(f"🔑 Введите <b>ключевые фразы</b> названия товара, который нужно исключить из авто-поднятия (указываются через запятую, например, \"samp аккаунт, со всеми данными\") ↓"), 
        reply_markup=templ.back_kb(calls.ExcludedBumpItemsPagination(page=last_page).pack())
    )
        

@router.callback_query(F.data == "enter_custom_commands_page")
async def callback_enter_custom_commands_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    await state.set_state(states.CustomCommandsStates.waiting_for_page)
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_comms_float_text(f"📃 Введите номер страницы для перехода ↓"), 
        reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack())
    )


@router.callback_query(F.data == "enter_new_custom_command")
async def callback_enter_new_custom_command(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    await state.set_state(states.CustomCommandsStates.waiting_for_new_custom_command)
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_new_comm_float_text(f"⌨️ Введите <b>новую команду</b> (например, <code>!тест</code>) ↓"), 
        reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack())
    )


@router.callback_query(F.data == "enter_custom_command_answer")
async def callback_enter_custom_command_answer(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        custom_commands = sett.get("custom_commands")
        custom_command = data.get("custom_command")
        if not custom_command:
            raise Exception("❌ Пользовательская команда не была найдена, повторите процесс с самого начала")
        
        await state.set_state(states.CustomCommandsStates.waiting_for_custom_command_answer)
        custom_command_answer = "\n".join(custom_commands[custom_command]) or "❌ Не задано"
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_comm_page_float_text(f"💬 Введите новый <b>текст ответа</b> команды <code>{custom_command}</code> ↓\n・ Текущее: <blockquote>{custom_command_answer}</blockquote>"), 
            reply_markup=templ.back_kb(calls.CustomCommandPage(command=custom_command).pack())
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_comm_page_float_text(e), 
            reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack())
        )


@router.callback_query(F.data == "enter_auto_deliveries_page")
async def callback_enter_auto_deliveries_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    await state.set_state(states.AutoDeliveriesStates.waiting_for_page)
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_delivs_float_text(f"📃 Введите номер страницы для перехода ↓"), 
        reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
    )


@router.callback_query(F.data == "enter_new_auto_delivery_keyphrases")
async def callback_enter_new_auto_delivery_keyphrases(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    await state.set_state(states.AutoDeliveriesStates.waiting_for_new_auto_delivery_keyphrases)
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_new_deliv_float_text(f"🔑 Введите <b>ключевые фразы</b> названия товара, на который нужно добавить авто-выдачу (указываются через запятую, например, \"telegram подписчики, авто-выдача\") ↓"), 
        reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
    )


@router.callback_query(F.data == "enter_auto_delivery_keyphrases")
async def callback_enter_auto_delivery_keyphrases(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        auto_delivery_index = data.get("auto_delivery_index")
        if auto_delivery_index is None:
            raise Exception("❌ Авто-выдача не была найдена, повторите процесс с самого начала")
        
        await state.set_state(states.AutoDeliveriesStates.waiting_for_auto_delivery_keyphrases)
        auto_deliveries = sett.get("auto_deliveries")
        auto_delivery_message = "</code>, <code>".join(auto_deliveries[auto_delivery_index]["keyphrases"]) or "❌ Не задано"
        
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_deliv_page_float_text(f"🔑 Введите новые <b>ключевые фразы</b> названия товара, на который авто-выдачи (указываются через запятую)\n・ Текущее: <code>{auto_delivery_message}</code>"), 
            reply_markup=templ.back_kb(calls.AutoDeliveryPage(index=auto_delivery_index).pack())
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_deliv_page_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
        )


@router.callback_query(F.data == "enter_auto_delivery_message")
async def callback_enter_auto_delivery_message(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        auto_delivery_index = data.get("auto_delivery_index")
        if auto_delivery_index is None:
            raise Exception("❌ Авто-выдача не была найдена, повторите процесс с самого начала")
        
        await state.set_state(states.AutoDeliveriesStates.waiting_for_auto_delivery_message)
        auto_deliveries = sett.get("auto_deliveries")
        auto_delivery_message = "\n".join(auto_deliveries[auto_delivery_index]["message"]) or "❌ Не задано"
        
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_deliv_page_float_text(f"💬 Введите новое <b>сообщение</b> после покупки\n・ Текущее: <blockquote>{auto_delivery_message}</blockquote>"), 
            reply_markup=templ.back_kb(calls.AutoDeliveryPage(index=auto_delivery_index).pack())
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_deliv_page_float_text(e), 
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
        )


@router.callback_query(F.data == "enter_messages_page")
async def callback_enter_messages_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    await state.set_state(states.MessagesStates.waiting_for_page)
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_mess_float_text(f"📃 Введите номер страницы для перехода ↓"), 
        reply_markup=templ.back_kb(calls.MessagesPagination(page=last_page).pack())
    )


@router.callback_query(F.data == "enter_message_text")
async def callback_enter_message_text(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        message_id = data.get("message_id")
        if not message_id:
            raise Exception("❌ ID сообщения не был найден, повторите процесс с самого начала")
        
        await state.set_state(states.MessagesStates.waiting_for_message_text)
        messages = sett.get("messages")
        mess_text = "\n".join(messages[message_id]["text"]) or "❌ Не задано"
        
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_mess_float_text(f"💬 Введите новый <b>текст сообщения</b> <code>{message_id}</code> ↓\n・ Текущее: <blockquote>{mess_text}</blockquote>"), 
            reply_markup=templ.back_kb(calls.MessagesPagination(page=last_page).pack())
        )
    except Exception as e:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        await throw_float_message(
            state=state, 
            message=callback.message, 
            text=templ.settings_mess_float_text(e), 
            reply_markup=templ.back_kb(calls.MessagesPagination(page=last_page).pack())
        )


@router.callback_query(F.data == "enter_tg_logging_chat_id")
async def callback_enter_tg_logging_chat_id(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.waiting_for_tg_logging_chat_id)
    config = sett.get("config")
    tg_logging_chat_id = config["playerok"]["tg_logging"]["chat_id"] or "✔️ Ваш чат с ботом"
    await throw_float_message(
        state=state, 
        message=callback.message, 
        text=templ.settings_logger_float_text(f"💬 Введите новый <b>ID чата для логов</b> (вы можете указать как цифровой ID, так и юзернейм чата) ↓\n・ Текущее: <code>{tg_logging_chat_id}</code>"), 
        reply_markup=templ.back_kb(calls.SettingsNavigation(to="logger").pack())
    )