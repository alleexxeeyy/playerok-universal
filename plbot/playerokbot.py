from __future__ import annotations
import asyncio
import time
from datetime import datetime, timedelta
import pytz
from threading import Thread
import textwrap
import shutil
import copy
from colorama import Fore

from playerokapi.account import Account
from playerokapi.enums import *
from playerokapi.types import *
from playerokapi.exceptions import *
from playerokapi.listener.events import *
from playerokapi.listener.listener import EventListener
from playerokapi.types import Chat, Item

from __init__ import ACCENT_COLOR, VERSION
from core.utils import (
    set_title, 
    shutdown, 
    run_async_in_thread
)
from core.handlers import (
    add_bot_event_handler, 
    add_playerok_event_handler, 
    call_bot_event, 
    call_playerok_event
)
from settings import DATA, Settings as sett
from logging import getLogger
from data import Data as data
from tgbot.telegrambot import (
    get_telegram_bot, 
    get_telegram_bot_loop
)
from tgbot.templates import (
    log_text, 
    log_new_mess_kb, 
    log_new_deal_kb
)

from .stats import (
    get_stats, 
    set_stats
)


def get_playerok_bot() -> PlayerokBot | None:
    if hasattr(PlayerokBot, "instance"):
        return getattr(PlayerokBot, "instance")


class PlayerokBot:
    def __new__(cls, *args, **kwargs) -> PlayerokBot:
        if not hasattr(cls, "instance"):
            cls.instance = super(PlayerokBot, cls).__new__(cls)
        return getattr(cls, "instance")

    def __init__(self):
        self.logger = getLogger("universal.playerok")

        self.config = sett.get("config")
        self.messages = sett.get("messages")
        self.custom_commands = sett.get("custom_commands")
        self.auto_deliveries = sett.get("auto_deliveries")
        self.auto_restore_items = sett.get("auto_restore_items")
        self.auto_bump_items = sett.get("auto_bump_items")

        self.initialized_users = data.get("initialized_users")
        self.saved_items = data.get("saved_items")
        self.latest_events_times = data.get("latest_events_times")
        self.stats = get_stats()

        self.account = self.playerok_account = Account(
            token=self.config["playerok"]["api"]["token"],
            user_agent=self.config["playerok"]["api"]["user_agent"],
            requests_timeout=self.config["playerok"]["api"]["requests_timeout"],
            proxy=self.config["playerok"]["api"]["proxy"] or None
        ).get()

        self.__saved_chats: dict[str, Chat] = {}

    def get_chat_by_id(self, chat_id: str) -> Chat:
        if chat_id in self.__saved_chats:
            return self.__saved_chats[chat_id]
        self.__saved_chats[chat_id] = self.account.get_chat(chat_id)
        return self.get_chat_by_id(chat_id)

    def get_chat_by_username(self, username: str) -> Chat:
        if username in self.__saved_chats:
            return self.__saved_chats[username]
        if username.lower() == "поддержка":
            chat = self.account.get_chat(self.account.support_chat_id)
        elif username.lower() == "уведомления":
            chat = self.account.get_chat(self.account.system_chat_id)
        else:
            chat = self.account.get_chat_by_username(username)
        self.__saved_chats[username] = chat
        return self.get_chat_by_username(username)
    
    def refresh_account(self):
        self.account = self.playerok_account = self.account.get()

    def check_banned(self):
        user = self.account.get_user(self.account.id)
        if user.is_blocked:
            self.logger.critical("")
            self.logger.critical(f"{Fore.LIGHTRED_EX}Ваш Playerok аккаунт был заблокирован! К сожалению, я не могу продолжать работу на заблокированном аккаунте...")
            self.logger.critical(f"Напишите в тех. поддержку Playerok, чтобы узнать причину бана и как можно быстрее решить эту проблему.")
            self.logger.critical("")
            shutdown()
    
    def msg(self, message_name: str, messages_config_name: str = "messages", 
            messages_data: dict = DATA, **kwargs) -> str | None:
        class SafeDict(dict):
            def __missing__(self, key):
                return "{" + key + "}"

        messages = sett.get(messages_config_name, messages_data) or {}
        mess = messages.get(message_name, {})
        if not mess.get("enabled"):
            return None
        message_lines: list[str] = mess.get("text", [])
        if not message_lines:
            return f"Сообщение {message_name} пустое"
        try:
            msg = "\n".join([line.format_map(SafeDict(**kwargs)) for line in message_lines])
            return msg
        except:
            pass
        return f"Не удалось получить сообщение {message_name}"
    
    def _event_datetime(self, event: str):
        if self.latest_events_times[event]:
            return (
                datetime.fromisoformat(self.latest_events_times[event]) 
                + timedelta(seconds=self.config["playerok"][event]["interval"])
            )
        else:
            return datetime.now()


    def send_message(self, chat_id: str, text: str | None = None, photo_file_path: str | None = None,
                     mark_chat_as_read: bool = None, exclude_watermark: bool = False, max_attempts: int = 3) -> ChatMessage:
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

        :param exclude_watermark: Пропустить и не использовать водяной знак под сообщением?
        :type exclude_watermark: `bool`

        :return: Объект отправленного сообщения.
        :rtype: `PlayerokAPI.types.ChatMessage`
        """
        if not text and not photo_file_path:
            return None
        for _ in range(max_attempts):
            try:
                if (
                    text
                    and self.config["playerok"]["watermark"]["enabled"]
                    and self.config["playerok"]["watermark"]["value"]
                    and not exclude_watermark
                ):
                    text += f"\n{self.config['playerok']['watermark']['value']}"
                mark_chat_as_read = (self.config["playerok"]["read_chat"]["enabled"] or False) if mark_chat_as_read is None else mark_chat_as_read
                mess = self.account.send_message(chat_id, text, photo_file_path, mark_chat_as_read)
                return mess
            except Exception as e:
                if text: msg = text.replace('\n', ' ').strip()
                else: msg = photo_file_path
                self.logger.error(f"{Fore.LIGHTRED_EX}Ошибка при отправке сообщения {Fore.LIGHTWHITE_EX}«{msg}» {Fore.LIGHTRED_EX}в чат {Fore.LIGHTWHITE_EX}{chat_id} {Fore.LIGHTRED_EX}: {Fore.WHITE}{e}")
                return
        if text: msg = text.replace('\n', ' ').strip()
        else: msg = photo_file_path
        self.logger.error(f"{Fore.LIGHTRED_EX}Не удалось отправить сообщение {Fore.LIGHTWHITE_EX}«{msg}» {Fore.LIGHTRED_EX}в чат {Fore.LIGHTWHITE_EX}{chat_id}")

    def _serealize_item(self, item: ItemProfile) -> dict:
        return {
            "id": item.id,
            "slug": item.slug,
            "priority": item.priority.name if item.priority else None,
            "status": item.status.name if item.status else None,
            "name": item.name,
            "price": item.price,
            "raw_price": item.raw_price,
            "seller_type": item.seller_type.name if item.seller_type else None,
            "attachment": {
                "id": item.attachment.id,
                "url": item.attachment.url,
                "filename": item.attachment.filename,
                "mime": item.attachment.mime,
            },
            "user": {
                "id": item.user.id,
                "username": item.user.username,
                "role": item.user.role.name if item.user.role else None,
                "avatar_url": item.user.avatar_url,
                "is_online": item.user.is_online,
                "is_blocked": item.user.is_blocked,
                "rating": item.user.rating,
                "reviews_count": item.user.reviews_count,
                "support_chat_id": item.user.support_chat_id,
                "system_chat_id": item.user.system_chat_id,
                "created_at": item.user.created_at
            },
            "approval_date": item.approval_date,
            "priority_position": item.priority_position,
            "views_counter": item.views_counter,
            "fee_multiplier": item.fee_multiplier,
            "created_at": item.created_at
        }
    
    def _deserealize_item(self, item_data: dict) -> ItemProfile:
        item_data = copy.deepcopy(item_data)
        user_data = item_data.pop("user")
        user_data["role"] = UserTypes.__members__.get(user_data["role"]) if user_data["role"] else None
        user = UserProfile(**user_data)
        user.__account = self.account
        item_data["user"] = user
        
        attachment_data = item_data.pop("attachment")
        attachment = FileObject(**attachment_data)
        item_data["attachment"] = attachment

        item_data["priority"] = PriorityTypes.__members__.get(item_data["priority"]) if item_data["priority"] else None
        item_data["status"] = ItemStatuses.__members__.get(item_data["status"]) if item_data["status"] else None
        item_data["seller_type"] = UserTypes.__members__.get(item_data["seller_type"]) if item_data["seller_type"] else None

        item = ItemProfile(**item_data)
        return item

    def get_my_items(
        self, 
        count: int = -1, 
        game_id: str | None = None, 
        category_id: str | None = None,
        statuses: list[ItemStatuses] | None = None
    ) -> list[ItemProfile]:
        """
        Получает все предметы аккаунта.

        :param count: Кол-во предеметов, которые нужно получить (не более 24 за один запрос) или -1, если нужно получить все, _опционально_.
        :type count: `int`

        :param game_id: ID игры/приложения, чьи предметы нужно получить, _опционально_.
        :type game_id: `str` or `None`

        :param category_id: ID категории игры/приложения, чьи предметы нужно получить, _опционально_.
        :type category_id: `str` or `None`

        :param statuses: Массив статусов предметов, которые нужно получить. Некоторые статусы можно получить только, если это профиль вашего аккаунта. Если не указано, получает сразу все возможные.
        :type statuses: `list[playerokapi.enums.ItemStatuses]` or `None`

        :return: Массив предметов профиля.
        :rtype: `list` of `playerokapi.types.ItemProfile`
        """
        my_items: list[ItemProfile] = []
        svd_items: list[dict] = []
        
        try:
            user = self.account.get_user(self.account.id)
            next_cursor = None

            while True:
                itm_list = user.get_items(
                    after_cursor=next_cursor, 
                    game_id=game_id, 
                    category_id=category_id
                )
                
                for itm in itm_list.items:
                    svd_items.append(self._serealize_item(itm))
                    
                    if statuses is None or itm.status in statuses:
                        my_items.append(itm)
                        if len(my_items) >= count and count != -1:
                            return my_items
                
                if not itm_list.page_info.has_next_page:
                    break
                next_cursor = itm_list.page_info.end_cursor
                time.sleep(0.5)
            
            self.saved_items = svd_items
        except (RequestError, RequestFailedError):
            for itm_dict in list(self.saved_items):
                itm = self._deserealize_item(itm_dict)
                
                if statuses is None or itm.status in statuses:
                    my_items.append(itm)
                    if len(my_items) >= count and count != -1:
                        return my_items

            if not my_items: 
                raise
            
        return my_items


    def bump_item(self, item: ItemProfile | MyItem):
        try:
            included = any(
                any(
                    phrase.lower() in item.name.lower()
                    or item.name.lower() == phrase.lower()
                    for phrase in included_item
                )
                for included_item in self.auto_bump_items["included"]
            )
            excluded = any(
                any(
                    phrase.lower() in item.name.lower()
                    or item.name.lower() == phrase.lower()
                    for phrase in excluded_item
                )
                for excluded_item in self.auto_bump_items["excluded"]
            )

            if (
                self.config["playerok"]["auto_bump_items"]["all"]
                and not excluded
            ) or (
                not self.config["playerok"]["auto_bump_items"]["all"]
                and included
            ):
                if not isinstance(item, MyItem):
                    try: item = self.account.get_item(item.id)
                    except: return
                    
                time.sleep(1)
                
                statuses: list[ItemPriorityStatus] = self.playerok_account.get_item_priority_statuses(item.id, item.raw_price)
                try: 
                    prem_status = [
                        status for status in statuses 
                        if status.type == PriorityTypes.PREMIUM
                        or status.price > 0
                    ][0]
                except: 
                    raise Exception("PREMIUM статус не найден")
                
                time.sleep(1)
                self.playerok_account.increase_item_priority_status(item.id, prem_status.id)
                    
                sequence = item.sequence
                item_name_frmtd = item.name[:32] + ("..." if len(item.name) > 32 else "")
                self.logger.info(
                    f"{Fore.LIGHTWHITE_EX}«{item_name_frmtd}» {Fore.WHITE}— {Fore.YELLOW}поднят. "
                    f"{Fore.WHITE}Позиция: {Fore.LIGHTWHITE_EX}{sequence} {Fore.WHITE}→ {Fore.YELLOW}1"
                )
        except Exception as e:
            self.logger.error(f"{Fore.LIGHTRED_EX}Ошибка при поднятии предмета «{item.name}»: {Fore.WHITE}{e}")

    def bump_items(self): 
        self.latest_events_times["auto_bump_items"] = datetime.now().isoformat()
        data.set("latest_events_times", self.latest_events_times)

        try:
            items = self.get_my_items(statuses=[ItemStatuses.APPROVED])
            
            for item in items:
                if item.priority == PriorityTypes.PREMIUM:
                    self.bump_item(item)
        except Exception as e:
            self.logger.error(f"{Fore.LIGHTRED_EX} Ошибка при поднятии предметов: {Fore.WHITE}{e}")

    def restore_item(self, item: Item | MyItem | ItemProfile):
        try:
            included = any(
                any(
                    phrase.lower() in item.name.lower()
                    or item.name.lower() == phrase.lower()
                    for phrase in included_item
                )
                for included_item in self.auto_restore_items["included"]
            )
            excluded = any(
                any(
                    phrase.lower() in item.name.lower()
                    or item.name.lower() == phrase.lower()
                    for phrase in excluded_item
                )
                for excluded_item in self.auto_restore_items["excluded"]
            )

            if (
                self.config["playerok"]["auto_restore_items"]["all"]
                and not excluded
            ) or (
                not self.config["playerok"]["auto_restore_items"]["all"]
                and included
            ):
                if not isinstance(item, MyItem):
                    try: item = self.account.get_item(item.id)
                    except: return
                    
                time.sleep(1)

                priority_statuses = self.account.get_item_priority_statuses(item.id, item.raw_price)
                try: 
                    priority_status = [
                        status for status in priority_statuses 
                        if status.type == PriorityTypes.DEFAULT 
                        or status.price == 0
                    ][0]
                except: 
                    priority_status = [status for status in priority_statuses][0]

                time.sleep(1)
                new_item = self.account.publish_item(item.id, priority_status.id)
                
                item_name_frmtd = item.name[:32] + ("..." if len(item.name) > 32 else "")
                
                if new_item.status in (ItemStatuses.PENDING_APPROVAL, ItemStatuses.APPROVED):
                    self.logger.info(f"{Fore.LIGHTWHITE_EX}«{item_name_frmtd}» {Fore.WHITE}— {Fore.YELLOW}товар восстановлен")
                else:
                    self.logger.error(f"{Fore.LIGHTRED_EX}Не удалось восстановить предмет «{item_name_frmtd}». Его статус: {Fore.WHITE}{new_item.status.name}")
        except Exception as e:
            self.logger.error(f"{Fore.LIGHTRED_EX}Ошибка при восстановлении предмета «{item.name}»: {Fore.WHITE}{e}")
            
    def restore_expired_items(self):
        try:
            restored_items = []
            items = self.get_my_items(statuses=[ItemStatuses.EXPIRED])
            
            for item in items:
                if item.id in restored_items:
                    continue
                restored_items.append(item.id)
                
                time.sleep(0.5)
                self.restore_item(item)
        except Exception as e:
            self.logger.error(f"{Fore.LIGHTRED_EX}Ошибка при восстановлении истёкших предметов: {Fore.WHITE}{e}")

    def request_withdrawal(self) -> bool:
        balance = "?"
        try:
            self.account = self.account.get()
            balance = self.account.profile.balance.withdrawable
            if balance <= 500:
                raise Exception("Слишком маленький баланс. Транзакция должна быть на сумму от 500₽")
            
            if self.config["playerok"]["auto_withdrawal"]["credentials_type"] == "card":
                provider = TransactionProviderIds.BANK_CARD_RU
                account = self.config["playerok"]["auto_withdrawal"]["card_id"]
                sbp_bank_member_id = None
            elif self.config["playerok"]["auto_withdrawal"]["credentials_type"] == "sbp":
                provider = TransactionProviderIds.SBP
                account = self.config["playerok"]["auto_withdrawal"]["sbp_phone_number"]
                sbp_bank_member_id = self.config["playerok"]["auto_withdrawal"]["sbp_bank_id"]
            
            self.account.request_withdrawal(
                provider=provider,
                account=account,
                value=balance,
                sbp_bank_member_id=sbp_bank_member_id
            )
            
            self.logger.info(f"{Fore.LIGHTWHITE_EX}{balance}₽ {Fore.WHITE}— {Fore.YELLOW}транзакция на вывод создана")
            return True
        except Exception as e:
            self.logger.error(f"{Fore.LIGHTRED_EX}Ошибка при создании транзакции на вывод {balance}₽: {Fore.WHITE}{e}")
        return False


    def log_new_message(self, message: ChatMessage, chat: Chat):
        plbot = get_playerok_bot()
        try: chat_user = [user.username for user in chat.users if user.id != plbot.account.id][0]
        except: chat_user = message.user.username
        ch_header = f"Новое сообщение в чате с {chat_user}:"
        self.logger.info(f"{ACCENT_COLOR}{ch_header.replace(chat_user, f'{Fore.LIGHTCYAN_EX}{chat_user}')}")
        self.logger.info(f"{ACCENT_COLOR}│ {Fore.LIGHTWHITE_EX}{message.user.username}:")
        max_width = shutil.get_terminal_size((80, 20)).columns - 40
        longest_line_len = 0
        text = ""
        if message.text is not None: text = message.text
        elif message.file is not None: text = f"{Fore.LIGHTMAGENTA_EX}Изображение {Fore.WHITE}({message.file.url})"
        for raw_line in text.split("\n"):
            if not raw_line.strip():
                self.logger.info(f"{ACCENT_COLOR}│")
                continue
            wrapped_lines = textwrap.wrap(raw_line, width=max_width)
            for wrapped in wrapped_lines:
                self.logger.info(f"{ACCENT_COLOR}│ {Fore.WHITE}{wrapped}")
                longest_line_len = max(longest_line_len, len(wrapped.strip()))
        underline_len = max(len(ch_header)-1, longest_line_len+2)
        self.logger.info(f"{ACCENT_COLOR}└{'─'*underline_len}")

    def log_new_deal(self, deal: ItemDeal):
        self.logger.info(f"{Fore.YELLOW}───────────────────────────────────────")
        self.logger.info(f"{Fore.YELLOW}Новая сделка {deal.id}:")
        self.logger.info(f" · Покупатель: {Fore.LIGHTWHITE_EX}{deal.user.username}")
        self.logger.info(f" · Товар: {Fore.LIGHTWHITE_EX}{deal.item.name}")
        self.logger.info(f" · Сумма: {Fore.LIGHTWHITE_EX}{deal.item.price}₽")
        self.logger.info(f"{Fore.YELLOW}───────────────────────────────────────")

    def log_new_review(self, deal: ItemDeal):
        self.logger.info(f"{Fore.YELLOW}───────────────────────────────────────")
        self.logger.info(f"{Fore.YELLOW}Новый отзыв по сделке {deal.id}:")
        self.logger.info(f" · Оценка: {Fore.LIGHTYELLOW_EX}{'★' * deal.review.rating or 5} ({deal.review.rating or 5})")
        self.logger.info(f" · Текст: {Fore.LIGHTWHITE_EX}{deal.review.text}")
        self.logger.info(f" · Оставил: {Fore.LIGHTWHITE_EX}{deal.review.creator.username}")
        self.logger.info(f" · Дата: {Fore.LIGHTWHITE_EX}{datetime.fromisoformat(deal.review.created_at).strftime('%d.%m.%Y %H:%M:%S')}")
        self.logger.info(f"{Fore.YELLOW}───────────────────────────────────────")

    def log_deal_status_changed(self, deal: ItemDeal, status_frmtd: str = "Неизвестный"):
        self.logger.info(f"{Fore.WHITE}───────────────────────────────────────")
        self.logger.info(f"{Fore.WHITE}Статус сделки {Fore.LIGHTWHITE_EX}{deal.id} {Fore.WHITE}изменился:")
        self.logger.info(f" · Статус: {Fore.LIGHTWHITE_EX}{status_frmtd}")
        self.logger.info(f" · Покупатель: {Fore.LIGHTWHITE_EX}{deal.user.username}")
        self.logger.info(f" · Товар: {Fore.LIGHTWHITE_EX}{deal.item.name}")
        self.logger.info(f" · Сумма: {Fore.LIGHTWHITE_EX}{deal.item.price}₽")
        self.logger.info(f"{Fore.WHITE}───────────────────────────────────────")

    def log_new_problem(self, deal: ItemDeal):
        self.logger.info(f"{Fore.YELLOW}───────────────────────────────────────")
        self.logger.info(f"{Fore.YELLOW}Новая жалоба в сделке {deal.id}:")
        self.logger.info(f" · Оставил: {Fore.LIGHTWHITE_EX}{deal.user.username}")
        self.logger.info(f" · Товар: {Fore.LIGHTWHITE_EX}{deal.item.name}")
        self.logger.info(f" · Сумма: {Fore.LIGHTWHITE_EX}{deal.item.price}₽")
        self.logger.info(f"{Fore.YELLOW}───────────────────────────────────────")


    async def _on_playerok_bot_init(self):
        self.stats.bot_launch_time = datetime.now()

        def endless_loop():
            while True:
                balance = self.account.profile.balance.value if self.account.profile.balance is not None else "?"
                set_title(f"Playerok Universal v{VERSION} | {self.account.username}: {balance}₽")
                if self.stats != get_stats(): set_stats(self.stats)
                if data.get("initialized_users") != self.initialized_users: data.set("initialized_users", self.initialized_users)
                if data.get("saved_items") != self.saved_items: data.set("saved_items", self.saved_items)
                if data.get("latest_events_times") != self.latest_events_times: data.set("latest_events_times", self.latest_events_times)
                if sett.get("config") != self.config: self.config = sett.get("config")
                if sett.get("messages") != self.messages: self.messages = sett.get("messages")
                if sett.get("custom_commands") != self.custom_commands: self.custom_commands = sett.get("custom_commands")
                if sett.get("auto_deliveries") != self.auto_deliveries: self.auto_deliveries = sett.get("auto_deliveries")
                if sett.get("auto_restore_items") != self.auto_restore_items: self.auto_restore_items = sett.get("auto_restore_items")
                if sett.get("auto_bump_items") != self.auto_bump_items: self.auto_bump_items = sett.get("auto_bump_items")
                time.sleep(3)

        def refresh_account_loop():
            while True:
                time.sleep(1800)
                self.refresh_account()

        def check_banned_loop():
            while True:
                self.check_banned()
                time.sleep(900)

        def restore_expired_items_loop():
            while True:
                if self.config["playerok"]["auto_restore_items"]["expired"]:
                    self.restore_expired_items()
                time.sleep(45)

        def bump_items_loop():
            while True:
                if (
                    self.config["playerok"]["auto_bump_items"]["enabled"]
                    and datetime.now() >= self._event_datetime("auto_bump_items")
                ):
                    self.bump_items()
                time.sleep(3)

        def withdrawal_loop():
            while True:
                if (
                    self.config["playerok"]["auto_withdrawal"]["enabled"]
                    and datetime.now() >= self._event_datetime("auto_withdrawal")
                ):
                    self.request_withdrawal()
                time.sleep(3)

        Thread(target=endless_loop, daemon=True).start()
        Thread(target=refresh_account_loop, daemon=True).start()
        Thread(target=check_banned_loop, daemon=True).start()
        Thread(target=restore_expired_items_loop, daemon=True).start()
        Thread(target=bump_items_loop, daemon=True).start()
        Thread(target=withdrawal_loop, daemon=True).start()

    async def _on_new_message(self, event: NewMessageEvent):
        if event.message.user is None:
            return
        self.log_new_message(event.message, event.chat)
        if event.message.user.id == self.account.id:
            return

        is_support_chat = event.chat.id in (self.account.system_chat_id, self.account.support_chat_id)
        if (
            self.config["playerok"]["tg_logging"]["enabled"]
            and (self.config["playerok"]["tg_logging"]["events"]["new_user_message"] 
            or self.config["playerok"]["tg_logging"]["events"]["new_system_message"])
        ):
            do = False
            if (
                self.config["playerok"]["tg_logging"]["events"]["new_user_message"] 
                and not is_support_chat
            ) or (
                self.config["playerok"]["tg_logging"]["events"]["new_system_message"] 
                and is_support_chat
            ): 
                do = True 
            
            if do:
                text = f"<b>{event.message.user.username}:</b> "
                text += event.message.text or ""
                text += f'<b><a href="{event.message.file.url}">{event.message.file.filename}</a></b>' if event.message.file else ""
                asyncio.run_coroutine_threadsafe(
                    get_telegram_bot().log_event(
                        text=log_text(
                            title=f'💬 Новое сообщение в <a href="https://playerok.com/chats/{event.chat.id}">чате</a>', 
                            text=text.strip()
                        ),
                        kb=log_new_mess_kb(event.message.user.username)
                    ), 
                    get_telegram_bot_loop()
                )

        if (
            not is_support_chat
            and event.message.text is not None
        ):
            if event.message.user.id not in self.initialized_users:
                self.initialized_users.append(event.message.user.id)
        
            if str(event.message.text).lower() in ("!команды", "!commands"):
                self.send_message(event.chat.id, self.msg("cmd_commands"))
            elif str(event.message.text).lower() in ("!продавец", "!seller"):
                asyncio.run_coroutine_threadsafe(
                    get_telegram_bot().call_seller(event.message.user.username, event.chat.id), 
                    get_telegram_bot_loop()
                )
                self.send_message(event.chat.id, self.msg("cmd_seller"))
            elif self.config["playerok"]["custom_commands"]["enabled"]:
                if event.message.text.lower() in [key.lower() for key in self.custom_commands.keys()]:
                    msg = "\n".join(self.custom_commands[event.message.text])
                    self.send_message(event.chat.id, msg)

    async def _on_new_review(self, event: NewReviewEvent):
        if event.deal.user.id == self.account.id:
            return
        
        self.log_new_review(event.deal)
        if (
            self.config["playerok"]["tg_logging"]["enabled"] 
            and self.config["playerok"]["tg_logging"]["events"]["new_review"]
        ):
            asyncio.run_coroutine_threadsafe(
                get_telegram_bot().log_event(
                    text=log_text(
                        title=f'💬✨ Новый отзыв по <a href="https://playerok.com/deal/{event.deal.id}">сделке</a>', 
                        text=f"<b>Оценка:</b> {'⭐' * event.deal.review.rating}\n<b>Оставил:</b> {event.deal.review.creator.username}\n<b>Текст:</b> {event.deal.review.text}\n<b>Дата:</b> {datetime.fromisoformat(event.deal.review.created_at).strftime('%d.%m.%Y %H:%M:%S')}"
                    ),
                    kb=log_new_mess_kb(event.deal.user.username)
                ), 
                get_telegram_bot_loop()
            )

        self.send_message(event.chat.id, self.msg(
            "new_review", 
            deal_id=event.deal.id, 
            deal_item_name=event.deal.item.name, 
            deal_item_price=event.deal.item.price,
            review_rating=event.deal.review.rating
        ))

    async def _on_new_problem(self, event: ItemPaidEvent):
        if event.deal.user.id == self.account.id:
            return

        self.log_new_problem(event.deal)
        if (
            self.config["playerok"]["tg_logging"]["enabled"] 
            and self.config["playerok"]["tg_logging"]["events"]["new_problem"]
        ):
            asyncio.run_coroutine_threadsafe(
                get_telegram_bot().log_event(
                    text=log_text(
                        title=f'🤬 Новая жалоба в <a href="https://playerok.com/deal/{event.deal.id}">сделке</a>', 
                        text=f"<b>Покупатель:</b> {event.deal.user.username}\n<b>Предмет:</b> {event.deal.item.name}"
                    ),
                    kb=log_new_mess_kb(event.deal.user.username)
                ), 
                get_telegram_bot_loop()
            )

    async def _on_new_deal(self, event: NewDealEvent):
        if event.deal.user.id == self.account.id:
            return
        try: event.deal.item = self.account.get_item(event.deal.item.id)
        except: pass
        
        self.log_new_deal(event.deal)
        if (
            self.config["playerok"]["tg_logging"]["enabled"] 
            and self.config["playerok"]["tg_logging"]["events"]["new_deal"]
        ):
            asyncio.run_coroutine_threadsafe(
                get_telegram_bot().log_event(
                    text=log_text(
                        title=f'📋 Новая <a href="https://playerok.com/deal/{event.deal.id}">сделка</a>', 
                        text=f"<b>Покупатель:</b> {event.deal.user.username}\n<b>Предмет:</b> {(event.deal.item.name or '-')}\n<b>Сумма:</b> {event.deal.item.price or '?'}₽"
                    ),
                    kb=log_new_deal_kb(event.deal.user.username, event.deal.id)
                ), 
                get_telegram_bot_loop()
            )

        self.send_message(event.chat.id, self.msg("new_deal", deal_item_name=(event.deal.item.name or "-"), deal_item_price=event.deal.item.price))
        
        is_support_chat = event.chat.id in (self.account.system_chat_id, self.account.support_chat_id)
        if (
            event.deal.user.id not in self.initialized_users
            and not is_support_chat
        ):
            self.send_message(event.chat.id, self.msg("first_message", username=event.deal.user.username))
            self.initialized_users.append(event.deal.user.id)
                
        if self.config["playerok"]["auto_deliveries"]["enabled"]:
            for auto_delivery in self.auto_deliveries:
                for phrase in auto_delivery["keyphrases"]:
                    if phrase.lower() in (event.deal.item.name or "").lower() or (event.deal.item.name or "").lower() == phrase.lower():
                        self.send_message(event.chat.id, "\n".join(auto_delivery["message"]))
                        break
        if self.config["playerok"]["auto_complete_deals"]["enabled"]:
            self.account.update_deal(event.deal.id, ItemDealStatuses.SENT)

    async def _on_item_paid(self, event: ItemPaidEvent):
        if event.deal.user.id == self.account.id:
            return
        
        if self.config["playerok"]["auto_restore_items"]["sold"]:
            if not event.deal.item.name:
                event.deal.item = self.account.get_item(event.deal.item.id)
                time.sleep(1)
            for _ in range(3):
                try: 
                    items = self.get_my_items(count=6, statuses=[ItemStatuses.SOLD])
                    item = [it for it in items if it.name == event.deal.item.name][0]
                    break
                except: 
                    time.sleep(4)
            else:
                return
            self.restore_item(item)
                
        

    async def _on_deal_status_changed(self, event: DealStatusChangedEvent):
        if event.deal.user.id == self.account.id:
            return
        
        status_frmtd = "Неизвестный"
        if event.deal.status is ItemDealStatuses.PAID: status_frmtd = "Оплачен"
        elif event.deal.status is ItemDealStatuses.PENDING: status_frmtd = "В ожидании отправки"
        elif event.deal.status is ItemDealStatuses.SENT: status_frmtd = "Продавец подтвердил выполнение"
        elif event.deal.status is ItemDealStatuses.CONFIRMED: status_frmtd = "Покупатель подтвердил сделку"
        elif event.deal.status is ItemDealStatuses.ROLLED_BACK: status_frmtd = "Возврат"

        self.log_deal_status_changed(event.deal, status_frmtd)
        if (
            self.config["playerok"]["tg_logging"]["enabled"] 
            and self.config["playerok"]["tg_logging"]["events"]["deal_status_changed"]
        ):
            asyncio.run_coroutine_threadsafe(
                get_telegram_bot().log_event(
                    log_text(
                        title=f'🔄️📋 Статус <a href="https://playerok.com/deal/{event.deal.id}/">сделки</a> изменился', 
                        text=f"<b>Новый статус:</b> {status_frmtd}"
                    )
                ), 
                get_telegram_bot_loop()
            )

        if event.deal.status is ItemDealStatuses.PENDING:
            self.send_message(event.chat.id, self.msg(
                "deal_pending", 
                deal_id=event.deal.id, 
                deal_item_name=event.deal.item.name, 
                deal_item_price=event.deal.item.price
            ))
        if event.deal.status is ItemDealStatuses.SENT:
            self.send_message(event.chat.id, self.msg(
                "deal_sent", 
                deal_id=event.deal.id, 
                deal_item_name=event.deal.item.name, 
                deal_item_price=event.deal.item.price
            ))
        if event.deal.status is ItemDealStatuses.CONFIRMED:
            self.send_message(event.chat.id, self.msg(
                "deal_confirmed", 
                deal_id=event.deal.id, 
                deal_item_name=event.deal.item.name, 
                deal_item_price=event.deal.item.price
            ))
            self.stats.deals_completed += 1
            if not event.deal.transaction:
                event.deal = self.account.get_deal(event.deal.id)
            self.stats.earned_money += round(getattr(event.deal.transaction, "value") or 0, 2)
        elif event.deal.status is ItemDealStatuses.ROLLED_BACK:
            self.send_message(event.chat.id, self.msg(
                "deal_refunded", 
                deal_id=event.deal.id, 
                deal_item_name=event.deal.item.name, 
                deal_item_price=event.deal.item.price
            ))
            self.stats.deals_refunded += 1


    async def run_bot(self):
        self.logger.info("")
        self.logger.info(f"{ACCENT_COLOR}───────────────────────────────────────")
        self.logger.info(f"{ACCENT_COLOR}Информация об аккаунте:")
        self.logger.info(f" · ID: {Fore.LIGHTWHITE_EX}{self.account.id}")
        self.logger.info(f" · Никнейм: {Fore.LIGHTWHITE_EX}{self.account.username}")
        if self.playerok_account.profile.balance:
            self.logger.info(f" · Баланс: {Fore.LIGHTWHITE_EX}{self.account.profile.balance.value}₽")
            self.logger.info(f"   · Доступно: {Fore.LIGHTWHITE_EX}{self.account.profile.balance.available}₽")
            self.logger.info(f"   · В ожидании: {Fore.LIGHTWHITE_EX}{self.account.profile.balance.pending_income}₽")
            self.logger.info(f"   · Заморожено: {Fore.LIGHTWHITE_EX}{self.account.profile.balance.frozen}₽")
        self.logger.info(f" · Активные продажи: {Fore.LIGHTWHITE_EX}{self.account.profile.stats.deals.outgoing.total - self.account.profile.stats.deals.outgoing.finished}")
        self.logger.info(f" · Активные покупки: {Fore.LIGHTWHITE_EX}{self.account.profile.stats.deals.incoming.total - self.account.profile.stats.deals.incoming.finished}")
        self.logger.info(f"{ACCENT_COLOR}───────────────────────────────────────")
        self.logger.info("")
        if self.config["playerok"]["api"]["proxy"]:
            user, password = self.config["playerok"]["api"]["proxy"].split("@")[0].split(":") if "@" in self.config["playerok"]["api"]["proxy"] else self.config["playerok"]["api"]["proxy"]
            ip, port = self.config["playerok"]["api"]["proxy"].split("@")[1].split(":") if "@" in self.config["playerok"]["api"]["proxy"] else self.config["playerok"]["api"]["proxy"]
            ip = ".".join([("*" * len(nums)) if i >= 3 else nums for i, nums in enumerate(ip.split("."), start=1)])
            port = f"{port[:3]}**"
            user = f"{user[:3]}*****" if user else "Без авторизации"
            password = f"{password[:3]}*****" if password else "Без авторизации"
            self.logger.info(f"{ACCENT_COLOR}───────────────────────────────────────")
            self.logger.info(f"{ACCENT_COLOR}Информация о прокси:")
            self.logger.info(f" · IP: {Fore.LIGHTWHITE_EX}{ip}:{port}")
            self.logger.info(f" · Юзер: {Fore.LIGHTWHITE_EX}{user}")
            self.logger.info(f" · Пароль: {Fore.LIGHTWHITE_EX}{password}")
            self.logger.info(f"{ACCENT_COLOR}───────────────────────────────────────")
            self.logger.info("")

        add_bot_event_handler("ON_PLAYEROK_BOT_INIT", PlayerokBot._on_playerok_bot_init, 0)
        add_playerok_event_handler(EventTypes.NEW_MESSAGE, PlayerokBot._on_new_message, 0)
        add_playerok_event_handler(EventTypes.NEW_REVIEW, PlayerokBot._on_new_review, 0)
        add_playerok_event_handler(EventTypes.DEAL_HAS_PROBLEM, PlayerokBot._on_new_problem, 0)
        add_playerok_event_handler(EventTypes.NEW_DEAL, PlayerokBot._on_new_deal, 0)
        add_playerok_event_handler(EventTypes.ITEM_PAID, PlayerokBot._on_item_paid, 0)
        add_playerok_event_handler(EventTypes.DEAL_STATUS_CHANGED, PlayerokBot._on_deal_status_changed, 0)

        async def listener_loop():
            listener = EventListener(self.account)
            for event in listener.listen():
                await call_playerok_event(event.type, [self, event])

        run_async_in_thread(listener_loop)
        self.logger.info(f"{Fore.YELLOW}Playerok бот запущен и активен")

        await call_bot_event("ON_PLAYEROK_BOT_INIT", [self])