from aiogram import types, Router, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import tgbot.templates.user_templates as Templates
from tgbot.states.states import *

from settings import Config, Messages, CustomCommands, AutoDeliveries


router = Router()


# /---- Команды ----\

@router.message(Command('start'))
async def handler_start(message: types.Message, state: FSMContext):
    """ Отрабатывает команду /start """
    try:
        await state.set_state(None)
        config = Config.get()
        if message.from_user.id != config["tg_admin_id"]:
            return
        await message.answer(text=Templates.Navigation.MenuNavigation.Default.text(),
                             reply_markup=Templates.Navigation.MenuNavigation.Default.kb(),
                             parse_mode="HTML")
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.message(Command('stats'))
async def handler_stats(message: types.Message, state: FSMContext):
    """ Отрабатывает команду /stats """
    try:
        await state.set_state(None)
        config = Config.get()
        if message.from_user.id != config["tg_admin_id"]:
            return
        await message.answer(text=Templates.Navigation.MenuNavigation.Stats.Default.text(),
                                reply_markup=Templates.Navigation.MenuNavigation.Stats.Default.kb(),
                                parse_mode="HTML")
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.message(Command('settings'))
async def handler_stats(message: types.Message, state: FSMContext):
    """ Отрабатывает команду /settings """
    try:
        await state.set_state(None)
        config = Config.get()
        if message.from_user.id != config["tg_admin_id"]:
            return
        await message.answer(text=Templates.Navigation.SettingsNavigation.Default.text(), 
                                reply_markup=Templates.Navigation.SettingsNavigation.Default.kb(),
                                parse_mode="HTML")
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

# /---- Настройки бота ----\

@router.message(MessagesNavigationStates.entering_messages_page)
async def handler_entering_messages_page(message: types.Message, state: FSMContext):
    """ Считывает введёный пользователем номер страницы сообщений и переходит на неё """
    try: 
        await state.set_state(None)
        def is_int(txt) -> bool:
            try:
                int(txt)
                return True
            except ValueError:
                return False

        if not is_int(message.text):
            return await message.answer(text=Templates.System.Error.text("Вы должны ввести числовое значение"), parse_mode="HTML")
        
        await message.answer(
            text=Templates.Navigation.Settings.Messages.Pagination.text(),
            reply_markup=Templates.Navigation.Settings.Messages.Pagination.kb(page=int(message.text)-1),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")
        
@router.message(MessagePageNavigationStates.entering_message_text)
async def handler_entering_message_text(message: types.Message, state: FSMContext):
    """ Считывает введённый пользователем новый текст сообщения и изменяет его в сообщениях """ 
    try:
        await state.set_state(None)
        await state.set_state(None)
        if len(message.text.strip()) <= 0:
            return await message.answer(text=Templates.System.Error.text("Слишком короткий текст"), parse_mode="HTML")

        data = await state.get_data()
        messages = Messages.get()
        messages[data["message_id"]] = []
        message_split_lines = message.text.strip().split('\n')
        for line in message_split_lines:
            messages[data["message_id"]].append(line)
        Messages.set(messages)
        await message.answer(
            text=Templates.Navigation.Settings.Messages.MessageTextChanged.text(message.text.strip(), data["message_id"]),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.message(BotSettingsNavigationStates.entering_token)
async def handler_entering_token(message: types.Message, state: FSMContext):
    """ Считывает введённый пользователем token и изменяет его в конфиге """ 
    try:
        await state.set_state(None)
        if len(message.text.strip()) <= 3 or len(message.text.strip()) >= 500:
            return await message.answer(text=Templates.System.Error.text("Слишком короткий или длинный токен"), parse_mode="HTML")

        config = Config.get()
        config["token"] = message.text.strip()
        Config.set(config)
        await message.answer(
            text=Templates.Navigation.Settings.Authorization.TokenChanged.text(message.text.strip()),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.message(BotSettingsNavigationStates.entering_user_agent)
async def handler_entering_user_agent(message: types.Message, state: FSMContext):
    """ Считывает введённый пользователем user_agent и изменяет его в конфиге """ 
    try:
        await state.set_state(None)
        if len(message.text.strip()) <= 3:
            return await message.answer(text=Templates.System.Error.text("Слишком короткий user_agent"), parse_mode="HTML")

        config = Config.get()
        config["user_agent"] = message.text.strip()
        Config.set(config)
        await message.answer(
            text=Templates.Navigation.Settings.Authorization.UserAgentChanged.text(message.text.strip()),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.message(BotSettingsNavigationStates.entering_playerokapi_requests_timeout)
async def handler_entering_playerokapi_requests_timeout(message: types.Message, state: FSMContext):
    """ Считывает введённый пользователем playerokapi_requests_timeout и изменяет его в конфиге """ 
    try:
        await state.set_state(None)
        def is_int(txt) -> bool:
            try:
                int(txt)
                return True
            except ValueError:
                return False

        if not is_int(message.text.strip()):
            return await message.answer(text=Templates.System.Error.text("Вы должны ввести числовое значение"), parse_mode="HTML")
        
        if int(message.text.strip()) < 0:
            return await message.answer(text=Templates.System.Error.text("Слишком низкое значение"), parse_mode="HTML")

        config = Config.get()
        config["playerokapi_requests_timeout"] = int(message.text.strip())
        Config.set(config)
        await message.answer(
            text=Templates.Navigation.Settings.Connection.PlayerokApiRequestsTimeoutChanged.text(message.text.strip()),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.message(BotSettingsNavigationStates.entering_playerokapi_listener_requests_delay)
async def handler_entering_playerokapi_listener_requests_delay(message: types.Message, state: FSMContext):
    """ Считывает введённый пользователем playerokapi_listener_requests_delay и изменяет его в конфиге """ 
    try:
        await state.set_state(None)
        def is_int(txt) -> bool:
            try:
                int(txt)
                return True
            except ValueError:
                return False

        if not is_int(message.text.strip()):
            return await message.answer(text=Templates.System.Error.text("Вы должны ввести числовое значение"), parse_mode="HTML")
        
        if int(message.text.strip()) < 0:
            return await message.answer(text=Templates.System.Error.text("Слишком низкое значение"), parse_mode="HTML")

        config = Config.get()
        config["playerokapi_listener_requests_delay"] = int(message.text.strip())
        Config.set(config)
        await message.answer(
            text=Templates.Navigation.Settings.Connection.PlayerokApiListenerRequestsDelayChanged.text(message.text.strip()),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.message(BotSettingsNavigationStates.entering_bot_event_notifications_chat_id)
async def handler_entering_bot_event_notifications_chat_id(message: types.Message, state: FSMContext):
    """ Считывает введённый пользователем bot_event_notifications_chat_id и изменяет его в конфиге """ 
    try:
        await state.set_state(None)
        def is_int(txt) -> bool:
            try:
                int(txt)
                return True
            except ValueError:
                return False
        
        if is_int(message.text.strip()) and int(message.text.strip()) < 0:
            return await message.answer(text=Templates.System.Error.text("Слишком низкое значение"), parse_mode="HTML")
        
        elif len(message.text.strip()) <= 0:
            return await message.answer(text=Templates.System.Error.text("Слишком короткое значение"), parse_mode="HTML")

        config = Config.get()
        config["bot_event_notifications_chat_id"] = message.text.strip()
        Config.set(config)
        await message.answer(
            text=Templates.Navigation.Settings.Notifications.ChatIdChanged.text(message.text.strip()),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.message(CustomCommandsNavigationStates.entering_custom_commands_page)
async def handler_entering_custom_commands_page(message: types.Message, state: FSMContext):
    """ Считывает введёный пользователем номер страницы пользовательских комманд и переходит на неё """
    try: 
        await state.set_state(None)
        def is_int(txt) -> bool:
            try:
                int(txt)
                return True
            except ValueError:
                return False

        if not is_int(message.text):
            return await message.answer(text=Templates.System.Error.text("Вы должны ввести числовое значение"), parse_mode="HTML")
        
        await message.answer(
            text=Templates.Navigation.Settings.CustomCommands.Pagination.text(),
            reply_markup=Templates.Navigation.Settings.CustomCommands.Pagination.kb(page=int(message.text)-1),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")
        
@router.message(CustomCommandPageNavigationStates.entering_custom_command)
async def handler_entering_custom_command(message: types.Message, state: FSMContext):
    """ Считывает введённую пользователем пользовательскую команду и запоминает """ 
    try:
        await state.set_state(None)
        if len(message.text.strip()) <= 0 or len(message.text.strip()) >= 32:
            return await message.answer(text=Templates.System.Error.text("Слишком короткая или длинная команда"), parse_mode="HTML")

        await state.update_data(new_custom_command=message.text.strip())
        await state.set_state(CustomCommandPageNavigationStates.entering_custom_command_answer)
        await message.answer(
            text=Templates.Navigation.Settings.CustomCommands.EnterCustomCommandAnswer.text(),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")
        
@router.message(CustomCommandPageNavigationStates.entering_custom_command_answer)
async def handler_entering_custom_command_answer(message: types.Message, state: FSMContext):
    """ Считывает введённый пользователем ответ на пользовательскую команду и запоминает """ 
    try:
        if len(message.text.strip()) <= 0:
            return await message.answer(text=Templates.System.Error.text("Слишком короткий ответ"), parse_mode="HTML")

        await state.update_data(new_custom_command_answer=message.text.strip())
        data = await state.get_data()
        await message.answer(
            text=Templates.Navigation.Settings.CustomCommands.ConfirmAddingCustomCommand.text(data["new_custom_command"], data["new_custom_command_answer"]),
            reply_markup=Templates.Navigation.Settings.CustomCommands.ConfirmAddingCustomCommand.kb(),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.message(CustomCommandPageNavigationStates.entering_new_custom_command_answer)
async def handler_entering_new_custom_command_answer(message: types.Message, state: FSMContext):
    """ Считывает введённый пользователем новый текст ответа на пользовательскую команду и изменяет его в конфиге """ 
    try:
        await state.set_state(None)
        data = await state.get_data()
        if len(message.text.strip()) <= 0:
            return await message.answer(text=Templates.System.Error.text("Слишком короткий текст"), parse_mode="HTML")

        custom_commands = CustomCommands.get()
        custom_commands[data["custom_command"]] = []
        answer_split_lines = message.text.strip().split('\n')
        for line in answer_split_lines:
            custom_commands[data["custom_command"]].append(line)
        CustomCommands.set(custom_commands)
        await message.answer(
            text=Templates.Navigation.Settings.CustomCommands.CustomCommandAnswerChanged.text(message.text.strip(), data["custom_command"]),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")


@router.message(AutoDeliveriesNavigationStates.entering_custom_commands_page)
async def handler_entering_custom_commands_page(message: types.Message, state: FSMContext):
    """ Считывает введёный пользователем номер страницы авто-выдач и переходит на неё """
    try: 
        await state.set_state(None)
        def is_int(txt) -> bool:
            try:
                int(txt)
                return True
            except ValueError:
                return False

        if not is_int(message.text):
            return await message.answer(text=Templates.System.Error.text("Вы должны ввести числовое значение"), parse_mode="HTML")
        
        await message.answer(
            text=Templates.Navigation.Settings.AutoDeliveries.Pagination.text(),
            reply_markup=Templates.Navigation.Settings.AutoDeliveries.Pagination.kb(page=int(message.text)-1),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")
        
@router.message(AutoDeliveryPageNavigationStates.entering_auto_delivery_keywords)
async def handler_entering_entering_auto_delivery_keywords(message: types.Message, state: FSMContext):
    """ Считывает введённые пользователем ключевые слова названия предмета автовыдачи и запоминает """ 
    try:
        await state.set_state(None)
        if len(message.text.strip()) <= 0:
            return await message.answer(text=Templates.System.Error.text("Некорректные ключевые слова"), parse_mode="HTML")
        
        keywords_split = message.text.strip().split(",")
        keywords = []
        for split in keywords_split:
            keywords.append(split.strip())

        await state.update_data(auto_delivery_keywords=keywords)
        await state.set_state(AutoDeliveryPageNavigationStates.entering_auto_delivery_message)
        await message.answer(
            text=Templates.Navigation.Settings.AutoDeliveries.EnterAutoDeliveryMessage.text(),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")
        
@router.message(AutoDeliveryPageNavigationStates.entering_auto_delivery_message)
async def handler_entering_auto_delivery_message(message: types.Message, state: FSMContext):
    """ Считывает введённое пользователем сообщение после покупки на автовыдачу и запоминает """ 
    try:
        if len(message.text.strip()) <= 0:
            return await message.answer(text=Templates.System.Error.text("Слишком короткий ответ"), parse_mode="HTML")

        await state.update_data(auto_delivery_message=message.text.strip())
        data = await state.get_data()
        await message.answer(
            text=Templates.Navigation.Settings.AutoDeliveries.ConfirmAddingAutoDelivery.text(data["auto_delivery_keywords"], data["auto_delivery_message"]),
            reply_markup=Templates.Navigation.Settings.AutoDeliveries.ConfirmAddingAutoDelivery.kb(),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.message(AutoDeliveryPageNavigationStates.entering_new_auto_delivery_keywords)
async def handler_entering_new_auto_delivery_keywords(message: types.Message, state: FSMContext):
    """ Считывает введённые пользователем новые ключевые слова названия предмета авто-выдачи и изменяет его в конфиге """ 
    try:
        await state.set_state(None)
        data = await state.get_data()
        if len(message.text.strip()) <= 0:
            return await message.answer(text=Templates.System.Error.text("Некорректные ключевые слова"), parse_mode="HTML")

        keywords_split = message.text.strip().split(",")
        keywords = []
        for split in keywords_split:
            keywords.append(split.strip())

        auto_deliveries = AutoDeliveries.get()
        auto_deliveries[data["auto_delivery_index"]]["keywords"] = keywords
        AutoDeliveries.set(auto_deliveries)

        await message.answer(
            text=Templates.Navigation.Settings.AutoDeliveries.AutoDeliveryKeywordsChanged.text(", ".join(keywords)),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.message(AutoDeliveryPageNavigationStates.entering_new_auto_delivery_message)
async def handler_entering_new_auto_delivery_message(message: types.Message, state: FSMContext):
    """ Считывает введённое пользователем новое сообщение после покупки на авто-выдачу и изменяет его в конфиге """ 
    try:
        await state.set_state(None)
        data = await state.get_data()
        if len(message.text.strip()) <= 0:
            return await message.answer(text=Templates.System.Error.text("Некорректное сообщение"), parse_mode="HTML")

        auto_deliveries = AutoDeliveries.get()
        auto_deliveries[data["auto_delivery_index"]]["message"] = message.text.strip().split("\n")
        AutoDeliveries.set(auto_deliveries)
        await message.answer(
            text=Templates.Navigation.Settings.AutoDeliveries.AutoDeliveryMessageChanged.text(message.text.strip()),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.message(BotSettingsNavigationStates.entering_messages_watermark)
async def handler_entering_messages_watermark(message: types.Message, state: FSMContext):
    """ Считывает введённый пользователем водяной знак и изменяет его в конфиге """ 
    try:
        await state.set_state(None)
        data = await state.get_data()
        if len(message.text.strip()) <= 0 or len(message.text.strip()) >= 150:
            return await message.answer(text=Templates.System.Error.text("Слишком короткий или длинный знак"), parse_mode="HTML")

        config = Config.get()
        config["messages_watermark"] = message.text.strip()
        Config.set(config)
        await message.answer(
            text=Templates.Navigation.Settings.Other.MessagesWatermarkChanged.text(message.text.strip()),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")