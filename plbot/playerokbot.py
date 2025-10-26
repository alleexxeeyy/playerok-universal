from __future__ import annotations
import asyncio
import time
from datetime import datetime
import time
import traceback
from threading import Thread
import textwrap
import shutil
from colorama import Fore
from aiogram.types import InlineKeyboardMarkup

from __init__ import VERSION
from playerokapi.account import Account
from playerokapi import exceptions as plapi_exceptions
from playerokapi.enums import *
from playerokapi.listener.events import *
from playerokapi.listener.listener import EventListener
from playerokapi.types import Chat, Item
from core.utils import set_title
from core.handlers import get_bot_event_handlers, set_bot_event_handlers, get_playerok_event_handlers, set_playerok_event_handlers
from settings import DATA, Settings as sett
from logging import getLogger
from data import Data as data
from tgbot.telegrambot import get_telegram_bot, get_telegram_bot_loop
from tgbot.templates import log_text, log_new_mess_kb, log_new_deal_kb

from .stats import get_stats, set_stats


def get_playerok_bot() -> None | PlayerokBot:
    if hasattr(PlayerokBot, "instance"):
        return getattr(PlayerokBot, "instance")

class PlayerokBot:
    def __new__(cls, *args, **kwargs) -> PlayerokBot:
        if not hasattr(cls, "instance"):
            cls.instance = super(PlayerokBot, cls).__new__(cls)
        return getattr(cls, "instance")

    def __init__(self):
        self.config = sett.get("config")
        self.messages = sett.get("messages")
        self.custom_commands = sett.get("custom_commands")
        self.auto_deliveries = sett.get("auto_deliveries")
        self.logger = getLogger(f"universal.playerok")
        self.playerok_account = Account(token=self.config["playerok"]["api"]["token"],
                                        user_agent=self.config["playerok"]["api"]["user_agent"],
                                        requests_timeout=self.config["playerok"]["api"]["requests_timeout"],
                                        proxy=self.config["playerok"]["api"]["proxy"] or None).get()

        self.initialized_users: list = data.get("initialized_users")
        self.stats = get_stats()

        self.__saved_chats: dict[str, Chat] = {}
        """Словарь последних запомненных чатов.\nВ формате: {`chat_id` _or_ `username`: `chat_obj`, ...}"""

    def get_chat_by_id(self, chat_id: str) -> Chat:
        """ 
        Получает чат с пользователем из запомненных чатов по его ID.
        Запоминает и получает чат, если он не запомнен.
        
        :param chat_id: ID чата.
        :type chat_id: `str`
        
        :return: Объект чата.
        :rtype: `playerokapi.types.Chat`
        """
        if chat_id in self.__saved_chats:
            return self.__saved_chats[chat_id]
        self.__saved_chats[chat_id] = self.playerok_account.get_chat(chat_id)
        return self.get_chat_by_id(chat_id)

    def get_chat_by_username(self, username: str) -> Chat:
        """ 
        Получает чат с пользователем из запомненных чатов по никнейму собеседника.
        Запоминает и получает чат, если он не запомнен.
        
        :param username: Юзернейм собеседника чата.
        :type username: `str`
        
        :return: Объект чата.
        :rtype: `playerokapi.types.Chat`
        """
        if username in self.__saved_chats:
            return self.__saved_chats[username]
        self.__saved_chats[username] = self.playerok_account.get_chat_by_username(username)
        return self.get_chat_by_username(username)

    def get_my_items(self, statuses: list[ItemStatuses] | None = None) -> list[types.ItemProfile]:
        """
        Получает все предметы аккаунта.

        :param statuses: Статусы, с которыми нужно получать предметы, _опционально_.
        :type statuses: `list[playerokapi.enums.ItemStatuses]` or `None`

        :return: Массив предметов профиля.
        :rtype: `list` of `playerokapi.types.ItemProfile`
        """
        user = self.playerok_account.get_user(self.playerok_account.id)
        my_items: list[types.ItemProfile] = []
        next_cursor = None
        while True:
            _items = user.get_items(statuses=statuses, after_cursor=next_cursor)
            for _item in _items.items:
                if _item.id not in [item.id for item in my_items]:
                    my_items.append(_item)
            if not _items.page_info.has_next_page:
                break
            next_cursor = _items.page_info.end_cursor
            time.sleep(0.3)
        return my_items
    

    def msg(self, message_name: str, exclude_watermark: bool = False,
            messages_config_name: str = "messages", messages_data: dict = DATA,
            **kwargs) -> str | None:
        """ 
        Получает отформатированное сообщение из словаря сообщений.

        :param message_name: Наименование сообщения в словаре сообщений (ID).
        :type message_name: `str`

        :param exclude_watermark: Пропустить и не использовать водяной знак.
        :type exclude_watermark: `bool`

        :param messages_config_name: Имя файла конфигурации сообщений.
        :type messages_config_name: `str`

        :param messages_data: Словарь данных конфигурационных файлов.
        :type messages_data: `dict` or `None`

        :return: Отформатированное сообщение или None, если сообщение выключено.
        :rtype: `str` or `None`
        """

        class SafeDict(dict):
            def __missing__(self, key):
                return "{" + key + "}"

        messages = sett.get(messages_config_name, messages_data) or {}
        mess: dict = messages.get(message_name, {})
        if mess.get("enabled") is False:
            return None
        message_lines: list[str] = mess.get("text", [])
        if message_lines and message_lines:
            try:
                formatted_lines = [line.format_map(SafeDict(**kwargs)) for line in message_lines]
                msg = "\n".join(formatted_lines)
                if not exclude_watermark and self.config["playerok"]["bot"]["messages_watermark_enabled"]:
                    msg += f'\n{self.config["playerok"]["bot"]["messages_watermark"]}' or ""
                return msg
            except:
                pass
        return f"Не удалось получить сообщение {message_name}"
    
    def send_message(self, chat_id: str, text: str | None = None, photo_file_path: str | None = None,
                     mark_chat_as_read: bool = None, max_attempts: int = 3) -> types.ChatMessage:
        """
        Кастомный метод отправки сообщения в чат Playerok.
        Пытается отправить за 3 попытки, если не удалось - выдаёт ошибку в консоль.\n
        Можно отправить текстовое сообщение `text` или фотографию `photo_file_path`.

        :param chat_id: ID чата, в который нужно отправить сообщение.
        :type chat_id: `str`

        :param text: Текст сообщения, _опционально_.
        :type text: `str` or `None`

        :param photo_file_path: Путь к файлу фотографии, _опционально_.
        :type photo_file_path: `str` or `None`

        :param mark_chat_as_read: Пометить чат, как прочитанный перед отправкой, _опционально_.
        :type mark_chat_as_read: `bool`

        :return: Объект отправленного сообщения.
        :rtype: `PlayerokAPI.types.ChatMessage`
        """
        if text is None and photo_file_path is None:
            return None
        for _ in range(max_attempts):
            try:
                mark_chat_as_read = (self.config["playerok"]["bot"]["read_chat_before_sending_message_enabled"] or False) if mark_chat_as_read is None else mark_chat_as_read
                mess = self.playerok_account.send_message(chat_id, text, photo_file_path, mark_chat_as_read)
                return mess
            except plapi_exceptions.RequestFailedError:
                continue
            except Exception as e:
                self.logger.error(f"{Fore.LIGHTRED_EX}Ошибка при отправке сообщения {Fore.LIGHTWHITE_EX}«{text}» {Fore.LIGHTRED_EX}в чат {Fore.LIGHTWHITE_EX}{chat_id} {Fore.LIGHTRED_EX}: {Fore.WHITE}{e}")
                return
        text = text.replace('\n', '').strip()
        self.logger.error(f"{Fore.LIGHTRED_EX}Не удалось отправить сообщение {Fore.LIGHTWHITE_EX}«{text}» {Fore.LIGHTRED_EX}в чат {Fore.LIGHTWHITE_EX}{chat_id}")

    def log_to_tg(self, text: str, kb: InlineKeyboardMarkup | None = None):
        """
        Отправляет сообщение всем авторизованным в боте пользователям.

        :param text: Текст сообщения.
        :type text: `str`
        
        :param kb: Клавиатура сообщения, _опционально_.
        :type kb: `aiogram.types.InlineKeyboardMarkup` or `None`
        """
        asyncio.run_coroutine_threadsafe(get_telegram_bot().log_event(text, kb), get_telegram_bot_loop())

    async def restore_last_sold_item(self, item: Item):
        """ 
        Восстанавливает последний проданный предмет. 
        
        :param item: Объект предмета, который нужно восстановить.
        :type item: `playerokapi.types.Item`
        """
        try:
            profile = self.playerok_account.get_user(id=self.playerok_account.id)
            items = profile.get_items(count=24, statuses=[ItemStatuses.SOLD]).items
            _item = [profile_item for profile_item in items if profile_item.name == item.name]
            if len(_item) <= 0: return
            try: item: types.MyItem = self.playerok_account.get_item(_item[0].id)
            except: item = _item[0]

            priority_statuses = self.playerok_account.get_item_priority_statuses(item.id, item.price)
            priority_status = None
            for status in priority_statuses:
                if isinstance(item, types.MyItem) and item.priority:
                    if status.type.name == item.priority.name:
                        priority_status = status
                elif status.type is PriorityTypes.DEFAULT:
                    priority_status = status
                if priority_status: break

            new_item = self.playerok_account.publish_item(item.id, priority_status.id)
            if new_item.status is ItemStatuses.PENDING_APPROVAL or new_item.status is ItemStatuses.APPROVED:
                self.logger.info(f"{Fore.LIGHTWHITE_EX}«{item.name}» {Fore.WHITE}— {Fore.YELLOW}товар восстановлен")
            else:
                self.logger.error(f"{Fore.LIGHTRED_EX}Не удалось восстановить предмет «{new_item.name}». Его статус: {Fore.WHITE}{new_item.status.name}")
        except Exception as e:
            self.logger.error(f"{Fore.LIGHTRED_EX}При восстановлении предмета «{item.name}» произошла ошибка: {Fore.WHITE}{e}")

    def log_new_message(self, message: types.ChatMessage, chat: types.Chat):
        plbot = get_playerok_bot()
        try: chat_user = [user.username for user in chat.users if user.id != plbot.playerok_account.id][0]
        except: chat_user = message.user.username
        ch_header = f"Новое сообщение в чате с {chat_user}:"
        self.logger.info(f"{Fore.LIGHTBLUE_EX}{ch_header.replace(chat_user, f'{Fore.LIGHTCYAN_EX}{chat_user}')}")
        self.logger.info(f"{Fore.LIGHTBLUE_EX}│ {Fore.LIGHTWHITE_EX}{message.user.username}:")
        max_width = shutil.get_terminal_size((80, 20)).columns - 40
        longest_line_len = 0
        text = ""
        if message.text is not None: text = message.text
        elif message.file is not None: text = f"{Fore.LIGHTMAGENTA_EX}Изображение {Fore.WHITE}({message.file.url})"
        for raw_line in text.split("\n"):
            if not raw_line.strip():
                self.logger.info(f"{Fore.LIGHTBLUE_EX}│")
                continue
            wrapped_lines = textwrap.wrap(raw_line, width=max_width)
            for wrapped in wrapped_lines:
                self.logger.info(f"{Fore.LIGHTBLUE_EX}│ {Fore.WHITE}{wrapped}")
                longest_line_len = max(longest_line_len, len(wrapped.strip()))
        underline_len = max(len(ch_header)-1, longest_line_len+2)
        self.logger.info(f"{Fore.LIGHTBLUE_EX}└{'─'*underline_len}")
    
    def log_new_deal(self, deal: types.ItemDeal):
        self.logger.info(f"{Fore.YELLOW}───────────────────────────────────────")
        self.logger.info(f"{Fore.YELLOW}Новая сделка {deal.id}:")
        self.logger.info(f" · Покупатель: {Fore.LIGHTWHITE_EX}{deal.user.username}")
        self.logger.info(f" · Товар: {Fore.LIGHTWHITE_EX}{deal.item.name}")
        self.logger.info(f" · Сумма: {Fore.LIGHTWHITE_EX}{deal.item.price}₽")
        self.logger.info(f"{Fore.YELLOW}───────────────────────────────────────")

    def log_new_review(self, deal: types.ItemDeal):
        self.logger.info(f"{Fore.YELLOW}───────────────────────────────────────")
        self.logger.info(f"{Fore.YELLOW}Новый отзыв по сделке {deal.id}:")
        self.logger.info(f" · Оценка: {Fore.LIGHTYELLOW_EX}{'★' * deal.review.rating or 5} ({deal.review.rating or 5})")
        self.logger.info(f" · Текст: {Fore.LIGHTWHITE_EX}{deal.review.text}")
        self.logger.info(f" · Оставил: {Fore.LIGHTWHITE_EX}{deal.review.user.username}")
        self.logger.info(f" · Дата: {Fore.LIGHTWHITE_EX}{datetime.fromisoformat(deal.review.created_at).strftime('%d.%m.%Y %H:%M:%S')}")
        self.logger.info(f"{Fore.YELLOW}───────────────────────────────────────")
    
    def log_deal_status_changed(self, deal: types.ItemDeal):
        status = "Неизвестный"
        if deal.status is ItemDealStatuses.PAID: status = "Оплачен"
        elif deal.status is ItemDealStatuses.PENDING: status = "В ожидании отправки"
        elif deal.status is ItemDealStatuses.SENT: status = "Продавец подтвердил выполнение"
        elif deal.status is ItemDealStatuses.CONFIRMED: status = "Покупатель подтвердил сделку"
        elif deal.status is ItemDealStatuses.ROLLED_BACK: status = "Возврат"
        self.logger.info(f"{Fore.WHITE}───────────────────────────────────────")
        self.logger.info(f"{Fore.WHITE}Статус сделки {Fore.LIGHTWHITE_EX}{deal.id} {Fore.WHITE}изменился:")
        self.logger.info(f" · Статус: {Fore.LIGHTWHITE_EX}{status}")
        self.logger.info(f" · Покупатель: {Fore.LIGHTWHITE_EX}{deal.user.username}")
        self.logger.info(f" · Товар: {Fore.LIGHTWHITE_EX}{deal.item.name}")
        self.logger.info(f" · Сумма: {Fore.LIGHTWHITE_EX}{deal.item.price}₽")
        self.logger.info(f"{Fore.WHITE}───────────────────────────────────────")
    
    def log_new_problem(self, deal: types.ItemDeal):
        self.logger.info(f"{Fore.YELLOW}───────────────────────────────────────")
        self.logger.info(f"{Fore.YELLOW}Новая жалоба в сделке {deal.id}:")
        self.logger.info(f" · Оставил: {Fore.LIGHTWHITE_EX}{deal.user.username}")
        self.logger.info(f" · Товар: {Fore.LIGHTWHITE_EX}{deal.item.name}")
        self.logger.info(f" · Сумма: {Fore.LIGHTWHITE_EX}{deal.item.price}₽")
        self.logger.info(f"{Fore.YELLOW}───────────────────────────────────────")

    async def run_bot(self, loop):
        self.logger.info(f"{Fore.GREEN}Playerok бот запущен и активен")
        self.logger.info("")
        self.logger.info(f"{Fore.LIGHTBLUE_EX}───────────────────────────────────────")
        self.logger.info(f"{Fore.LIGHTBLUE_EX}Информация об аккаунте:")
        self.logger.info(f" · ID: {Fore.LIGHTWHITE_EX}{self.playerok_account.id}")
        self.logger.info(f" · Никнейм: {Fore.LIGHTWHITE_EX}{self.playerok_account.username}")
        if self.playerok_account.profile.balance:
            self.logger.info(f" · Баланс: {Fore.LIGHTWHITE_EX}{self.playerok_account.profile.balance.value}₽")
            self.logger.info(f"   · Доступно: {Fore.LIGHTWHITE_EX}{self.playerok_account.profile.balance.available}₽")
            self.logger.info(f"   · В ожидании: {Fore.LIGHTWHITE_EX}{self.playerok_account.profile.balance.pending_income}₽")
            self.logger.info(f"   · Заморожено: {Fore.LIGHTWHITE_EX}{self.playerok_account.profile.balance.frozen}₽")
        self.logger.info(f" · Активные продажи: {Fore.LIGHTWHITE_EX}{self.playerok_account.profile.stats.deals.outgoing.total - self.playerok_account.profile.stats.deals.outgoing.finished}")
        self.logger.info(f" · Активные покупки: {Fore.LIGHTWHITE_EX}{self.playerok_account.profile.stats.deals.incoming.total - self.playerok_account.profile.stats.deals.incoming.finished}")
        self.logger.info(f"{Fore.LIGHTBLUE_EX}───────────────────────────────────────")
        self.logger.info("")
        if self.config["playerok"]["api"]["proxy"]:
            user, password = self.config["playerok"]["api"]["proxy"].split("@")[0].split(":") if "@" in self.config["playerok"]["api"]["proxy"] else self.config["playerok"]["api"]["proxy"]
            ip, port = self.config["playerok"]["api"]["proxy"].split("@")[1].split(":") if "@" in self.config["playerok"]["api"]["proxy"] else self.config["playerok"]["api"]["proxy"]
            self.logger.info(f"{Fore.LIGHTBLUE_EX}───────────────────────────────────────")
            self.logger.info(f"{Fore.LIGHTBLUE_EX}Информация о прокси:")
            self.logger.info(f" · IP: {Fore.LIGHTWHITE_EX}{ip}:{port}")
            self.logger.info(f" · Юзер: {(f'{Fore.LIGHTWHITE_EX}{user[:3]}' + '*' * 5) if user else f'Без авторизации'}")
            self.logger.info(f" · Пароль: {(f'{Fore.LIGHTWHITE_EX}{password[:3]}' + '*' * 5) if password else f'Без авторизации'}")
            self.logger.info(f"{Fore.LIGHTBLUE_EX}───────────────────────────────────────")
            self.logger.info("")

        def on_playerok_bot_init(plbot: PlayerokBot):
            self.stats.bot_launch_time = datetime.now()

            def endless_loop():
                while True:
                    try:
                        balance = self.playerok_account.profile.balance.value if self.playerok_account.profile.balance is not None else "?"
                        set_title(f"Playerok Universal v{VERSION} | {self.playerok_account.username}: {balance}₽")
                        if plbot.stats != get_stats(): set_stats(plbot.stats)
                        if data.get("initialized_users") != self.initialized_users: data.set("initialized_users", self.initialized_users)
                        if sett.get("config") != self.config: self.config = sett.get("config")
                        if sett.get("messages") != self.messages: self.messages = sett.get("messages")
                        if sett.get("custom_commands") != self.custom_commands: self.custom_commands = sett.get("custom_commands")
                        if sett.get("auto_deliveries") != self.auto_deliveries: self.auto_deliveries = sett.get("auto_deliveries")
                    except Exception:
                        self.logger.error(f"{Fore.LIGHTRED_EX}В бесконечном цикле произошла ошибка: {Fore.WHITE}{e}")
                    time.sleep(3)

            Thread(target=endless_loop, daemon=True).start()

        bot_event_handlers = get_bot_event_handlers()
        bot_event_handlers["ON_PLAYEROK_BOT_INIT"].insert(0, on_playerok_bot_init)
        set_bot_event_handlers(bot_event_handlers)

        async def on_new_message(plbot: PlayerokBot, event: NewMessageEvent):
            try:
                this_chat = event.chat
                self.log_new_message(event.message, event.chat)
                if self.config["playerok"]["bot"]["tg_logging_enabled"] and (self.config["playerok"]["bot"]["tg_logging_events"]["new_user_message"] or self.config["playerok"]["bot"]["tg_logging_events"]["new_system_message"]):
                    if event.message.user.username != self.playerok_account.username:
                        do = False
                        if self.config["playerok"]["bot"]["tg_logging_events"]["new_user_message"] and event.message.user.username not in ["Playerok.com", "Поддержка"]: do = True 
                        if self.config["playerok"]["bot"]["tg_logging_events"]["new_system_message"] and event.message.user.username in ["Playerok.com", "Поддержка"]: do = True 
                        if do:
                            text = f"<b>{event.message.user.username}:</b> {event.message.text or ''}"
                            if event.message.file:
                                text += f' <b><a href="{event.message.file.url}">{event.message.file.filename}</a></b>'
                            self.log_to_tg(text=log_text(f'💬 Новое сообщение в <a href="https://playerok.com/chats/{event.chat.id}">чате</a>', text.strip()),
                                            kb=log_new_mess_kb(event.message.user.username))

                if event.message.user is not None:
                    if event.message.user.id != self.playerok_account.id and event.chat.id not in [self.playerok_account.system_chat_id, self.playerok_account.support_chat_id]:
                        if event.message.user.id not in self.initialized_users:
                            self.send_message(this_chat.id, self.msg("first_message", username=event.message.user.username))
                            self.initialized_users.append(event.message.user.id)

                        if self.config["playerok"]["bot"]["custom_commands_enabled"]:
                            if event.message.text in self.custom_commands.keys():
                                msg = "\n".join(self.custom_commands[event.message.text]) + (f'\n{self.config["playerok"]["bot"]["messages_watermark"]}' if self.config["playerok"]["bot"]["messages_watermark_enabled"] else "")
                                self.send_message(this_chat.id, msg)
                        if str(event.message.text).lower() == "!команды" or str(event.message.text).lower() == "!commands":
                            self.send_message(this_chat.id, self.msg("cmd_commands"))
                        if str(event.message.text).lower() == "!продавец" or str(event.message.text).lower() == "!seller":
                            asyncio.run_coroutine_threadsafe(get_telegram_bot().call_seller(event.message.user.username, this_chat.id), get_telegram_bot_loop())
                            self.send_message(this_chat.id, self.msg("cmd_seller"))
            except Exception:
                self.logger.error(f"{Fore.LIGHTRED_EX}При обработке ивента новых сообщений произошла ошибка: {Fore.WHITE}")
                traceback.print_exc()

        async def on_new_deal(plbot: PlayerokBot, event: NewDealEvent):
            try:
                this_chat = event.chat
                self.log_new_deal(event.deal)
                if self.config["playerok"]["bot"]["tg_logging_enabled"] and self.config["playerok"]["bot"]["tg_logging_events"]["new_deal"]:
                    self.log_to_tg(text=log_text(f'📋 Новая <a href="https://playerok.com/deal/{event.deal.id}">сделка</a>', f"<b>Покупатель:</b> {event.deal.user.username}\n<b>Предмет:</b> {event.deal.item.name}\n<b>Сумма:</b> {event.deal.item.price or '?'}₽"),
                                   kb=log_new_deal_kb(event.deal.user.username, event.deal.id))
                self.send_message(this_chat.id, self.msg("new_deal", deal_item_name=event.deal.item.name, deal_item_price=event.deal.item.price))
                if self.config["playerok"]["bot"]["auto_deliveries_enabled"]:
                    for auto_delivery in self.auto_deliveries:
                        for phrase in auto_delivery["keyphrases"]:
                            if phrase.lower() in event.deal.item.name.lower() or event.deal.item.name.lower() == phrase.lower():
                                self.send_message(this_chat.id, "\n".join(auto_delivery["message"]))
                                break
                if self.config["playerok"]["bot"]["auto_complete_deals_enabled"]:
                    if event.deal.user.id != self.playerok_account.id:
                        self.playerok_account.update_deal(event.deal.id, ItemDealStatuses.SENT)
            except Exception:
                self.logger.error(f"{Fore.LIGHTRED_EX}При обработке ивента новой сделки произошла ошибка: {Fore.WHITE}")
                traceback.print_exc()

        async def on_new_review(plbot: PlayerokBot, event: NewReviewEvent):
            try:
                self.log_new_review(event.deal)
                if self.config["playerok"]["bot"]["tg_logging_enabled"] and self.config["playerok"]["bot"]["tg_logging_events"]["new_review"]:
                    self.log_to_tg(text=log_text(f'💬✨ Новый отзыв по <a href="https://playerok.com/deal/{event.deal.id}">сделке</a>', f"<b>Оценка:</b> {'⭐' * event.deal.review.rating}\n<b>Оставил:</b> {event.deal.review.creator.username}\n<b>Текст:</b> {event.deal.review.text}\n<b>Дата:</b> {datetime.fromisoformat(event.deal.review.created_at).strftime('%d.%m.%Y %H:%M:%S')}"),
                                   kb=log_new_mess_kb(event.deal.user.username))
            except Exception:
                self.logger.error(f"{Fore.LIGHTRED_EX}При обработке ивента новых отзывов произошла ошибка: {Fore.WHITE}")
                traceback.print_exc()

        async def on_item_paid(plbot: PlayerokBot, event: ItemPaidEvent):
            try:
                if self.config["playerok"]["bot"]["auto_restore_items_enabled"]:
                    await self.restore_last_sold_item(event.deal.item)
            except Exception:
                self.logger.error(f"{Fore.LIGHTRED_EX}При обработке ивента новых сообщений произошла ошибка: {Fore.WHITE}")
                traceback.print_exc()

        async def on_new_problem(plbot: PlayerokBot, event: ItemPaidEvent):
            try:
                self.log_new_problem(event.deal)
                if self.config["playerok"]["bot"]["tg_logging_enabled"] and self.config["playerok"]["bot"]["tg_logging_events"]["new_problem"]:
                    self.log_to_tg(text=log_text(f'🤬 Новая жалоба в <a href="https://playerok.com/deal/{event.deal.id}">сделке</a>', f"<b>Покупатель:</b> {event.deal.user.username}\n<b>Предмет:</b> {event.deal.item.name}"),
                                   kb=log_new_mess_kb(event.deal.user.username))
            except Exception:
                self.logger.error(f"{Fore.LIGHTRED_EX}При обработке ивента новых сообщений произошла ошибка: {Fore.WHITE}")
                traceback.print_exc()

        async def on_deal_status_changed(plbot: PlayerokBot, event: DealStatusChangedEvent):
            try:
                this_chat = event.chat
                if event.deal.user.id != self.playerok_account.id:
                    self.log_deal_status_changed(event.deal)
                    status = "Неизвестный"
                    if event.deal.status is ItemDealStatuses.PAID: status = "Оплачен"
                    elif event.deal.status is ItemDealStatuses.PENDING: status = "В ожидании отправки"
                    elif event.deal.status is ItemDealStatuses.SENT: status = "Продавец подтвердил выполнение"
                    elif event.deal.status is ItemDealStatuses.CONFIRMED: status = "Покупатель подтвердил сделку"
                    elif event.deal.status is ItemDealStatuses.ROLLED_BACK: status = "Возврат"
                    if self.config["playerok"]["bot"]["tg_logging_enabled"] and self.config["playerok"]["bot"]["tg_logging_events"]["deal_status_changed"]:
                        self.log_to_tg(log_text(f'🔄️📋 Статус <a href="https://playerok.com/deal/{event.deal.id}/">сделки</a> изменился', f"<b>Новый статус:</b> {status}"))
                    if event.deal.status is ItemDealStatuses.PENDING:
                        self.send_message(this_chat.id, self.msg("deal_pending", deal_id=event.deal.id, deal_item_name=event.deal.item.name, deal_item_price=event.deal.item.price))
                    if event.deal.status is ItemDealStatuses.SENT:
                        self.send_message(this_chat.id, self.msg("deal_sent", deal_id=event.deal.id, deal_item_name=event.deal.item.name, deal_item_price=event.deal.item.price))
                    if event.deal.status is ItemDealStatuses.CONFIRMED:
                        self.send_message(this_chat.id, self.msg("deal_confirmed", deal_id=event.deal.id, deal_item_name=event.deal.item.name, deal_item_price=event.deal.item.price))
                        self.stats.deals_completed += 1
                        if event.deal.transaction:
                            self.stats.earned_money += round(event.deal.transaction.value or 0, 2)
                    elif event.deal.status is ItemDealStatuses.ROLLED_BACK:
                        self.send_message(this_chat.id, self.msg("deal_confirmed", deal_id=event.deal.id, deal_item_name=event.deal.item.name, deal_item_price=event.deal.item.price))
                        self.stats.deals_refunded += 1
            except Exception:
                self.logger.error(f"{Fore.LIGHTRED_EX}При обработке ивента смены статуса сделки произошла ошибка: {Fore.WHITE}")
                traceback.print_exc()
            
        playerok_event_handlers = get_playerok_event_handlers()
        playerok_event_handlers[EventTypes.NEW_MESSAGE].insert(0, on_new_message)
        playerok_event_handlers[EventTypes.NEW_DEAL].insert(0, on_new_deal)
        playerok_event_handlers[EventTypes.NEW_REVIEW].insert(0, on_new_review)
        playerok_event_handlers[EventTypes.DEAL_STATUS_CHANGED].insert(0, on_deal_status_changed)
        playerok_event_handlers[EventTypes.DEAL_HAS_PROBLEM].insert(0, on_new_problem)
        playerok_event_handlers[EventTypes.ITEM_PAID].insert(0, on_item_paid)
        set_playerok_event_handlers(playerok_event_handlers)

        bot_event_handlers = get_bot_event_handlers()
        def handle_on_playerok_bot_init():
            """ 
            Запускается при инициализации FunPay бота.
            Запускает за собой все хендлеры ON_PLAYEROK_BOT_INIT 
            """
            for handler in bot_event_handlers.get("ON_PLAYEROK_BOT_INIT", []):
                try:
                    handler(self)
                except Exception as e:
                    self.logger.error(f"{Fore.LIGHTRED_EX}Ошибка при обработке хендлера ивента ON_PLAYEROK_BOT_INIT: {Fore.WHITE}{e}")
        handle_on_playerok_bot_init()

        self.logger.info(f"Слушатель событий запущен")
        listener = EventListener(self.playerok_account)

        async_tasks = set()

        for event in listener.listen(requests_delay=self.config["playerok"]["api"]["listener_requests_delay"]):
            playerok_event_handlers = get_playerok_event_handlers() # чтобы каждый раз брать свежие хендлеры, ибо модули могут отключаться/включаться
            if event.type in playerok_event_handlers:
                for handler in playerok_event_handlers[event.type]:
                    task = asyncio.run_coroutine_threadsafe(self.handle(handler, event), loop)
                    async_tasks.add(task)
                    task.add_done_callback(async_tasks.discard)


    async def handle(self, handler, event, *args, **kwargs):
        try:
            await handler(self, event)
        except Exception as e:
            self.logger.error(
                f"{Fore.LIGHTRED_EX}Ошибка при обработке хендлера {handler} в ивенте {event.type.name}: {Fore.WHITE}{e}")