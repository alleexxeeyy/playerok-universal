from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from settings import Settings as sett

from .. import templates as templ
from .. import callback_datas as calls
from .. import states as states
from ..helpful import throw_float_message
from .navigation import *
from .pagination import *


router = Router()


@router.callback_query(F.data == "enter_cookies")
async def callback_enter_cookies(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.waiting_for_cookies)
    
    config = sett.get("config")
    cookies = config["playerok"]["api"]["cookies"] or "❌ Не задано"
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.settings_auth_float_text(
            f"🍪 Введите новые <b>Cookie-данные</b> вашего аккаунта:"
            f"\n・ Текущие: <blockquote>{cookies}</blockquote>"
        ),
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
        text=templ.settings_auth_float_text(
            f"🎩 Введите новый <b>User Agent</b> вашего браузера:"
            f"\n・ Текущее: <code>{user_agent}</code>"
        ),
        reply_markup=templ.back_kb(calls.SettingsNavigation(to="auth").pack())
    )


@router.callback_query(F.data == "enter_pl_proxy")
async def callback_enter_pl_proxy(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.waiting_for_pl_proxy)
    
    config = sett.get("config")
    proxy = config["playerok"]["api"]["proxy"] or "❌ Не задано"
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.settings_conn_float_text(
            f"🌐 Введите новый <b>прокси для FunPay</b> (формат: user:pass@ip:port или ip:port):"
            f"\n・ Текущий: <code>{proxy}</code>"
        ),
        reply_markup=templ.back_kb(calls.SettingsNavigation(to="conn").pack())
    )


@router.callback_query(F.data == "enter_tg_proxy")
async def callback_enter_tg_proxy(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.waiting_for_tg_proxy)
    
    config = sett.get("config")
    proxy = config["telegram"]["api"]["proxy"] or "❌ Не задано"
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.settings_conn_float_text(
            f"🌐 Введите новый <b>прокси для Telegram</b> (формат: user:pass@ip:port или ip:port):"
            f"\n・ Текущий: <code>{proxy}</code>"
        ),
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
        text=templ.settings_conn_float_text(
            f"🛜 Введите новый <b>таймаут подключения</b> (в секундах):"
            f"\n・ Текущее: <code>{requests_timeout}</code>"
        ),
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
        text=templ.settings_other_float_text(
            f"✍️©️ Введите новый <b>водяной знак</b> под сообщениями:"
            f"\n・ Текущее: <code>{watermark_value}</code>"
        ),
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
        text=templ.settings_new_restore_included_float_text(
            f"🔑 Введите <b>ключевые фразы</b> названия товара, который нужно включить в авто-восстановление "
            f"(указываются через запятую, например, \"samp аккаунт, со всеми данными\"):"
        ),
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
        text=templ.settings_new_restore_excluded_float_text(
            f"🔑 Введите <b>ключевые фразы</b> названия товара, который нужно исключить из авто-восстановления "
            f"(указываются через запятую, например, \"samp аккаунт, со всеми данными\"):"
        ),
        reply_markup=templ.back_kb(calls.ExcludedRestoreItemsPagination(page=last_page).pack())
    )


@router.callback_query(F.data == "enter_new_included_complete_deal_keyphrases")
async def callback_enter_new_included_complete_deal_keyphrases(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    
    await state.set_state(states.CompleteDealsStates.waiting_for_new_included_complete_deal_keyphrases)
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.settings_new_complete_included_float_text(
            f"🔑 Введите <b>ключевые фразы</b> названия товара, сделку по которому нужно включить в авто-подтверждение "
            f"(указываются через запятую, например, \"samp аккаунт, со всеми данными\"):"
        ),
        reply_markup=templ.back_kb(calls.IncludedCompleteDealsPagination(page=last_page).pack())
    )


@router.callback_query(F.data == "enter_new_excluded_complete_dealm_keyphrases")
async def callback_enter_new_excluded_complete_deal_keyphrases(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    
    await state.set_state(states.CompleteDealsStates.waiting_for_new_excluded_complete_deal_keyphrases)
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.settings_new_complete_excluded_float_text(
            f"🔑 Введите <b>ключевые фразы</b> названия товара, сделку по которому нужно исключить из авто-подтверждения "
            f"(указываются через запятую, например, \"samp аккаунт, со всеми данными\"):"
        ),
        reply_markup=templ.back_kb(calls.ExcludedCompleteDealsPagination(page=last_page).pack())
    )


@router.callback_query(F.data == "enter_auto_bump_items_interval")
async def callback_enter_auto_bump_items_interval(callback: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(states.BumpItemsStates.waiting_for_bump_items_interval)
        
        config = sett.get("config")
        interval = config["playerok"]["auto_bump_items"]["interval"]
        
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.settings_bump_float_text(
                f"⏲️ Введите <b>интервал поднятия предметов</b>:"
                f"\n・ Текущее: <code>{interval}</code> сек."
            ),
            reply_markup=templ.back_kb(calls.SettingsNavigation(to="bump").pack())
        )
    except:
        import traceback
        traceback.print_exc()


@router.callback_query(F.data == "enter_new_included_bump_item_keyphrases")
async def callback_enter_new_included_bump_item_keyphrases(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    
    await state.set_state(states.BumpItemsStates.waiting_for_new_included_bump_item_keyphrases)
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.settings_new_bump_included_float_text(
            f"🔑 Введите <b>ключевые фразы</b> названия товара, который нужно включить в авто-поднятие "
            f"(указываются через запятую, например, \"samp аккаунт, со всеми данными\"):"
        ),
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
        text=templ.settings_new_bump_excluded_float_text(
            f"🔑 Введите <b>ключевые фразы</b> названия товара, который нужно исключить из авто-поднятия "
            f"(указываются через запятую, например, \"samp аккаунт, со всеми данными\"):"
        ),
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
        text=templ.settings_comms_float_text(f"📃 Введите номер страницы для перехода:"),
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
        text=templ.settings_new_comm_float_text(f"⌨️ Введите <b>новую команду</b> (например, <code>!тест</code>):"),
        reply_markup=templ.back_kb(calls.CustomCommandsPagination(page=last_page).pack())
    )


@router.callback_query(F.data == "enter_custom_command_answer")
async def callback_enter_custom_command_answer(callback: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(None)

        data = await state.get_data()
        last_page = data.get("last_page", 0)
        
        command = data.get("custom_command")
        if not command:
            return await callback_custom_commands_pagination(
                callback,
                calls.CustomCommandsPagination(page=last_page),
                state
            )
        
        await state.set_state(states.CustomCommandsStates.waiting_for_custom_command_answer)
        custom_commands = sett.get("custom_commands")
        custom_command_answer = "\n".join(custom_commands[command]) or "❌ Не задано"
        
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.settings_comm_page_float_text(
                f"💬 Введите новый <b>текст ответа</b> команды <code>{command}</code>:"
                f"\n・ Текущее: <blockquote>{custom_command_answer}</blockquote>"
            ),
            reply_markup=templ.back_kb(calls.CustomCommandPage(command=command).pack())
        )
    except Exception as e:
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
        text=templ.settings_delivs_float_text(f"📃 Введите номер страницы для перехода:"),
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
        text=templ.settings_new_deliv_float_text(
            f"🔑 Введите <b>ключевые фразы</b> названия товара, на который нужно добавить авто-выдачу "
            f"(указываются через запятую, например, \"telegram подписчики, авто-выдача\"):"
        ),
        reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
    )


@router.callback_query(F.data == "enter_auto_delivery_keyphrases")
async def callback_enter_auto_delivery_keyphrases(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        
        index = data.get("auto_delivery_index")
        if index is None:
            return await callback_auto_deliveries_pagination(
                callback,
                calls.AutoDeliveriesPagination(page=last_page),
                state
            )
        
        await state.set_state(states.AutoDeliveriesStates.waiting_for_auto_delivery_keyphrases)
        auto_deliveries = sett.get("auto_deliveries")
        auto_delivery_message = "</code>, <code>".join(auto_deliveries[index]["keyphrases"]) or "❌ Не задано"
        
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.settings_deliv_page_float_text(
                f"🔑 Введите новые <b>ключевые фразы</b> названия товара, на который авто-выдачи (указываются через запятую)"
                f"\n・ Текущее: <code>{auto_delivery_message}</code>"
            ),
            reply_markup=templ.back_kb(calls.AutoDeliveryPage(index=index).pack())
        )
    except Exception as e:
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
        last_page = data.get("last_page", 0)
        
        index = data.get("auto_delivery_index")
        if index is None:
            return await callback_auto_deliveries_pagination(
                callback,
                calls.AutoDeliveriesPagination(page=last_page),
                state
            )
        
        await state.set_state(states.AutoDeliveriesStates.waiting_for_auto_delivery_message)
        auto_deliveries = sett.get("auto_deliveries")
        auto_delivery_message = "\n".join(auto_deliveries[index]["message"]) or "❌ Не задано"
        
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.settings_deliv_page_float_text(
                f"💬 Введите новое <b>сообщение</b> после покупки"
                f"\n・ Текущее: <blockquote>{auto_delivery_message}</blockquote>"
            ),
            reply_markup=templ.back_kb(calls.AutoDeliveryPage(index=index).pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.settings_deliv_page_float_text(e),
            reply_markup=templ.back_kb(calls.AutoDeliveriesPagination(page=last_page).pack())
        )


@router.callback_query(F.data == "enter_auto_delivery_goods_add")
async def callback_enter_auto_delivery_goods_add(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        
        index = data.get("auto_delivery_index")
        if index is None:
            return await callback_auto_deliveries_pagination(
                callback,
                calls.AutoDeliveriesPagination(page=last_page),
                state
            )
        
        await state.set_state(states.AutoDeliveriesStates.waiting_for_auto_delivery_goods_add)
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.settings_new_deliv_goods_float_text(
                f"📦 Отправьте <b>товары</b> для добавления в поштучную выдачу (1 строка = 1 товар, можно прислать .txt файл с товарами):"
            ),
            reply_markup=templ.back_kb(calls.DelivGoodsPagination(page=last_page).pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.settings_new_deliv_goods_float_text(e),
            reply_markup=templ.back_kb(calls.DelivGoodsPagination(page=last_page).pack())
        )


@router.callback_query(F.data == "enter_auto_withdrawal_interval")
async def callback_enter_auto_withdrawal_interval(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)

    config = sett.get("config")
    interval = config["playerok"]["auto_withdrawal"]["interval"]

    await state.set_state(states.SettingsStates.waiting_for_auto_withdrawal_interval)
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.settings_withdrawal_float_text(
            f"⏱️ Введите новый <b>интервал вывода средств</b> (в секундах):"
            f"\n・ Текущее: <code>{interval}</code> сек."
        ),
        reply_markup=templ.back_kb(calls.SettingsNavigation(to="withdrawal").pack())
    )


@router.callback_query(F.data == "enter_usdt_address")
async def callback_enter_usdt_address(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)

    await state.set_state(states.SettingsStates.waiting_for_usdt_address)
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.settings_withdrawal_usdt_float_text(
            f"💲 Введите <b>адрес кошелька</b> USDT (TRC20):"
        ),
        reply_markup=templ.back_kb(calls.SettingsNavigation(to="withdrawal").pack())
    )


@router.callback_query(F.data == "enter_messages_page")
async def callback_enter_messages_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    
    await state.set_state(states.MessagesStates.waiting_for_page)
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.settings_mess_float_text(f"📃 Введите номер страницы для перехода:"),
        reply_markup=templ.back_kb(calls.MessagesPagination(page=last_page).pack())
    )


@router.callback_query(F.data == "enter_message_text")
async def callback_enter_message_text(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        
        message_id = data.get("message_id")
        if not message_id:
            return await callback_messages_pagination(
                callback,
                calls.MessagesPagination(page=last_page),
                state
            )
        
        await state.set_state(states.MessagesStates.waiting_for_message_text)
        messages = sett.get("messages")
        mess_text = "\n".join(messages[message_id]["text"]) or "❌ Не задано"
        
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.settings_mess_float_text(
                f"💬 Введите новый <b>текст сообщения</b> <code>{message_id}</code>:"
                f"\n・ Текущее: <blockquote>{mess_text}</blockquote>"
            ),
            reply_markup=templ.back_kb(calls.MessagesPagination(page=last_page).pack())
        )
    except Exception as e:
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
        text=templ.settings_logger_float_text(
            f"💬 Введите новый <b>ID чата для логов</b> (вы можете указать как цифровой ID, так и юзернейм чата):"
            f"\n・ Текущее: <code>{tg_logging_chat_id}</code>"
        ),
        reply_markup=templ.back_kb(calls.SettingsNavigation(to="logger").pack())
    )


@router.callback_query(F.data == "enter_logs_max_file_size")
async def callback_enter_logs_max_file_size(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.waiting_for_logs_max_file_size)
    
    config = sett.get("config")
    max_file_size = config["logs"]["max_file_size"] or "❌ Не указано"
    
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.logs_float_text(
            f"📄 Введите новый <b>максимальный размер файла логов</b> (в мегабайтах):"
            f"\n・ Текущее: <b>{max_file_size} MB</b>"
        ),
        reply_markup=templ.back_kb(calls.MenuNavigation(to="logs").pack())
    )