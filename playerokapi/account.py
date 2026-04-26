from __future__ import annotations
from typing import *
from logging import getLogger
from typing import Literal
import json
import time
import os
import tempfile
import shutil
import uuid

import tls_requests
import curl_cffi

from . import types
from .exceptions import *
from .parser import *
from .enums import *
from .misc import (
    PERSISTED_QUERIES, 
    QUERIES
)


logger = getLogger("playerokapi")


def get_account() -> Account | None:
    if hasattr(Account, "instance"):
        return getattr(Account, "instance")


class Account:
    """
    Класс, описывающий данные и методы Playerok аккаунта.

    :param token: Токен аккаунта.
    :type token: `str` or `None`

    :param ddg5: Cookie для обхода защиты DDoS-Guard (полное название: `__ddg5_`).
                \n **Примечание:** эта Cookie "умирает" каждый раз, когда:
                \n - меняется IP
                \n - меняется User-Agent / TLS fingerprint
                \n - сервер обновил ключи/алгоритм
                \n Чтобы API работал, эта Cookie должна быть взята из Cookie-данных аккаунта, токен которого вы указали, и запросы должны идти с того же IP-адреса, под которым Вы авторизовывались на Playerok.
                \n Если она недействительна, при запросах будет вызываться исключение `BotCheckDetectedException`.
    :type ddg5: `str`

    :param cookies: Куки-данные авторизованного аккаунта. Можно указывать вместо параметров `token`, `ddg5`.
    :type cookies: `str` or `dict[str, str]` or `None`

    :param user_agent: Юзер-агент браузера.
    :type user_agent: `str` or `None`

    :param proxy: IPV4 прокси в формате: `user:pass@ip:port` или `ip:port`, _опционально_.
    :type proxy: `str` or `None`

    :param requests_timeout: Таймаут ожидания ответов на запросы.
    :type requests_timeout: `int`
    """
    def __new__(cls, *args, **kwargs) -> Account:
        if not hasattr(cls, "instance"):
            cls.instance = super(Account, cls).__new__(cls)
        return getattr(cls, "instance")

    def __init__(
        self, 
        token: str = None, 
        ddg5: str = "", 
        cookies: str | dict[str, str] = None,
        user_agent: str = "", 
        proxy: str = None, 
        requests_timeout: int = 15,
        **kwargs
    ):
        if not any((token, cookies)):
            raise TypeError("Должен быть указать один из обязательных аргументов: token или cookies")

        self.token = token
        """Токен сессии аккаунта."""

        self.ddg5 = ddg5
        """Cookie для обхода защиты DDoS-Guard."""

        self.cookies = cookies
        """Куки-данные авторизованного аккаунта."""
        
        if isinstance(cookies, str):
            self.cookies = {
                c.split("=")[0].strip(): c.split("=")[1].strip() for c
                in cookies.split(";") if c.strip() and "=" in c
            }

        if not self.cookies:
            self.cookies = {
                "token": self.token,
                "__ddg5_": self.ddg5
            }

        self.user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
        """Юзер-агент браузера."""

        self.requests_timeout = requests_timeout
        """Таймаут ожидания ответов на запросы."""
        
        self.proxy = proxy
        """Прокси."""

        self.__proxy_string = f"http://{self.proxy.replace('https://', '').replace('http://', '')}" if self.proxy else None
        """Строка прокси."""

        self.base_url = "https://playerok.com"
        """Базовый URL для всех запросов."""

        self.id: str | None = None
        """ID аккаунта. \n\n_Заполняется при первом использовании get()_"""
        self.username: str | None = None
        """Никнейм аккаунта. \n\n_Заполняется при первом использовании get()_"""
        self.email: str | None = None
        """Email почта аккаунта. \n\n_Заполняется при первом использовании get()_"""
        self.role: str | None = None
        """Роль аккаунта. \n\n_Заполняется при первом использовании get()_"""
        self.support_chat_id: str | None = None
        """ID чата поддержки. \n\n_Заполняется при первом использовании get()_"""
        self.system_chat_id: str | None = None
        """ID системного чата. \n\n_Заполняется при первом использовании get()_"""
        self.unread_chats_counter: int | None = None
        """Количество непрочитанных чатов. \n\n_Заполняется при первом использовании get()_"""
        self.is_blocked: bool | None = None
        """Заблокирован ли аккаунт. \n\n_Заполняется при первом использовании get()_"""
        self.is_blocked_for: str | None = None
        """Причина блокировки аккаунта. \n\n_Заполняется при первом использовании get()_"""
        self.created_at: str | None = None
        """Дата создания аккаунта. \n\n_Заполняется при первом использовании get()_"""
        self.last_item_created_at: str | None = None
        """Дата создания последнего предмета. \n\n_Заполняется при первом использовании get()_"""
        self.has_frozen_balance: bool | None = None
        """Заморожен ли баланс аккаунта. \n\n_Заполняется при первом использовании get()_"""
        self.has_confirmed_phone_number: bool | None = None
        """Подтверждён ли номер телефона. \n\n_Заполняется при первом использовании get()_"""
        self.can_publish_items: bool | None = None
        """Может ли продавать предметы. \n\n_Заполняется при первом использовании get()_"""
        self.profile: AccountProfile | None = None
        """Профиль аккаунта (не путать с профилем пользователя). \n\n_Заполняется при первом использовании get()_"""

        self._is_initiated = False
        """Инициализирован ли аккаунт. """

        self._cert_path = os.path.join(os.path.dirname(__file__), "cacert.pem")
        self._tmp_cert_path = os.path.join(tempfile.gettempdir(), "cacert.pem")
        shutil.copyfile(self._cert_path, self._tmp_cert_path)

        self._refresh_clients()

    def _refresh_clients(self):
        self.__tls_requests = tls_requests.Client(
            proxy=self.__proxy_string
        )
        self.__curl_session = curl_cffi.Session(
            impersonate="chrome",
            timeout=self.requests_timeout,
            proxy=self.__proxy_string,
            verify=self._tmp_cert_path
        )

    def request(
        self, 
        method: Literal["get", "post"], 
        url: str, 
        headers: dict[str, str], 
        payload: dict[str, str] | None = None, 
        files: dict | None = None,
        pass_304: bool = True
    ) -> requests.Response:
        """
        Отправляет запрос на сервер playerok.com.

        :param method: Метод запроса: post, get.
        :type method: `str`

        :param url: URL запроса.
        :type url: `str`

        :param headers: Заголовки запроса.
        :type headers: `dict[str, str]`
        
        :param payload: Payload запроса.
        :type payload: `dict[str, str]` or `None`
        
        :param files: Файлы запроса.
        :type files: `dict` or `None`

        :return: Ответа запроса requests.
        :rtype: `requests.Response`
        """
        try: x_gql_op = payload.get("operationName", "viewer")
        except: x_gql_op = "viewer"
        _headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "access-control-allow-headers": "sentry-trace, baggage",
            "apollo-require-preflight": "true",
            "apollographql-client-name": "web",
            "content-type": "application/json",
            "cookie": "; ".join([f"{k}={v}" for k, v in self.cookies.items()]),
            "priority": "u=1, i",
            "origin": "https://playerok.com",
            "referer": "https://playerok.com/",
            "sec-ch-ua": '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
            "sec-ch-ua-arch": '"x86"',
            "sec-ch-ua-bitness": '"64"',
            "sec-ch-ua-full-version": '"146.0.7680.180"',
            "sec-ch-ua-full-version-list": '"Chromium";v="146.0.7680.180", "Not-A.Brand";v="24.0.0.0", "Google Chrome";v="146.0.7680.180"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-model": '""',
            "sec-ch-ua-platform": '"Windows"',
            "sec-ch-ua-platform-version": '"19.0.0"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": self.user_agent,
            "x-gql-op": x_gql_op,
            "x-gql-path": "/",
            "x-timezone-offset": "-240",
            "x-apollo-operation-name": x_gql_op
        }
        headers = {k: v for k, v in _headers.items() if k not in headers.keys()}
                
        def make_req():
            err = ""

            for _ in range(3):
                try:
                    if method == "get":
                        r = self.__curl_session.get(
                            url=url, 
                            params=payload, 
                            headers=headers, 
                            timeout=self.requests_timeout
                        )
                    elif method == "post":
                        if files:
                            r = self.__tls_requests.post(
                                url=url, 
                                json=payload if not files else None, 
                                data=payload if files else None, 
                                headers=headers, 
                                files=files, 
                                timeout=self.requests_timeout
                            )
                        else:
                            r = self.__curl_session.post(
                                url=url, 
                                json=payload,
                                headers=headers, 
                                timeout=self.requests_timeout
                            )
                    return r
                except Exception as e:
                    err = str(e)
                    logger.debug(f"Ошибка при отправке запроса: {e}")
                    logger.debug(f"Отправляю запрос повторно...")
                
            raise RequestSendingError(url, err)

        sigs = [
            "<title>Just a moment...</title>",
            "window._cf_chl_opt",
            "Enable JavaScript and cookies to continue",
            "Checking your browser before accessing",
            "cf-browser-verification",
            "Cloudflare Ray ID"
        ]
        
        resp = make_req()
        if any(sig in resp.text for sig in sigs):
            raise BotCheckDetectedException()

        cookie_headers = {
            v.split("=")[0]: v.split("=")[1].split(";")[0] 
            for k, v in resp.headers.multi_items() if k.lower() == "set-cookie"
        }
        for k, v in cookie_headers.items():
            self.cookies[k] = v
        
        json = {}
        try: json = resp.json()
        except: pass
        
        if "errors" in json:
            raise RequestPlayerokError(resp)

        if resp.status_code != 200 and not (resp.status_code == 304 and pass_304):
           raise RequestFailedError(resp)
        
        return resp
    
    def get(self) -> Account:
        """
        Получает/обновляет данные об аккаунте.

        :return: Объект аккаунта с обновлёнными данными.
        :rtype: `playerokapi.account.Account`
        """
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "viewer",
            "query": QUERIES.get("viewer"),
            "variables": {}
        }
        
        r = self.request("post", f"{self.base_url}/graphql", headers, payload).json()
        data: dict = r["data"]["viewer"]
        if data is None:
            raise UnauthorizedError()
        
        self.id = data.get("id")
        self.username = data.get("username")
        self.email = data.get("email")
        self.role = data.get("role")
        self.has_frozen_balance = data.get("hasFrozenBalance")
        self.support_chat_id = data.get("supportChatId")
        self.system_chat_id = data.get("systemChatId")
        self.unread_chats_counter = data.get("unreadChatsCounter")
        self.is_blocked = data.get("isBlocked")
        self.is_blocked_for = data.get("isBlockedFor")
        self.created_at = data.get("createdAt")
        self.last_item_created_at = data.get("lastItemCreatedAt")
        self.has_confirmed_phone_number = data.get("hasConfirmedPhoneNumber")
        self.can_publish_items = data.get("canPublishItems")
        self.unread_chats_counter = data.get("unreadChatsCounter")
        self._is_initiated = True

        headers = {"accept": "*/*"}
        payload = {
            "operationName": "user",
            "variables": json.dumps({
                "username": self.username, 
                "hasSupportAccess": False
            }),
            "extensions": json.dumps({
                "persistedQuery": {
                    "version": 1, 
                    "sha256Hash": PERSISTED_QUERIES.get("user")
                }
            })
        }
        
        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        data: dict = r["data"]["user"]
        
        if data.get("__typename") == "User": 
            self.profile = account_profile(data)
        
        return self
    
    def get_user(
        self, 
        id: str | None = None, 
        username: str | None = None
    ) -> types.UserProfile:
        """
        Получает профиль пользователя.\n
        Можно получить по любому из двух параметров:

        :param id: ID пользователя, _опционально_.
        :type id: `str` or `None`

        :param username: Никнейм пользователя, _опционально_.
        :type username: `str` or `None`

        :return: Объект профиля пользователя.
        :rtype: `playerokapi.types.UserProfile`
        """
        if not any((id, username)):
            raise TypeError("Не был передан ни один из обязательных аргументов: id, username")
        
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "user",
            "variables": json.dumps({
                "id": id, 
                "username": username, 
                "hasSupportAccess": False
            }),
            "extensions": json.dumps({
                "persistedQuery": {
                    "version": 1, 
                    "sha256Hash": PERSISTED_QUERIES.get("user")
                }
            })
        }

        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        data: dict = r["data"]["user"]
        if data.get("__typename") == "UserFragment": profile = data
        elif data.get("__typename") == "User": profile = data.get("profile")
        else: profile = None
        
        return user_profile(profile)

    def get_deals(
        self, 
        count: int = 24, 
        statuses: list[ItemDealStatuses] | None = None, 
        direction: ItemDealDirections | None = None, 
        after_cursor: str = None
    ) -> types.ItemDealList:
        """
        Получает сделки аккаунта.

        :param count: Кол-во сделок, которые нужно получить (не более 24 за один запрос).
        :type count: `int`

        :param statuses: Статусы сделок, которые нужно получать, _опционально_.
        :type statuses: `list[playerokapi.enums.ItemDealsStatuses]` or `None`

        :param direction: Направление сделок, _опционально_.
        :type direction: `playerokapi.enums.ItemDealsDirections` or `None`

        :param after_cursor: Курсор, с которого будет идти парсинг (если нету - ищет с самого начала страницы), _опционально_.
        :type after_cursor: `str`
        
        :return: Страница сделок.
        :rtype: `playerokapi.types.ItemDealList`
        """
        if not self._is_initiated:
            raise NotInitiatedError()

        str_statuses = [status.name for status in statuses] if statuses else None
        str_direction = direction.name if direction else None
        
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "deals",
            "variables": json.dumps({
                "pagination": {
                    "first": count, 
                    "after": after_cursor
                }, 
                "filter": {
                    "userId": self.id, 
                    "direction": str_direction, 
                    "status": str_statuses
                }, 
                "showForbiddenImage": True
            }),
            "extensions": json.dumps({
                "persistedQuery": {
                    "version": 1, 
                    "sha256Hash": PERSISTED_QUERIES.get("deals")
                }
            })
        }
        
        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        return item_deal_list(r["data"]["deals"])

    def get_deal(
        self, 
        deal_id: str
    ) -> types.ItemDeal:
        """
        Получает сделку.

        :param deal_id: ID сделки.
        :type deal_id: `str`
        
        :return: Объект сделки.
        :rtype: `playerokapi.types.ItemDeal`
        """
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "deal",
            "variables": json.dumps({
                "id": deal_id,
                "hasSupportAccess": False,
                "showForbiddenImage": True
            }),
            "extensions": json.dumps({
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": PERSISTED_QUERIES.get("deal")
                }
            })
        } 
        
        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        return item_deal(r["data"]["deal"])
    
    def update_deal(
        self, 
        deal_id: str, 
        new_status: ItemDealStatuses
    ) -> types.ItemDeal:
        """
        Обновляет статус сделки
        (используется, чтобы подтвердить, оформить возврат и т.д).

        :param deal_id: ID сделки.
        :type deal_id: `str`

        :param new_status: Новый статус сделки.
        :type new_status: `playerokapi.enums.ItemDealStatuses`
        
        :return: Объект обновлённой сделки.
        :rtype: `playerokapi.types.ItemDeal`
        """
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "updateDeal",
            "variables": {
                "input": {
                    "id": deal_id,
                    "status": new_status.name
                }
            },
            "query": QUERIES.get("updateDeal")
        }
        
        r = self.request("post", f"{self.base_url}/graphql", headers, payload).json()
        return item_deal(r["data"]["updateDeal"])

    def get_games(
        self, 
        count: int = 24, 
        type: GameTypes | None = None, 
        after_cursor: str = None
    ) -> types.GameList:
        """
        Получает все игры или/и приложения.

        :param count: Кол-во игр, которые нужно получить (не более 24 за один запрос).
        :type count: `int`

        :param type: Тип игр, которые нужно получать. По умолчанию не указано, значит будут все сразу, _опционально_.
        :type type: `playerokapi.enums.GameTypes` or `None`

        :param after_cursor: Курсор, с которого будет идти парсинг (если нету - ищет с самого начала страницы), _опционально_.
        :type after_cursor: `str`
        
        :return: Страница игр.
        :rtype: `playerokapi.types.GameList`
        """
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "games",
            "variables": json.dumps({
                "pagination": {
                    "first": count,
                    "after": after_cursor
                },
                "filter": {
                    "type": type.name if type else None
                }
            }),
            "extensions": json.dumps({
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": PERSISTED_QUERIES.get("games")
                }
            })
        }

        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        return game_list(r["data"]["games"])
    
    def get_game(
        self, 
        id: str | None = None, 
        slug: str | None = None
    ) -> types.Game:
        """
        Получает игру/приложение.\n
        Можно получить по любому из двух параметров:

        :param id: ID игры/приложения, _опционально_.
        :type id: `str` or `None`

        :param slug: Имя страницы игры/приложения, _опционально_.
        :type slug: `str` or `None`
        
        :return: Объект игры.
        :rtype: `playerokapi.types.Game`
        """
        if not any((id, slug)):
            raise TypeError("Не был передан ни один из обязательных аргументов: id, slug")
        
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "GamePage",
            "variables": json.dumps({
                "id": id,
                "slug": slug
            }),
            "extensions": json.dumps({
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": PERSISTED_QUERIES.get("GamePage")
                }
            })
        }
        
        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        return game(r["data"]["game"])

    def get_game_category(
        self, 
        id: str | None = None, 
        game_id: str | None = None,
        slug: str | None = None
    ) -> types.GameCategory:
        """
        Получает категорию игры/приложения.\n
        Можно получить параметру `id` или по связке параметров `game_id` и `slug`

        :param id: ID категории, _опционально_.
        :type id: `str` or `None`

        :param game_id: ID игры категории (лучше указывать в связке со slug, чтобы находить точную категорию), _опционально_.
        :type game_id: `str` or `None`

        :param slug: Имя страницы категории, _опционально_.
        :type slug: `str` or `None`
        
        :return: Объект категории игры.
        :rtype: `playerokapi.types.GameCategory`
        """
        if not id and not all((game_id, slug)):
            if not id and (game_id or slug):
                raise TypeError("Связка аргументов game_id, slug была передана не полностью")
            raise TypeError("Не был передан ни один из обязательных аргументов: id, game_id, slug")

        headers = {"accept": "*/*"}
        payload = {
            "operationName": "GamePageCategory",
            "variables": json.dumps({
                "id": id,
                "gameId": game_id,
                "slug": slug
            }),
            "extensions": json.dumps({
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": PERSISTED_QUERIES.get("GamePageCategory")
                }
            })
        }

        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        return game_category(r["data"]["gameCategory"])
    
    def get_game_category_agreements(
        self, 
        game_category_id: str, 
        user_id: str | None = None,
        count: int = 24, 
        after_cursor: str | None = None
    ) -> types.GameCategoryAgreementList:
        """
        Получает соглашения пользователя на продажу предметов в категории (если пользователь уже принял эти соглашения - список будет пуст).

        :param game_category_id: ID категории игры.
        :type game_category_id: `str`

        :param user_id: ID пользователя, чьи соглашения нужно получить. Если не указан, будет получать по ID вашего аккаунта, _опционально_.
        :type user_id: `str` or `None`

        :param count: Кол-во соглашений, которые нужно получить (не более 24 за один запрос).
        :type count: `int`
        
        :param after_cursor: Курсор, с которого будет идти парсинг (если нету - ищет с самого начала страницы), _опционально_.
        :type after_cursor: `str` or `None`
        
        :return: Страница соглашений.
        :rtype: `playerokapi.types.GameCategoryAgreementList`
        """
        if not user_id and not self._is_initiated:
            raise NotInitiatedError()

        headers = {"accept": "*/*"}
        payload = {
            "operationName": "gameCategoryAgreements",
            "variables": json.dumps({
                "pagination": {
                    "first": count,
                    "after": after_cursor
                },
                "filter": {
                    "gameCategoryId": game_category_id,
                    "userId": user_id if user_id else self.id
                }
            }),
            "extensions": json.dumps({
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": PERSISTED_QUERIES.get("gameCategoryAgreements")
                }
            })
        }

        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        return game_category_agreement_list(r["data"]["gameCategoryAgreements"])
    
    def get_game_category_obtaining_types(
        self, 
        game_category_id: str, 
        count: int = 24,
        after_cursor: str | None = None
    ) -> types.GameCategoryObtainingTypeList:
        """
        Получает типы (способы) получения предмета в категории.
        
        :param game_category_id: ID категории игры.
        :type game_category_id: `str`

        :param count: Кол-во соглашений, которые нужно получить (не более 24 за один запрос).
        :type count: `int`
        
        :param after_cursor: Курсор, с которого будет идти парсинг (если нету - ищет с самого начала страницы), _опционально_.
        :type after_cursor: `str` or `None`
        
        :return: Страница соглашений.
        :rtype: `playerokapi.types.GameCategoryAgreementList`
        """
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "gameCategoryObtainingTypes",
            "variables": json.dumps({
                "pagination": {
                    "first": count,
                    "after": after_cursor
                },
                "filter": {
                    "gameCategoryId": game_category_id
                }
            }),
            "extensions": json.dumps({
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": PERSISTED_QUERIES.get("gameCategoryObtainingTypes")
                }
            })
        }

        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        return game_category_obtaining_type_list(r["data"]["gameCategoryObtainingTypes"])
    
    def get_game_category_instructions(
        self, 
        game_category_id: str, 
        obtaining_type_id: str, 
        count: int = 24,
        type: GameCategoryInstructionTypes | None = None, 
        after_cursor: str | None = None
    ) -> types.GameCategoryInstructionList:
        """
        Получает инструкции по продаже/покупке в категории.
        
        :param game_category_id: ID категории игры.
        :type game_category_id: `str`
        
        :param obtaining_type_id: ID типа (способа) получения предмета.
        :type obtaining_type_id: `str`

        :param count: Кол-во инструкций, которые нужно получить (не более 24 за один запрос).
        :type count: `int`
        
        :param type: Тип инструкции: для продавца или для покупателя, _опционально_.
        :type type: `enums.GameCategoryInstructionTypes` or `None`

        :param after_cursor: Курсор, с которого будет идти парсинг (если нету - ищет с самого начала страницы), _опционально_.
        :type after_cursor: `str` or `None`
        
        :return: Страница инструкий.
        :rtype: `playerokapi.types.GameCategoryInstructionList`
        """
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "gameCategoryInstructions",
            "variables": json.dumps({
                "pagination": {
                    "first": count,
                    "after": after_cursor
                },
                "filter": {
                    "gameCategoryId": game_category_id,
                    "obtainingTypeId": obtaining_type_id,
                    "type": type.name if type else None
                }
            }),
            "extensions": json.dumps({
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": PERSISTED_QUERIES.get("gameCategoryInstructions")
                }
            })
        }

        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        return game_category_instruction_list(r["data"]["gameCategoryInstructions"])

    def get_game_category_data_fields(
        self, 
        game_category_id: str, 
        obtaining_type_id: str, 
        count: int = 24,
        type: GameCategoryDataFieldTypes | None = None, 
        after_cursor: str | None = None
    ) -> types.GameCategoryDataFieldList:
        """
        Получает поля с данными категории (которые отправляются после покупки).
        
        :param game_category_id: ID категории игры.
        :type game_category_id: `str`
        
        :param obtaining_type_id: ID типа (способа) получения предмета.
        :type obtaining_type_id: `str`

        :param count: Кол-во инструкций, которые нужно получить (не более 24 за один запрос).
        :type count: `int`
        
        :param type: Тип полей с данными, _опционально_.
        :type type: `enums.GameCategoryDataFieldTypes` or `None`

        :param after_cursor: Курсор, с которого будет идти парсинг (если нету - ищет с самого начала страницы), _опционально_.
        :type after_cursor: `str` or `None`
        
        :return: Страница полей с данными.
        :rtype: `playerokapi.types.GameCategoryDataFieldList`
        """
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "gameCategoryDataFields",
            "variables": json.dumps({
                "pagination": {
                    "first": count,
                    "after": after_cursor
                },
                "filter": {
                    "gameCategoryId": game_category_id,
                    "obtainingTypeId": obtaining_type_id,
                    "type": type.name if type else None
                }
            }),
            "extensions": json.dumps({
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": PERSISTED_QUERIES.get("gameCategoryDataFields")
                }
            })
        }

        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        return game_category_data_field_list(r["data"]["gameCategoryDataFields"])
    
    def get_chats(
        self, 
        count: int = 24, 
        type: ChatTypes | None = None,
        status: ChatStatuses | None = None, 
        after_cursor: str | None = None
    ) -> types.ChatList:
        """
        Получает все чаты аккаунта.

        :param count: Кол-во чатов, которые нужно получить (не более 24 за один запрос).
        :type count: `int`

        :param type: Тип чатов, которые нужно получать. По умолчанию не указано, значит будут все сразу, _опционально_.
        :type type: `playerokapi.enums.ChatTypes` or `None`

        :param status: Статус чатов, которые нужно получать. По умолчанию не указано, значит будут любые, _опционально_.
        :type status: `playerokapi.enums.ChatStatuses` or `None`
        
        :param after_cursor: Курсор, с которого будет идти парсинг (если нету - ищет с самого начала страницы), _опционально_.
        :type after_cursor: `str` or `None`
        
        :return: Страница чатов.
        :rtype: `playerokapi.types.ChatList`
        """
        if not self._is_initiated:
            raise NotInitiatedError()
        
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "userChats",
            "variables": json.dumps({
                "pagination": {
                    "first": count,
                    "after": after_cursor
                },
                "filter": {
                    "userId": self.id,
                    "type": type.name if type else None,
                    "status": status.name if status else None
                },
                "hasSupportAccess": False
            }),
            "extensions": json.dumps({
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": PERSISTED_QUERIES.get("userChats")
                }
            })
        }
        
        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        return chat_list(r["data"]["chats"])
    
    def get_chat(
        self, 
        chat_id: str
    ) -> types.Chat:
        """
        Получает чат.

        :param chat_id: ID чата.
        :type chat_id: `str`
        
        :return: Объект чата.
        :rtype: `playerokapi.types.Chat`
        """
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "chat",
            "variables": json.dumps({
                "id": chat_id,
                "hasSupportAccess": False
            }),
            "extensions": json.dumps({
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": PERSISTED_QUERIES.get("chat")
                }
            })
        }

        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        return chat(r["data"]["chat"])
    
    def get_chat_by_username(
        self, 
        username: str
    ) -> types.Chat | None:
        """
        Получает чат по никнейму собеседника.

        :param username: Никнейм собеседника.
        :type username: `str`

        :return: Объект чата.
        :rtype: `playerokapi.types.Chat` or `None`
        """
        next_cursor = None
        while True:
            chats = self.get_chats(count=24, after_cursor=next_cursor)
            for chat in chats.chats:
                if any(user for user in chat.users if user.username.lower() == username.lower()):
                    return chat
            if not chats.page_info.has_next_page:
                break
            next_cursor = chats.page_info.end_cursor
    
    def get_chat_messages(
        self, 
        chat_id: str, 
        count: int = 24,
        after_cursor: str | None = None
    ) -> types.ChatMessageList:
        """
        Получает сообщения чата.

        :param chat_id: ID чата.
        :type chat_id: `str`

        :param count: Кол-во сообщений, которые нужно получить (не более 24 за один запрос).
        :type count: `int`

        :param after_cursor: Курсор, с которого будет идти парсинг (если нету - ищет с самого начала страницы), _опционально_.
        :type after_cursor: `str` or `None`
        
        :return: Страница сообщений.
        :rtype: `playerokapi.types.ChatMessageList`
        """
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "chatMessages",
            "variables": json.dumps({
                "pagination": {
                    "first": count,
                    "after": after_cursor
                },
                "filter": {
                    "chatId": chat_id
                },
                "hasSupportAccess": False,
                "showForbiddenImage": True
            }),
            "extensions": json.dumps({
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": PERSISTED_QUERIES.get("chatMessages")
                }
            })
        }

        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        return chat_message_list(r["data"]["chatMessages"])

    def mark_chat_as_read(
        self, 
        chat_id: str
    ) -> types.Chat:
        """
        Помечает чат как прочитанный (все сообщения).

        :param chat_id: ID чата.
        :type chat_id: `str`

        :return: Объект чата с обновлёнными данными.
        :rtype: `playerokapi.types.Chat`
        """
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "markChatAsRead",
            "query": QUERIES.get("markChatAsRead"),
            "variables": {
                "input": {
                    "chatId": chat_id
                }
            }
        }

        r = self.request("post", f"{self.base_url}/graphql", headers, payload).json()
        return chat(r["data"]["markChatAsRead"])

    def upload_chat_image_into_temporary_store(
        self, 
        photo_file_path: str,
        chat_id: str
    ) -> types.Chat:
        """
        Выкладывает изображение чата во временное хранилище
        (перед отправкой сообщения с изображением).

        :param chat_id: ID чата.
        :type chat_id: `str`

        :return: Объект чата с обновлёнными данными.
        :rtype: `playerokapi.types.Chat`
        """
        headers = {"accept": "*/*"}
        operations = {
            "operationName": "uploadChatImageIntoTemporaryStore",
            "query": QUERIES.get("uploadChatImageIntoTemporaryStore"),
            "variables": {
                "file": None,
                "input": {
                    "chatId": chat_id,
                    "clientAttachmentId": str(uuid.uuid4())
                }
            }
        }
        
        files = {"1": open(photo_file_path, "rb")}
        map = {"1": ["variables.file"]} if photo_file_path else None
        payload = {
            "operations": json.dumps(operations), 
            "map": json.dumps(map)
        }
        
        r = self.request("post", f"{self.base_url}/graphql", headers, payload, files).json()
        return temporary_attachment_upload_output(r["data"]["uploadChatImageIntoTemporaryStore"])

    def send_message(
        self, 
        chat_id: str, 
        text: str | None = None,
        photo_file_paths: list[str] = [], 
        mark_chat_as_read: bool = False
    ) -> types.ChatMessage:
        """
        Отправляет сообщение в чат.\n
        Можно отправить текстовое сообщение `text` или фотографию `photo_file_path`.

        :param chat_id: ID чата, в который нужно отправить сообщение.
        :type chat_id: `str`

        :param text: Текст сообщения, _опционально_.
        :type text: `str` or `None`

        :param photo_file_paths: Массив путей к файлам фотографий, _опционально_.
        :type photo_file_paths: `list` of `str`

        :param mark_chat_as_read: Пометить чат, как прочитанный перед отправкой, _опционально_.
        :type mark_chat_as_read: `bool`

        :return: Объект отправленного сообщения.
        :rtype: `playerokapi.types.ChatMessage`
        """
        if not any((text, photo_file_paths)):
            raise TypeError("Не был передан ни один из обязательных аргументов: text, photo_file_paths")
        
        if mark_chat_as_read:
            self.mark_chat_as_read(chat_id=chat_id)
        
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "createChatMessage",
            "query": QUERIES.get("createChatMessage"),
            "variables": {
                "input": {
                    "chatId": chat_id,
                    "imagesIds": [],
                    "text": text or ""
                }
            }
        }
        
        for file_path in photo_file_paths:
            image = self.upload_chat_image_into_temporary_store(file_path, chat_id)
            if image:
                payload["variables"]["input"]["imagesIds"].append(image.id)
        
        r = self.request("post", f"{self.base_url}/graphql", headers, payload).json()
        return chat_message(r["data"]["createChatMessage"])
 
    def create_item(
        self, 
        game_category_id: str, 
        obtaining_type_id: str, 
        name: str, 
        price: int, 
        description: str, 
        options: list[GameCategoryOption], 
        data_fields: list[GameCategoryDataField],
        attachments: list[str]
    ) -> types.Item:
        """
        Создаёт предмет (после создания помещается в черновик, а не сразу выставляется на продажу).

        :param game_category_id: ID категории игры, в которой необходимо создать предмет.
        :type game_category_id: `str`

        :param obtaining_type_id: ID типа получения предмета.
        :type obtaining_type_id: `str`

        :param name: Название предмета.
        :type name: `str`

        :param price: Цена предмета.
        :type price: `int` or `str`

        :param description: Описание предмета.
        :type description: `str`

        :param options: Массив **выбранных** опций (аттрибутов) предмета.
        :type options: `list[playerokapi.types.GameCategoryOption]`

        :param data_fields: Массив полей с данными предмета. \n
            !!! Должны быть заполнены данные с типом поля `ITEM_DATA`, то есть те данные, которые указываются при заполнении информации о товаре.
            Поля с типом `OBTAINING_DATA` **заполнять и передавать не нужно**, так как эти данные будет указывать сам покупатель при оформлении предмета.
        :type data_fields: `list[playerokapi.types.GameCategoryDataField]`

        :param attachments: Массив файлов-приложений предмета. Указываются пути к файлам.
        :type attachments: `list[str]`

        :return: Объект созданного предмета.
        :rtype: `playerokapi.types.Item`
        """
        payload_attributes = {option.field: option.value for option in options}
        payload_data_fields = [{"fieldId": field.id, "value": field.value} for field in data_fields]
        
        headers = {"accept": "*/*"}
        operations = {
            "operationName": "createItem",
            "query": QUERIES.get("createItem"),
            "variables": {
                "input": {
                    "gameCategoryId": game_category_id,
                    "obtainingTypeId": obtaining_type_id,
                    "name": name,
                    "price": int(price),
                    "description": description,
                    "attributes": payload_attributes,
                    "dataFields": payload_data_fields
                },
                "attachments": [None] * len(attachments)
            }
        }
        
        map = {}
        files = {}
        
        for i, att in enumerate(attachments, start=1):
            map[str(i)] = [f"variables.attachments.{i-1}"]
            files[str(i)] = open(att, "rb")
        
        payload = {
            "operations": json.dumps(operations),
            "map": json.dumps(map)
        }

        r = self.request("post", f"{self.base_url}/graphql", headers, payload, files).json()
        return item(r["data"]["createItem"])
    
    def update_item(
        self, 
        id: str, 
        name: str | None = None, 
        price: int | None = None, 
        description: str | None = None, 
        options: list[GameCategoryOption] | None = None, 
        data_fields: list[GameCategoryDataField] | None = None, 
        remove_attachments: list[str] | None = None, 
        add_attachments: list[str] | None = None
    ) -> types.Item:
        """
        Обновляет предмет аккаунта.

        :param id: ID предмета.
        :type id: `str`

        :param name: Название предмета.
        :type name: `str` or `None`

        :param price: Цена предмета.
        :type price: `int` or `str` or `None`

        :param description: Описание предмета.
        :type description: `str` or `None`

        :param options: Массив **выбранных** опций (аттрибутов) предмета.
        :type options: `list[playerokapi.types.GameCategoryOption]` or `None`

        :param data_fields: Массив полей с данными предмета. \n
            !!! Должны быть заполнены данные с типом поля `ITEM_DATA`, то есть те данные, которые указываются при заполнении информации о товаре.
            Поля с типом `OBTAINING_DATA` **заполнять и передавать не нужно**, так как эти данные будет указывать сам покупатель при оформлении предмета.
        :type data_fields: `list[playerokapi.types.GameCategoryDataField]` or `None`

        :param remove_attachments: Массив ID файлов-приложений предмета, которые нужно удалить.
        :type remove_attachments: `list[str]` or `None`

        :param add_attachments: Массив файлов-приложений предмета, которые нужно добавить. Указываются пути к файлам.
        :type add_attachments: `list[str]` or `None`

        :return: Объект обновлённого предмета.
        :rtype: `playerokapi.types.Item`
        """
        payload_attributes = {option.field: option.value for option in options} if options is not None else None
        payload_data_fields = [{"fieldId": field.id, "value": field.value} for field in data_fields] if data_fields is not None else None
        
        headers = {"accept": "*/*"}
        operations = {
            "operationName": "updateItem",
            "query": QUERIES.get("updateItem"),
            "variables": {
                "input": {
                    "id": id
                },
                "addedAttachments": [None] * len(add_attachments) if add_attachments else None
            }
        }
        if name: operations["variables"]["input"]["name"] = name
        if price: operations["variables"]["input"]["price"] = int(price)
        if description: operations["variables"]["input"]["description"] = description
        if options: operations["variables"]["input"]["attributes"] = payload_attributes
        if data_fields: operations["variables"]["input"]["dataFields"] = payload_data_fields
        if remove_attachments: operations["variables"]["input"]["removedAttachments"] = remove_attachments

        map = {}
        files = {}
        
        if add_attachments:
            for i, att in enumerate(add_attachments, start=1):
                map[str(i)] = [f"variables.addedAttachments.{i-1}"]
                files[str(i)] = open(att, "rb")
        
        payload = {
            "operations": json.dumps(operations),
            "map": json.dumps(map)
        }
        
        r = self.request("post", f"{self.base_url}/graphql", headers, payload if files else operations, files if files else None).json()
        return item(r["data"]["updateItem"])

    def remove_item(
        self, 
        id: str
    ) -> bool:
        """
        Полностью удаляет предмет вашего аккаунта.

        :param id: ID предмета.
        :type id: `str`
        """
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "removeItem",
            "query": QUERIES.get("removeItem"),
            "variables": {
                "id": id,
            }
        }
        
        self.request("post", f"{self.base_url}/graphql", headers, payload)
        return True
    
    def publish_item(
        self, 
        item_id: str, 
        priority_status_id: str, 
        transaction_provider_id: TransactionProviderIds = TransactionProviderIds.LOCAL
    ) -> types.Item:
        """
        Выставляет предмет на продажу.

        :param item_id: ID предмета.
        :type item_id: `str`

        :param priority_status_id: ID статуса приоритета предмета, под которым его нужно выставить на продажу.
        :type priority_status_id: `str`

        :param transaction_provider_id: ID провайдера транзакции.
        :type transaction_provider_id: `playerokapi.types.TransactionProviderIds`

        :return: Объект опубликованного предмета.
        :rtype: `playerokapi.types.Item`
        """
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "publishItem",
            "query": QUERIES.get("publishItem"),
            "variables": {
                "input": {
                    "transactionProviderId": transaction_provider_id.name,
                    "priorityStatuses": [priority_status_id],
                    "itemId": item_id
                }
            }
        }

        r = self.request("post", f"{self.base_url}/graphql", headers, payload).json()
        return item(r["data"]["publishItem"])

    def get_items(
        self, 
        game_id: str | None = None, 
        category_id: str | None = None, 
        count: int = 24,
        status: ItemStatuses = ItemStatuses.APPROVED, 
        after_cursor: str | None = None
    ) -> types.ItemProfileList:
        """
        Получает предметы игры/приложения.\n
        Можно получить по любому из двух параметров: `game_id`, `category_id`.

        :param game_id: ID игры/приложения, _опционально_.
        :type game_id: `str` or `None`

        :param category_id: ID категории игры/приложения, _опционально_.
        :type category_id: `str` or `None`

        :param count: Кол-во предеметов, которые нужно получить (не более 24 за один запрос).
        :type count: `int`

        :param status: Тип предметов, которые нужно получать: активные или проданные. По умолчанию активные.
        :type status: `playerokapi.enums.ItemStatuses`

        :param after_cursor: Курсор, с которого будет идти парсинг (если нету - ищет с самого начала страницы), _опционально_.
        :type after_cursor: `str` or `None`
        
        :return: Страница профилей предметов.
        :rtype: `playerokapi.types.ItemProfileList`
        """
        if not any((game_id, category_id)):
            raise TypeError("Не был передан ни один из обязательных аргументов: game_id, category_id")
        
        headers = {"accept": "*/*"}
        filter = {"gameId": game_id, "status": [status.name] if status else None} if not category_id else {"gameCategoryId": category_id, "status": [status.name] if status else None}
        payload = {
            "operationName": "items",
            "variables": json.dumps({
                "pagination": {
                    "first": count,
                    "after": after_cursor
                },
                "filter": filter
            }),
            "extensions": json.dumps({
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": PERSISTED_QUERIES.get("items")
                }
            })
        }

        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        return item_profile_list(r["data"]["items"])

    def get_item(
        self, 
        id: str | None = None, 
        slug: str | None = None
    ) -> types.MyItem | types.Item | types.ItemProfile:
        """
        Получает предмет (товар).\n
        Можно получить по любому из двух параметров:

        :param id: ID предмета, _опционально_.
        :type id: `str` or `None`

        :param slug: Имя страницы предмета, _опционально_.
        :type slug: `str` or `None`
        
        :return: Объект предмета.
        :rtype: `playerokapi.types.MyItem` or `playerokapi.types.Item` or `playerokapi.types.ItemProfile`
        """
        if not any((id, slug)):
            raise TypeError("Не был передан ни один из обязательных аргументов: id, slug")
        
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "item",
            "variables": json.dumps({
                "id": id,
                "slug": slug,
                "hasSupportAccess": False,
                "showForbiddenImage": True
            }),
            "extensions": json.dumps({
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": PERSISTED_QUERIES.get("item")
                }
            })
        }
        
        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        data: dict = r["data"]["item"]
        if data["__typename"] == "MyItem": _item = my_item(data)
        elif data["__typename"] == "ItemProfile": _item = item_profile(data)
        elif data["__typename"] in ["Item", "ForeignItem"]: _item = item(data)
        else: _item = None
        return _item

    def get_item_priority_statuses(
        self, 
        item_id: str, 
        item_price: int | str
    ) -> list[types.ItemPriorityStatus]:
        """
        Получает статусы приоритетов для предмета.

        :param item_id: ID предмета.
        :type item_id: `str`

        :param item_price: Цена предмета.
        :type item_price: `int` or `str`
        
        :return: Массив статусов приоритета предмета.
        :rtype: `list[playerokapi.types.ItemPriorityStatus]`
        """
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "itemPriorityStatuses",
            "variables": json.dumps({
                "itemId": item_id,
                "price": int(item_price)
            }),
            "extensions": json.dumps({
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": PERSISTED_QUERIES.get("itemPriorityStatuses")
                }
            })
        }

        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        return [item_priority_status(status) for status in r["data"]["itemPriorityStatuses"]]

    def increase_item_priority_status(
        self, 
        item_id: str, 
        priority_status_id: str, 
        payment_method_id: TransactionPaymentMethodIds | None = None, 
        transaction_provider_id: TransactionProviderIds = TransactionProviderIds.LOCAL
    ) -> types.Item:
        """
        Повышает статус приоритета предмета.

        :param item_id: ID предмета.
        :type item_id: `str`

        :param priority_status_id: ID статуса приоритета, на который нужно изменить.
        :type priority_status_id: `int` or `str`

        :param payment_method_id: Метод оплаты, _опционально_.
        :type payment_method_id: `playerokapi.enums.TransactionPaymentMethodIds` or `None`

        :param transaction_provider_id: ID провайдера транзакции (LOCAL - с баланса кошелька на сайте).
        :type transaction_provider_id: `playerokapi.enums.TransactionProviderIds`
        
        :return: Объект обновлённого предмета.
        :rtype: `playerokapi.types.Item`
        """
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "increaseItemPriorityStatus",
            "query": QUERIES.get("increaseItemPriorityStatus"),
            "variables": {
                "input": {
                    "itemId": item_id,
                    "priorityStatuses": [priority_status_id],
                    "transactionProviderData": {
                        "paymentMethodId": payment_method_id.name if payment_method_id else None
                    },
                    "transactionProviderId": transaction_provider_id.name
                }
            }
        }

        r = self.request("post", f"{self.base_url}/graphql", headers, payload).json()
        return item(r["data"]["increaseItemPriorityStatus"])

    def get_transaction_providers(
        self, 
        direction: TransactionProviderDirections = TransactionProviderDirections.IN
    ) -> list[types.TransactionProvider]:
        """
        Получает всех провайдеров транзакций.

        :param direction: Направление транзакций (пополнение/вывод).
        :type direction: `playerokapi.enums.TransactionProviderDirections`
        
        :return: Список провайдеров транзакий.
        :rtype: `list` of `playerokapi.types.TransactionProvider`
        """
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "transactionProviders",
            "variables": json.dumps({
                "filter": {
                    "direction": direction.name if direction else None
                }
            }),
            "extensions": json.dumps({
                "persistedQuery": {
                    "version": 1, 
                    "sha256Hash": PERSISTED_QUERIES.get("transactionProviders")
                }
            })
        }

        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        return [transaction_provider(provider) for provider in r["data"]["transactionProviders"]]

    def get_transactions(
        self, 
        count: int = 24, 
        operation: TransactionOperations | None = None, 
        min_value: int | None = None,
        max_value: int | None = None, 
        provider_id: TransactionProviderIds | None = None, 
        status: TransactionStatuses | None = None,
        after_cursor: str | None = None
    ) -> TransactionList:
        """
        Получает все транзакции аккаунта.

        :param count: Кол-во транзакциий которые нужно получить (не более 24 за один запрос).
        :type count: `int`

        :param operation: Операция транзакции, _опционально_.
        :type operation: `playerokapi.enums.TransactionOperations` or `None`

        :param min_value: Минимальная сумма транзакции, _опционально_.
        :type min_value: `int` or `None`

        :param max_value: Максимальная сумма транзакции, _опционально_.
        :type max_value: `int` or `None`

        :param provider_id: ID провайдера транзакции, _опционально_.
        :type provider_id: `playerokapi.enums.TransactionProviderIds` or `None`

        :param status: Статус транзакции, _опционально_.
        :type status: `playerokapi.enums.TransactionStatuses` or `None`

        :param after_cursor: Курсор, с которого будет идти парсинг (если нету - ищет с самого начала страницы), _опционально_.
        :type after_cursor: `str` or `None`
        
        :return: Страница транзакций.
        :rtype: `playerokapi.types.TransactionList`
        """
        if not self._is_initiated:
            raise NotInitiatedError()
        
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "transactions",
            "variables": {
                "pagination": {
                    "first": count, 
                    "after": after_cursor
                }, 
                "filter": {
                    "userId": self.id
                }, 
                "hasSupportAccess": False
            },
            "extensions": {
                "persistedQuery": {
                    "version": 1, 
                    "sha256Hash": PERSISTED_QUERIES.get("transactions")
                }
            }
        }
        
        if operation: payload["variables"]["filter"]["operation"] = [operation.name]
        if min_value or max_value:
            payload["variables"]["filter"]["value"] = {}
            if min_value: payload["variables"]["filter"]["value"]["min"] = str(min_value)
            if max_value: payload["variables"]["filter"]["value"]["max"] = str(max_value)
        if provider_id: payload["variables"]["filter"]["providerId"] = [provider_id.name]
        if status: payload["variables"]["filter"]["status"] = [status.name]

        payload["variables"] = json.dumps(payload["variables"])
        payload["extensions"] = json.dumps(payload["extensions"])
        
        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        return transaction_list(r["data"]["transactions"])
    
    def get_sbp_bank_members(self) -> list[SBPBankMember]:
        """
        Получает всех членов банка СБП.

        :return: Объект провайдера транзакции.
        :rtype: `list` of `playerokapi.types.SBPBankMember`
        """
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "SbpBankMembers",
            "variables": {},
            "extensions": json.dumps({
                "persistedQuery": {
                    "version": 1, 
                    "sha256Hash": PERSISTED_QUERIES.get("SbpBankMembers")
                }
            })
        }

        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        return [sbp_bank_member(member) for member in r["data"]["sbpBankMembers"]]
    
    def get_verified_cards(
        self, 
        count: int = 24, 
        after_cursor: str | None = None,
        direction: SortDirections = SortDirections.ASC
    ) -> types.UserBankCardList:
        """
        Получает верифицированные карты аккаунта.

        :param count: Кол-во банковских карт, которые нужно получить (не более 24 за один запрос).
        :type count: `int`

        :param after_cursor: Курсор, с которого будет идти парсинг (если нету - ищет с самого начала страницы), _опционально_.
        :type after_cursor: `str` or `None`

        :param direction: Тип сортировки банковских карт.
        :type direction: `playerokapi.enums.SortDirections`
        
        :return: Страница банковских карт пользователя.
        :rtype: `playerokapi.types.UserBankCardList`
        """
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "verifiedCards",
            "variables": json.dumps({
                "pagination": {
                    "first": count, 
                    "after": after_cursor
                }, 
                "sort": {
                    "direction": direction.name
                }, 
                "field": "createdAt"
            }),
            "extensions": json.dumps({
                "persistedQuery": {
                    "version": 1, 
                    "sha256Hash": PERSISTED_QUERIES.get("verifiedCards")
                }
            })
        }

        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        return user_bank_card_list(r["data"]["verifiedCards"])
    
    def delete_card(
        self, 
        card_id: str
    ) -> bool:
        """
        Удаляет карту из сохранённых в аккаунте.

        :param card_id: ID банковской карты.
        :type card_id: `str`
        
        :return: True, если карта удалилась, иначе False
        :rtype: `bool`
        """
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "deleteCard",
            "query": QUERIES.get("deleteCard"),
            "variables": {
                "input": {
                    "cardId": card_id
                }
            }
        }

        r = self.request("post", f"{self.base_url}/graphql", headers, payload).json()
        return r["data"]["deleteCard"]
    
    def request_withdrawal(
        self, 
        provider: TransactionProviderIds, 
        account: str, 
        value: int,
        payment_method_id: TransactionPaymentMethodIds | None = None,
        sbp_bank_member_id: str | None = None
    ) -> types.Transaction:
        """
        Создаёт запрос на вывод средств с баланса аккаунта.

        :param provider: Провайдер транзакции.
        :type provider: `playerokapi.enums.TransactionProviderIds`

        :param account: ID добавленной карты (или номер телефона, если провайдер СБП), на которую нужно совершить вывод.
        :type account: `str`

        :param value: Сумма вывода.
        :type value: `int`

        :param payment_method_id: ID платёжного метода, _опционально_.
        :type payment_method_id: `playerokapi.enums.TransactionPaymentMethodIds` or `None`

        :param sbp_bank_member_id: ID члена банка СБП (только если указан провайдер СБП), _опционально_.
        :type sbp_bank_member_id: `str` or `None`
        
        :return: Объект транзакции вывода.
        :rtype: `playerokapi.types.Transaction`
        """
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "requestWithdrawal",
            "query": QUERIES.get("requestWithdrawal"),
            "variables": {
                "input": {
                    "provider": provider.name,
                    "account": account,
                    "value": value,
                    "providerData": {
                        "paymentMethodId": payment_method_id.name if payment_method_id else None,
                        "sbpBankMemberId": sbp_bank_member_id if sbp_bank_member_id else None
                    }
                }
            }
        }
        
        r = self.request("post", f"{self.base_url}/graphql", headers, payload).json()
        return transaction(r["data"]["requestWithdrawal"])
    
    def remove_transaction(
        self, 
        transaction_id: str
    ) -> types.Transaction:
        """
        Удаляет транзакцию (например, можно отменить вывод).

        :param transaction_id: ID транзакции.
        :type transaction_id: `str`
        
        :return: Объект отменённой транзакции.
        :rtype: `playerokapi.types.Transaction`
        """
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "removeTransaction",
            "query": QUERIES.get("removeTransaction"),
            "variables": {
                "id": transaction_id
            }
        }

        r = self.request("post", f"{self.base_url}/graphql", headers, payload).json()
        return transaction(r["data"]["removeTransaction"])