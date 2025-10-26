from __future__ import annotations
import tls_requests
from typing import *
import json
import random
import time
from logging import getLogger

from . import types
from .exceptions import *
from .parser import *
from .enums import *


def get_account() -> None | Account:
    if hasattr(Account, "instance"):
        return getattr(Account, "instance")

class Account:
    """
    Класс, описывающий данные и методы Playerok аккаунта.

    :param token: Токен аккаунта.
    :type token: `str`

    :param user_agent: Юзер-агент браузера, _опционально_.
    :type user_agent: `str`

    :param proxy: IPV4 прокси в формате: `user:pass@ip:port` или `ip:port`, _опционально_.
    :type proxy: `str`

    :param requests_timeout: Таймаут ожидания ответов на запросы.
    :type requests_timeout: `int`

    :param request_max_retries: Максимальное количество повторных попыток отправки запроса, если была обнаружена CloudFlare защита.
    :type request_max_retries: `int`
    """

    def __new__(cls, *args, **kwargs) -> Account:
        if not hasattr(cls, "instance"):
            cls.instance = super(Account, cls).__new__(cls)
        return getattr(cls, "instance")

    def __init__(
            self, 
            token: str, 
            user_agent: str = "", 
            proxy: str = None, 
            requests_timeout: int = 15,
            request_max_retries: int = 5,
            **kwargs
        ):
        self.token = token
        """ Токен сессии аккаунта. """
        self.user_agent = user_agent
        """ Юзер-агент браузера. """
        self.requests_timeout = requests_timeout
        """ Таймаут ожидания ответов на запросы. """
        self.proxy = proxy
        """ Прокси. """
        self.request_max_retries = request_max_retries
        """ Максимальное количество повторных попыток отправки запроса. """

        self.base_url = "https://playerok.com"
        """ Базовый URL для всех запросов. """

        self.id: str | None = None
        """ ID аккаунта. \n\n_Заполняется при первом использовании get()_ """
        self.username: str | None = None
        """ Никнейм аккаунта. \n\n_Заполняется при первом использовании get()_ """
        self.email: str | None = None
        """ Email почта аккаунта. \n\n_Заполняется при первом использовании get()_ """
        self.role: str | None = None
        """ Роль аккаунта. \n\n_Заполняется при первом использовании get()_ """
        self.support_chat_id: str | None = None
        """ ID чата поддержки. \n\n_Заполняется при первом использовании get()_ """
        self.system_chat_id: str | None = None
        """ ID системного чата. \n\n_Заполняется при первом использовании get()_ """
        self.unread_chats_counter: int | None = None
        """ Количество непрочитанных чатов. \n\n_Заполняется при первом использовании get()_ """
        self.is_blocked: bool | None = None
        """ Заблокирован ли аккаунт. \n\n_Заполняется при первом использовании get()_ """
        self.is_blocked_for: str | None = None
        """ Причина блокировки аккаунта. \n\n_Заполняется при первом использовании get()_ """
        self.created_at: str | None = None
        """ Дата создания аккаунта. \n\n_Заполняется при первом использовании get()_ """
        self.last_item_created_at: str | None = None
        """ Дата создания последнего предмета. \n\n_Заполняется при первом использовании get()_ """
        self.has_frozen_balance: bool | None = None
        """ Заморожен ли баланс аккаунта. \n\n_Заполняется при первом использовании get()_ """
        self.has_confirmed_phone_number: bool | None = None
        """ Подтверждён ли номер телефона. \n\n_Заполняется при первом использовании get()_ """
        self.can_publish_items: bool | None = None
        """ Может ли продавать предметы. \n\n_Заполняется при первом использовании get()_ """
        self.profile: AccountProfile | None = None
        """ Профиль аккаунта (не путать с профилем пользователя). \n\n_Заполняется при первом использовании get()_ """

        self.__client = tls_requests.Client(proxy=f"http://{self.proxy.replace('https://', '').replace('http://', '')}" if self.proxy else None)
        self.__logger = getLogger("playerokapi")

    def request(self, method: str, url: str, headers: dict[str, str], 
                payload: dict[str, str] | None = None, files: dict | None = None) -> requests.Response:
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

        agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.132 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.96 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.90 Mobile Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edg/118.0.2088.62 Chrome/118.0.5993.90 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:119.0) Gecko/20100101 Firefox/119.0",
            "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36 OPR/88.0.0.0",
            "Opera/9.80 (Windows NT 6.3; U; en) Presto/2.12.388 Version/12.16"
        ]
        _headers = {
            "accept": "*/*",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "access-control-allow-headers": "sentry-trace, baggage",
            "apollo-require-preflight": "true",
            "apollographql-client-name": "web",
            "content-type": "application/json",
            "origin": "https://playerok.com",
            "priority": "u=1, i",
            "referer": "https://playerok.com/",
            "sec-ch-ua": "\"Chromium\";v=\"140\", \"Not=A?Brand\";v=\"24\", \"Google Chrome\";v=\"140\"",
            "sec-ch-ua-arch": "\"x86\"",
            "sec-ch-ua-bitness": "\"64\"",
            "sec-ch-ua-full-version": "\"140.0.7339.186\"",
            "sec-ch-ua-full-version-list": "\"Chromium\";v=\"140.0.7339.186\", \"Not=A?Brand\";v=\"24.0.0.0\", \"Google Chrome\";v=\"140.0.7339.186\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-model": "\"\"",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-ch-ua-platform-version": "\"19.0.0\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-gql-op": "viewer",
            "x-timezone-offset": "-180"
        }
        for k, v in _headers.items():
            if k not in headers.keys():
                headers[k] = v
                
        def make_req():
            headers["cookie"] = f"token={self.token}"
            headers["user-agent"] = self.user_agent if self.user_agent else random.choice(agents)

            if method == "get":
                r = self.__client.get(url=url, params=payload, headers=headers, 
                            timeout=self.requests_timeout)
            elif method == "post":
                r = self.__client.post(url=url, json=payload if not files else None, 
                                data=payload if files else None, headers=headers, 
                                files=files, timeout=self.requests_timeout)
            else: 
                return
            return r
        resp = make_req()

        cloudflare_signatures = [
            "<title>Just a moment...</title>",
            "window._cf_chl_opt",
            "Enable JavaScript and cookies to continue",
            "Checking your browser before accessing",
            "cf-browser-verification",
            "Cloudflare Ray ID"
        ]
        if any(sig in resp.text for sig in cloudflare_signatures):
            for attempt in range(self.request_max_retries):
                resp = make_req()
                if not any(sig in resp.text for sig in cloudflare_signatures):
                    break
                delay = min(120.0, 5.0 * (2 ** attempt))
                self.__logger.error(f"Cloudflare Detected, пробую отправить запрос снова через {delay} сек.")
                time.sleep(delay)
                self.__client = tls_requests.Client(proxy=f"http://{self.proxy.replace('https://', '').replace('http://', '')}" if self.proxy else None)
            else:
                raise CloudflareDetectedException(resp)
        try:
            if "errors" in resp.json():
                raise RequestError(resp)
        except:
            pass
        if resp.status_code != 200:
           raise RequestFailedError(resp)
        return resp
    
    def get(self) -> Account:
        """
        Получает/обновляет данные об аккаунте.

        :return: Профиль аккаунта с обновлёнными данными.
        :rtype: `playerokapi.Account`
        """
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "viewer",
            "query": "query viewer {\n  viewer {\n    ...Viewer\n    __typename\n  }\n}\n\nfragment Viewer on User {\n  id\n  username\n  email\n  role\n  hasFrozenBalance\n  supportChatId\n  systemChatId\n  unreadChatsCounter\n  isBlocked\n  isBlockedFor\n  createdAt\n  lastItemCreatedAt\n  hasConfirmedPhoneNumber\n  canPublishItems\n  profile {\n    id\n    avatarURL\n    testimonialCounter\n    __typename\n  }\n  __typename\n}",
            "query": "query viewer {\n  viewer {\n    ...Viewer\n    __typename\n  }\n}\n\nfragment Viewer on User {\n  id\n  username\n  email\n  role\n  hasFrozenBalance\n  supportChatId\n  systemChatId\n  unreadChatsCounter\n  isBlocked\n  isBlockedFor\n  createdAt\n  lastItemCreatedAt\n  hasConfirmedPhoneNumber\n  canPublishItems\n  profile {\n    id\n    avatarURL\n    testimonialCounter\n    __typename\n  }\n  __typename\n}",
            "variables": {}
        }
        r = self.request("post", f"{self.base_url}/graphql", headers, payload)
        rjson = r.json()
        data: dict = rjson["data"]["viewer"]
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
        
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "user",
            "variables": json.dumps({"username": self.username, "hasSupportAccess": False}, ensure_ascii=False),
            "extensions": json.dumps({"persistedQuery": {"version": 1, "sha256Hash": "2e2e3b656d2ba48e0b2cd5eeedf88ef70e4aabb4ac4d9d9e9b8feff343a37d98"}}, ensure_ascii=False)
        }
        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        data: dict = r["data"]["user"]
        if data.get("__typename") == "User": self.profile = account_profile(data)
        return self
    
    def get_user(self, id: str | None = None, username: str | None = None) -> types.UserProfile:
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
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "user",
            "variables": json.dumps({"id": id, "username": username, "hasSupportAccess": False}, ensure_ascii=False),
            "extensions": json.dumps({"persistedQuery": {"version": 1, "sha256Hash": "2e2e3b656d2ba48e0b2cd5eeedf88ef70e4aabb4ac4d9d9e9b8feff343a37d98"}}, ensure_ascii=False)
        }
        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        data: dict = r["data"]["user"]
        if data.get("__typename") == "UserFragment": profile = data
        elif data.get("__typename") == "User": profile = data.get("profile")
        else: profile = None
        return user_profile(profile)

    def get_deals(self, count: int = 24, status: list[ItemDealStatuses] | None = None, 
                  direction: ItemDealDirections | None = None, after_cursor: str = None) -> types.ItemDealList:
        """
        Получает сделки аккаунта.

        :param count: Кол-во сделок, которые нужно получить (не более 24 за один запрос).
        :type count: `int`

        :param status: Статусы заявок, которые нужно получать, _опционально_.
        :type status: `list[playerokapi.enums.ItemDealsStatuses]` or `None`

        :param direction: Направление сделок, _опционально_.
        :type direction: `playerokapi.enums.ItemDealsDirections` or `None`

        :param after_cursor: Курсор, с которого будет идти парсинг (если нету - ищет с самого начала страницы), _опционально_.
        :type after_cursor: `str`
        
        :return: Страница сделок.
        :rtype: `playerokapi.types.ItemDealList`
        """
        str_statuses = [] if status else None
        if status:
            for v in status:
                str_statuses.append(v.name)
        str_direction = direction.name if direction else None
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "deals",
            "variables": json.dumps({"pagination": {"first": count, "after": after_cursor}, "filter": {"userId": self.id, "direction": str_direction, "status": str_statuses}, "showForbiddenImage": True}, ensure_ascii=False),
            "extensions": json.dumps({"persistedQuery": {"version": 1, "sha256Hash": "c3b623b5fe0758cf91b2335ebf36ff65f8650a6672a792a3ca7a36d270d396fb"}}, ensure_ascii=False)
        }
        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        return item_deal_list(r["data"]["deals"])

    def get_deal(self, deal_id: str) -> types.ItemDeal:
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
            "variables": json.dumps({"id": deal_id, "hasSupportAccess": False, "showForbiddenImage": True}, ensure_ascii=False),
            "extensions": json.dumps({"persistedQuery": {"version": 1, "sha256Hash": "1a9015540fceaa065033750a98d3613ee1c8e73371cedd4d8ef0e7eb5b8ff470"}}, ensure_ascii=False)
        }
        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        return item_deal(r["data"]["deal"])
    
    def update_deal(self, deal_id: str, new_status: ItemDealStatuses) -> types.ItemDeal:
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
            "query": "mutation updateDeal($input: UpdateItemDealInput!) {\n  updateDeal(input: $input) {\n    ...RegularItemDeal\n    __typename\n  }\n}\n\nfragment RegularItemDeal on ItemDeal {\n  id\n  status\n  direction\n  statusExpirationDate\n  statusDescription\n  obtaining\n  hasProblem\n  reportProblemEnabled\n  completedBy {\n    ...MinimalUserFragment\n    __typename\n  }\n  props {\n    ...ItemDealProps\n    __typename\n  }\n  prevStatus\n  completedAt\n  createdAt\n  logs {\n    ...ItemLog\n    __typename\n  }\n  transaction {\n    ...ItemDealTransaction\n    __typename\n  }\n  user {\n    ...UserEdgeNode\n    __typename\n  }\n  chat {\n    ...RegularChatId\n    __typename\n  }\n  item {\n    ...PartialDealItem\n    __typename\n  }\n  testimonial {\n    ...RegularItemDealTestimonial\n    __typename\n  }\n  obtainingFields {\n    ...GameCategoryDataFieldWithValue\n    __typename\n  }\n  commentFromBuyer\n  __typename\n}\n\nfragment MinimalUserFragment on UserFragment {\n  id\n  username\n  role\n  __typename\n}\n\nfragment ItemDealProps on ItemDealProps {\n  autoConfirmPeriod\n  __typename\n}\n\nfragment ItemLog on ItemLog {\n  id\n  event\n  createdAt\n  user {\n    ...UserEdgeNode\n    __typename\n  }\n  __typename\n}\n\nfragment UserEdgeNode on UserFragment {\n  ...RegularUserFragment\n  __typename\n}\n\nfragment RegularUserFragment on UserFragment {\n  id\n  username\n  role\n  avatarURL\n  isOnline\n  isBlocked\n  rating\n  testimonialCounter\n  createdAt\n  supportChatId\n  systemChatId\n  __typename\n}\n\nfragment ItemDealTransaction on Transaction {\n  id\n  operation\n  direction\n  providerId\n  status\n  value\n  createdAt\n  paymentMethodId\n  statusExpirationDate\n  __typename\n}\n\nfragment RegularChatId on Chat {\n  id\n  __typename\n}\n\nfragment PartialDealItem on Item {\n  ...PartialDealMyItem\n  ...PartialDealForeignItem\n  __typename\n}\n\nfragment PartialDealMyItem on MyItem {\n  id\n  slug\n  priority\n  status\n  name\n  price\n  priorityPrice\n  rawPrice\n  statusExpirationDate\n  sellerType\n  approvalDate\n  createdAt\n  priorityPosition\n  viewsCounter\n  feeMultiplier\n  comment\n  attachments {\n    ...RegularFile\n    __typename\n  }\n  user {\n    ...UserEdgeNode\n    __typename\n  }\n  game {\n    ...RegularGameProfile\n    __typename\n  }\n  category {\n    ...MinimalGameCategory\n    __typename\n  }\n  dataFields {\n    ...GameCategoryDataFieldWithValue\n    __typename\n  }\n  obtainingType {\n    ...MinimalGameCategoryObtainingType\n    __typename\n  }\n  __typename\n}\n\nfragment RegularFile on File {\n  id\n  url\n  filename\n  mime\n  __typename\n}\n\nfragment RegularGameProfile on GameProfile {\n  id\n  name\n  type\n  slug\n  logo {\n    ...PartialFile\n    __typename\n  }\n  __typename\n}\n\nfragment PartialFile on File {\n  id\n  url\n  __typename\n}\n\nfragment MinimalGameCategory on GameCategory {\n  id\n  slug\n  name\n  __typename\n}\n\nfragment GameCategoryDataFieldWithValue on GameCategoryDataFieldWithValue {\n  id\n  label\n  type\n  inputType\n  copyable\n  hidden\n  required\n  value\n  __typename\n}\n\nfragment MinimalGameCategoryObtainingType on GameCategoryObtainingType {\n  id\n  name\n  description\n  gameCategoryId\n  noCommentFromBuyer\n  instructionForBuyer\n  instructionForSeller\n  sequence\n  feeMultiplier\n  props {\n    minTestimonialsForSeller\n    __typename\n  }\n  __typename\n}\n\nfragment PartialDealForeignItem on ForeignItem {\n  id\n  slug\n  priority\n  status\n  name\n  price\n  rawPrice\n  sellerType\n  approvalDate\n  priorityPosition\n  createdAt\n  viewsCounter\n  feeMultiplier\n  comment\n  attachments {\n    ...RegularFile\n    __typename\n  }\n  user {\n    ...UserEdgeNode\n    __typename\n  }\n  game {\n    ...RegularGameProfile\n    __typename\n  }\n  category {\n    ...MinimalGameCategory\n    __typename\n  }\n  dataFields {\n    ...GameCategoryDataFieldWithValue\n    __typename\n  }\n  obtainingType {\n    ...MinimalGameCategoryObtainingType\n    __typename\n  }\n  __typename\n}\n\nfragment RegularItemDealTestimonial on Testimonial {\n  id\n  status\n  text\n  rating\n  createdAt\n  updatedAt\n  creator {\n    ...RegularUserFragment\n    __typename\n  }\n  moderator {\n    ...RegularUserFragment\n    __typename\n  }\n  user {\n    ...RegularUserFragment\n    __typename\n  }\n  __typename\n}"
        }

        r = self.request("post", f"{self.base_url}/graphql", headers, payload).json()
        return item_deal(r["data"]["updateDeal"])

    def get_games(self, count: int = 24, type: GameTypes | None = None, 
                  after_cursor: str = None) -> types.GameList:
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
            "variables": json.dumps({"pagination": {"first": count, "after": after_cursor}, "filter": {"type": type.name} if type else {}}, ensure_ascii=False),
            "extensions": json.dumps({"persistedQuery": {"version": 1, "sha256Hash": "b9f6675fd5923bc5c247388e8e3209c3eede460ed328dbe6a9ec8e6428d3649b"}}, ensure_ascii=False)
        }
        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        return game_list(r["data"]["games"])
    
    def get_game(self, id: str | None = None, slug: str | None = None) -> types.Game:
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
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "GamePage",
            "variables": json.dumps({"id": id, "slug": slug}, ensure_ascii=False),
            "extensions": json.dumps({"persistedQuery": {"version": 1, "sha256Hash": "12e701986f07aaaf57327b1133b9a1f3050b851c99b19293adfac40cfed0e41d"}}, ensure_ascii=False)
        }
        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        return game(r["data"]["game"])

    def get_game_category(self, id: str | None = None, game_id: str | None = None,
                          slug: str | None = None) -> types.GameCategory:
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
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "GamePageCategory",
            "variables": json.dumps({"id": id, "gameId": game_id, "slug": slug}, ensure_ascii=False),
            "extensions": json.dumps({"persistedQuery": {"version": 1, "sha256Hash": "d81943c23bc558591f70286ad69bb6bf7f6229d04aae39fb0a9701d78a9fd749"}}, ensure_ascii=False)
        }
        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        return game_category(r["data"]["gameCategory"])
    
    def get_game_category_agreements(self, game_category_id: str, user_id: str | None = None,
                                     count: int = 24, after_cursor: str | None = None) -> types.GameCategoryAgreementList:
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
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "gameCategoryAgreements",
            "variables": json.dumps({"pagination": {"first": count, "after": after_cursor}, "filter": {"gameCategoryId": game_category_id, "userId": user_id if user_id else self.id}}, ensure_ascii=False),
            "extensions": json.dumps({"persistedQuery": {"version": 1, "sha256Hash": "3ea4b047196ed9f84aa5eb652299c4bd73f2e99e9fdf4587877658d9ea6330f6 "}}, ensure_ascii=False)
        }
        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        return game_category_agreement_list(r["data"]["gameCategoryAgreements"])
    
    def get_game_category_obtaining_types(self, game_category_id: str, count: int = 24,
                                          after_cursor: str | None = None) -> types.GameCategoryObtainingTypeList:
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
            "variables": json.dumps({"pagination": {"first": count, "after": after_cursor}, "filter": {"gameCategoryId": game_category_id}}, ensure_ascii=False),
            "extensions": json.dumps({"persistedQuery": {"version": 1, "sha256Hash": "15b0991414821528251930b4c8161c299eb39882fd635dd5adb1a81fb0570aea"}}, ensure_ascii=False)
        }
        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        return game_category_obtaining_type_list(r["data"]["gameCategoryObtainingTypes"])
    
    def get_game_category_instructions(self, game_category_id: str, obtaining_type_id: str, count: int = 24,
                                       type: GameCategoryInstructionTypes | None = None, after_cursor: str | None = None) -> types.GameCategoryInstructionList:
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
            "variables": json.dumps({"pagination": {"first": count, "after": after_cursor}, "filter": {"gameCategoryId": game_category_id, "obtainingTypeId": obtaining_type_id, "type": type.name if type else None}}, ensure_ascii=False),
            "extensions": json.dumps({"persistedQuery": {"version": 1, "sha256Hash": "5991cead6a8ca46195bc4f7ae3164e7606105dbb82834c910658edeb0a1d1918"}}, ensure_ascii=False)
        }
        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        return game_category_instruction_list(r["data"]["gameCategoryInstructions"])

    def get_game_category_data_fields(self, game_category_id: str, obtaining_type_id: str, count: int = 24,
                                      type: GameCategoryDataFieldTypes | None = None, after_cursor: str | None = None) -> types.GameCategoryDataFieldList:
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
            "variables": json.dumps({"pagination": {"first": count, "after": after_cursor}, "filter": {"gameCategoryId": game_category_id, "obtainingTypeId": obtaining_type_id, "type": type.name if type else None}}, ensure_ascii=False),
            "extensions": json.dumps({"persistedQuery": {"version": 1, "sha256Hash": "6fdadfb9b05880ce2d307a1412bc4f2e383683061c281e2b65a93f7266ea4a49"}}, ensure_ascii=False)
        }
        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        return game_category_data_field_list(r["data"]["gameCategoryDataFields"])
    
    def get_chats(self, count: int = 24, type: ChatTypes | None = None,
                  status: ChatStatuses | None = None, after_cursor: str | None = None) -> types.ChatList:
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
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "chats",
            "variables": json.dumps({"pagination": {"first": count, "after": after_cursor}, "filter": {"userId": self.id, "type": type.name if type else None, "status": status.name if status else None}, "hasSupportAccess": False}, ensure_ascii=False),
            "extensions": json.dumps({"persistedQuery": {"version": 1, "sha256Hash": "f7e6ee4fbb892abbd196342110e2abb0be309e2bd6671abb2963d0809c511d05"}}, ensure_ascii=False)
        }
        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        return chat_list(r["data"]["chats"])
    
    def get_chat(self, chat_id: str) -> types.Chat:
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
            "variables": json.dumps({"id": chat_id, "hasSupportAccess": False}, ensure_ascii=False),
            "extensions": json.dumps({"persistedQuery": {"version": 1, "sha256Hash": "bb024dc0652fc7c1302a64a117d56d99fb0d726eb4b896ca803dca55f611d933"}}, ensure_ascii=False)
        }
        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        return chat(r["data"]["chat"])
    
    def get_chat_by_username(self, username: str) -> types.Chat | None:
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
                if any([user for user in chat.users if user.username.lower() == username.lower()]):
                    return chat
            if not chats.page_info.has_next_page:
                break
            next_cursor = chats.page_info.end_cursor
    
    def get_chat_messages(self, chat_id: str, count: int = 24,
                          after_cursor: str | None = None) -> types.ChatMessageList:
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
            "variables": json.dumps({"pagination": {"first": count, "after": after_cursor}, "filter": {"chatId": chat_id}, "hasSupportAccess": False, "showForbiddenImage": True}, ensure_ascii=False),
            "extensions": json.dumps({"persistedQuery": {"version": 1, "sha256Hash": "8640a1c606ed878f15836a3ae5d5a3da9dccb0bd809f073d010680a8e4dcd06a"}}, ensure_ascii=False)
        }
        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        return chat_message_list(r["data"]["chatMessages"])

    def mark_chat_as_read(self, chat_id: str) -> types.Chat:
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
            "query": "mutation markChatAsRead($input: MarkChatAsReadInput!) {\n	markChatAsRead(input: $input) {\n		...RegularChat\n		__typename\n	}\n}\n\nfragment RegularChat on Chat {\n	id\n	type\n	unreadMessagesCounter\n	bookmarked\n	isTextingAllowed\n	owner {\n		...ChatParticipant\n		__typename\n	}\n	agent {\n		...ChatParticipant\n		__typename\n	}\n	participants {\n		...ChatParticipant\n		__typename\n	}\n	deals {\n		...ChatActiveItemDeal\n		__typename\n	}\n	status\n	startedAt\n	finishedAt\n	__typename\n}\n\nfragment ChatParticipant on UserFragment {\n	...RegularUserFragment\n	__typename\n}\n\nfragment RegularUserFragment on UserFragment {\n	id\n	username\n	role\n	avatarURL\n	isOnline\n	isBlocked\n	rating\n	testimonialCounter\n	createdAt\n	supportChatId\n	systemChatId\n	__typename\n}\n\nfragment ChatActiveItemDeal on ItemDealProfile {\n	id\n	direction\n	status\n	hasProblem\n	testimonial {\n		id\n		rating\n		__typename\n	}\n	item {\n		...ChatDealItemEdgeNode\n		__typename\n	}\n	user {\n		...RegularUserFragment\n		__typename\n	}\n	__typename\n}\n\nfragment ChatDealItemEdgeNode on ItemProfile {\n	...ChatDealMyItemEdgeNode\n	...ChatDealForeignItemEdgeNode\n	__typename\n}\n\nfragment ChatDealMyItemEdgeNode on MyItemProfile {\n	id\n	slug\n	priority\n	status\n	name\n	price\n	rawPrice\n	statusExpirationDate\n	sellerType\n	attachment {\n		...PartialFile\n		__typename\n	}\n	user {\n		...UserItemEdgeNode\n		__typename\n	}\n	approvalDate\n	createdAt\n	priorityPosition\n	feeMultiplier\n	__typename\n}\n\nfragment PartialFile on File {\n	id\n	url\n	__typename\n}\n\nfragment UserItemEdgeNode on UserFragment {\n	...UserEdgeNode\n	__typename\n}\n\nfragment UserEdgeNode on UserFragment {\n	...RegularUserFragment\n	__typename\n}\n\nfragment ChatDealForeignItemEdgeNode on ForeignItemProfile {\n	id\n	slug\n	priority\n	status\n	name\n	price\n	rawPrice\n	sellerType\n	attachment {\n		...PartialFile\n		__typename\n	}\n	user {\n		...UserItemEdgeNode\n		__typename\n	}\n	approvalDate\n	priorityPosition\n	createdAt\n	feeMultiplier\n	__typename\n}",
            "variables": {
                "input": {
                    "chatId": chat_id
                }
            }
        }
        r = self.request("post", f"{self.base_url}/graphql", headers, payload).json()
        return chat(r["data"]["markChatAsRead"])
    
    def send_message(self, chat_id: str, text: str | None = None,
                     photo_file_path: str | None = None, mark_chat_as_read: bool = False) -> types.ChatMessage:
        """
        Отправляет сообщение в чат.\n
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
        :rtype: `playerokapi.types.ChatMessage`
        """
        if mark_chat_as_read:
            self.mark_chat_as_read(chat_id=chat_id)
        headers = {"accept": "*/*"}
        if photo_file_path: query = "mutation createChatMessage($input: CreateChatMessageInput!, $file: Upload, $showForbiddenImage: Boolean) {\n  createChatMessage(input: $input, file: $file) {\n    ...RegularChatMessage\n    __typename\n  }\n}\n\nfragment RegularChatMessage on ChatMessage {\n  id\n  text\n  createdAt\n  deletedAt\n  isRead\n  isSuspicious\n  isBulkMessaging\n  game {\n    ...RegularGameProfile\n    __typename\n  }\n  file {\n    ...PartialFile\n    __typename\n  }\n  user {\n    ...ChatMessageUserFields\n    __typename\n  }\n  deal {\n    ...ChatMessageItemDeal\n    __typename\n  }\n  item {\n    ...ItemEdgeNode\n    __typename\n  }\n  transaction {\n    ...RegularTransaction\n    __typename\n  }\n  moderator {\n    ...UserEdgeNode\n    __typename\n  }\n  eventByUser {\n    ...ChatMessageUserFields\n    __typename\n  }\n  eventToUser {\n    ...ChatMessageUserFields\n    __typename\n  }\n  isAutoResponse\n  event\n  buttons {\n    ...ChatMessageButton\n    __typename\n  }\n  images {\n    ...RegularFile\n    __typename\n  }\n  __typename\n}\n\nfragment RegularGameProfile on GameProfile {\n  id\n  name\n  type\n  slug\n  logo {\n    ...PartialFile\n    __typename\n  }\n  __typename\n}\n\nfragment PartialFile on File {\n  id\n  url\n  __typename\n}\n\nfragment ChatMessageUserFields on UserFragment {\n  ...UserEdgeNode\n  __typename\n}\n\nfragment UserEdgeNode on UserFragment {\n  ...RegularUserFragment\n  __typename\n}\n\nfragment RegularUserFragment on UserFragment {\n  id\n  username\n  role\n  avatarURL\n  isOnline\n  isBlocked\n  rating\n  testimonialCounter\n  createdAt\n  supportChatId\n  systemChatId\n  __typename\n}\n\nfragment ChatMessageItemDeal on ItemDeal {\n  id\n  direction\n  status\n  statusDescription\n  hasProblem\n  user {\n    ...ChatParticipant\n    __typename\n  }\n  testimonial {\n    ...ChatMessageDealTestimonial\n    __typename\n  }\n  item {\n    id\n    name\n    price\n    slug\n    rawPrice\n    sellerType\n    user {\n      ...ChatParticipant\n      __typename\n    }\n    category {\n      id\n      __typename\n    }\n    attachments(showForbiddenImage: $showForbiddenImage) {\n      ...PartialFile\n      __typename\n    }\n    isAttachmentsForbidden\n    comment\n    dataFields {\n      ...GameCategoryDataFieldWithValue\n      __typename\n    }\n    obtainingType {\n      ...GameCategoryObtainingType\n      __typename\n    }\n    __typename\n  }\n  obtainingFields {\n    ...GameCategoryDataFieldWithValue\n    __typename\n  }\n  chat {\n    id\n    type\n    __typename\n  }\n  transaction {\n    id\n    statusExpirationDate\n    __typename\n  }\n  statusExpirationDate\n  commentFromBuyer\n  __typename\n}\n\nfragment ChatParticipant on UserFragment {\n  ...RegularUserFragment\n  __typename\n}\n\nfragment ChatMessageDealTestimonial on Testimonial {\n  id\n  status\n  text\n  rating\n  createdAt\n  updatedAt\n  creator {\n    ...RegularUserFragment\n    __typename\n  }\n  moderator {\n    ...RegularUserFragment\n    __typename\n  }\n  user {\n    ...RegularUserFragment\n    __typename\n  }\n  __typename\n}\n\nfragment GameCategoryDataFieldWithValue on GameCategoryDataFieldWithValue {\n  id\n  label\n  type\n  inputType\n  copyable\n  hidden\n  required\n  value\n  __typename\n}\n\nfragment GameCategoryObtainingType on GameCategoryObtainingType {\n  id\n  name\n  description\n  gameCategoryId\n  noCommentFromBuyer\n  instructionForBuyer\n  instructionForSeller\n  sequence\n  feeMultiplier\n  agreements {\n    ...MinimalGameCategoryAgreement\n    __typename\n  }\n  props {\n    minTestimonialsForSeller\n    __typename\n  }\n  __typename\n}\n\nfragment MinimalGameCategoryAgreement on GameCategoryAgreement {\n  description\n  iconType\n  id\n  sequence\n  __typename\n}\n\nfragment ItemEdgeNode on ItemProfile {\n  ...MyItemEdgeNode\n  ...ForeignItemEdgeNode\n  __typename\n}\n\nfragment MyItemEdgeNode on MyItemProfile {\n  id\n  slug\n  priority\n  status\n  name\n  price\n  rawPrice\n  statusExpirationDate\n  sellerType\n  attachment(showForbiddenImage: $showForbiddenImage) {\n    ...PartialFile\n    __typename\n  }\n  isAttachmentsForbidden\n  user {\n    ...UserItemEdgeNode\n    __typename\n  }\n  approvalDate\n  createdAt\n  priorityPosition\n  viewsCounter\n  feeMultiplier\n  __typename\n}\n\nfragment UserItemEdgeNode on UserFragment {\n  ...UserEdgeNode\n  __typename\n}\n\nfragment ForeignItemEdgeNode on ForeignItemProfile {\n  id\n  slug\n  priority\n  status\n  name\n  price\n  rawPrice\n  sellerType\n  attachment(showForbiddenImage: $showForbiddenImage) {\n    ...PartialFile\n    __typename\n  }\n  isAttachmentsForbidden\n  user {\n    ...UserItemEdgeNode\n    __typename\n  }\n  approvalDate\n  priorityPosition\n  createdAt\n  viewsCounter\n  feeMultiplier\n  __typename\n}\n\nfragment RegularTransaction on Transaction {\n  id\n  operation\n  direction\n  providerId\n  provider {\n    ...RegularTransactionProvider\n    __typename\n  }\n  user {\n    ...RegularUserFragment\n    __typename\n  }\n  creator {\n    ...RegularUserFragment\n    __typename\n  }\n  status\n  statusDescription\n  statusExpirationDate\n  value\n  fee\n  createdAt\n  props {\n    ...RegularTransactionProps\n    __typename\n  }\n  verifiedAt\n  verifiedBy {\n    ...UserEdgeNode\n    __typename\n  }\n  completedBy {\n    ...UserEdgeNode\n    __typename\n  }\n  paymentMethodId\n  completedAt\n  isSuspicious\n  spbBankName\n  __typename\n}\n\nfragment RegularTransactionProvider on TransactionProvider {\n  id\n  name\n  fee\n  minFeeAmount\n  description\n  account {\n    ...RegularTransactionProviderAccount\n    __typename\n  }\n  props {\n    ...TransactionProviderPropsFragment\n    __typename\n  }\n  limits {\n    ...ProviderLimits\n    __typename\n  }\n  paymentMethods {\n    ...TransactionPaymentMethod\n    __typename\n  }\n  __typename\n}\n\nfragment RegularTransactionProviderAccount on TransactionProviderAccount {\n  id\n  value\n  userId\n  __typename\n}\n\nfragment TransactionProviderPropsFragment on TransactionProviderPropsFragment {\n  requiredUserData {\n    ...TransactionProviderRequiredUserData\n    __typename\n  }\n  tooltip\n  __typename\n}\n\nfragment TransactionProviderRequiredUserData on TransactionProviderRequiredUserData {\n  email\n  phoneNumber\n  eripAccountNumber\n  __typename\n}\n\nfragment ProviderLimits on ProviderLimits {\n  incoming {\n    ...ProviderLimitRange\n    __typename\n  }\n  outgoing {\n    ...ProviderLimitRange\n    __typename\n  }\n  __typename\n}\n\nfragment ProviderLimitRange on ProviderLimitRange {\n  min\n  max\n  __typename\n}\n\nfragment TransactionPaymentMethod on TransactionPaymentMethod {\n  id\n  name\n  fee\n  providerId\n  account {\n    ...RegularTransactionProviderAccount\n    __typename\n  }\n  props {\n    ...TransactionProviderPropsFragment\n    __typename\n  }\n  limits {\n    ...ProviderLimits\n    __typename\n  }\n  __typename\n}\n\nfragment RegularTransactionProps on TransactionPropsFragment {\n  creatorId\n  dealId\n  paidFromPendingIncome\n  paymentURL\n  successURL\n  fee\n  paymentAccount {\n    id\n    value\n    __typename\n  }\n  paymentGateway\n  alreadySpent\n  exchangeRate\n  amountAfterConversionRub\n  amountAfterConversionUsdt\n  userData {\n    account\n    email\n    ipAddress\n    phoneNumber\n    __typename\n  }\n  __typename\n}\n\nfragment ChatMessageButton on ChatMessageButton {\n  type\n  url\n  text\n  __typename\n}\n\nfragment RegularFile on File {\n  id\n  url\n  filename\n  mime\n  __typename\n}"
        elif text: query = "mutation createChatMessage($input: CreateChatMessageInput!, $file: Upload) {\n  createChatMessage(input: $input, file: $file) {\n    ...RegularChatMessage\n    __typename\n  }\n}\n\nfragment RegularChatMessage on ChatMessage {\n  id\n  text\n  createdAt\n  deletedAt\n  isRead\n  isSuspicious\n  isBulkMessaging\n  game {\n    ...RegularGameProfile\n    __typename\n  }\n  file {\n    ...PartialFile\n    __typename\n  }\n  user {\n    ...ChatMessageUserFields\n    __typename\n  }\n  deal {\n    ...ChatMessageItemDeal\n    __typename\n  }\n  item {\n    ...ItemEdgeNode\n    __typename\n  }\n  transaction {\n    ...RegularTransaction\n    __typename\n  }\n  moderator {\n    ...UserEdgeNode\n    __typename\n  }\n  eventByUser {\n    ...ChatMessageUserFields\n    __typename\n  }\n  eventToUser {\n    ...ChatMessageUserFields\n    __typename\n  }\n  isAutoResponse\n  event\n  buttons {\n    ...ChatMessageButton\n    __typename\n  }\n  __typename\n}\n\nfragment RegularGameProfile on GameProfile {\n  id\n  name\n  type\n  slug\n  logo {\n    ...PartialFile\n    __typename\n  }\n  __typename\n}\n\nfragment PartialFile on File {\n  id\n  url\n  __typename\n}\n\nfragment ChatMessageUserFields on UserFragment {\n  ...UserEdgeNode\n  __typename\n}\n\nfragment UserEdgeNode on UserFragment {\n  ...RegularUserFragment\n  __typename\n}\n\nfragment RegularUserFragment on UserFragment {\n  id\n  username\n  role\n  avatarURL\n  isOnline\n  isBlocked\n  rating\n  testimonialCounter\n  createdAt\n  supportChatId\n  systemChatId\n  __typename\n}\n\nfragment ChatMessageItemDeal on ItemDeal {\n  id\n  direction\n  status\n  statusDescription\n  hasProblem\n  user {\n    ...ChatParticipant\n    __typename\n  }\n  testimonial {\n    ...ChatMessageDealTestimonial\n    __typename\n  }\n  item {\n    id\n    name\n    price\n    slug\n    rawPrice\n    sellerType\n    user {\n      ...ChatParticipant\n      __typename\n    }\n    category {\n      id\n      __typename\n    }\n    attachments {\n      ...PartialFile\n      __typename\n    }\n    comment\n    dataFields {\n      ...GameCategoryDataFieldWithValue\n      __typename\n    }\n    obtainingType {\n      ...GameCategoryObtainingType\n      __typename\n    }\n    __typename\n  }\n  obtainingFields {\n    ...GameCategoryDataFieldWithValue\n    __typename\n  }\n  chat {\n    id\n    type\n    __typename\n  }\n  transaction {\n    id\n    statusExpirationDate\n    __typename\n  }\n  statusExpirationDate\n  commentFromBuyer\n  __typename\n}\n\nfragment ChatParticipant on UserFragment {\n  ...RegularUserFragment\n  __typename\n}\n\nfragment ChatMessageDealTestimonial on Testimonial {\n  id\n  status\n  text\n  rating\n  createdAt\n  updatedAt\n  creator {\n    ...RegularUserFragment\n    __typename\n  }\n  moderator {\n    ...RegularUserFragment\n    __typename\n  }\n  user {\n    ...RegularUserFragment\n    __typename\n  }\n  __typename\n}\n\nfragment GameCategoryDataFieldWithValue on GameCategoryDataFieldWithValue {\n  id\n  label\n  type\n  inputType\n  copyable\n  hidden\n  required\n  value\n  __typename\n}\n\nfragment GameCategoryObtainingType on GameCategoryObtainingType {\n  id\n  name\n  description\n  gameCategoryId\n  noCommentFromBuyer\n  instructionForBuyer\n  instructionForSeller\n  sequence\n  feeMultiplier\n  agreements {\n    ...MinimalGameCategoryAgreement\n    __typename\n  }\n  props {\n    minTestimonialsForSeller\n    __typename\n  }\n  __typename\n}\n\nfragment MinimalGameCategoryAgreement on GameCategoryAgreement {\n  description\n  iconType\n  id\n  sequence\n  __typename\n}\n\nfragment ItemEdgeNode on ItemProfile {\n  ...MyItemEdgeNode\n  ...ForeignItemEdgeNode\n  __typename\n}\n\nfragment MyItemEdgeNode on MyItemProfile {\n  id\n  slug\n  priority\n  status\n  name\n  price\n  rawPrice\n  statusExpirationDate\n  sellerType\n  attachment {\n    ...PartialFile\n    __typename\n  }\n  user {\n    ...UserItemEdgeNode\n    __typename\n  }\n  approvalDate\n  createdAt\n  priorityPosition\n  viewsCounter\n  feeMultiplier\n  __typename\n}\n\nfragment UserItemEdgeNode on UserFragment {\n  ...UserEdgeNode\n  __typename\n}\n\nfragment ForeignItemEdgeNode on ForeignItemProfile {\n  id\n  slug\n  priority\n  status\n  name\n  price\n  rawPrice\n  sellerType\n  attachment {\n    ...PartialFile\n    __typename\n  }\n  user {\n    ...UserItemEdgeNode\n    __typename\n  }\n  approvalDate\n  priorityPosition\n  createdAt\n  viewsCounter\n  feeMultiplier\n  __typename\n}\n\nfragment RegularTransaction on Transaction {\n  id\n  operation\n  direction\n  providerId\n  provider {\n    ...RegularTransactionProvider\n    __typename\n  }\n  user {\n    ...RegularUserFragment\n    __typename\n  }\n  creator {\n    ...RegularUserFragment\n    __typename\n  }\n  status\n  statusDescription\n  statusExpirationDate\n  value\n  fee\n  createdAt\n  props {\n    ...RegularTransactionProps\n    __typename\n  }\n  verifiedAt\n  verifiedBy {\n    ...UserEdgeNode\n    __typename\n  }\n  completedBy {\n    ...UserEdgeNode\n    __typename\n  }\n  paymentMethodId\n  completedAt\n  isSuspicious\n  __typename\n}\n\nfragment RegularTransactionProvider on TransactionProvider {\n  id\n  name\n  fee\n  minFeeAmount\n  description\n  account {\n    ...RegularTransactionProviderAccount\n    __typename\n  }\n  props {\n    ...TransactionProviderPropsFragment\n    __typename\n  }\n  limits {\n    ...ProviderLimits\n    __typename\n  }\n  paymentMethods {\n    ...TransactionPaymentMethod\n    __typename\n  }\n  __typename\n}\n\nfragment RegularTransactionProviderAccount on TransactionProviderAccount {\n  id\n  value\n  userId\n  __typename\n}\n\nfragment TransactionProviderPropsFragment on TransactionProviderPropsFragment {\n  requiredUserData {\n    ...TransactionProviderRequiredUserData\n    __typename\n  }\n  tooltip\n  __typename\n}\n\nfragment TransactionProviderRequiredUserData on TransactionProviderRequiredUserData {\n  email\n  phoneNumber\n  __typename\n}\n\nfragment ProviderLimits on ProviderLimits {\n  incoming {\n    ...ProviderLimitRange\n    __typename\n  }\n  outgoing {\n    ...ProviderLimitRange\n    __typename\n  }\n  __typename\n}\n\nfragment ProviderLimitRange on ProviderLimitRange {\n  min\n  max\n  __typename\n}\n\nfragment TransactionPaymentMethod on TransactionPaymentMethod {\n  id\n  name\n  fee\n  providerId\n  account {\n    ...RegularTransactionProviderAccount\n    __typename\n  }\n  props {\n    ...TransactionProviderPropsFragment\n    __typename\n  }\n  limits {\n    ...ProviderLimits\n    __typename\n  }\n  __typename\n}\n\nfragment RegularTransactionProps on TransactionPropsFragment {\n  creatorId\n  dealId\n  paidFromPendingIncome\n  paymentURL\n  successURL\n  fee\n  paymentAccount {\n    id\n    value\n    __typename\n  }\n  paymentGateway\n  alreadySpent\n  exchangeRate\n  amountAfterConversionRub\n  amountAfterConversionUsdt\n  __typename\n}\n\nfragment ChatMessageButton on ChatMessageButton {\n  type\n  url\n  text\n  __typename\n}"
        operations = {
            "operationName": "createChatMessage",
            "query": query,
            "variables": {
                "input": {
                    "chatId": chat_id
                }
            }
        }
        if photo_file_path:
            operations["variables"]["file"] = None
        elif text:
            operations["variables"]["input"]["text"] = text
        files = {"1": open(photo_file_path, "rb")} if photo_file_path else None
        map = {"1":["variables.file"]} if photo_file_path else None
        payload = operations if photo_file_path is None else {"operations": json.dumps(operations), "map": json.dumps(map)}
        r = self.request("post", f"{self.base_url}/graphql", headers, payload, files).json()
        return chat_message(r["data"]["createChatMessage"])

    def create_item(self, game_category_id: str, obtaining_type_id: str, name: str, price: int, 
                    description: str, options: list[GameCategoryOption], data_fields: list[GameCategoryDataField],
                    attachments: list[str]) -> types.Item:
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
        payload_attributes = {}
        for option in options:
            payload_attributes[option.field] = option.value
        payload_data_fields = []
        for field in data_fields:
            payload_data_fields.append({"fieldId": field.id, "value": field.value})

        headers = {"accept": "*/*"}
        operations = {
            "operationName": "createItem",
            "query": "mutation createItem($input: CreateItemInput!, $attachments: [Upload!]!) {\n  createItem(input: $input, attachments: $attachments) {\n    ...RegularItem\n    __typename\n  }\n}\n\nfragment RegularItem on Item {\n  ...RegularMyItem\n  ...RegularForeignItem\n  __typename\n}\n\nfragment RegularMyItem on MyItem {\n  ...ItemFields\n  prevPrice\n  priority\n  sequence\n  priorityPrice\n  statusExpirationDate\n  comment\n  viewsCounter\n  statusDescription\n  editable\n  statusPayment {\n    ...StatusPaymentTransaction\n    __typename\n  }\n  moderator {\n    id\n    username\n    __typename\n  }\n  approvalDate\n  deletedAt\n  createdAt\n  updatedAt\n  mayBePublished\n  prevFeeMultiplier\n  sellerNotifiedAboutFeeChange\n  __typename\n}\n\nfragment ItemFields on Item {\n  id\n  slug\n  name\n  description\n  rawPrice\n  price\n  attributes\n  status\n  priorityPosition\n  sellerType\n  feeMultiplier\n  user {\n    ...ItemUser\n    __typename\n  }\n  buyer {\n    ...ItemUser\n    __typename\n  }\n  attachments {\n    ...PartialFile\n    __typename\n  }\n  category {\n    ...RegularGameCategory\n    __typename\n  }\n  game {\n    ...RegularGameProfile\n    __typename\n  }\n  comment\n  dataFields {\n    ...GameCategoryDataFieldWithValue\n    __typename\n  }\n  obtainingType {\n    ...GameCategoryObtainingType\n    __typename\n  }\n  __typename\n}\n\nfragment ItemUser on UserFragment {\n  ...UserEdgeNode\n  __typename\n}\n\nfragment UserEdgeNode on UserFragment {\n  ...RegularUserFragment\n  __typename\n}\n\nfragment RegularUserFragment on UserFragment {\n  id\n  username\n  role\n  avatarURL\n  isOnline\n  isBlocked\n  rating\n  testimonialCounter\n  createdAt\n  supportChatId\n  systemChatId\n  __typename\n}\n\nfragment PartialFile on File {\n  id\n  url\n  __typename\n}\n\nfragment RegularGameCategory on GameCategory {\n  id\n  slug\n  name\n  categoryId\n  gameId\n  obtaining\n  options {\n    ...RegularGameCategoryOption\n    __typename\n  }\n  props {\n    ...GameCategoryProps\n    __typename\n  }\n  noCommentFromBuyer\n  instructionForBuyer\n  instructionForSeller\n  useCustomObtaining\n  autoConfirmPeriod\n  autoModerationMode\n  agreements {\n    ...RegularGameCategoryAgreement\n    __typename\n  }\n  feeMultiplier\n  __typename\n}\n\nfragment RegularGameCategoryOption on GameCategoryOption {\n  id\n  group\n  label\n  type\n  field\n  value\n  valueRangeLimit {\n    min\n    max\n    __typename\n  }\n  __typename\n}\n\nfragment GameCategoryProps on GameCategoryPropsObjectType {\n  minTestimonials\n  minTestimonialsForSeller\n  __typename\n}\n\nfragment RegularGameCategoryAgreement on GameCategoryAgreement {\n  description\n  gameCategoryId\n  gameCategoryObtainingTypeId\n  iconType\n  id\n  sequence\n  __typename\n}\n\nfragment RegularGameProfile on GameProfile {\n  id\n  name\n  type\n  slug\n  logo {\n    ...PartialFile\n    __typename\n  }\n  __typename\n}\n\nfragment GameCategoryDataFieldWithValue on GameCategoryDataFieldWithValue {\n  id\n  label\n  type\n  inputType\n  copyable\n  hidden\n  required\n  value\n  __typename\n}\n\nfragment GameCategoryObtainingType on GameCategoryObtainingType {\n  id\n  name\n  description\n  gameCategoryId\n  noCommentFromBuyer\n  instructionForBuyer\n  instructionForSeller\n  sequence\n  feeMultiplier\n  agreements {\n    ...MinimalGameCategoryAgreement\n    __typename\n  }\n  props {\n    minTestimonialsForSeller\n    __typename\n  }\n  __typename\n}\n\nfragment MinimalGameCategoryAgreement on GameCategoryAgreement {\n  description\n  iconType\n  id\n  sequence\n  __typename\n}\n\nfragment StatusPaymentTransaction on Transaction {\n  id\n  operation\n  direction\n  providerId\n  status\n  statusDescription\n  statusExpirationDate\n  value\n  props {\n    paymentURL\n    __typename\n  }\n  __typename\n}\n\nfragment RegularForeignItem on ForeignItem {\n  ...ItemFields\n  __typename\n}",
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
        i=0
        for att in attachments:
            i+=1
            map[str(i)] = [f"variables.attachments.{i-1}"]
            files[str(i)] = open(att, "rb")
        payload = {
            "operations": json.dumps(operations),
            "map": json.dumps(map)
        }

        r = self.request("post", f"{self.base_url}/graphql", headers, payload, files).json()
        return item(r["data"]["createItem"])
    
    def update_item(self, id: str, name: str | None = None, price: int | None = None, description: str | None = None, 
                    options: list[GameCategoryOption] | None = None, data_fields: list[GameCategoryDataField] | None = None, 
                    remove_attachments: list[str] | None = None, add_attachments: list[str] | None = None) -> types.Item:
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
        payload_attributes = {} if options is not None else None
        if options:
            for option in options:
                payload_attributes[option.field] = option.value
        payload_data_fields = [] if data_fields is not None else None
        if data_fields:
            for field in data_fields:
                payload_data_fields.append({"fieldId": field.id, "value": field.value})

        headers = {"accept": "*/*"}
        operations = {
            "operationName": "updateItem",
            "query": "mutation updateItem($input: UpdateItemInput!, $addedAttachments: [Upload!]) {\n  updateItem(input: $input, addedAttachments: $addedAttachments) {\n    ...RegularItem\n    __typename\n  }\n}\n\nfragment RegularItem on Item {\n  ...RegularMyItem\n  ...RegularForeignItem\n  __typename\n}\n\nfragment RegularMyItem on MyItem {\n  ...ItemFields\n  prevPrice\n  priority\n  sequence\n  priorityPrice\n  statusExpirationDate\n  comment\n  viewsCounter\n  statusDescription\n  editable\n  statusPayment {\n    ...StatusPaymentTransaction\n    __typename\n  }\n  moderator {\n    id\n    username\n    __typename\n  }\n  approvalDate\n  deletedAt\n  createdAt\n  updatedAt\n  mayBePublished\n  prevFeeMultiplier\n  sellerNotifiedAboutFeeChange\n  __typename\n}\n\nfragment ItemFields on Item {\n  id\n  slug\n  name\n  description\n  rawPrice\n  price\n  attributes\n  status\n  priorityPosition\n  sellerType\n  feeMultiplier\n  user {\n    ...ItemUser\n    __typename\n  }\n  buyer {\n    ...ItemUser\n    __typename\n  }\n  attachments {\n    ...PartialFile\n    __typename\n  }\n  category {\n    ...RegularGameCategory\n    __typename\n  }\n  game {\n    ...RegularGameProfile\n    __typename\n  }\n  comment\n  dataFields {\n    ...GameCategoryDataFieldWithValue\n    __typename\n  }\n  obtainingType {\n    ...GameCategoryObtainingType\n    __typename\n  }\n  __typename\n}\n\nfragment ItemUser on UserFragment {\n  ...UserEdgeNode\n  __typename\n}\n\nfragment UserEdgeNode on UserFragment {\n  ...RegularUserFragment\n  __typename\n}\n\nfragment RegularUserFragment on UserFragment {\n  id\n  username\n  role\n  avatarURL\n  isOnline\n  isBlocked\n  rating\n  testimonialCounter\n  createdAt\n  supportChatId\n  systemChatId\n  __typename\n}\n\nfragment PartialFile on File {\n  id\n  url\n  __typename\n}\n\nfragment RegularGameCategory on GameCategory {\n  id\n  slug\n  name\n  categoryId\n  gameId\n  obtaining\n  options {\n    ...RegularGameCategoryOption\n    __typename\n  }\n  props {\n    ...GameCategoryProps\n    __typename\n  }\n  noCommentFromBuyer\n  instructionForBuyer\n  instructionForSeller\n  useCustomObtaining\n  autoConfirmPeriod\n  autoModerationMode\n  agreements {\n    ...RegularGameCategoryAgreement\n    __typename\n  }\n  feeMultiplier\n  __typename\n}\n\nfragment RegularGameCategoryOption on GameCategoryOption {\n  id\n  group\n  label\n  type\n  field\n  value\n  valueRangeLimit {\n    min\n    max\n    __typename\n  }\n  __typename\n}\n\nfragment GameCategoryProps on GameCategoryPropsObjectType {\n  minTestimonials\n  minTestimonialsForSeller\n  __typename\n}\n\nfragment RegularGameCategoryAgreement on GameCategoryAgreement {\n  description\n  gameCategoryId\n  gameCategoryObtainingTypeId\n  iconType\n  id\n  sequence\n  __typename\n}\n\nfragment RegularGameProfile on GameProfile {\n  id\n  name\n  type\n  slug\n  logo {\n    ...PartialFile\n    __typename\n  }\n  __typename\n}\n\nfragment GameCategoryDataFieldWithValue on GameCategoryDataFieldWithValue {\n  id\n  label\n  type\n  inputType\n  copyable\n  hidden\n  required\n  value\n  __typename\n}\n\nfragment GameCategoryObtainingType on GameCategoryObtainingType {\n  id\n  name\n  description\n  gameCategoryId\n  noCommentFromBuyer\n  instructionForBuyer\n  instructionForSeller\n  sequence\n  feeMultiplier\n  agreements {\n    ...MinimalGameCategoryAgreement\n    __typename\n  }\n  props {\n    minTestimonialsForSeller\n    __typename\n  }\n  __typename\n}\n\nfragment MinimalGameCategoryAgreement on GameCategoryAgreement {\n  description\n  iconType\n  id\n  sequence\n  __typename\n}\n\nfragment StatusPaymentTransaction on Transaction {\n  id\n  operation\n  direction\n  providerId\n  status\n  statusDescription\n  statusExpirationDate\n  value\n  props {\n    paymentURL\n    __typename\n  }\n  __typename\n}\n\nfragment RegularForeignItem on ForeignItem {\n  ...ItemFields\n  __typename\n}",
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
            i=0
            for att in add_attachments:
                i+=1
                map[str(i)] = [f"variables.addedAttachments.{i-1}"]
                files[str(i)] = open(att, "rb")
        payload = {
            "operations": json.dumps(operations),
            "map": json.dumps(map)
        }
        r = self.request("post", f"{self.base_url}/graphql", headers, payload if files else operations, files if files else None).json()
        return item(r["data"]["updateItem"])

    def remove_item(self, id: str) -> bool:
        """
        Полностью удаляет предмет вашего аккаунта.

        :param id: ID предмета.
        :type id: `str`
        """
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "removeItem",
            "query": "mutation removeItem($id: UUID!) {\n  removeItem(id: $id) {\n    ...RegularItem\n    __typename\n  }\n}\n\nfragment RegularItem on Item {\n  ...RegularMyItem\n  ...RegularForeignItem\n  __typename\n}\n\nfragment RegularMyItem on MyItem {\n  ...ItemFields\n  prevPrice\n  priority\n  sequence\n  priorityPrice\n  statusExpirationDate\n  comment\n  viewsCounter\n  statusDescription\n  editable\n  statusPayment {\n    ...StatusPaymentTransaction\n    __typename\n  }\n  moderator {\n    id\n    username\n    __typename\n  }\n  approvalDate\n  deletedAt\n  createdAt\n  updatedAt\n  mayBePublished\n  prevFeeMultiplier\n  sellerNotifiedAboutFeeChange\n  __typename\n}\n\nfragment ItemFields on Item {\n  id\n  slug\n  name\n  description\n  rawPrice\n  price\n  attributes\n  status\n  priorityPosition\n  sellerType\n  feeMultiplier\n  user {\n    ...ItemUser\n    __typename\n  }\n  buyer {\n    ...ItemUser\n    __typename\n  }\n  attachments {\n    ...PartialFile\n    __typename\n  }\n  category {\n    ...RegularGameCategory\n    __typename\n  }\n  game {\n    ...RegularGameProfile\n    __typename\n  }\n  comment\n  dataFields {\n    ...GameCategoryDataFieldWithValue\n    __typename\n  }\n  obtainingType {\n    ...GameCategoryObtainingType\n    __typename\n  }\n  __typename\n}\n\nfragment ItemUser on UserFragment {\n  ...UserEdgeNode\n  __typename\n}\n\nfragment UserEdgeNode on UserFragment {\n  ...RegularUserFragment\n  __typename\n}\n\nfragment RegularUserFragment on UserFragment {\n  id\n  username\n  role\n  avatarURL\n  isOnline\n  isBlocked\n  rating\n  testimonialCounter\n  createdAt\n  supportChatId\n  systemChatId\n  __typename\n}\n\nfragment PartialFile on File {\n  id\n  url\n  __typename\n}\n\nfragment RegularGameCategory on GameCategory {\n  id\n  slug\n  name\n  categoryId\n  gameId\n  obtaining\n  options {\n    ...RegularGameCategoryOption\n    __typename\n  }\n  props {\n    ...GameCategoryProps\n    __typename\n  }\n  noCommentFromBuyer\n  instructionForBuyer\n  instructionForSeller\n  useCustomObtaining\n  autoConfirmPeriod\n  autoModerationMode\n  agreements {\n    ...RegularGameCategoryAgreement\n    __typename\n  }\n  feeMultiplier\n  __typename\n}\n\nfragment RegularGameCategoryOption on GameCategoryOption {\n  id\n  group\n  label\n  type\n  field\n  value\n  valueRangeLimit {\n    min\n    max\n    __typename\n  }\n  __typename\n}\n\nfragment GameCategoryProps on GameCategoryPropsObjectType {\n  minTestimonials\n  minTestimonialsForSeller\n  __typename\n}\n\nfragment RegularGameCategoryAgreement on GameCategoryAgreement {\n  description\n  gameCategoryId\n  gameCategoryObtainingTypeId\n  iconType\n  id\n  sequence\n  __typename\n}\n\nfragment RegularGameProfile on GameProfile {\n  id\n  name\n  type\n  slug\n  logo {\n    ...PartialFile\n    __typename\n  }\n  __typename\n}\n\nfragment GameCategoryDataFieldWithValue on GameCategoryDataFieldWithValue {\n  id\n  label\n  type\n  inputType\n  copyable\n  hidden\n  required\n  value\n  __typename\n}\n\nfragment GameCategoryObtainingType on GameCategoryObtainingType {\n  id\n  name\n  description\n  gameCategoryId\n  noCommentFromBuyer\n  instructionForBuyer\n  instructionForSeller\n  sequence\n  feeMultiplier\n  agreements {\n    ...MinimalGameCategoryAgreement\n    __typename\n  }\n  props {\n    minTestimonialsForSeller\n    __typename\n  }\n  __typename\n}\n\nfragment MinimalGameCategoryAgreement on GameCategoryAgreement {\n  description\n  iconType\n  id\n  sequence\n  __typename\n}\n\nfragment StatusPaymentTransaction on Transaction {\n  id\n  operation\n  direction\n  providerId\n  status\n  statusDescription\n  statusExpirationDate\n  value\n  props {\n    paymentURL\n    __typename\n  }\n  __typename\n}\n\nfragment RegularForeignItem on ForeignItem {\n  ...ItemFields\n  __typename\n}",
            "variables": {
                "id": id,
            }
        }
        self.request("post", f"{self.base_url}/graphql", headers, payload)
        return True
    
    def publish_item(self, item_id: str, priority_status_id: str, 
                     transaction_provider_id: TransactionProviderIds = TransactionProviderIds.LOCAL) -> types.Item:
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
            "query": "mutation publishItem($input: PublishItemInput!) {\n  publishItem(input: $input) {\n    ...RegularItem\n    __typename\n  }\n}\n\nfragment RegularItem on Item {\n  ...RegularMyItem\n  ...RegularForeignItem\n  __typename\n}\n\nfragment RegularMyItem on MyItem {\n  ...ItemFields\n  prevPrice\n  priority\n  sequence\n  priorityPrice\n  statusExpirationDate\n  comment\n  viewsCounter\n  statusDescription\n  editable\n  statusPayment {\n    ...StatusPaymentTransaction\n    __typename\n  }\n  moderator {\n    id\n    username\n    __typename\n  }\n  approvalDate\n  deletedAt\n  createdAt\n  updatedAt\n  mayBePublished\n  prevFeeMultiplier\n  sellerNotifiedAboutFeeChange\n  __typename\n}\n\nfragment ItemFields on Item {\n  id\n  slug\n  name\n  description\n  rawPrice\n  price\n  attributes\n  status\n  priorityPosition\n  sellerType\n  feeMultiplier\n  user {\n    ...ItemUser\n    __typename\n  }\n  buyer {\n    ...ItemUser\n    __typename\n  }\n  attachments {\n    ...PartialFile\n    __typename\n  }\n  category {\n    ...RegularGameCategory\n    __typename\n  }\n  game {\n    ...RegularGameProfile\n    __typename\n  }\n  comment\n  dataFields {\n    ...GameCategoryDataFieldWithValue\n    __typename\n  }\n  obtainingType {\n    ...GameCategoryObtainingType\n    __typename\n  }\n  __typename\n}\n\nfragment ItemUser on UserFragment {\n  ...UserEdgeNode\n  __typename\n}\n\nfragment UserEdgeNode on UserFragment {\n  ...RegularUserFragment\n  __typename\n}\n\nfragment RegularUserFragment on UserFragment {\n  id\n  username\n  role\n  avatarURL\n  isOnline\n  isBlocked\n  rating\n  testimonialCounter\n  createdAt\n  supportChatId\n  systemChatId\n  __typename\n}\n\nfragment PartialFile on File {\n  id\n  url\n  __typename\n}\n\nfragment RegularGameCategory on GameCategory {\n  id\n  slug\n  name\n  categoryId\n  gameId\n  obtaining\n  options {\n    ...RegularGameCategoryOption\n    __typename\n  }\n  props {\n    ...GameCategoryProps\n    __typename\n  }\n  noCommentFromBuyer\n  instructionForBuyer\n  instructionForSeller\n  useCustomObtaining\n  autoConfirmPeriod\n  autoModerationMode\n  agreements {\n    ...RegularGameCategoryAgreement\n    __typename\n  }\n  feeMultiplier\n  __typename\n}\n\nfragment RegularGameCategoryOption on GameCategoryOption {\n  id\n  group\n  label\n  type\n  field\n  value\n  valueRangeLimit {\n    min\n    max\n    __typename\n  }\n  __typename\n}\n\nfragment GameCategoryProps on GameCategoryPropsObjectType {\n  minTestimonials\n  minTestimonialsForSeller\n  __typename\n}\n\nfragment RegularGameCategoryAgreement on GameCategoryAgreement {\n  description\n  gameCategoryId\n  gameCategoryObtainingTypeId\n  iconType\n  id\n  sequence\n  __typename\n}\n\nfragment RegularGameProfile on GameProfile {\n  id\n  name\n  type\n  slug\n  logo {\n    ...PartialFile\n    __typename\n  }\n  __typename\n}\n\nfragment GameCategoryDataFieldWithValue on GameCategoryDataFieldWithValue {\n  id\n  label\n  type\n  inputType\n  copyable\n  hidden\n  required\n  value\n  __typename\n}\n\nfragment GameCategoryObtainingType on GameCategoryObtainingType {\n  id\n  name\n  description\n  gameCategoryId\n  noCommentFromBuyer\n  instructionForBuyer\n  instructionForSeller\n  sequence\n  feeMultiplier\n  agreements {\n    ...MinimalGameCategoryAgreement\n    __typename\n  }\n  props {\n    minTestimonialsForSeller\n    __typename\n  }\n  __typename\n}\n\nfragment MinimalGameCategoryAgreement on GameCategoryAgreement {\n  description\n  iconType\n  id\n  sequence\n  __typename\n}\n\nfragment StatusPaymentTransaction on Transaction {\n  id\n  operation\n  direction\n  providerId\n  status\n  statusDescription\n  statusExpirationDate\n  value\n  props {\n    paymentURL\n    __typename\n  }\n  __typename\n}\n\nfragment RegularForeignItem on ForeignItem {\n  ...ItemFields\n  __typename\n}",
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

    def get_items(self, game_id: str | None = None, category_id: str | None = None, count: int = 24,
                  status: ItemStatuses = ItemStatuses.APPROVED, after_cursor: str | None = None) -> types.ItemProfileList:
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
        headers = {"accept": "*/*"}
        filter = {"gameId": game_id, "status": [status.name] if status else None} if not category_id else {"gameCategoryId": category_id, "status": [status.name] if status else None}
        payload = {
            "operationName": "items",
            "variables": json.dumps({"pagination": {"first": count, "after": after_cursor}, "filter": filter}, ensure_ascii=False),
            "extensions": json.dumps({"persistedQuery": {"version": 1, "sha256Hash": "29ff7e8c607c7b3f2fa3c7a9e02a3a184bf92905e8ea75ba237c8c7f005287a3"}}, ensure_ascii=False)
        }
        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        return item_profile_list(r["data"]["items"])

    def get_item(self, id: str | None = None, slug: str | None = None) -> types.MyItem | types.Item | types.ItemProfile:
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
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "item",
            "variables": json.dumps({"id": id, "slug": slug, "hasSupportAccess": False, "showForbiddenImage": True}, ensure_ascii=False),
            "extensions": json.dumps({"persistedQuery": {"version": 1, "sha256Hash": "e3e341306a7c3400d7e5d47d1f716406d8fe02b74d3faacd733af9b2d64304d0"}}, ensure_ascii=False)
        }
        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        data: dict = r["data"]["item"]
        if data["__typename"] == "MyItem": _item = my_item(data)
        elif data["__typename"] == "ItemProfile": _item = item_profile(data)
        elif data["__typename"] in ["Item", "ForeignItem"]: _item = item(data)
        else: _item = None
        return _item

    def get_item_priority_statuses(self, item_id: str, item_price: str) -> list[types.ItemPriorityStatus]:
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
            "variables": json.dumps({"itemId": item_id, "price": int(item_price)}, ensure_ascii=False),
            "extensions": json.dumps({"persistedQuery": {"version": 1, "sha256Hash": "b922220c6f979537e1b99de6af8f5c13727daeff66727f679f07f986ce1c025a"}}, ensure_ascii=False)
        }
        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        return [item_priority_status(status) for status in r["data"]["itemPriorityStatuses"]]

    def increase_item_priority_status(self, item_id: str, priority_status_id: str, payment_method_id: TransactionPaymentMethodIds | None = None, 
                                      transaction_provider_id: TransactionProviderIds = TransactionProviderIds.LOCAL) -> types.Item:
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
            "query": "mutation increaseItemPriorityStatus($input: PublishItemInput!) {\n  increaseItemPriorityStatus(input: $input) {\n    ...RegularItem\n    __typename\n  }\n}\n\nfragment RegularItem on Item {\n  ...RegularMyItem\n  ...RegularForeignItem\n  __typename\n}\n\nfragment RegularMyItem on MyItem {\n  ...ItemFields\n  prevPrice\n  priority\n  sequence\n  priorityPrice\n  statusExpirationDate\n  comment\n  viewsCounter\n  statusDescription\n  editable\n  statusPayment {\n    ...StatusPaymentTransaction\n    __typename\n  }\n  moderator {\n    id\n    username\n    __typename\n  }\n  approvalDate\n  deletedAt\n  createdAt\n  updatedAt\n  mayBePublished\n  prevFeeMultiplier\n  sellerNotifiedAboutFeeChange\n  __typename\n}\n\nfragment ItemFields on Item {\n  id\n  slug\n  name\n  description\n  rawPrice\n  price\n  attributes\n  status\n  priorityPosition\n  sellerType\n  feeMultiplier\n  user {\n    ...ItemUser\n    __typename\n  }\n  buyer {\n    ...ItemUser\n    __typename\n  }\n  attachments {\n    ...PartialFile\n    __typename\n  }\n  category {\n    ...RegularGameCategory\n    __typename\n  }\n  game {\n    ...RegularGameProfile\n    __typename\n  }\n  comment\n  dataFields {\n    ...GameCategoryDataFieldWithValue\n    __typename\n  }\n  obtainingType {\n    ...GameCategoryObtainingType\n    __typename\n  }\n  __typename\n}\n\nfragment ItemUser on UserFragment {\n  ...UserEdgeNode\n  __typename\n}\n\nfragment UserEdgeNode on UserFragment {\n  ...RegularUserFragment\n  __typename\n}\n\nfragment RegularUserFragment on UserFragment {\n  id\n  username\n  role\n  avatarURL\n  isOnline\n  isBlocked\n  rating\n  testimonialCounter\n  createdAt\n  supportChatId\n  systemChatId\n  __typename\n}\n\nfragment PartialFile on File {\n  id\n  url\n  __typename\n}\n\nfragment RegularGameCategory on GameCategory {\n  id\n  slug\n  name\n  categoryId\n  gameId\n  obtaining\n  options {\n    ...RegularGameCategoryOption\n    __typename\n  }\n  props {\n    ...GameCategoryProps\n    __typename\n  }\n  noCommentFromBuyer\n  instructionForBuyer\n  instructionForSeller\n  useCustomObtaining\n  autoConfirmPeriod\n  autoModerationMode\n  agreements {\n    ...RegularGameCategoryAgreement\n    __typename\n  }\n  feeMultiplier\n  __typename\n}\n\nfragment RegularGameCategoryOption on GameCategoryOption {\n  id\n  group\n  label\n  type\n  field\n  value\n  valueRangeLimit {\n    min\n    max\n    __typename\n  }\n  __typename\n}\n\nfragment GameCategoryProps on GameCategoryPropsObjectType {\n  minTestimonials\n  minTestimonialsForSeller\n  __typename\n}\n\nfragment RegularGameCategoryAgreement on GameCategoryAgreement {\n  description\n  gameCategoryId\n  gameCategoryObtainingTypeId\n  iconType\n  id\n  sequence\n  __typename\n}\n\nfragment RegularGameProfile on GameProfile {\n  id\n  name\n  type\n  slug\n  logo {\n    ...PartialFile\n    __typename\n  }\n  __typename\n}\n\nfragment GameCategoryDataFieldWithValue on GameCategoryDataFieldWithValue {\n  id\n  label\n  type\n  inputType\n  copyable\n  hidden\n  required\n  value\n  __typename\n}\n\nfragment GameCategoryObtainingType on GameCategoryObtainingType {\n  id\n  name\n  description\n  gameCategoryId\n  noCommentFromBuyer\n  instructionForBuyer\n  instructionForSeller\n  sequence\n  feeMultiplier\n  agreements {\n    ...MinimalGameCategoryAgreement\n    __typename\n  }\n  props {\n    minTestimonialsForSeller\n    __typename\n  }\n  __typename\n}\n\nfragment MinimalGameCategoryAgreement on GameCategoryAgreement {\n  description\n  iconType\n  id\n  sequence\n  __typename\n}\n\nfragment StatusPaymentTransaction on Transaction {\n  id\n  operation\n  direction\n  providerId\n  status\n  statusDescription\n  statusExpirationDate\n  value\n  props {\n    paymentURL\n    __typename\n  }\n  __typename\n}\n\nfragment RegularForeignItem on ForeignItem {\n  ...ItemFields\n  __typename\n}",
            "variables": {
                "input": {
                    "itemId": item_id,
                    "priorityStatuses": [priority_status_id],
                    "transactionProviderData": {
                        "paymentMethodId": payment_method_id.name
                    },
                    "transactionProviderId": transaction_provider_id.name
                }
            }
        }
        r = self.request("post", f"{self.base_url}/graphql", headers, payload).json()
        return item(r["data"]["increaseItemPriorityStatus"])

    def get_transaction_providers(self, direction: TransactionProviderDirections = TransactionProviderDirections.IN) -> list[types.TransactionProvider]:
        """
        Получает все провайдеры транзакций.

        :param direction: Направление транзакций (пополнение/вывод).
        :type direction: `playerokapi.enums.TransactionProviderDirections`
        
        :return: Список провайдеров транзакий.
        :rtype: `list` of `playerokapi.types.TransactionProvider`
        """
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "transactionProviders",
            "variables": json.dumps({"filter": {"direction": direction.name if direction else None}}, ensure_ascii=False),
            "extensions": json.dumps({"persistedQuery": {"version": 1, "sha256Hash": "31960e5dd929834c1f85bc685db80657ff576373076f016b2578c0a34e6e9f42"}}, ensure_ascii=False)
        }
        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        return [transaction_provider(provider) for provider in r["data"]["transactionProviders"]]

    def get_transactions(self, count: int = 24, operation: TransactionOperations | None = None, min_value: int | None = None,
                         max_value: int | None = None, provider_id: TransactionProviderIds | None = None, status: TransactionStatuses | None = None,
                         after_cursor: str | None = None) -> TransactionList:
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
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "transactions",
            "variables": {"pagination": {"first": count, "after": after_cursor}, "filter": {"userId": self.id}, "hasSupportAccess": False},
            "extensions": json.dumps({"persistedQuery": {"version": 1, "sha256Hash": "3b9925106c3fe9308ac632254fd70da347b5701f243ab8690477d5a7ca37c2c8"}}, ensure_ascii=False)
        }
        if operation: payload["variables"]["filter"]["operation"] = [operation.name]
        if min_value or max_value:
            payload["variables"]["filter"]["value"] = {}
            if min_value: payload["variables"]["filter"]["value"]["min"] = str(min_value)
            if max_value: payload["variables"]["filter"]["value"]["max"] = str(max_value)
        if provider_id: payload["variables"]["filter"]["providerId"] = [provider_id.name]
        if status: payload["variables"]["filter"]["status"] = [status.name]
        payload["variables"] = json.dumps(payload["variables"], ensure_ascii=False),
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
            "variables": json.dumps({}, ensure_ascii=False),
            "extensions": json.dumps({"persistedQuery": {"version": 1, "sha256Hash": "ef7902598e855fa15fb5e3112156ac226180f0b009a36606fc80a18f00b80c63"}}, ensure_ascii=False)
        }
        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        return [sbp_bank_member(member) for member in r["data"]["sbpBankMembers"]]
    
    def get_verified_cards(self, count: int = 24, after_cursor: str | None = None,
                           direction: SortDirections = SortDirections.ASC) -> types.UserBankCardList:
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
            "variables": json.dumps({"pagination": {"first": count, "after": after_cursor}, "sort": {"direction": direction.name}, "field": "createdAt"}, ensure_ascii=False),
            "extensions": json.dumps({"persistedQuery": {"version": 1, "sha256Hash": "eb338d8432981307a2b3d322b3310b2447cab3a6acf21aba4b8773b97e72d1aa"}}, ensure_ascii=False)
        }
        r = self.request("get", f"{self.base_url}/graphql", headers, payload).json()
        return user_bank_card_list(r["data"]["verifiedCards"])
    
    def delete_card(self, card_id: str) -> bool:
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
            "query": "mutation deleteCard($input: DeleteCardInput!) {\n  deleteCard(input: $input)\n}",
            "variables": {
                "input": {
                    "cardId": card_id
                }
            }
        }
        r = self.request("post", f"{self.base_url}/graphql", headers, payload).json()
        return r["data"]["deleteCard"]
    
    def request_withdrawal(self, provider: TransactionProviderIds, account: str, value: int,
                           payment_method_id: TransactionPaymentMethodIds | None = None,
                           sbp_bank_member_id: str | None = None) -> types.Transaction:
        """
        Отправляет запрос на вывод средств с баланса аккаунта.

        :param provider: Провайдер транзакции.
        :type provider: `playerokapi.enums.TransactionProviderIds`

        :param account: ID добавленной карты или номер телефона, если провайдер СБП, на которые нужно совершить вывод.
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
            "query": "mutation requestWithdrawal($input: CreateWithdrawalTransactionInput!) {\n  requestWithdrawal(input: $input) {\n    ...RegularTransaction\n    __typename\n  }\n}\n\nfragment RegularTransaction on Transaction {\n  id\n  operation\n  direction\n  providerId\n  provider {\n    ...RegularTransactionProvider\n    __typename\n  }\n  user {\n    ...RegularUserFragment\n    __typename\n  }\n  creator {\n    ...RegularUserFragment\n    __typename\n  }\n  status\n  statusDescription\n  statusExpirationDate\n  value\n  fee\n  createdAt\n  props {\n    ...RegularTransactionProps\n    __typename\n  }\n  verifiedAt\n  verifiedBy {\n    ...UserEdgeNode\n    __typename\n  }\n  completedBy {\n    ...UserEdgeNode\n    __typename\n  }\n  paymentMethodId\n  completedAt\n  isSuspicious\n  spbBankName\n  __typename\n}\n\nfragment RegularTransactionProvider on TransactionProvider {\n  id\n  name\n  fee\n  minFeeAmount\n  description\n  account {\n    ...RegularTransactionProviderAccount\n    __typename\n  }\n  props {\n    ...TransactionProviderPropsFragment\n    __typename\n  }\n  limits {\n    ...ProviderLimits\n    __typename\n  }\n  paymentMethods {\n    ...TransactionPaymentMethod\n    __typename\n  }\n  __typename\n}\n\nfragment RegularTransactionProviderAccount on TransactionProviderAccount {\n  id\n  value\n  userId\n  providerId\n  paymentMethodId\n  __typename\n}\n\nfragment TransactionProviderPropsFragment on TransactionProviderPropsFragment {\n  requiredUserData {\n    ...TransactionProviderRequiredUserData\n    __typename\n  }\n  tooltip\n  __typename\n}\n\nfragment TransactionProviderRequiredUserData on TransactionProviderRequiredUserData {\n  email\n  phoneNumber\n  eripAccountNumber\n  __typename\n}\n\nfragment ProviderLimits on ProviderLimits {\n  incoming {\n    ...ProviderLimitRange\n    __typename\n  }\n  outgoing {\n    ...ProviderLimitRange\n    __typename\n  }\n  __typename\n}\n\nfragment ProviderLimitRange on ProviderLimitRange {\n  min\n  max\n  __typename\n}\n\nfragment TransactionPaymentMethod on TransactionPaymentMethod {\n  id\n  name\n  fee\n  providerId\n  account {\n    ...RegularTransactionProviderAccount\n    __typename\n  }\n  props {\n    ...TransactionProviderPropsFragment\n    __typename\n  }\n  limits {\n    ...ProviderLimits\n    __typename\n  }\n  __typename\n}\n\nfragment RegularUserFragment on UserFragment {\n  id\n  username\n  role\n  avatarURL\n  isOnline\n  isBlocked\n  rating\n  testimonialCounter\n  createdAt\n  supportChatId\n  systemChatId\n  __typename\n}\n\nfragment RegularTransactionProps on TransactionPropsFragment {\n  creatorId\n  dealId\n  paidFromPendingIncome\n  paymentURL\n  successURL\n  fee\n  paymentAccount {\n    id\n    value\n    __typename\n  }\n  paymentGateway\n  alreadySpent\n  exchangeRate\n  amountAfterConversionRub\n  amountAfterConversionUsdt\n  userData {\n    account\n    email\n    ipAddress\n    phoneNumber\n    __typename\n  }\n  __typename\n}\n\nfragment UserEdgeNode on UserFragment {\n  ...RegularUserFragment\n  __typename\n}",
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
    
    def remove_transaction(self, transaction_id: str) -> types.Transaction:
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
            "query": "mutation removeTransaction($id: UUID!) {\n  removeTransaction(id: $id) {\n    ...RegularTransaction\n    __typename\n  }\n}\n\nfragment RegularTransaction on Transaction {\n  id\n  operation\n  direction\n  providerId\n  provider {\n    ...RegularTransactionProvider\n    __typename\n  }\n  user {\n    ...RegularUserFragment\n    __typename\n  }\n  creator {\n    ...RegularUserFragment\n    __typename\n  }\n  status\n  statusDescription\n  statusExpirationDate\n  value\n  fee\n  createdAt\n  props {\n    ...RegularTransactionProps\n    __typename\n  }\n  verifiedAt\n  verifiedBy {\n    ...UserEdgeNode\n    __typename\n  }\n  completedBy {\n    ...UserEdgeNode\n    __typename\n  }\n  paymentMethodId\n  completedAt\n  isSuspicious\n  spbBankName\n  __typename\n}\n\nfragment RegularTransactionProvider on TransactionProvider {\n  id\n  name\n  fee\n  minFeeAmount\n  description\n  account {\n    ...RegularTransactionProviderAccount\n    __typename\n  }\n  props {\n    ...TransactionProviderPropsFragment\n    __typename\n  }\n  limits {\n    ...ProviderLimits\n    __typename\n  }\n  paymentMethods {\n    ...TransactionPaymentMethod\n    __typename\n  }\n  __typename\n}\n\nfragment RegularTransactionProviderAccount on TransactionProviderAccount {\n  id\n  value\n  userId\n  providerId\n  paymentMethodId\n  __typename\n}\n\nfragment TransactionProviderPropsFragment on TransactionProviderPropsFragment {\n  requiredUserData {\n    ...TransactionProviderRequiredUserData\n    __typename\n  }\n  tooltip\n  __typename\n}\n\nfragment TransactionProviderRequiredUserData on TransactionProviderRequiredUserData {\n  email\n  phoneNumber\n  eripAccountNumber\n  __typename\n}\n\nfragment ProviderLimits on ProviderLimits {\n  incoming {\n    ...ProviderLimitRange\n    __typename\n  }\n  outgoing {\n    ...ProviderLimitRange\n    __typename\n  }\n  __typename\n}\n\nfragment ProviderLimitRange on ProviderLimitRange {\n  min\n  max\n  __typename\n}\n\nfragment TransactionPaymentMethod on TransactionPaymentMethod {\n  id\n  name\n  fee\n  providerId\n  account {\n    ...RegularTransactionProviderAccount\n    __typename\n  }\n  props {\n    ...TransactionProviderPropsFragment\n    __typename\n  }\n  limits {\n    ...ProviderLimits\n    __typename\n  }\n  __typename\n}\n\nfragment RegularUserFragment on UserFragment {\n  id\n  username\n  role\n  avatarURL\n  isOnline\n  isBlocked\n  rating\n  testimonialCounter\n  createdAt\n  supportChatId\n  systemChatId\n  __typename\n}\n\nfragment RegularTransactionProps on TransactionPropsFragment {\n  creatorId\n  dealId\n  paidFromPendingIncome\n  paymentURL\n  successURL\n  fee\n  paymentAccount {\n    id\n    value\n    __typename\n  }\n  paymentGateway\n  alreadySpent\n  exchangeRate\n  amountAfterConversionRub\n  amountAfterConversionUsdt\n  userData {\n    account\n    email\n    ipAddress\n    phoneNumber\n    __typename\n  }\n  __typename\n}\n\nfragment UserEdgeNode on UserFragment {\n  ...RegularUserFragment\n  __typename\n}",
            "variables": {
                "id": transaction_id
            }
        }
        r = self.request("post", f"{self.base_url}/graphql", headers, payload).json()
        return transaction(r["data"]["removeTransaction"])