from aiogram import F, Router, types
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters.callback_data import CallbackData
import traceback
import math

import playerokapi.types as plapi_types

import tgbot.templates.user_templates as Templates
import tgbot.callback_datas.user_callback_datas as CallbackDatas
from tgbot.states.states import *

from plbot import get_playerok_bot

from settings import Config, CustomCommands, AutoDeliveries
from core.modules_manager import ModulesManager
import time

router = Router()

@router.callback_query(F.data == "destroy")
async def callback_back(call: CallbackQuery, state: FSMContext):
    """ Отработка удаления сообщения """
    try:
        await call.message.delete()
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e),
                                  parse_mode="HTML")

@router.callback_query(CallbackDatas.MenuNavigation.filter())
async def callback_menu_navigation(callback: CallbackQuery, callback_data: CallbackDatas.MenuNavigation):
    """ Навигация в главном меню """
    to = callback_data.to
    try:
        if to == "default":
            await callback.message.edit_text(text=Templates.Navigation.MenuNavigation.Default.text(),
                                             reply_markup=Templates.Navigation.MenuNavigation.Default.kb(),
                                             parse_mode="HTML")
        elif to == "settings":
            await callback.message.edit_text(text=Templates.Navigation.SettingsNavigation.Default.text(),
                                             reply_markup=Templates.Navigation.SettingsNavigation.Default.kb(),
                                             parse_mode="HTML")
        elif to == "stats":
            try:
                await callback.message.edit_text(text=Templates.Navigation.MenuNavigation.Stats.Loading.text(),
                                                 reply_markup=Templates.Navigation.MenuNavigation.Stats.Default.kb(),
                                                 parse_mode="HTML")
                await callback.message.edit_text(text=Templates.Navigation.MenuNavigation.Stats.Default.text(),
                                                 reply_markup=Templates.Navigation.MenuNavigation.Stats.Default.kb(),
                                                 parse_mode="HTML")
            except Exception as e:
                await callback.message.edit_text(text=Templates.Navigation.MenuNavigation.Stats.Error.text(),
                                                 reply_markup=Templates.Navigation.MenuNavigation.Stats.Default.kb(),
                                                 parse_mode="HTML")
        elif to == "profile":
            try:
                await callback.message.edit_text(text=Templates.Navigation.MenuNavigation.Profile.Loading.text(),
                                                 reply_markup=Templates.Navigation.MenuNavigation.Profile.Default.kb(),
                                                 parse_mode="HTML")
                await callback.message.edit_text(text=Templates.Navigation.MenuNavigation.Profile.Default.text(),
                                                 reply_markup=Templates.Navigation.MenuNavigation.Profile.Default.kb(),
                                                 parse_mode="HTML")
            except Exception as e:
                await callback.message.edit_text(text=Templates.Navigation.MenuNavigation.Profile.Error.text(),
                                                 reply_markup=Templates.Navigation.MenuNavigation.Profile.Default.kb(),
                                                 parse_mode="HTML")
                raise e
        elif to == "instruction":
            await callback.message.edit_text(text=Templates.Navigation.InstructionNavigation.Default.text(),
                                             reply_markup=Templates.Navigation.InstructionNavigation.Default.kb(),
                                             parse_mode="HTML")
    except Exception as e:
        await callback.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(CallbackDatas.InstructionNavigation.filter())
async def callback_instruction_navgiation(callback: CallbackQuery, callback_data: CallbackDatas.InstructionNavigation, state: FSMContext):
    """ Навигация в инструкции """
    to = callback_data.to
    try:
        if to == "default":
            await callback.message.edit_text(text=Templates.Navigation.InstructionNavigation.Default.text(),
                                             reply_markup=Templates.Navigation.InstructionNavigation.Default.kb(),
                                             parse_mode="HTML")
        if to == "commands":
            await callback.message.edit_text(text=Templates.Navigation.InstructionNavigation.Commands.text(),
                                             reply_markup=Templates.Navigation.InstructionNavigation.Commands.kb(),
                                             parse_mode="HTML")
    except Exception as e:
        await callback.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(CallbackDatas.SettingsNavigation.filter())
async def callback_settings_navigation(callback: CallbackQuery, callback_data: CallbackDatas.SettingsNavigation, state: FSMContext):
    """ Навигация в настройках """
    to = callback_data.to
    try:
        if to == "default":
            try:
                await callback.message.edit_text(text=Templates.Navigation.Settings.Default.Loading.text(),
                                                 reply_markup=Templates.Navigation.Settings.Default.Default.kb(),
                                                 parse_mode="HTML")
                await callback.message.edit_text(text=Templates.Navigation.Settings.Default.Default.text(),
                                                 reply_markup=Templates.Navigation.Settings.Default.Default.kb(),
                                                 parse_mode="HTML")
            except Exception as e:
                await callback.message.edit_text(text=Templates.Navigation.Settings.Default.Error.text(),
                                                 reply_markup=Templates.Navigation.Settings.Default.Default.kb(),
                                                 parse_mode="HTML")
                raise e
    except Exception as e:
        await callback.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(CallbackDatas.BotSettingsNavigation.filter())
async def callback_botsettings_navigation(callback: CallbackQuery, callback_data: CallbackDatas.BotSettingsNavigation):
    """ Навигация в настройках бота """
    to = callback_data.to
    try:
        
        if to == "default":
            try:
                await callback.message.edit_text(text=Templates.Navigation.Settings.Default.Loading.text(),
                                                reply_markup=Templates.Navigation.Settings.Default.Default.kb(),
                                                parse_mode="HTML")
                await callback.message.edit_text(text=Templates.Navigation.Settings.Default.Default.text(),
                                                reply_markup=Templates.Navigation.Settings.Default.Default.kb(),
                                                parse_mode="HTML")
            except Exception as e:
                await callback.message.edit_text(text=Templates.Navigation.Settings.Default.Error.text(),
                                                reply_markup=Templates.Navigation.Settings.Default.Default.kb(),
                                                parse_mode="HTML")
                raise e
        if to == "connection":
            try:
                await callback.message.edit_text(text=Templates.Navigation.Settings.Connection.Loading.text(),
                                                reply_markup=Templates.Navigation.Settings.Connection.Default.kb(),
                                                parse_mode="HTML")
                await callback.message.edit_text(text=Templates.Navigation.Settings.Connection.Default.text(),
                                                reply_markup=Templates.Navigation.Settings.Connection.Default.kb(),
                                                parse_mode="HTML")
            except Exception as e:
                await callback.message.edit_text(text=Templates.Navigation.Settings.Connection.Error.text(),
                                                reply_markup=Templates.Navigation.Settings.Connection.Default.kb(),
                                                parse_mode="HTML")
                raise e
        if to == "authorization":
            try:
                await callback.message.edit_text(text=Templates.Navigation.Settings.Authorization.Loading.text(),
                                                reply_markup=Templates.Navigation.Settings.Authorization.Default.kb(),
                                                parse_mode="HTML")
                await callback.message.edit_text(text=Templates.Navigation.Settings.Authorization.Default.text(),
                                                reply_markup=Templates.Navigation.Settings.Authorization.Default.kb(),
                                                parse_mode="HTML")
            except Exception as e:
                await callback.message.edit_text(text=Templates.Navigation.Settings.Authorization.Error.text(),
                                                reply_markup=Templates.Navigation.Settings.Authorization.Default.kb(),
                                                parse_mode="HTML")
                raise e
        if to == "items":
            try:
                await callback.message.edit_text(text=Templates.Navigation.Settings.Items.Loading.text(),
                                                    reply_markup=Templates.Navigation.Settings.Items.Default.kb(),
                                                    parse_mode="HTML")
                await callback.message.edit_text(text=Templates.Navigation.Settings.Items.Default.text(),
                                                    reply_markup=Templates.Navigation.Settings.Items.Default.kb(),
                                                    parse_mode="HTML")
            except Exception as e:
                await callback.message.edit_text(text=Templates.Navigation.Settings.Items.Error.text(),
                                                reply_markup=Templates.Navigation.Settings.Items.Default.kb(),
                                                parse_mode="HTML")
                raise e
        if to == "other":
            try:
                await callback.message.edit_text(text=Templates.Navigation.Settings.Other.Loading.text(),
                                                reply_markup=Templates.Navigation.Settings.Other.Default.kb(),
                                                parse_mode="HTML")
                await callback.message.edit_text(text=Templates.Navigation.Settings.Other.Default.text(),
                                                reply_markup=Templates.Navigation.Settings.Other.Default.kb(),
                                                parse_mode="HTML")
            except Exception as e:
                await callback.message.edit_text(text=Templates.Navigation.Settings.Other.Error.text(),
                                                reply_markup=Templates.Navigation.Settings.Other.Default.kb(),
                                                parse_mode="HTML")
                raise e
    except Exception as e:
        await callback.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "enter_token")
async def callback_enter_token(call: CallbackQuery, state: FSMContext):
    """ Отрабатывает ввод нового token """
    try:
        await state.set_state(BotSettingsNavigationStates.entering_token)
        await call.message.answer(text=Templates.Navigation.Settings.Authorization.EnterToken.text(),
                                  parse_mode="HTML")
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "enter_user_agent")
async def callback_enter_user_agent(call: CallbackQuery, state: FSMContext):
    """ Отрабатывает ввод нового golden_key """
    try:
        await state.set_state(BotSettingsNavigationStates.entering_user_agent)
        await call.message.answer(text=Templates.Navigation.Settings.Authorization.EnterUserAgent.text(),
                                  parse_mode="HTML")
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "enter_playerokapi_requests_timeout")
async def callback_enter_playerokapi_requests_timeout(call: CallbackQuery, state: FSMContext):
    """ Отрабатывает ввод нового playerokapi_requests_timeout """
    try:
        await state.set_state(BotSettingsNavigationStates.entering_playerokapi_requests_timeout)
        await call.message.answer(text=Templates.Navigation.Settings.Connection.EnterPlayerokApiRequestsTimeout.text(),
                                  parse_mode="HTML")
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "enter_playerokapi_listener_requests_delay")
async def callback_enter_playerokapi_listener_requests_delay(call: CallbackQuery, state: FSMContext):
    """ Отрабатывает ввод нового enter_playerokapi_listener_requests_delay """
    try:
        await state.set_state(BotSettingsNavigationStates.entering_playerokapi_listener_requests_delay)
        await call.message.answer(text=Templates.Navigation.Settings.Connection.EnterPlayerokApiListenerRequestsDelay.text(),
                                  parse_mode="HTML")
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "enable_auto_restore_items")
async def callback_enable_auto_restore_items(call: CallbackQuery):
    """ Включает автоматическое восстановление предметов """
    try:
        config = Config.get()
        config["auto_restore_items_enabled"] = True
        Config.set(config)
        callback_data = CallbackDatas.BotSettingsNavigation(to="items")
        return await callback_botsettings_navigation(call, callback_data)
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "disable_auto_restore_items")
async def callback_disable_auto_restore_items(call: CallbackQuery):
    """ Выключает автоматическое поднятие лотов """
    try:
        config = Config.get()
        config["auto_restore_items_enabled"] = False
        Config.set(config)
        callback_data = CallbackDatas.BotSettingsNavigation(to="items")
        return await callback_botsettings_navigation(call, callback_data)
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "premium_auto_restore_items_priority_status")
async def callback_premium_auto_restore_items_priority_status(call: CallbackQuery):
    """ Переключает статус приоритета для поднятых предметов на RPEMIUM """
    try:
        config = Config.get()
        config["auto_restore_items_priority_status"] = "PREMIUM"
        Config.set(config)
        callback_data = CallbackDatas.BotSettingsNavigation(to="items")
        return await callback_botsettings_navigation(call, callback_data)
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "default_auto_restore_items_priority_status")
async def callback_default_auto_restore_items_priority_status(call: CallbackQuery):
    """ Переключает статус приоритета для поднятых предметов на DEFAULT """
    try:
        config = Config.get()
        config["auto_restore_items_priority_status"] = "DEFAULT"
        Config.set(config)
        callback_data = CallbackDatas.BotSettingsNavigation(to="items")
        return await callback_botsettings_navigation(call, callback_data)
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "disable_read_chat_before_sending_message")
async def callback_disable_read_chat_before_sending_message(call: CallbackQuery):
    """ Выключает чтение чата перед отправкой сообщения """
    try:
        config = Config.get()
        config["read_chat_before_sending_message_enabled"] = False
        Config.set(config)
        callback_data = CallbackDatas.BotSettingsNavigation(to="other")
        return await callback_botsettings_navigation(call, callback_data)
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "enable_read_chat_before_sending_message")
async def callback_enable_read_chat_before_sending_message(call: CallbackQuery):
    """ Включает чтение чата перед отправкой сообщения """
    try:
        config = Config.get()
        config["read_chat_before_sending_message_enabled"] = True
        Config.set(config)
        callback_data = CallbackDatas.BotSettingsNavigation(to="other")
        return await callback_botsettings_navigation(call, callback_data)
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "disable_auto_complete_deals")
async def callback_disable_auto_complete_deals(call: CallbackQuery):
    """ Выключает автоподтверждение выполнения заказа """
    try:
        config = Config.get()
        config["auto_complete_deals_enabled"] = False
        Config.set(config)
        callback_data = CallbackDatas.BotSettingsNavigation(to="other")
        return await callback_botsettings_navigation(call, callback_data)
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "enable_auto_complete_deals")
async def callback_enable_auto_complete_deals(call: CallbackQuery):
    """ Включает автоподтверждение выполнения заказа """
    try:
        config = Config.get()
        config["auto_complete_deals_enabled"] = True
        Config.set(config)
        callback_data = CallbackDatas.BotSettingsNavigation(to="other")
        return await callback_botsettings_navigation(call, callback_data)
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "disable_first_message")
async def callback_disable_first_message(call: CallbackQuery):
    """ Выключает приветственное сообщение """
    try:
        config = Config.get()
        config["first_message_enabled"] = False
        Config.set(config)
        callback_data = CallbackDatas.BotSettingsNavigation(to="other")
        return await callback_botsettings_navigation(call, callback_data)
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "enable_first_message")
async def callback_enable_first_message(call: CallbackQuery):
    """ Включает приветственное сообщение """
    try:
        config = Config.get()
        config["first_message_enabled"] = True
        Config.set(config)
        callback_data = CallbackDatas.BotSettingsNavigation(to="other")
        return await callback_botsettings_navigation(call, callback_data)
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "disable_custom_commands")
async def callback_disable_custom_commands(call: CallbackQuery):
    """ Выключает пользовательские ответы """
    try:
        config = Config.get()
        config["custom_commands_enabled"] = False
        Config.set(config)
        callback_data = CallbackDatas.BotSettingsNavigation(to="other")
        return await callback_botsettings_navigation(call, callback_data)
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "enable_custom_commands")
async def callback_enable_custom_commands(call: CallbackQuery):
    """ Включает пользовательские ответы """
    try:
        config = Config.get()
        config["custom_commands_enabled"] = True
        Config.set(config)
        callback_data = CallbackDatas.BotSettingsNavigation(to="other")
        return await callback_botsettings_navigation(call, callback_data)
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "disable_auto_delivery")
async def callback_disable_auto_delivery(call: CallbackQuery):
    """ Выключает авто-выдачу """
    try:
        config = Config.get()
        config["auto_deliveries_enabled"] = False
        Config.set(config)
        callback_data = CallbackDatas.BotSettingsNavigation(to="other")
        return await callback_botsettings_navigation(call, callback_data)
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "enable_auto_delivery")
async def callback_enable_auto_delivery(call: CallbackQuery):
    """ Включает авто-выдачу """
    try:
        config = Config.get()
        config["auto_deliveries_enabled"] = True
        Config.set(config)
        callback_data = CallbackDatas.BotSettingsNavigation(to="other")
        return await callback_botsettings_navigation(call, callback_data)
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "disable_messages_watermark")
async def callback_disable_messages_watermark(call: CallbackQuery):
    """ Выключает водяныой знак под сообщениями """
    try:
        config = Config.get()
        config["messages_watermark_enabled"] = False
        Config.set(config)
        callback_data = CallbackDatas.BotSettingsNavigation(to="other")
        return await callback_botsettings_navigation(call, callback_data)
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "enable_messages_watermark")
async def callback_enable_messages_watermark(call: CallbackQuery):
    """ Включает водяной знак под сообщениями """
    try:
        config = Config.get()
        config["messages_watermark_enabled"] = True
        Config.set(config)
        callback_data = CallbackDatas.BotSettingsNavigation(to="other")
        return await callback_botsettings_navigation(call, callback_data)
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "enter_messages_watermark")
async def callback_enter_messages_watermark(call: CallbackQuery, state: FSMContext):
    """ Включает водяной знак под сообщениями """
    try:
        await state.set_state(BotSettingsNavigationStates.entering_messages_watermark)
        await call.message.answer(text=Templates.Navigation.Settings.Other.EnterMessagesWatermark.text(),
                                  parse_mode="HTML") 
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(CallbackDatas.CustomCommandsPagination.filter())
async def callback_custom_commands_pagination(callback: CallbackQuery, callback_data: CallbackDatas.CustomCommandsPagination, state: FSMContext):
    """ Срабатывает при пагинации в пользовательских командах """
    page = callback_data.page
    await state.update_data(last_page=page)
    try:
        await callback.message.edit_text(text=Templates.Navigation.Settings.CustomCommands.Pagination.text(),
                                         reply_markup=Templates.Navigation.Settings.CustomCommands.Pagination.kb(page),
                                         parse_mode="HTML")
    except Exception as e:
        await callback.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(CallbackDatas.CustomCommandPage.filter())
async def callback_custom_command_page(callback: CallbackQuery, callback_data: CallbackDatas.CustomCommandPage, state: FSMContext):
    """ Срабатывает при переходе на страницу редактирования пользовательской команды """
    command = callback_data.command
    data = await state.get_data()
    await state.update_data(custom_command=command)
    last_page = data.get("last_page") if data.get("last_page") in data else 0
    try:
        await callback.message.edit_text(text=Templates.Navigation.Settings.CustomCommands.Page.Loading.text(),
                                         reply_markup=Templates.Navigation.Settings.CustomCommands.Page.Default.kb(command, last_page),
                                         parse_mode="HTML")
        await callback.message.edit_text(text=Templates.Navigation.Settings.CustomCommands.Page.Default.text(command),
                                         reply_markup=Templates.Navigation.Settings.CustomCommands.Page.Default.kb(command, last_page),
                                         parse_mode="HTML")
    except Exception as e:
        await callback.message.edit_text(text=Templates.Navigation.Settings.CustomCommands.Page.Error.text(),
                                         reply_markup=Templates.Navigation.Settings.CustomCommands.Page.Default.kb(command, last_page),
                                         parse_mode="HTML")
        await callback.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "enter_custom_commands_page")
async def callback_enter_custom_commands_page(call: CallbackQuery, state: FSMContext):
    """ Отрабатывает ввод страницы пользовательских команд """
    try:
        await state.set_state(CustomCommandsNavigationStates.entering_custom_commands_page)
        await call.message.answer(text=Templates.Navigation.Settings.CustomCommands.EnterCustomCommandsPage.text(),
                                  parse_mode="HTML")
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e),
                                  parse_mode="HTML")

@router.callback_query(F.data == "enter_custom_command")
async def callback_enter_custom_command(call: CallbackQuery, state: FSMContext):
    """ Отрабатывает ввод пользовательской команды """
    try:
        await state.set_state(CustomCommandPageNavigationStates.entering_custom_command)
        await call.message.answer(text=Templates.Navigation.Settings.CustomCommands.EnterCustomCommand.text(),
                                  parse_mode="HTML") 
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "add_custom_command")
async def callback_add_custom_command(call: CallbackQuery, state: FSMContext):
    """ Добавляет пользовательскую команду """
    try:
        data = await state.get_data()
        custom_commands = CustomCommands.get()
        new_custom_command = data.get("new_custom_command")
        new_custom_command_answer = data.get("new_custom_command_answer")
        if not new_custom_command:
            raise Exception("Новая пользовательская команда не была найдена, повторите процесс с самого начала")
        if not new_custom_command_answer:
            raise Exception("Ответ на новую пользовательскую команду не был найден, повторите процесс с самого начала")
        
        custom_commands[new_custom_command] = []
        for line in new_custom_command_answer.splitlines():
            custom_commands[new_custom_command].append(line)
        CustomCommands.set(custom_commands)
        await call.message.edit_text(text=Templates.Navigation.Settings.CustomCommands.CustomCommandAdded.text(new_custom_command),
                                     parse_mode="HTML") 
        await state.set_state(None)
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "enter_new_custom_command_answer")
async def callback_enter_new_custom_command_answer(call: CallbackQuery, state: FSMContext):
    """ Отрабатывает ввод нового ответа на пользовательскую команду """
    try:
        data = await state.get_data()
        custom_command = data.get("custom_command")
        if not custom_command:
            raise Exception("Пользовательская команда не была найдена, повторите процесс с самого начала")
        
        await state.set_state(CustomCommandPageNavigationStates.entering_new_custom_command_answer)
        await call.message.answer(text=Templates.Navigation.Settings.CustomCommands.EnterNewCustomCommandAnswer.text(custom_command),
                                  parse_mode="HTML") 
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "confirm_deleting_custom_command")
async def callback_confirm_deleting_custom_command(call: CallbackQuery, state: FSMContext):
    """ Отрабатывает подтверждения удаления пользовательской команды """
    try:
        data = await state.get_data()
        custom_command = data.get("custom_command")
        if not custom_command:
            raise Exception("Пользовательская команда не была найдена, повторите процесс с самого начала")
        
        await call.message.answer(text=Templates.Navigation.Settings.CustomCommands.ConfirmDeletingCustomCommand.text(custom_command),
                                  reply_markup=Templates.Navigation.Settings.CustomCommands.ConfirmDeletingCustomCommand.kb(),
                                  parse_mode="HTML") 
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "delete_custom_command")
async def callback_delete_custom_command(call: CallbackQuery, state: FSMContext):
    """ Удаляет пользовательскую команду """
    try:
        data = await state.get_data()
        custom_commands = CustomCommands.get()
        custom_command = data.get("custom_command")
        if not custom_command:
            raise Exception("Пользовательская команда не была найдена, повторите процесс с самого начала")
        
        del custom_commands[custom_command]
        CustomCommands.set(custom_commands)
        await call.message.edit_text(text=Templates.Navigation.Settings.CustomCommands.CustomComandDeleted.text(custom_command),
                                     parse_mode="HTML") 
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")


@router.callback_query(CallbackDatas.AutoDeliveriesPagination.filter())
async def callback_auto_delivery_pagination(callback: CallbackQuery, callback_data: CallbackDatas.AutoDeliveriesPagination, state: FSMContext):
    """ Срабатывает при пагинации в авто-выдаче """
    page = callback_data.page
    data = await state.get_data()
    await state.update_data(last_page=page)
    try:
        await callback.message.edit_text(text=Templates.Navigation.Settings.AutoDeliveries.Pagination.text(),
                                         reply_markup=Templates.Navigation.Settings.AutoDeliveries.Pagination.kb(page),
                                         parse_mode="HTML")
    except Exception as e:
        await callback.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(CallbackDatas.AutoDeliveryPage.filter())
async def callback_custom_command_page(callback: CallbackQuery, callback_data: CallbackDatas.AutoDeliveryPage, state: FSMContext):
    """ Срабатывает при переходе на страницу редактирования авто-выдачи """
    index = callback_data.index
    data = await state.get_data()
    await state.update_data(auto_delivery_index=index)
    last_page = data.get("last_page") if data.get("last_page") else 0
    try:
        await callback.message.edit_text(text=Templates.Navigation.Settings.AutoDeliveries.Page.Loading.text(),
                                         reply_markup=Templates.Navigation.Settings.AutoDeliveries.Page.Default.kb(index, last_page),
                                         parse_mode="HTML")
        await callback.message.edit_text(text=Templates.Navigation.Settings.AutoDeliveries.Page.Default.text(index),
                                         reply_markup=Templates.Navigation.Settings.AutoDeliveries.Page.Default.kb(index, last_page),
                                         parse_mode="HTML")
    except Exception as e:
        await callback.message.edit_text(text=Templates.Navigation.Settings.AutoDeliveries.Page.Error.text(),
                                         reply_markup=Templates.Navigation.Settings.AutoDeliveries.Page.Default.kb(index, last_page),
                                         parse_mode="HTML")
        await callback.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "enter_auto_deliveries_page")
async def callback_enter_auto_deliveries_page(call: CallbackQuery, state: FSMContext):
    """ Отрабатывает ввод страницы авто-выдачи """
    try:
        await state.set_state(AutoDeliveriesNavigationStates.entering_custom_commands_page)
        await call.message.answer(text=Templates.Navigation.Settings.AutoDeliveries.EnterAutoDeliveryPage.text(),
                                  parse_mode="HTML")
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "enter_auto_delivery_keywords")
async def callback_enter_auto_delivery_keywords(call: CallbackQuery, state: FSMContext):
    """ Отрабатывает ввод ключевых слов названия предмета авто-выдачи """
    try:
        await state.set_state(AutoDeliveryPageNavigationStates.entering_auto_delivery_keywords)
        await call.message.answer(text=Templates.Navigation.Settings.AutoDeliveries.EnterAutoDeliveryKeywords.text(),
                                  parse_mode="HTML") 
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "add_auto_delivery")
async def callback_add_auto_delivery(call: CallbackQuery, state: FSMContext):
    """ Добавляет автовыдачу """
    try:
        data = await state.get_data()
        auto_deliveries = AutoDeliveries.get()
        auto_delivery_keywords: str = data.get("auto_delivery_keywords")
        auto_delivery_message: str = data.get("auto_delivery_message")
        if not auto_delivery_keywords:
            raise Exception("Ключевые слова предмета авто-выдачи не были найдены, повторите процесс с самого начала")
        if not auto_delivery_message:
            raise Exception("Сообщение после покупки авто-доставки не было найдено, повторите процесс с самого начала")

        auto_deliveries: list = AutoDeliveries.get()
        auto_deliveries.append({"keywords": auto_delivery_keywords, "message": auto_delivery_message.splitlines()})
        AutoDeliveries.set(auto_deliveries)
        await call.message.edit_text(text=Templates.Navigation.Settings.AutoDeliveries.AutoDeliveryAdded.text(auto_delivery_keywords),
                                     parse_mode="HTML") 
        await state.set_state(None)
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "enter_new_auto_delivery_keywords")
async def callback_enter_new_auto_delivery_keywords(call: CallbackQuery, state: FSMContext):
    """ Отрабатывает ввод нового сообщения после покупки авто-выдачи """
    try:
        data = await state.get_data()
        auto_delivery_index = data.get("auto_delivery_index")
        if auto_delivery_index is None:
            raise Exception("Автовыдача не была найдена, повторите процесс с самого начала")
        
        await state.set_state(AutoDeliveryPageNavigationStates.entering_new_auto_delivery_keywords)
        await call.message.answer(text=Templates.Navigation.Settings.AutoDeliveries.EnterNewAutoDeliveryKeywords.text(auto_delivery_index),
                                  parse_mode="HTML") 
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "enter_new_auto_delivery_message")
async def callback_enter_new_auto_delivery_message(call: CallbackQuery, state: FSMContext):
    """ Отрабатывает ввод нового сообщения после покупки авто-выдачи """
    try:
        data = await state.get_data()
        auto_delivery_index = data.get("auto_delivery_index")
        if not auto_delivery_index is None:
            raise Exception("Автовыдача не была найдена, повторите процесс с самого начала")
        
        await state.set_state(AutoDeliveryPageNavigationStates.entering_new_auto_delivery_message)
        await call.message.answer(text=Templates.Navigation.Settings.AutoDeliveries.EnterNewAutoDeliveryMessage.text(auto_delivery_index),
                                  parse_mode="HTML") 
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "confirm_deleting_auto_delivery")
async def callback_confirm_deleting_auto_delivery(call: CallbackQuery, state: FSMContext):
    """ Отрабатывает подтверждения удаления авто-выдачи """
    try:
        data = await state.get_data()
        auto_delivery_index = data.get("auto_delivery_index")
        if not auto_delivery_index:
            raise Exception("Автовыдача не была найдена, повторите процесс с самого начала")
        
        await call.message.answer(text=Templates.Navigation.Settings.AutoDeliveries.ConfirmDeletingAutoDelivery.text(auto_delivery_index),
                                  reply_markup=Templates.Navigation.Settings.AutoDeliveries.ConfirmDeletingAutoDelivery.kb(),
                                  parse_mode="HTML") 
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "delete_auto_delivery")
async def callback_delete_auto_delivery(call: CallbackQuery, state: FSMContext):
    """ Удаляет автовыдачу """
    try:
        data = await state.get_data()
        auto_deliveries = AutoDeliveries.get()
        auto_delivery_index = data.get("auto_delivery_index")
        if not auto_delivery_index:
            raise Exception("Автовыдача не была найдена, повторите процесс с самого начала")
        
        del auto_deliveries[auto_delivery_index]
        AutoDeliveries.set(auto_deliveries)
        await call.message.edit_text(text=Templates.Navigation.Settings.AutoDeliveries.AutoDeliveryDeleted.text(auto_delivery_index),
                                     parse_mode="HTML") 
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")


@router.callback_query(CallbackDatas.MessagesPagination.filter())
async def callback_messages_pagination(callback: CallbackQuery, callback_data: CallbackDatas.MessagesPagination, state: FSMContext):
    """ Срабатывает при пагинации в сообщениях """
    page = callback_data.page
    await state.update_data(last_page=page)
    try:
        await callback.message.edit_text(text=Templates.Navigation.Settings.Messages.Pagination.text(),
                                         reply_markup=Templates.Navigation.Settings.Messages.Pagination.kb(page),
                                         parse_mode="HTML")
    except Exception as e:
        await callback.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")
    
@router.callback_query(CallbackDatas.MessagePage.filter())
async def callback_messages_pagination(callback: CallbackQuery, callback_data: CallbackDatas.MessagePage, state: FSMContext):
    """ Срабатывает при переходе на страницу редактирования сообщения """
    message_id = callback_data.message_id
    data = await state.get_data()
    await state.update_data(message_id=message_id)
    last_page = data.get("last_page") if data.get("last_page") else 0
    try:
        await callback.message.edit_text(text=Templates.Navigation.Settings.Messages.Page.Loading.text(),
                                         reply_markup=Templates.Navigation.Settings.Messages.Page.Default.kb(message_id, last_page),
                                         parse_mode="HTML")
        await callback.message.edit_text(text=Templates.Navigation.Settings.Messages.Page.Default.text(message_id),
                                         reply_markup=Templates.Navigation.Settings.Messages.Page.Default.kb(message_id, last_page),
                                         parse_mode="HTML")
    except Exception as e:
        await callback.message.edit_text(text=Templates.Navigation.Settings.Messages.Page.Error.text(),
                                         reply_markup=Templates.Navigation.Settings.Messages.Page.Default.kb(message_id, last_page),
                                         parse_mode="HTML")
        await callback.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")
        
@router.callback_query(F.data == "enter_messages_page")
async def callback_enter_messages_page(call: CallbackQuery, state: FSMContext):
    """ Отрабатывает ввод страницы сообщений """
    try:
        await state.set_state(MessagesNavigationStates.entering_messages_page)
        await call.message.answer(text=Templates.Navigation.Settings.Messages.EnterMessagesPage.text(),
                                parse_mode="HTML")
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e),
                                  parse_mode="HTML")

@router.callback_query(F.data == "enter_message_text")
async def callback_enter_message_text(call: CallbackQuery, state: FSMContext):
    """ Отрабатывает ввод нового текста сообщения """
    try:
        data = await state.get_data()
        message_id = data.get("message_id")
        if not message_id:
            raise Exception("ID сообщения не был найден, повторите процесс с самого начала")

        await state.set_state(MessagePageNavigationStates.entering_message_text)
        await call.message.answer(text=Templates.Navigation.Settings.Messages.EnterMessageText.text(message_id),
                                  parse_mode="HTML") 
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(CallbackDatas.ModulesPagination.filter())
async def callback_modules_pagination(callback: CallbackQuery, callback_data: CallbackDatas.ModulesPagination, state: FSMContext):
    """ Срабатывает при пагинации в модулях """
    page = callback_data.page
    await state.update_data(last_page=page)
    try:
        await callback.message.edit_text(text=Templates.Navigation.Modules.Pagination.text(),
                                         reply_markup=Templates.Navigation.Modules.Pagination.kb(page),
                                         parse_mode="HTML")
    except Exception as e:
        await callback.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(CallbackDatas.ModulePage.filter())
async def callback_module_page(callback: CallbackQuery, callback_data: CallbackDatas.ModulePage, state: FSMContext):
    """ Срабатывает при переходе на страницу управления модулем """
    module_uuid = callback_data.uuid
    data = await state.get_data()
    await state.update_data(module_uuid=module_uuid)
    last_page = data.get("last_page") if data.get("last_page") else 0
    try:
        await callback.message.edit_text(text=Templates.Navigation.Modules.Page.Loading.text(),
                                         reply_markup=Templates.Navigation.Modules.Page.Default.kb(module_uuid, last_page),
                                         parse_mode="HTML")
        await callback.message.edit_text(text=Templates.Navigation.Modules.Page.Default.text(module_uuid),
                                         reply_markup=Templates.Navigation.Modules.Page.Default.kb(module_uuid, last_page),
                                         parse_mode="HTML")
    except Exception as e:
        await callback.message.edit_text(text=Templates.Navigation.Modules.Page.Error.text(),
                                         reply_markup=Templates.Navigation.Modules.Page.Default.kb(module_uuid, last_page),
                                         parse_mode="HTML")
        await callback.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "disable_module")
async def callback_disable_module(call: CallbackQuery, state: FSMContext):
    """ Выключение модуля """
    try:
        data = await state.get_data()
        module_uuid = data.get("module_uuid")
        if not module_uuid:
            raise Exception("UUID модуля не был найден, повторите процесс с самого начала")
        if not ModulesManager.disable_module(module_uuid):
            raise Exception("Не удалось отключить модуль, попробуйте позже (см. консоль на наличие ошибки)")
        
        callback_data = CallbackDatas.ModulePage(uuid=module_uuid)
        return await callback_module_page(call, callback_data, state)
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")

@router.callback_query(F.data == "enable_module")
async def callback_enable_module(call: CallbackQuery, state: FSMContext):
    """ Включение модуля """
    try:
        data = await state.get_data()
        module_uuid = data.get("module_uuid")
        if not module_uuid:
            raise Exception("UUID модуля не был найден, повторите процесс с самого начала")
        if not ModulesManager.enable_module(module_uuid):
            raise Exception("Не удалось включить модуль, попробуйте позже (см. консоль на наличие ошибки)")
        
        callback_data = CallbackDatas.ModulePage(uuid=module_uuid)
        return await callback_module_page(call, callback_data, state)
    except Exception as e:
        await call.message.answer(text=Templates.System.Error.text(e), parse_mode="HTML")