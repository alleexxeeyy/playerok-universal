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
    log_new_deal_kb,
    log_new_problem_kb,
    log_item_kb,
    log_deal_kb,
    log_transaction_kb,
    destroy_kb
)

from .msg_types import (
    msg_account,
    msg_user_from_chat,
    msg_item,
    msg_deal,
    msg_chat
)


logger = getLogger("universal.playerok")


def get_playerok_bot() -> PlayerokBot | None:
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
        self.auto_restore_items = sett.get("auto_restore_items")
        self.auto_complete_deals = sett.get("auto_complete_deals")
        self.auto_bump_items = sett.get("auto_bump_items")

        self.initialized_users = data.get("initialized_users")
        self.saved_items = data.get("saved_items")
        self.cached_orders = data.get("cached_orders")

        self.account = self.playerok_account = Account(
            cookies=self.config["playerok"]["api"]["cookies"],
            user_agent=self.config["playerok"]["api"]["user_agent"],
            proxy=self.config["playerok"]["api"]["proxy"] or None,
            requests_timeout=self.config["playerok"]["api"]["requests_timeout"]
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
        try: 
            self.account = self.playerok_account = self.account.get()
        except Exception as e:
            logger.error(f"{Fore.LIGHTRED_EX}Ошибка при обновлении аккаунта: {Fore.WHITE}{e}")

    def check_banned(self):
        try:
            user = self.account.get_user(self.account.id)
            if user.is_blocked:
                logger.critical("")
                logger.critical(f"{Fore.LIGHTRED_EX}Ваш Playerok аккаунт был заблокирован! К сожалению, я не могу продолжать работу на заблокированном аккаунте...")
                logger.critical(f"Напишите в тех. поддержку Playerok, чтобы узнать причину бана и как можно быстрее решить эту проблему.")
                logger.critical("")
                shutdown()
        except Exception as e:
            logger.error(f"{Fore.LIGHTRED_EX}Ошибка при проверке на блокировку: {Fore.WHITE}{e}")

    def _format_msg_text(self, text: str, **kwargs):

        class SafeDict(dict):
            def __missing__(self, key):
                if "." in key:
                    parts = key.split(".")
                    obj = self.get(parts[0])
                    if obj is None:
                        return "{" + key + "}"
                    try:
                        for part in parts[1:]:
                            obj = getattr(obj, part) if hasattr(obj, part) else obj[part]
                        return obj
                    except (AttributeError, KeyError, TypeError):
                        return "{" + key + "}"
                return "{" + key + "}"
            
        return text.format_map(SafeDict(**kwargs))

    def msg(self, message_name: str, messages_config_name: str = "messages", 
            messages_data: dict = DATA, **kwargs) -> str | None:
        kwargs["account"] = msg_account(self.account.profile)

        messages = sett.get(messages_config_name, messages_data) or {}
        mess = messages.get(message_name, {})
        if not mess.get("enabled"):
            return None
        
        message_lines: list[str] = mess.get("text", [])
        if not message_lines:
            return f"Сообщение {message_name} пустое"
        
        try:
            msg = self._format_msg_text("\n".join(message_lines), **kwargs)
            return msg
        except:
            pass
        
        return f"Не удалось получить сообщение {message_name}"
        
    def _do_call_event(self, last_time, interval):
        if not last_time:
            return True
        
        if datetime.now() >= (
            datetime.fromisoformat(last_time) 
            + timedelta(seconds=interval)
        ):
            return True
        
        return False


    def send_message(self, chat_id: str, text: str | None = None, images: list[str | bytes] = [],
                     mark_chat_as_read: bool = None, exclude_watermark: bool = False, max_attempts: int = 3) -> ChatMessage | None:
        """
        Кастомный метод отправки сообщения в чат Playerok.
        Пытается отправить за N попыток, если не удалось - выдаёт ошибку в консоль.
        """
        
        if not any((text, images)): 
            return
        
        for _ in range(max_attempts):
            try:
                read_chat_enabled = self.config["playerok"]["read_chat"]
                watermark_enabled = self.config["playerok"]["watermark"]["enabled"]
                watermark = self.config["playerok"]["watermark"]["value"]
                
                if text and watermark_enabled and watermark and not exclude_watermark:
                    text += f"\n{watermark}"
                
                mark_chat_as_read = (read_chat_enabled or False) if mark_chat_as_read is None else mark_chat_as_read
                mess = self.account.send_message(
                    chat_id=chat_id, 
                    text=text, 
                    images=images, 
                    mark_chat_as_read=mark_chat_as_read
                )
                
                return mess
            except Exception as e:
                err = e
        else:
            err = "Не удалось отправить сообщение"
        
        msg = ""
        if text: 
            msg += text.replace('\n', ' ').strip()
        if images:
            msg += f", Изображения ({len(images)})"
        
        logger.error(
            f"{Fore.LIGHTRED_EX}Ошибка при отправке сообщения «{msg}» "
            f"{Fore.LIGHTRED_EX}в чат {chat_id}{Fore.LIGHTRED_EX}: {Fore.WHITE}{err}"
        )

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
        statuses: list[ItemStatuses] = [ItemStatuses.APPROVED],
        game_id: str | None = None, 
        category_id: str | None = None,
        obtaining_type_id: str | None = None,
        count: int = -1
    ) -> list[ItemProfile]:
        """
        Получает все товары аккаунта и сохраняет их.
        Берёт из сохранённых товары, которые не удалось получить
        """
        
        my_items: list[ItemProfile] = []
        svd_items: list[dict] = []
        next_cursor = None
        
        try:
            while True:
                itm_list = self.account.get_my_items(
                    after_cursor=next_cursor, 
                    game_id=game_id, 
                    category_id=category_id,
                    obtaining_type_id=obtaining_type_id,
                    statuses=statuses,
                    count=count if count != -1 else 24
                )
                
                for itm in itm_list.items:
                    svd_items.append(self._serealize_item(itm))
                    my_items.append(itm)
                    
                    if len(my_items) >= count and count != -1:
                        return my_items
                
                if not itm_list.page_info.has_next_page:
                    break
                
                next_cursor = itm_list.page_info.end_cursor
                time.sleep(0.5)
            
            self.saved_items = svd_items
        except (RequestPlayerokError, RequestFailedError):
            for itm_dict in list(self.saved_items):
                itm = self._deserealize_item(itm_dict)
                
                if statuses is None or itm.status in statuses:
                    my_items.append(itm)
                    if len(my_items) >= count and count != -1:
                        return my_items
                    
            if not my_items: 
                raise
            
        return my_items

    def log_to_tg(self, text, kb=None):
        asyncio.run_coroutine_threadsafe(
            get_telegram_bot().log_event(text=text, kb=kb), 
            get_telegram_bot_loop()
        )


    def bump_item(self, item: ItemProfile | MyItem):
        try:
            name_frmtd = item.name[:32] + ("..." if len(item.name) > 32 else "")
            
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
                statuses = self.account.get_item_priority_statuses(item.id, item.raw_price)
                
                prem_status = next((st for st in statuses if st.type == PriorityTypes.PREMIUM or st.price > 0), None)
                if not prem_status:
                    raise Exception("PREMIUM статус не найден")
                
                time.sleep(1)
                self.account.increase_item_priority_status(item.id, prem_status.id)
                    
                logger.info(
                    f"{Fore.LIGHTWHITE_EX}«{name_frmtd}» {Fore.WHITE}— {Fore.YELLOW}поднят. "
                    f"{Fore.WHITE}Позиция: {Fore.LIGHTWHITE_EX}{item.sequence} {Fore.WHITE}→ {Fore.YELLOW}1"
                )

                if (
                    self.config["playerok"]["notifications"]["enabled"]
                    and self.config["playerok"]["notifications"]["events"]["item_bumped"]
                ):
                    self.log_to_tg(
                        log_text(f'⬆️ Товар <a href="https://playerok.com/products/{item.slug}">«{item.name}»</a> поднят. Позиция: {item.sequence} → 1'),
                        log_item_kb(item.id)
                    )

                return True
        except Exception as e:
            logger.error(f"{Fore.LIGHTRED_EX}Ошибка при поднятии товара «{name_frmtd}»: {Fore.WHITE}{e}")
            if (
                self.config["playerok"]["notifications"]["enabled"]
                and self.config["playerok"]["notifications"]["events"]["item_bumped"]
            ):
                self.log_to_tg(
                    log_text(
                        f'❌ Ошибка при поднятии товара <a href="https://playerok.com/products/{item.slug}">«{item.name}»</a>',
                        f"<blockquote>{e}</blockquote>"
                    ),
                    log_item_kb(item.id)
                )
            return False

    def bump_items(self): 
        try:
            self.config["playerok"]["auto_bump_items"]["last_time"] = datetime.now().isoformat()
            sett.set("config", self.config)

            items = self.get_my_items(statuses=[ItemStatuses.APPROVED])
            up_items = [it for it in items if it.priority != PriorityTypes.DEFAULT]
            
            total = len(up_items)
            cnt = 0
            
            for item in up_items:
                if self.bump_item(item):
                    cnt += 1

            return True, total, cnt, None
        except Exception as e:
            logger.error(f"{Fore.LIGHTRED_EX}Ошибка при поднятии товаров: {Fore.WHITE}{e}")
            return False, 0, 0, e

    def restore_item(self, item: Item | MyItem | ItemProfile):
        try:
            name_frmtd = item.name[:32] + ("..." if len(item.name) > 32 else "")
            
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
                statuses = self.account.get_item_priority_statuses(item.id, item.raw_price)

                pr_status = next(
                    (st for st in statuses if st.type == PriorityTypes.DEFAULT or st.price == 0), 
                    statuses[0]
                )

                time.sleep(1)
                new_item = self.account.publish_item(item.id, pr_status.id)
                
                logger.info(
                    f"{Fore.LIGHTWHITE_EX}«{name_frmtd}» "
                    f"{Fore.WHITE}— {Fore.YELLOW}товар восстановлен"
                )
                if (
                    self.config["playerok"]["notifications"]["enabled"]
                    and self.config["playerok"]["notifications"]["events"]["item_restored"]
                ):
                    self.log_to_tg(
                        log_text(f'♻️ Товар <a href="https://playerok.com/products/{new_item.slug}">«{item.name}»</a> восстановлен'),
                        log_item_kb(item.id)
                    )
                return True
        except Exception as e:
            logger.error(f"{Fore.LIGHTRED_EX}Ошибка при восстановлении товара «{name_frmtd}»: {Fore.WHITE}{e}")
            if (
                self.config["playerok"]["notifications"]["enabled"]
                and self.config["playerok"]["notifications"]["events"]["item_restored"]
            ):
                self.log_to_tg(
                    log_text(
                        f'❌ Ошибка при восстановлении товара <a href="https://playerok.com/products/{item.slug}">«{item.name}»</a>',
                        f"<blockquote>{e}</blockquote>"
                    ),
                    log_item_kb(item.id)
                )
            return False
            
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
            logger.error(f"{Fore.LIGHTRED_EX}Ошибка при восстановлении истёкших товаров: {Fore.WHITE}{e}")

    def request_withdrawal(self) -> bool:
        try:
            self.config["playerok"]["auto_withdrawal"]["last_time"] = datetime.now().isoformat()
            sett.set("config", self.config)
            
            self.account = self.account.get()

            balance = self.account.profile.balance.withdrawable if self.account.profile.balance else 0
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
            elif self.config["playerok"]["auto_withdrawal"]["credentials_type"] == "usdt":
                provider = TransactionProviderIds.USDT
                account = self.config["playerok"]["auto_withdrawal"]["usdt_address"]
                sbp_bank_member_id = None
            
            trans = self.account.request_withdrawal(
                provider=provider,
                account=account,
                value=balance,
                sbp_bank_member_id=sbp_bank_member_id
            )
            
            logger.info(
                f"{Fore.LIGHTWHITE_EX}{balance or '?'}₽ {Fore.WHITE}"
                f"— {Fore.YELLOW}транзакция на вывод создана"
            )

            if (
                self.config["playerok"]["notifications"]["enabled"]
                and self.config["playerok"]["notifications"]["events"]["withdrawal_requested"]
            ):
                self.log_to_tg(
                    log_text(f'💳 Транзакция на вывод {balance}₽ успешно создана'),
                    log_transaction_kb(trans.id)
                )

            return True, balance, None
        except Exception as e:
            logger.error(f"{Fore.LIGHTRED_EX}Ошибка при создании транзакции на вывод {balance}₽: {Fore.WHITE}{e}")
            if (
                self.config["playerok"]["notifications"]["enabled"]
                and self.config["playerok"]["notifications"]["events"]["withdrawal_requested"]
            ):
                self.log_to_tg(
                    log_text(
                        f'❌ Ошибка при создании транзакции на вывод {balance}₽',
                        f"<blockquote>{e}</blockquote>"
                    ),
                    destroy_kb()
                )
            return False, 0, e


    def log_new_message(self, message: ChatMessage, chat: Chat):
        plbot = get_playerok_bot()
        
        chat_user = next((u.username for u in chat.users if u.id != plbot.account.id), None)
        if not chat_user:
            chat_user = message.user.username
        
        ch_header = f"Новое сообщение в чате с {chat_user}:"
        
        logger.info(f"{ACCENT_COLOR}{ch_header.replace(chat_user, f'{Fore.LIGHTCYAN_EX}{chat_user}')}")
        logger.info(f"{ACCENT_COLOR}│ {Fore.LIGHTWHITE_EX}{message.user.username}:")
        
        max_width = shutil.get_terminal_size((80, 20)).columns - 40
        longest_line_len = 0
        text = ""
        
        if message.text: 
            text = message.text
        if message.images: 
            text = f"{Fore.LIGHTMAGENTA_EX}*Изображения ({len(message.images)})*" + ((f" {Fore.WHITE}" + text) if text else "")
        
        for raw_line in text.split("\n"):
            if not raw_line.strip():
                logger.info(f"{ACCENT_COLOR}│")
                continue
            
            wrapped_lines = textwrap.wrap(raw_line, width=max_width)
            for wrapped in wrapped_lines:
                logger.info(f"{ACCENT_COLOR}│ {Fore.WHITE}{wrapped}")
                longest_line_len = max(longest_line_len, len(wrapped.strip()))
        
        underline_len = max(len(ch_header)-1, longest_line_len+2)
        logger.info(f"{ACCENT_COLOR}└{'─'*underline_len}")

    def log_new_deal(self, deal: ItemDeal):
        logger.info(f"{Fore.YELLOW}───────────────────────────────────────")
        logger.info(f"{Fore.YELLOW}Новая сделка {deal.id}:")
        logger.info(f" · Покупатель: {Fore.LIGHTWHITE_EX}{deal.user.username}")
        logger.info(f" · Товар: {Fore.LIGHTWHITE_EX}{deal.item.name}")
        logger.info(f" · Сумма: {Fore.LIGHTWHITE_EX}{deal.item.price}₽")
        logger.info(f"{Fore.YELLOW}───────────────────────────────────────")

    def log_new_review(self, deal: ItemDeal):
        logger.info(f"{Fore.YELLOW}───────────────────────────────────────")
        logger.info(f"{Fore.YELLOW}Новый отзыв по сделке {deal.id}:")
        logger.info(f" · Оценка: {Fore.LIGHTYELLOW_EX}{'⭐' * deal.review.rating or 5} ({deal.review.rating or 5})")
        logger.info(f" · Текст: {Fore.LIGHTWHITE_EX}{deal.review.text or '-'}")
        logger.info(f" · Оставил: {Fore.LIGHTWHITE_EX}{deal.review.creator.username}")
        logger.info(f" · Дата: {Fore.LIGHTWHITE_EX}{datetime.fromisoformat(deal.review.created_at).strftime('%d.%m.%Y %H:%M:%S')}")
        logger.info(f"{Fore.YELLOW}───────────────────────────────────────")

    def log_deal_status_changed(self, deal: ItemDeal, status_frmtd: str = "Неизвестный"):
        logger.info(f"{Fore.WHITE}───────────────────────────────────────")
        logger.info(f"{Fore.WHITE}Статус сделки {Fore.LIGHTWHITE_EX}{deal.id} {Fore.WHITE}изменился:")
        logger.info(f" · Статус: {Fore.LIGHTWHITE_EX}{status_frmtd}")
        logger.info(f" · Покупатель: {Fore.LIGHTWHITE_EX}{deal.user.username}")
        logger.info(f" · Товар: {Fore.LIGHTWHITE_EX}{deal.item.name}")
        logger.info(f" · Сумма: {Fore.LIGHTWHITE_EX}{deal.item.price}₽")
        logger.info(f"{Fore.WHITE}───────────────────────────────────────")

    def log_new_problem(self, deal: ItemDeal):
        logger.info(f"{Fore.YELLOW}───────────────────────────────────────")
        logger.info(f"{Fore.YELLOW}Новая жалоба в сделке {deal.id}:")
        logger.info(f" · Оставил: {Fore.LIGHTWHITE_EX}{deal.user.username}")
        logger.info(f" · Товар: {Fore.LIGHTWHITE_EX}{deal.item.name}")
        logger.info(f" · Сумма: {Fore.LIGHTWHITE_EX}{deal.item.price}₽")
        logger.info(f"{Fore.YELLOW}───────────────────────────────────────")


    def _event_datetime(self, latest_event_time, event_interval):
        if latest_event_time:
            return (
                datetime.fromisoformat(latest_event_time) 
                + timedelta(seconds=event_interval)
            )
        else:
            return datetime.now()

    async def _on_playerok_bot_init(self):
        def endless_loop():
            while True:
                balance = self.account.profile.balance.value if self.account.profile.balance is not None else "?"
                set_title(f"Playerok Universal v{VERSION} | {self.account.username}: {balance}₽")
                
                if sett.get("config") != self.config: 
                    self.config = sett.get("config")
                if sett.get("messages") != self.messages: 
                    self.messages = sett.get("messages")
                if sett.get("custom_commands") != self.custom_commands: 
                    self.custom_commands = sett.get("custom_commands")
                if sett.get("auto_deliveries") != self.auto_deliveries: 
                    self.auto_deliveries = sett.get("auto_deliveries")
                if sett.get("auto_restore_items") != self.auto_restore_items: 
                    self.auto_restore_items = sett.get("auto_restore_items")
                if sett.get("auto_complete_deals") != self.auto_complete_deals: 
                    self.auto_complete_deals = sett.get("auto_complete_deals")
                if sett.get("auto_bump_items") != self.auto_bump_items: 
                    self.auto_bump_items = sett.get("auto_bump_items")
                
                if data.get("initialized_users") != self.initialized_users: 
                    data.set("initialized_users", self.initialized_users)
                if data.get("saved_items") != self.saved_items: 
                    data.set("saved_items", self.saved_items)
                if data.get("cached_orders") != self.cached_orders: 
                    data.set("cached_orders", self.cached_orders)
                
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
                    and self._do_call_event(
                        self.config["playerok"]["auto_bump_items"]["last_time"],
                        self.config["playerok"]["auto_bump_items"]["interval"]
                    )
                ):
                    self.bump_items()
                time.sleep(3)

        def withdrawal_loop():
            while True:
                if (
                    self.config["playerok"]["auto_withdrawal"]["enabled"]
                    and self._do_call_event(
                        self.config["playerok"]["auto_withdrawal"]["last_time"],
                        self.config["playerok"]["auto_withdrawal"]["interval"]
                    )
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
        if not event.message.user:
            return
        
        self.log_new_message(event.message, event.chat)
        
        if event.message.user.id == self.account.id:
            return

        is_support_chat = event.chat.id in (self.account.system_chat_id, self.account.support_chat_id)
        if (
            self.config["playerok"]["notifications"]["enabled"]
            and (self.config["playerok"]["notifications"]["events"]["new_user_message"] 
            or self.config["playerok"]["notifications"]["events"]["new_system_message"])
        ):
            if (
                self.config["playerok"]["notifications"]["events"]["new_user_message"] 
                and not is_support_chat
            ) or (
                self.config["playerok"]["notifications"]["events"]["new_system_message"] 
                and is_support_chat
            ): 
                text = event.message.text or ""
                
                if event.message.images:
                    imgs = []
                    for i, file in enumerate(event.message.images, start=1):
                        imgs.append(f'<a href="{file.url}">*Изображение {i}*</a>')
                    text = ", ".join(imgs) + ((" " + text) if text else "")

                text = text or f"<i>Без сообщения</i>"
                
                self.log_to_tg(
                    log_text(
                        f'💬 Новое сообщение в <a href="https://playerok.com/chats/{event.chat.id}">чате</a>', 
                        f"<b>{event.message.user.username}:</b> <blockquote>{text.strip()}</blockquote>"
                    ),
                    log_new_mess_kb(event.chat.id)
                )

        if (
            not is_support_chat
            and event.message.text is not None
        ):
            if event.message.user.id not in self.initialized_users:
                self.initialized_users.append(event.message.user.id)
            
            elif event.message.text.lower() in ("!продавец", "!seller"):
                asyncio.run_coroutine_threadsafe(
                    get_telegram_bot().call_seller(event.message.user.username, event.chat.id), 
                    get_telegram_bot_loop()
                )
                self.send_message(event.chat.id, self.msg(
                    "cmd_seller", 
                    user=msg_user_from_chat(event.chat),
                    chat=msg_chat(event.chat)
                ))
            
            elif event.message.text.lower() in [key.lower() for key in self.custom_commands.keys()]:
                msg = self._format_msg_text(
                    "\n".join(self.custom_commands[event.message.text]),
                    account=msg_account(self.account.profile),
                    user=msg_user_from_chat(event.chat),
                    chat=msg_chat(event.chat)
                )
                self.send_message(event.chat.id, msg)

    async def _on_new_review(self, event: NewReviewEvent):
        if event.deal.user.id == self.account.id:
            return
        
        self.log_new_review(event.deal)
        
        if (
            self.config["playerok"]["notifications"]["enabled"] 
            and self.config["playerok"]["notifications"]["events"]["new_review"]
        ):
            text_frmtd = f"<blockquote>{event.deal.review.text}</blockquote>" if event.deal.review.text else "<i>Без текста</i>"
            self.log_to_tg(
                log_text(
                    f'🌟 Новый отзыв в <a href="https://playerok.com/deal/{event.deal.id}">сделке</a>', 
                    (f"<b>👤 Оставил:</b> {event.deal.review.creator.username}"
                    f"\n<b>✨ Оценка:</b> {'⭐' * event.deal.review.rating}"
                    f"\n<b>🏷️ Текст:</b> {text_frmtd}")
                ),
                log_new_mess_kb(event.chat.id)
            )

        self.send_message(event.chat.id, self.msg(
            "new_review", 
            user=msg_user_from_chat(event.chat),
            chat=msg_chat(event.chat),
            deal=msg_deal(event.deal),
            item=msg_item(event.deal.item),
            review_rating=event.deal.review.rating
        ))

    async def _on_new_problem(self, event: ItemPaidEvent):
        if event.deal.user.id == self.account.id:
            return

        self.log_new_problem(event.deal)
        self.send_message(event.chat.id, self.msg(
            "deal_has_problem", 
            user=msg_user_from_chat(event.chat),
            chat=msg_chat(event.chat),
            deal=msg_deal(event.deal),
            item=msg_item(event.deal.item)
        ))

        if (
            self.config["playerok"]["notifications"]["enabled"] 
            and self.config["playerok"]["notifications"]["events"]["new_problem"]
        ):
            self.log_to_tg(
                log_text(
                    f'🤬 Новая проблема в <a href="https://playerok.com/deal/{event.deal.id}">сделке</a>', 
                    (f"<b>👤 Покупатель:</b> {event.deal.user.username}"
                    f"\n<b>🛍️ Товар:</b> {event.deal.item.name}")
                ),
                log_new_problem_kb(event.chat.id)
            )

    async def _on_deal_confirmed(self, event: DealConfirmedEvent):
        if event.deal.user.id == self.account.id:
            return
        
        self.send_message(event.chat.id, self.msg(
            "deal_confirmed", 
            user=msg_user_from_chat(event.chat),
            chat=msg_chat(event.chat),
            deal=msg_deal(event.deal),
            item=msg_item(event.deal.item)
        ))

    async def _on_deal_rolled_back(self, event: DealRolledBackEvent):
        if event.deal.user.id == self.account.id:
            return
        
        self.send_message(event.chat.id, self.msg(
            "deal_refunded", 
            user=msg_user_from_chat(event.chat),
            chat=msg_chat(event.chat),
            deal=msg_deal(event.deal),
            item=msg_item(event.deal.item)
        ))

    async def _on_new_deal(self, event: NewDealEvent):
        if event.deal.user.id == self.account.id:
            return
            
        try: event.deal.item = self.account.get_item(event.deal.item.id)
        except: pass

        self.cached_orders[event.deal.id] = {
            "id": event.deal.id,
            "price": event.deal.item.price,
            "status": event.deal.status.name,
            "date": datetime.now(pytz.timezone("Europe/Moscow")).isoformat(),
            "item_id": event.deal.item.id,
            "item_name": event.deal.item.name
        }
        
        self.log_new_deal(event.deal)
        if (
            self.config["playerok"]["notifications"]["enabled"] 
            and self.config["playerok"]["notifications"]["events"]["new_deal"]
        ):
            self.log_to_tg(
                log_text(
                    f'📋 Новая <a href="https://playerok.com/deal/{event.deal.id}">сделка</a>', 
                    (f"<b>👤 Покупатель:</b> {event.deal.user.username}"
                    f"\n<b>🛍️ Товар:</b> {(event.deal.item.name or '-')}"
                    f"\n<b>💰 Сумма:</b> {event.deal.item.price or '?'}₽")
                ),
                log_new_deal_kb(event.chat.id, event.deal.id)
            )

        self.send_message(event.chat.id, self.msg(
            "new_deal", 
            user=msg_user_from_chat(event.chat),
            chat=msg_chat(event.chat),
            deal=msg_deal(event.deal),
            item=msg_item(event.deal.item)
        ))
        
        is_support_chat = event.chat.id in (self.account.system_chat_id, self.account.support_chat_id)
        if (
            event.deal.user.id not in self.initialized_users
            and not is_support_chat
        ):
            self.send_message(event.chat.id, self.msg(
                "first_message", 
                user=msg_user_from_chat(event.chat),
                chat=msg_chat(event.chat),
                deal=msg_deal(event.deal),
                item=msg_item(event.deal.item)
            ))
            self.initialized_users.append(event.deal.user.id)
                
        for i, auto_delivery in enumerate(list(self.auto_deliveries)):
            for phrase in auto_delivery["keyphrases"]:
                if (
                    phrase.lower() in (event.deal.item.name or "").lower() 
                    or (event.deal.item.name or "").lower() == phrase.lower()
                ):
                    piece = auto_delivery.get("piece", False)
                    if piece:
                        goods =  auto_delivery.get("goods", [])
                        try: good = goods[0]
                        except: break

                        mess = self.send_message(event.chat.id, good)
                        if mess:
                            logger.info(
                                f"{Fore.YELLOW}Покупателю {Fore.LIGHTYELLOW_EX}{event.deal.user.username or '?'} "
                                f"{Fore.YELLOW}выдан товар {Fore.LIGHTYELLOW_EX}«{good}»{Fore.YELLOW}. "
                                f"Остаток: {Fore.LIGHTYELLOW_EX}{len(goods)-1}"
                            )
                            self.auto_deliveries[i]["goods"].pop(goods.index(good))
                            sett.set("auto_deliveries", self.auto_deliveries)
                    else:
                        msg = auto_delivery.get("message", "")
                        if msg:
                            mess = self.send_message(event.chat.id, "\n".join(msg))
                            if mess:
                                logger.info(
                                    f"{Fore.YELLOW}Покупателю {Fore.LIGHTYELLOW_EX}{event.deal.user.username or '?'} "
                                    f"{Fore.YELLOW}отправлено сообщение авто-выдачи {Fore.LIGHTYELLOW_EX}«{' '.join(msg)}»"
                                )
                    
                    break
        
        if self.config["playerok"]["auto_complete_deals"]["enabled"]:
            if not event.deal.item.name:
                try: event.deal.item = self.account.get_item(event.deal.item.id)
                except: return

            included = any(
                any(
                    phrase.lower() in event.deal.item.name.lower()
                    or event.deal.item.name.lower() == phrase.lower()
                    for phrase in included_item
                )
                for included_item in self.auto_complete_deals["included"]
            )
            excluded = any(
                any(
                    phrase.lower() in event.deal.item.name.lower()
                    or event.deal.item.name.lower() == phrase.lower()
                    for phrase in excluded_item
                )
                for excluded_item in self.auto_complete_deals["excluded"]
            )

            if (
                self.config["playerok"]["auto_complete_deals"]["all"]
                and not excluded
            ) or (
                not self.config["playerok"]["auto_complete_deals"]["all"]
                and included
            ):
                self.account.update_deal(event.deal.id, ItemDealStatuses.SENT)
                logger.info(
                    f"{Fore.YELLOW}Сделка подтверждена автоматически "
                    f"{Fore.WHITE}(https://playerok.com/deal/{event.deal.id})"
                )

    async def _on_item_paid(self, event: ItemPaidEvent):
        if event.deal.user.id == self.account.id:
            return
        
        if self.config["playerok"]["auto_restore_items"]["sold"]:
            if not event.deal.item.name:
                event.deal.item = self.account.get_item(event.deal.item.id)
                time.sleep(1)
            
            for _ in range(3):
                try: 
                    items = self.get_my_items(count=12, statuses=[ItemStatuses.SOLD])
                    
                    item = next((
                        i for i in items 
                        if i.name == event.deal.item.name
                        and (event.deal.item.priority and i.priority == event.deal.item.priority)
                    ), None)
                    if not item:
                        raise

                    break
                except: 
                    time.sleep(4)
            else:
                return
            
            self.restore_item(item)

    async def _on_item_sent(self, event: ItemSentEvent):
        if event.deal.user.id == self.account.id:
            return
        
        self.send_message(event.chat.id, self.msg(
            "deal_sent", 
            user=msg_user_from_chat(event.chat),
            chat=msg_chat(event.chat),
            deal=msg_deal(event.deal),
            item=msg_item(event.deal.item)
        ))

    async def _on_deal_status_changed(self, event: DealStatusChangedEvent):
        if event.deal.user.id == self.account.id:
            return
        
        if event.deal.status and event.deal.id in self.cached_orders:
            self.cached_orders[event.deal.id]["status"] = event.deal.status.name
        
        status_frmtd = "Неизвестный"
        if event.deal.status is ItemDealStatuses.PAID: 
            status_frmtd = "Оплачено"
        elif event.deal.status is ItemDealStatuses.PENDING: 
            status_frmtd = "В ожидании"
        elif event.deal.status is ItemDealStatuses.SENT: 
            status_frmtd = "Товар отправлен"
        elif event.deal.status is ItemDealStatuses.CONFIRMED: 
            status_frmtd = "Выполнено"
        elif event.deal.status is ItemDealStatuses.ROLLED_BACK: 
            status_frmtd = "Возврат"

        self.log_deal_status_changed(event.deal, status_frmtd)
        if (
            self.config["playerok"]["notifications"]["enabled"] 
            and self.config["playerok"]["notifications"]["events"]["deal_status_changed"]
        ):
            self.log_to_tg(
                log_text(f'🔃 Статус <a href="https://playerok.com/deal/{event.deal.id}/">сделки</a> изменился на «{status_frmtd}»'),
                log_deal_kb(event.deal.id)
            )


    async def run_bot(self):
        logger.info("")
        logger.info(f"{Fore.YELLOW}Playerok бот запущен и активен")
        logger.info("")
        
        logger.info(f"{Fore.YELLOW}───────────────────────────────────────")
        logger.info(f"{Fore.YELLOW}Информация об аккаунте:")
        logger.info(f" · ID: {Fore.LIGHTWHITE_EX}{self.account.id}")
        logger.info(f" · Никнейм: {Fore.LIGHTWHITE_EX}{self.account.username}")

        profile = self.account.profile
        if profile.balance:
            logger.info(f" · Баланс: {Fore.LIGHTWHITE_EX}{profile.balance.value}₽")
            logger.info(f"   · Доступно: {Fore.LIGHTWHITE_EX}{profile.balance.available}₽")
            logger.info(f"   · В ожидании: {Fore.LIGHTWHITE_EX}{profile.balance.pending_income}₽")
            logger.info(f"   · Заморожено: {Fore.LIGHTWHITE_EX}{profile.balance.frozen}₽")
        
        logger.info(f" · Активные продажи: {Fore.LIGHTWHITE_EX}{profile.stats.deals.outgoing.total - profile.stats.deals.outgoing.finished}")
        logger.info(f" · Активные покупки: {Fore.LIGHTWHITE_EX}{profile.stats.deals.incoming.total - profile.stats.deals.incoming.finished}")
        logger.info(f"{Fore.YELLOW}───────────────────────────────────────")
        
        proxy = self.config["playerok"]["api"]["proxy"]
        if proxy:
            if "@" in proxy:
                user, password = proxy.split("@")[0].split(":")
                ip, port = proxy.split("@")[1].split(":")
            else:
                user, password = None, None
                ip, port = proxy.split(":")
            
            ip = ".".join([("*" * len(nums)) if i >= 3 else nums for i, nums in enumerate(ip.split("."), start=1)])
            port = f"{port[:3]}**"
            user = f"{user[:3]}*****" if user else "-"
            password = f"{password[:3]}*****" if password else "-"

            logger.info("")
            logger.info(f"{Fore.YELLOW}───────────────────────────────────────")
            logger.info(f"{Fore.YELLOW}Информация о прокси:")
            logger.info(f" · IP: {Fore.LIGHTWHITE_EX}{ip}:{port}")
            logger.info(f" · Юзер: {Fore.LIGHTWHITE_EX}{user}")
            logger.info(f" · Пароль: {Fore.LIGHTWHITE_EX}{password}")
            logger.info(f"{Fore.YELLOW}───────────────────────────────────────")
            logger.info("")

        add_bot_event_handler("ON_PLAYEROK_BOT_INIT", PlayerokBot._on_playerok_bot_init, 0)
        add_playerok_event_handler(EventTypes.NEW_MESSAGE, PlayerokBot._on_new_message, 0)
        add_playerok_event_handler(EventTypes.NEW_REVIEW, PlayerokBot._on_new_review, 0)
        add_playerok_event_handler(EventTypes.NEW_DEAL, PlayerokBot._on_new_deal, 0)
        add_playerok_event_handler(EventTypes.ITEM_PAID, PlayerokBot._on_item_paid, 0)
        add_playerok_event_handler(EventTypes.ITEM_SENT, PlayerokBot._on_item_sent, 0)
        add_playerok_event_handler(EventTypes.DEAL_HAS_PROBLEM, PlayerokBot._on_new_problem, 0)
        add_playerok_event_handler(EventTypes.DEAL_CONFIRMED, PlayerokBot._on_deal_confirmed, 0)
        add_playerok_event_handler(EventTypes.DEAL_ROLLED_BACK, PlayerokBot._on_deal_rolled_back, 0)
        add_playerok_event_handler(EventTypes.DEAL_STATUS_CHANGED, PlayerokBot._on_deal_status_changed, 0)

        async def listener_loop():
            listener = EventListener(self.account)
            for event in listener.listen():
                await call_playerok_event(event.type, [self, event])

        run_async_in_thread(listener_loop)
        await call_bot_event("ON_PLAYEROK_BOT_INIT", [self])