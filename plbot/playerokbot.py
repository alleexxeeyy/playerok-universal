import asyncio
import time
from datetime import datetime, timedelta
import time
import traceback
from threading import Thread
from colorama import Fore, Style

from settings import Config, Messages, CustomCommands, AutoDeliveries
from logging import getLogger
from .data import Data
from .utils.stats import get_stats, set_stats

from playerokapi.account import Account
from playerokapi import exceptions as plapi_exceptions
from playerokapi.enums import *
from playerokapi.listener.events import *
from playerokapi.listener.listener import EventListener
from playerokapi.types import Chat, Item

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from tgbot.telegrambot import TelegramBot

from bot_settings.app import CURRENT_VERSION
from core.console import set_title, restart
from core.handlers_manager import HandlersManager

from . import set_playerok_bot

PREFIX = F"{Fore.LIGHTWHITE_EX}[playerok bot]{Fore.WHITE}"


class PlayerokBot:
    """
    Класс, запускающий и инициализирующий Playerok бота.

    :param tgbot: Объект класса TelegramBot
    :param tgbot_loop: loop, в котором запущен Telegram бот
    """

    def __init__(self, tgbot: 'TelegramBot' = None, 
                 tgbot_loop: asyncio.AbstractEventLoop = None):
        self.config = Config.get()
        self.messages = Messages.get()
        self.custom_commands = CustomCommands.get()
        self.auto_deliveries = AutoDeliveries.get()
        self.logger = getLogger(f"UNIVERSAL.TelegramBot")

        self.tgbot = tgbot
        """ Класс, содержащий данные и методы Telegram бота """
        self.tgbot_loop = tgbot_loop
        """ Объект loop, в котором запущен Telegram бот """

        try:
            self.playerok_account = Account(token=self.config["token"],
                                            user_agent=self.config["user_agent"],
                                            requests_timeout=self.config["playerokapi_requests_timeout"]).get()
            """ Класс, содержащий данные и методы аккаунта Playerok """
        except plapi_exceptions.UnauthorizedError as e:
            self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}Не удалось подключиться к вашему Playerok аккаунту. Ошибка: {Fore.WHITE}{e}")
            print(f"{Fore.LIGHTWHITE_EX}Начать снова настройку конфига? +/-")
            a = input(f"{Fore.WHITE}> {Fore.LIGHTWHITE_EX}")
            if a == "+":
                Config.configure_config()
                restart()
            else:
                self.logger.info(f"{PREFIX} Вы отказались от настройки конфига. Перезагрузим бота и попробуем снова подключиться к вашему аккаунту...")
                restart()

        self.initialized_users: list = Data.get_initialized_users()
        """ Инициализированные пользователи. """
        self.stats: dict = get_stats()
        """ Словарь статистика бота с момента запуска. """

        self.refresh_account_next_time = datetime.now() + timedelta(seconds=3600)
        """ Время следующего обновление данных об аккаунте. """
        self.try_restore_items_next_time = datetime.now()
        """ Время следующей попытки восстановить предметы. """

        self.__saved_chats: dict[str, Chat] = {}
        """ 
        Словарь последних запомненных чатов.\n
        В формате: {`chat_id` _or_ `username`: `chat_obj`, ...}
        """

        set_playerok_bot(self)

    def get_chat_by_id(self, chat_id: str) -> Chat:
        """ 
        Получает чат с пользователем из запомненных чатов по его ID, 
        если его он запомнен, иначе находит его с помощью запроса.
        """
        if chat_id in self.__saved_chats:
            return self.__saved_chats[chat_id]
        self.__saved_chats[chat_id] = self.playerok_account.get_chat(chat_id)
        return self.get_chat_by_id(chat_id)

    def get_chat_by_username(self, username: str) -> Chat:
        """ 
        Получает чат с пользователем из запомненных чатов по никнейму собеседника, 
        если его он запомнен, иначе находит его с помощью запроса.
        """
        if username in self.__saved_chats:
            return self.__saved_chats[username]
        self.__saved_chats[username] = self.playerok_account.get_chat_by_username(username)
        return self.get_chat_by_username(username)

    def msg(self, message_name: str, exclude_watermark: bool = False, **kwargs) -> str:
        """ 
        Получает отформатированное сообщение из словаря сообщений.

        :param message_name: Наименование сообщения в словаре сообщений (ID).
        :type message_name: str

        :param exclude_watermark: Пропустить и не использовать водяной знак.
        :type exclude_watermark: bool
        """

        class SafeDict(dict):
            def __missing__(self, key):
                return "{" + key + "}"
        
        message_lines: list[str] = self.messages[message_name]
        if message_lines:
            try:
                formatted_lines = [line.format_map(SafeDict(**kwargs)) for line in message_lines]
                msg = "\n".join(formatted_lines)
                if not exclude_watermark and self.config["messages_watermark_enabled"]:
                    msg += f'\n{self.config["messages_watermark"]}'
                return msg
            except:
                pass
        return "Не удалось получить сообщение"
    
    async def restore_last_sold_item(self):
        """ 
        Восстанавливает последний проданный предмет. 
        
        :param item_id: Объект предмета, который нужно восстановить.
        :type item_id: `playerok.types.Item`
        """

        try:
            profile = self.playerok_account.get_user(id=self.playerok_account.id)
            item = profile.get_items(count=1, statuses=[ItemStatuses.SOLD]).items[0]
            priority_statuses = self.playerok_account.get_item_priority_statuses(item.id, item.price)
            priority_status = None
            for status in priority_statuses:
                if status.type is PriorityTypes.__members__.get(self.config["auto_restore_items_priority_status"]):
                    priority_status = status
                    break
            else:
                for status in priority_statuses:
                    if status.type is PriorityTypes.DEFAULT:
                        priority_status = status
                        break

            new_item = self.playerok_account.publish_item(item.id, priority_status.id)
            if new_item.status is ItemStatuses.PENDING_APPROVAL or new_item.status is ItemStatuses.APPROVED:
                self.logger.info(f"{PREFIX} Предмет {Fore.LIGHTYELLOW_EX}«{item.name}» {Fore.WHITE}был автоматически восстановлен после его покупки")
            else:
                self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}Не удалось восстановить предмет «{new_item.name}». Его статус: {Fore.WHITE}{new_item.status.name}")
        except plapi_exceptions.RequestError as e:
            if e.error_code == "TOO_MANY_REQUESTS":
                self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При попытке восстановления предмета «{item.name}» произошла ошибка 429 слишком частых запросов. Ждём 10 секунд и пробуем снова")
                time.sleep(10)
            else:
                self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При восстановлении предмета «{item.name}» произошла ошибка запроса {e.error_code}: {Fore.WHITE}\n{e}")
        except Exception as e:
            self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При восстановлении предмета «{item.name}» произошла ошибка: {Fore.WHITE}{e}")

    async def run_bot(self) :
        """ Основная функция-запускатор бота. """

        # --- задаём начальные хендлеры бота ---
        def handler_on_playerok_bot_init(plbot: PlayerokBot):
            """ Начальный хендлер ON_INIT. """
            def endless_loop(cycle_delay=5):
                """ Действия, которые должны выполняться в другом потоке, вне цикла раннера. """
                while True:
                    try:
                        set_playerok_bot(plbot)
                        if self.playerok_account.profile.balance is not None: balance = self.playerok_account.profile.balance.value
                        else: balance = 0
                        set_title(f"Playerok Universal v{CURRENT_VERSION} | {self.playerok_account.username}: {balance} RUB")
                        if Data.get_initialized_users() != plbot.initialized_users:
                            Data.set_initialized_users(plbot.initialized_users)
                        if Config.get() != plbot.config:
                            plbot.config = Config.get()
                        if Messages.get() != plbot.messages:
                            plbot.messages = Messages.get()
                        if CustomCommands.get() != plbot.custom_commands:
                            plbot.custom_commands = CustomCommands.get()
                        if AutoDeliveries.get() != plbot.auto_deliveries:
                            plbot.auto_deliveries = AutoDeliveries.get()

                        '''if self.config["auto_restore_items_enabled"]:
                            if datetime.now() > self.try_restore_items_next_time:
                                user = plbot.playerok_account.get_user(id=plbot.playerok_account.id)
                                break_flag = False
                                first_item = None
                                next_cursor = None
                                while True:
                                    try:
                                        item_list = user.get_items(statuses=[ItemStatuses.EXPIRED, ItemStatuses.SOLD], after_cursor=next_cursor)
                                        if not item_list.items:
                                            break
                                        next_cursor = item_list.page_info.end_cursor
                                        for item in item_list.items:
                                            try:
                                                if first_item is not None:
                                                    if first_item.id == item.id:
                                                        break_flag = True
                                                        break
                                                if first_item is None:
                                                    first_item = item
                                                priority_statuses = self.playerok_account.get_item_priority_statuses(item.id, item.price)
                                                priority_status = None
                                                for status in priority_statuses:
                                                    if status.type is PriorityTypes.__members__.get(self.config["auto_restore_items_priority_status"]):
                                                        priority_status = status

                                                new_item = self.playerok_account.publish_item(item.id, priority_status.id)
                                                if new_item.status is ItemStatuses.PENDING_APPROVAL or new_item.status is ItemStatuses.APPROVED:
                                                    self.logger.info(f"{PREFIX} Предмет {Fore.LIGHTYELLOW_EX}«{item.name}» {Fore.WHITE}был автоматически восстановлен после его покупки")
                                                else:
                                                    self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}Не удалось восстановить предмет «{new_item.name}». Его статус: {Fore.WHITE}{new_item.status.name}")
                                            except plapi_exceptions.RequestError as e:
                                                if e.error_code == "TOO_MANY_REQUESTS":
                                                    self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При попытке восстановления предмета «{item.name}» произошла ошибка 429 слишком частых запросов. Ждём 10 секунд и пробуем снова")
                                                    time.sleep(10)
                                                else:
                                                    self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При попытке восстановления предмета «{item.name}» произошла ошибка запроса {e.error_code}: {Fore.WHITE}\n{e}")
                                            except Exception as e:
                                                self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При попытке восстановления предмета «{item.name}» произошла ошибка: {Fore.WHITE}{e}")
                                        if break_flag:
                                            break
                                    except Exception as e:
                                        self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При восстановлении предметов произошла ошибка: {Fore.WHITE}{e}")
                                self.try_restore_items_next_time = datetime.now() + timedelta(seconds=60)'''
                                    
                        if datetime.now() > self.refresh_account_next_time:
                            self.playerok_account = Account(token=self.config["token"],
                                                            user_agent=self.config["user_agent"],
                                                            requests_timeout=self.config["playerokapi_requests_timeout"]).get()
                            self.playerok_account = datetime.now() + timedelta(seconds=3600)
                    except plapi_exceptions.RequestError as e:
                        if e.error_code == "TOO_MANY_REQUESTS":
                            self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}В бесконечном цикле произошла ошибка 429 слишком частых запросов. Ждём 10 секунд и пробуем снова")
                            time.sleep(10)
                        else:
                            self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}В бесконечном цикле произошла ошибка запроса {e.error_code}: {Fore.WHITE}\n{e}")
                    except Exception:
                        self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}В бесконечном цикле произошла ошибка: {Fore.WHITE}")
                        traceback.print_exc()
                    time.sleep(cycle_delay)

            endless_loop_thread = Thread(target=endless_loop, daemon=True)
            endless_loop_thread.start()

        bot_event_handlers = HandlersManager.get_bot_event_handlers()
        bot_event_handlers["ON_PLAYEROK_BOT_INIT"].insert(0, handler_on_playerok_bot_init)
        HandlersManager.set_bot_event_handlers(bot_event_handlers)

        async def handler_new_message(plbot: PlayerokBot, event: NewMessageEvent):
            """ Начальный хендлер новых сообщений. """
            try:
                this_chat = event.chat
                if self.config["first_message_enabled"]:
                    if event.message.user is not None:
                        if event.message.user.id == event.message.user.id and event.message.user.id not in plbot.initialized_users:
                            try:
                                plbot.playerok_account.send_message(this_chat.id, 
                                                                    plbot.msg("user_not_initialized",
                                                                            buyer_username=event.message.user.username),
                                                                    self.config.get("read_chat_before_sending_message_enabled") or False)
                                plbot.initialized_users.append(event.message.user.id)
                            except Exception as e:
                                self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При отправке приветственного сообщения для {event.message.user.username} произошла ошибка: {Fore.WHITE}{e}")

                if event.message.user is not None:
                    if event.message.user.id != plbot.playerok_account.id:
                        if self.config["custom_commands_enabled"]:
                            if event.message.text in self.custom_commands.keys():
                                try:
                                    message = "\n".join(self.custom_commands[event.message.text])
                                    plbot.playerok_account.send_message(this_chat.id, 
                                                                        message, 
                                                                        self.config.get("read_chat_before_sending_message_enabled") or False)
                                except Exception as e:
                                    self.logger.info(f"{PREFIX} {Fore.LIGHTRED_EX}При вводе пользовательской команды \"{event.message.text}\" у {event.message.user.username} произошла ошибка: {Fore.WHITE}{e}")
                                    plbot.playerok_account.send_message(this_chat.id, 
                                                                        plbot.msg("command_error"),
                                                                        self.config.get("read_chat_before_sending_message_enabled") or False)
                        if str(event.message.text).lower() == "!команды" or str(event.message.text).lower() == "!commands":
                            try:
                                plbot.playerok_account.send_message(this_chat.id, 
                                                                    plbot.msg("buyer_command_commands"),
                                                                    self.config.get("read_chat_before_sending_message_enabled") or False)
                            except Exception as e:
                                self.logger.info(f"{PREFIX} {Fore.LIGHTRED_EX}При вводе команды \"!команды\" у {event.message.user.username} произошла ошибка: {Fore.WHITE}{e}")
                                plbot.playerok_account.send_message(this_chat.id, 
                                                                    plbot.msg("command_error"),
                                                                    self.config.get("read_chat_before_sending_message_enabled") or False)
                        if str(event.message.text).lower() == "!продавец" or str(event.message.text).lower() == "!seller":
                            try:
                                asyncio.run_coroutine_threadsafe(plbot.tgbot.call_seller(event.message.user.username, this_chat.id), self.tgbot_loop)
                                plbot.playerok_account.send_message(this_chat.id, 
                                                                    plbot.msg("buyer_command_seller"),
                                                                    self.config.get("read_chat_before_sending_message_enabled") or False)
                            except Exception as e:
                                self.logger.log(f"{PREFIX} {Fore.LIGHTRED_EX}При вводе команды \"!продавец\" у {event.message.user.username} произошла ошибка: {Fore.WHITE}{e}")
                                plbot.playerok_account.send_message(this_chat.id, 
                                                                    plbot.msg("command_error"),
                                                                    self.config.get("read_chat_before_sending_message_enabled") or False)
            except plapi_exceptions.RequestError as e:
                if e.error_code == "TOO_MANY_REQUESTS":
                    self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При обработке ивента новых сообщений произошла ошибка 429 слишком частых запросов. Ждём 10 секунд и пробуем снова")
                    time.sleep(10)
                else:
                    self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При обработке ивента новых сообщений произошла ошибка {e.error_code}: {Fore.WHITE}\n{e}")
            except Exception:
                self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При обработке ивента новых сообщений произошла ошибка: {Fore.WHITE}")
                traceback.print_exc()

        async def handler_new_deal(plbot: PlayerokBot, event: NewDealEvent):
            """ Начальный хендлер нового заказа. """
            try:
                try:
                    this_chat = event.chat
                    self.logger.info(f"{PREFIX} 🛒  {Fore.LIGHTYELLOW_EX}Новая сделка: {Fore.WHITE}Пользователь {Fore.LIGHTYELLOW_EX}{event.deal.user.username}{Fore.WHITE} оплатил предмет {Fore.LIGHTYELLOW_EX}«{event.deal.item.name}»{Fore.WHITE} на сумму {Fore.LIGHTYELLOW_EX}{event.deal.item.price} р.")
                    
                    break_flag = False
                    if self.config["auto_deliveries_enabled"]:
                        for auto_delivery in self.auto_deliveries:
                            for keyword in auto_delivery["keywords"]:
                                if keyword.lower() in event.deal.item.name.lower():
                                    self.playerok_account.send_message(this_chat.id, 
                                                                        "\n".join(auto_delivery["message"]),
                                                                        self.config.get("read_chat_before_sending_message_enabled") or False)
                                    self.logger.info(f"{PREFIX} 🚀  На оплаченный предмет {Fore.LIGHTYELLOW_EX}«{event.deal.item.name}»{Fore.WHITE} от покупателя {Fore.LIGHTYELLOW_EX}{event.deal.user.username}{Fore.WHITE} было автоматически выдано пользовательское сообщение после покупки (ключевое слово: {keyword})")
                                    break_flag = True
                                    break
                            if break_flag: break

                    if self.config["auto_complete_deals_enabled"]:
                        if event.deal.user.id != plbot.playerok_account.id:
                            self.playerok_account.update_deal(event.deal.id, ItemDealStatuses.SENT)
                            self.logger.info(f"{PREFIX} ☑️  Заказ {Fore.LIGHTYELLOW_EX}{event.deal.id}{Fore.WHITE} от покупателя {Fore.LIGHTYELLOW_EX}{event.deal.user.username}{Fore.WHITE} был автоматически подтверждён")
                
                except Exception as e:
                    self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При обработке новой сделки от {event.deal.user.username} произошла ошибка: {Fore.WHITE}{e}")
            except plapi_exceptions.RequestError as e:
                if e.error_code == "TOO_MANY_REQUESTS":
                    self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При обработке ивента новой сделки произошла ошибка 429 слишком частых запросов. Ждём 10 секунд и пробуем снова")
                    time.sleep(10)
                else:
                    self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При обработке ивента новой сделки произошла ошибка {e.error_code}: {Fore.WHITE}\n{e}")
            except Exception:
                self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При обработке ивента новой сделки произошла ошибка: {Fore.WHITE}")
                traceback.print_exc()

        async def handler_item_paid(plbot: PlayerokBot, event: ItemPaidEvent):
            try:
                if self.config["auto_restore_items_enabled"]:
                    await self.restore_last_sold_item()
            except plapi_exceptions.RequestError as e:
                if e.error_code == "TOO_MANY_REQUESTS":
                    self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При обработке ивента новых сообщений произошла ошибка 429 слишком частых запросов. Ждём 10 секунд и пробуем снова")
                    time.sleep(10)
                else:
                    self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При обработке ивента новых сообщений произошла ошибка {e.error_code}: {Fore.WHITE}\n{e}")
            except Exception:
                self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При обработке ивента новых сообщений произошла ошибка: {Fore.WHITE}")
                traceback.print_exc()

        async def handler_deal_status_changed(plbot: PlayerokBot, event: DealStatusChangedEvent):
            """ Начальный хендлер изменения статуса заказа """
            try:
                this_chat = event.chat
                try:
                    if event.deal.status is ItemDealStatuses.CONFIRMED:
                        plbot.stats["earned_money"] += event.deal.transaction.value or 0
                        plbot.stats["earned_money"] = round(plbot.stats["earned_money"], 2)
                    elif event.deal.status is ItemDealStatuses.ROLLED_BACK:
                        plbot.stats["orders_refunded"] += 1
                except Exception as e:
                    self.logger.info(f"{PREFIX} {Fore.LIGHTRED_EX}При подсчёте статистики произошла ошибка: {Fore.WHITE}{e}")
                finally:
                    set_stats(plbot.stats)

                if event.deal.status is ItemDealStatuses.CONFIRMED or event.deal.status is ItemDealStatuses.ROLLED_BACK:
                    if event.deal.status is ItemDealStatuses.CONFIRMED:
                        plbot.playerok_account.send_message(this_chat.id, 
                                                            plbot.msg("deal_confirmed"),
                                                            self.config.get("read_chat_before_sending_message_enabled") or False)
            except plapi_exceptions.RequestError as e:
                if e.error_code == "TOO_MANY_REQUESTS":
                    self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При обработке ивента смены статуса сделки произошла ошибка 429 слишком частых запросов. Ждём 10 секунд и пробуем снова")
                    time.sleep(10)
                else:
                    self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При обработке ивента смены статуса сделки произошла ошибка {e.error_code}: {Fore.WHITE}\n{e}")
            except Exception:
                self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При обработке ивента смены статуса сделки произошла ошибка: {Fore.WHITE}")
                traceback.print_exc()
            
        playerok_event_handlers = HandlersManager.get_playerok_event_handlers()
        playerok_event_handlers[EventTypes.NEW_MESSAGE].insert(0, handler_new_message)
        playerok_event_handlers[EventTypes.NEW_DEAL].insert(0, handler_new_deal)
        playerok_event_handlers[EventTypes.DEAL_STATUS_CHANGED].insert(0, handler_deal_status_changed)
        playerok_event_handlers[EventTypes.ITEM_PAID].insert(0, handler_item_paid)
        HandlersManager.set_playerok_event_handlers(playerok_event_handlers)

        bot_event_handlers = HandlersManager.get_bot_event_handlers()
        def handle_on_playerok_bot_init():
            """ 
            Запускается при инициализации Playerok бота.
            Запускает за собой все хендлеры ON_PLAYEROK_BOT_INIT 
            """
            if "ON_PLAYEROK_BOT_INIT" in bot_event_handlers:
                for handler in bot_event_handlers["ON_PLAYEROK_BOT_INIT"]:
                    try:
                        handler(self)
                    except Exception as e:
                        self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}Ошибка при обработке хендлера ивента ON_PLAYEROK_BOT_INIT: {Fore.WHITE}{e}")
        handle_on_playerok_bot_init()

        self.logger.info(f"{PREFIX} Playerok бот запущен и активен")
        listener = EventListener(self.playerok_account)
        for event in listener.listen(requests_delay=self.config["playerokapi_listener_requests_delay"]):
            playerok_event_handlers = HandlersManager.get_playerok_event_handlers() # чтобы каждый раз брать свежие хендлеры, ибо модули могут отключаться/включаться
            if event.type in playerok_event_handlers:
                for handler in playerok_event_handlers[event.type]:
                    try:
                        await handler(self, event)
                    except plapi_exceptions.RequestError as e:
                        if e.error_code == "TOO_MANY_REQUESTS":
                            self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}Произошла ошибка 429 слишком частых запросов при обработке хендлера {handler} в ивенте {event.type.name}. Ждём 10 секунд и пробуем снова")
                            time.sleep(10)
                        else:
                            self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}Произошла ошибка {e.error_code} при обработке хендлера {handler} в ивенте {event.type.name}: {Fore.WHITE}\n{e}")
                    except Exception as e:
                        self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}Произошла ошибка при обработке хендлера {handler} в ивенте {event.type.name}: {Fore.WHITE}{e}")