from __future__ import annotations
from typing import *
import json

from .account import Account, get_account
from . import parser
from .enums import *



class FileObject:
    """
    Объект файла.

    :param id: ID файла.
    :type id: `str`

    :param url: URL файла.
    :type url: `str`

    :param filename: Имя файла.
    :type filename: `str` or `None`

    :param mime: Mime файла.
    :type mime: `str` or `None`
    """
    def __init__(self, id: str, url: str, 
                 filename: str | None, mime: str | None):
        self.id: str = id
        """ ID файла. """
        self.url: str = url
        """ URL файла. """
        self.filename: str | None = filename
        """ Имя файла. """
        self.mime: str | None = mime
        """ Mime файла. """


class AccountBalance:
    """
    Подкласс, описывающий баланс аккаунта.

    :param id: ID баланса.
    :type id: `str`

    :param value: Сумма баланса.
    :type value: `int`

    :param frozen: Сумма замороженного баланса.
    :type frozen: `int`

    :param available: Сумма доступного баланса.
    :type available: `int`

    :param withdrawable: Сумма баланса, доступного для вывода.
    :type withdrawable: `int`

    :param pending_income: Ожидаемый доход.
    :type pending_income: `int`
    """
    def __init__(self, id: str, value: int, frozen: int, available: int, 
                 withdrawable: int, pending_income: int):
        self.id: str = id
        """ ID баланса. """
        self.value: int = value
        """ Сумма общего баланса. """
        self.frozen: int = frozen
        """ Сумма замороженного баланса. """
        self.available: int = available
        """ Сумма доступного баланса. """
        self.withdrawable: int = withdrawable
        """ Сумма баланса, доступного для вывода. """
        self.pending_income: int = pending_income
        """ Ожидаемый доход. """


class AccountIncomingDealsStats:
    """
    Подкласс, описывающий статистику входящих сделок аккаунта.

    :param total: Всего исходящих сделок.
    :type total: `int`

    :param finished: Завершённых исходящих сделок.
    :type finished: `int`
    """
    def __init__(self, total: int, finished: int):
        self.total: int = total
        """ Всего исходящих сделок. """
        self.finished: int = finished
        """ Кол-во завершённых исходящих сделок. """


class AccountOutgoingDealsStats:
    """
    Подкласс, описывающий статистику исходящих сделок аккаунта.

    :param total: Всего исходящих сделок.
    :type total: `int`

    :param finished: Завершённых исходящих сделок.
    :type finished: `int`
    """
    def __init__(self, total: int, finished: int):
        self.total = total
        """ Всего исходящих сделок. """
        self.finished = finished
        """ Кол-во завершённых исходящих сделок. """


class AccountDealsStats:
    """
    Подкласс, описывающий статистику сделок аккаунта.

    :param incoming: Входящие сделки.
    :type incoming: `playerokapi.types.AccountIncomingDealsStats`

    :param outgoing: Исходящие сделки.
    :type outgoing: `playerokapi.types.AccountOutgoingDealsStats`
    """
    def __init__(self, incoming: AccountIncomingDealsStats, outgoing: AccountOutgoingDealsStats):
        self.incoming: AccountIncomingDealsStats = incoming
        """ Входящие сделки. """
        self.outgoing: AccountOutgoingDealsStats = outgoing
        """ Исходящие сделки. """


class AccountItemsStats:
    """
    Подкласс, описывающий статистику предметов аккаунта.

    :param total: Всего предметов.
    :type total: `int`

    :param finished: Завершённых предметов.
    :type finished: `int`
    """
    def __init__(self, total: int, finished: int):
        self.total: int = total
        """ Всего предметов. """
        self.finished: int = finished
        """ Кол-во завершённых предметов. """


class AccountStats:
    """
    Подкласс, описывающий статистику аккаунта.

    :param items: Статистика предметов.
    :type items: `playerokapi.types.AccountItemsStats`

    :param deals: Статистика сделок.
    :type deals: `playerokapi.types.AccountDealsStats`
    """
    def __init__(self, items: AccountItemsStats, deals: AccountDealsStats):
        self.items: AccountItemsStats = items
        """ Статистика предметов. """
        self.deals: AccountDealsStats = deals
        """ Статистика сделок. """


class AccountProfile:
    """
    Класс, описывающий профиль аккаунта.

    :param id: ID аккаунта.
    :type id: `str`

    :param username: Никнейм аккаунта.
    :type username: `str`

    :param email: Почта аккаунта.
    :type email: `str`

    :param balance: Объект баланса аккаунта.
    :type balance: `playerokapi.types.AccountBalance`

    :param stats: Статистика аккаунта.
    :type stats: `str`

    :param role: Роль аккаунта.
    :type role: `playerokapi.enums.UserTypes`

    :param avatar_url: URL аватара аккаунта.
    :type avatar_url: `str`

    :param is_online: В онлайне ли сейчас аккаунт.
    :type is_online: `bool`

    :param is_blocked: Заблокирован ли аккаунт.
    :type is_blocked: `bool`

    :param is_blocked_for: Причина блокировки.
    :type is_blocked_for: `str`

    :param is_verified: Верифицирован ли аккаунт.
    :type is_verified: `bool`

    :param rating: Рейтинг аккаунта (0-5).
    :type rating: `int`

    :param reviews_count: Кол-во отзывов на аккаунте.
    :type reviews_count: `int`

    :param created_at: Дата создания аккаунта.
    :type created_at: `str`

    :param support_chat_id: ID чата поддержки.
    :type support_chat_id: `str`

    :param system_chat_id: ID системного чата.
    :type system_chat_id: `str`

    :param has_frozen_balance: Заморожен ли баланс на аккаунте.
    :type has_frozen_balance: `bool`

    :param has_enabled_notifications: Включены ли уведомления на аккаунте.
    :type has_enabled_notifications: `bool`
    """
    def __init__(self, id: str, username: str, email: str, balance: AccountBalance, stats: AccountStats, role: UserTypes, avatar_url: str, is_online: bool, is_blocked: bool,
                 is_blocked_for: str, is_verified: bool, rating: int, reviews_count: int, created_at: str, support_chat_id: str, system_chat_id: str,
                 has_frozen_balance: bool, has_enabled_notifications: bool):
        self.id: str = id
        """ ID аккаунта. """
        self.username: str = username
        """ Никнейм аккаунта. """
        self.email: str = email
        """ Почта аккаунта. """
        self.balance: AccountBalance = balance
        """ Объект баланса аккаунта. """
        self.stats: AccountStats = stats
        """ Статистика аккаунта. """
        self.role: UserTypes  = role
        """ Роль аккаунта. """
        self.avatar_url: str = avatar_url
        """ URL аватара аккаунта. """
        self.is_online: bool = is_online
        """ В онлайне ли сейчас аккаунт. """
        self.is_blocked: bool = is_blocked
        """ Заблокирован ли аккаунт. """
        self.is_blocked_for: bool = is_blocked_for
        """ Причина блокировки аккаунта. """
        self.is_verified: bool = is_verified
        """ Верифицирован ли аккаунт. """
        self.rating: int = rating
        """ Рейтинг аккаунта (0-5). """
        self.reviews_count: int = reviews_count
        """ Кол-во отзывов на аккаунте. """
        self.created_at: str = created_at
        """ Дата создания аккаунта. """
        self.support_chat_id: str = support_chat_id
        """ ID чата поддержки аккаунта. """
        self.system_chat_id: str = system_chat_id
        """ ID системного чата аккаунта. """
        self.has_frozen_balance: bool = has_frozen_balance
        """ Заморожен ли баланс на аккаунте. """
        self.has_enabled_notifications: bool = has_enabled_notifications
        """ Включены ли уведомления на аккаунте. """


class UserProfile:
    """
    Класс, описывающий профиль пользователя.

    :param id: ID пользователя.
    :type id: `str`

    :param username: Никнейм пользователя.
    :type username: `str`

    :param role: Роль пользователя.
    :type role: `playerokapi.enums.UserTypes`

    :param avatar_url: URL аватара пользователя.
    :type avatar_url: `str`

    :param is_online: В онлайне ли сейчас пользователь.
    :type is_online: `bool`

    :param is_blocked: Заблокирован ли пользователь.
    :type is_blocked: `bool`

    :param rating: Рейтинг пользователя (0-5).
    :type rating: `int`

    :param reviews_count: Кол-во отзывов пользователя.
    :type reviews_count: `int`

    :param support_chat_id: ID чата поддержки.
    :type support_chat_id: `str` or `None`

    :param system_chat_id: ID системного чата.
    :type system_chat_id: `str` or `None`

    :param created_at: Дата создания аккаунта пользователя.
    :type created_at: `str`
    """
    def __init__(self, id: str, username: str, role: UserTypes, avatar_url: str, is_online: bool, is_blocked: bool, 
                 rating: int, reviews_count: int, support_chat_id: str, system_chat_id: str | None, created_at: str | None):
        self.id: str = id
        """ ID пользователя. """
        self.username: str = username
        """ Никнейм пользователя. """
        self.role: UserTypes = role
        """ Роль пользователя. """
        self.avatar_url: str = avatar_url
        """ URL аватара. """
        self.is_online: bool = is_online
        """ В онлайне ли сейчас пользователь. """
        self.is_blocked: bool = is_blocked
        """ Заблокирован ли пользователь. """
        self.rating: int = rating
        """ Рейтинг пользователя (0-5). """
        self.reviews_count: int = reviews_count
        """ Кол-во отзывов пользователя. """
        self.support_chat_id: str | None = support_chat_id
        """ ID чата поддержки. """
        self.system_chat_id: str | None = system_chat_id
        """ ID системного чата. """
        self.created_at: str = created_at
        """ Дата создания аккаунта пользователя. """

        self.__account: Account | None = get_account()
        """ Объект аккаунта (для методов). """


    def get_items(self, count: int = 24, statuses: list[ItemStatuses] | None = None,
                  after_cursor: str | None = None) -> ItemProfileList:
        """
        Получает предметы пользователя.

        :param count: Кол-во предеметов, которые нужно получить (не более 24 за один запрос), _опционально_.
        :type count: `int`

        :param status: Массив типов предметов, которые нужно получить. Некоторые статусы можно получить только, если это профиль вашего аккаунта. Если не указано, получает сразу все возможные.
        :type status: `list[playerokapi.enums.ItemStatuses]`

        :param after_cursor: Курсор, с которого будет идти парсинг (если нету - ищет с самого начала страницы), _опционально_.
        :type after_cursor: `str` or `None`
        
        :return: Страница профилей предметов.
        :rtype: `PlayerokAPI.types.ItemProfileList`
        """
        payload_status = [] if statuses else None
        if statuses:
            for status in statuses:
                payload_status.append(status.name)
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Origin": self.__account.base_url
        }
        payload = {
            "operationName": "items",
            "variables": json.dumps({"pagination": {"first": count, "after": after_cursor}, "filter": {"userId": self.id, "status": payload_status}, "showForbiddenImage": False}, ensure_ascii=False),
            "extensions": json.dumps({"persistedQuery": {"version": 1, "sha256Hash": "29ff7e8c607c7b3f2fa3c7a9e02a3a184bf92905e8ea75ba237c8c7f005287a3"}}, ensure_ascii=False)
        }
        r = self.__account.request("get", f"{self.__account.base_url}/graphql", headers, payload).json()
        return parser.item_profile_list(r["data"]["items"])

    def get_reviews(self, count: int = 24, status: ReviewStatuses = ReviewStatuses.APPROVED, 
                    comment_required: bool = False, rating: int | None = None, game_id: str | None = None, 
                    category_id: str | None = None, min_item_price: int | None = None, max_item_price: int | None = None, 
                    sort_direction: SortDirections = SortDirections.DESC, sort_field: str = "createdAt", after_cursor: str | None = None) -> ReviewList:
        """
        Получает отзывы пользователя.

        :param count: Кол-во отзывов, которые нужно получить (не более 24 за один запрос), _опционально_.
        :type count: `int`

        :param status: Тип отзывов, которые нужно получить.
        :type status: `playerokapi.enums.ReviewStatuses`

        :param comment_required: Обязателен ли комментарий в отзыве, _опционально_.
        :type comment_required: `bool`

        :param rating: Рейтинг отзывов (1-5), _опционально_.
        :type rating: `int` or `None`

        :param game_id: ID игры отзывов, _опционально_.
        :type game_id: `str` or `None`

        :param category_id: ID категории отзывов, _опционально_.
        :type category_id: `str` or `None`

        :param min_item_price: Минимальная цена предмета отзыва, _опционально_.
        :type min_item_price: `bool` or `None`

        :param max_item_price: Максимальная цена предмета отзыва, _опционально_.
        :type max_item_price: `bool` or `None`

        :param sort_direction: Тип сортировки.
        :type sort_direction: `playerokapi.enums.SortDirections`

        :param sort_field: Поле, по которому будет идти сортировка (по умолчанию `createdAt` - по дате)
        :type sort_field: `str`

        :param after_cursor: Курсор, с которого будет идти парсинг (если нету - ищет с самого начала страницы), _опционально_.
        :type after_cursor: `str` or `None`
        
        :return: Страница отзывов.
        :rtype: `PlayerokAPI.types.ReviewList`
        """
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Origin": self.__account.base_url,
        }

        filters = {"userId": self.id, "status": [status.name] if status else None}
        if comment_required is not None:
            filters["hasComment"] = comment_required
        if game_id is not None:
            filters["gameId"] = game_id
        if category_id is not None:
            filters["categoryId"] = category_id
        if rating is not None:
            filters["rating"] = rating
        if min_item_price is not None or max_item_price is not None:
            item_price = {}
            if min_item_price is not None:
                item_price["min"] = min_item_price
            if max_item_price is not None:
                item_price["max"] = max_item_price
            filters["itemPrice"] = item_price
        payload = {
            "operationName": "testimonials",
            "variables": json.dumps({"pagination": {"first": count, "after": after_cursor}, "filter": filters, "sort": {"direction": sort_direction.name if sort_direction else None, "field": sort_field}}, ensure_ascii=False),
            "extensions": json.dumps({"persistedQuery": {"version": 1, "sha256Hash": "773d40b7efec82a4b86021ba8bcaa462f68eb236e255926f2168c5cd4685e881"}}, ensure_ascii=False)
        }
        r = self.__account.request("get", f"{self.__account.base_url}/graphql", headers, payload).json()
        return parser.review_list(r["data"]["testimonials"])


class Event:
    #TODO: Сделать класс ивента Event

    def __init__(self):
        pass


class ItemDeal:
    """
    Объект сделки с предметом.

    :param id: ID сделки.
    :type id: `str`

    :param status: Статус сделки.
    :type status: `playerokapi.enums.ItemDealStatuses`

    :param status_expiration_date: Дата истечения статуса.
    :type status_expiration_date: `str` or `None`

    :param status_description: Описание статуса сделки.
    :type status_description: `str` or `None`

    :param direction: Направление сделки (покупка/продажа).
    :type direction: `playerokapi.enums.ItemDealDirections`

    :param obtaining: Получение сделки.
    :type obtaining: `str` or `None`

    :param has_problem: Есть ли проблема в сделке.
    :type has_problem: `bool`

    :param report_problem_enabled: Включено ли обжалование проблемы.
    :type report_problem_enabled: `bool` or `None`

    :param completed_user: Профиль пользователя, подтвердившего сделку.
    :type completed_user: `playerokapi.types.UserProfile` or `None`

    :param props: Реквизиты сделки.
    :type props: `str` or `None`

    :param previous_status: Предыдущий статус.
    :type previous_status: `playerokapi.enums.ItemDealStatuses` or `None`

    :param completed_at: Дата подтверждения сделки.
    :type completed_at: `str` or `None`

    :param created_at: Дата создания сделки.
    :type created_at: `str` or `None`

    :param logs: Логи сделки.
    :type logs: `list[playerokapi.types.ItemLog]` or `None`

    :param transaction: Транзакция сделки.
    :type transaction: `playerokapi.types.Transaction` or `None`

    :param user: Профиль пользователя, совершившего сделку.
    :type user: `playerokapi.types.UserProfile`

    :param chat: Чат сделки (передаётся только его ID).
    :type chat: `playerokapi.types.Chat` or `None`

    :param item: Предмет сделки.
    :type item: `playerokapi.types.Item`

    :param review: Отзыв по сделке.
    :type review: `playerokapi.types.Review` or `None`

    :param obtaining_fields: Получаемые поля.
    :type obtaining_fields: `list[playerokapi.types.GameCategoryDataField]` or `None`

    :param comment_from_buyer: Комментарий от покупателя.
    :type comment_from_buyer: `str` or `None`
    """
    def __init__(self, id: str, status: ItemDealStatuses, status_expiration_date: str | None, status_description: str | None, 
                 direction: ItemDealDirections, obtaining: str | None, has_problem: bool, report_problem_enabled: bool | None, 
                 completed_user: UserProfile | None, props: str | None, previous_status: ItemDealStatuses | None, 
                 completed_at: str, created_at: str, logs: list[ItemLog] | None, transaction: Transaction | None,
                 user: UserProfile, chat: Chat | None, item: Item, review: Review | None, obtaining_fields: list[GameCategoryDataField] | None,
                 comment_from_buyer: str | None):
        self.id: str = id
        """ ID сделки. """
        self.status: ItemDealStatuses = status
        """ Статус сделки. """
        self.status_expiration_date: str | None = status_expiration_date
        """ Дата истечения статуса. """
        self.status_description: str | None = status_description
        """ Описание статуса сделки. """
        self.direction: ItemDealDirections = direction
        """ Направление сделки (покупка/продажа). """
        self.obtaining: str | None = obtaining
        """ Получение сделки. """
        self.has_problem: bool = has_problem
        """ Есть ли проблема в сделке. """
        self.report_problem_enabled: bool | None = report_problem_enabled
        """ Включено ли обжалование проблемы. """
        self.completed_user: UserProfile | None = completed_user
        """ Профиль пользователя, подтвердившего сделку. """
        self.props: str | None = props
        """ Реквизиты сделки. """
        self.previous_status: ItemDealStatuses | None = previous_status
        """ Предыдущий статус. """
        self.completed_at: str | None = completed_at
        """ Дата подтверждения сделки. """
        self.created_at: str | None = created_at
        """ Дата создания сделки. """
        self.logs: list[ItemLog] | None = logs
        """ Логи сделки. """
        self.transaction: Transaction | None = transaction
        """ Транзакция сделки. """
        self.user: UserProfile = user
        """ Профиль пользователя, совершившего сделку. """
        self.chat: Chat | None = chat
        """ Чат сделки (передаётся только его ID). """
        self.item: Item = item
        """ Предмет сделки. """
        self.review: Review | None = review
        """ Отзыв по сделке. """
        self.obtaining_fields: list[GameCategoryDataField] | None = obtaining_fields
        """ Получаемые поля. """
        self.comment_from_buyer: str | None = comment_from_buyer
        """ Комментарий от покупателя. """


class ItemDealPageInfo:
    """
    Подкласс, описывающий информацию о странице сделок.

    :param start_cursor: Курсор начала страницы.
    :type start_cursor: `str`

    :param end_cursor: Курсок конца страницы.
    :type end_cursor: `str`

    :param has_previous_page: Имеет ли предыдущую страницу.
    :type has_previous_page: `bool`

    :param has_next_page: Имеет ли следующую страницу.
    :type has_next_page: `bool`
    """
    def __init__(self, start_cursor: str, end_cursor: str,
                 has_previous_page: bool, has_next_page: bool):
        self.start_cursor: str = start_cursor
        """ Курсор начала страницы. """
        self.end_cursor: str = end_cursor
        """ Курсор конца страницы. """
        self.has_previous_page: bool = has_previous_page
        """ Имеет ли предыдущую страницу. """
        self.has_next_page: bool = has_next_page
        """ Имеет ли следующую страницу. """


class ItemDealList:
    """
    Класс, описывающий страницу отзывов.

    :param deals: Сделки страницы.
    :type deals: `list[playerokapi.types.ItemDeal]`

    :param page_info: Информация о странице.
    :type page_info: `playerokapi.types.ItemDealPageInfo`

    :param total_count: Всего сделок.
    :type total_count: `int`
    """
    def __init__(self, deals: list[ItemDeal], page_info: ItemDealPageInfo,
                 total_count: int):
        self.deals: list[ItemDeal] = deals
        """ Сделки страницы. """
        self.page_info: ItemDealPageInfo = page_info
        """ Информация о странице. """
        self.total_count: int = total_count
        """ Всего сделок. """


class GameCategoryAgreement:
    """
    Подкласс, описывающий соглашения покупателя.

    :param id: ID соглашения.
    :type id: `str`

    :param description: Описание соглашения.
    :type description: `str`

    :param icontype: Тип иконки соглашения.
    :type icontype: `playerokapi.enums.GameCategoryAgreementIconTypes`

    :param sequence: Последовательность соглашения.
    :type sequence: `str`
    """
    def __init__(self, id: str, description: str, 
                 icontype: GameCategoryAgreementIconTypes, sequence: int):
        self.id: str = id
        """ ID соглашения. """
        self.description: str = description
        """ Описание соглашения. """
        self.icontype: GameCategoryAgreementIconTypes = icontype
        """ Тип иконки соглашения. """
        self.sequence: str = sequence
        """ Последовательность соглашения. """


class GameCategoryAgreementPageInfo:
    """
    Подкласс, описывающий информацию о странице соглашений покупателя.

    :param start_cursor: Курсор начала страницы.
    :type start_cursor: `str`

    :param end_cursor: Курсок конца страницы.
    :type end_cursor: `str`

    :param has_previous_page: Имеет ли предыдущую страницу.
    :type has_previous_page: `bool`

    :param has_next_page: Имеет ли следующую страницу.
    :type has_next_page: `bool`
    """
    def __init__(self, start_cursor: str, end_cursor: str,
                 has_previous_page: bool, has_next_page: bool):
        self.start_cursor: str = start_cursor
        """ Курсор начала страницы. """
        self.end_cursor: str = end_cursor
        """ Курсор конца страницы. """
        self.has_previous_page: bool = has_previous_page
        """ Имеет ли предыдущую страницу. """
        self.has_next_page: bool = has_next_page
        """ Имеет ли следующую страницу. """


class GameCategoryAgreementList:
    """
    Класс, описывающий страницу соглашений покупателя.

    :param agreements: Соглашения страницы.
    :type agreements: `list[playerokapi.types.GameCategoryAgreement]`

    :param page_info: Информация о странице.
    :type page_info: `playerokapi.types.GameCategoryAgreementPageInfo`

    :param total_count: Всего соглашений.
    :type total_count: `int`
    """
    def __init__(self, agreements: list[GameCategoryAgreement], page_info: GameCategoryAgreementPageInfo,
                 total_count: int):
        self.agreements: list[GameCategoryAgreement] = agreements
        """ Соглашения страницы. """
        self.page_info: GameCategoryAgreementPageInfo = page_info
        """ Информация о странице. """
        self.total_count: int = total_count
        """ Всего соглашений. """


class GameCategoryObtainingType:
    """
    Подкласс, описывающий тип (способ) получения предмета в категории.

    :param id: ID способа.
    :type id: `str`

    :param name: Название способа.
    :type name: `str`

    :param description: Описание способа.
    :type description: `str`

    :param game_category_id: ID категории игры способа.
    :type game_category_id: `str`

    :param no_comment_from_buyer: Без комментария от покупателя?
    :type no_comment_from_buyer: `bool`

    :param instruction_for_buyer: Инструкция для покупателя.
    :type instruction_for_buyer: `str`

    :param instruction_for_seller: Инструкция для продавца.
    :type instruction_for_seller: `str`

    :param sequence: Последовательность способа.
    :type sequence: `int`

    :param fee_multiplier: Множитель комиссии.
    :type fee_multiplier: `float`

    :param agreements: Соглашения покупателя на покупку/продавца на продажу.
    :type agreements: `list[playerokapi.types.GameCategoryAgreement]`

    :param props: Пропорции категории.
    :type props: `playerokapi.types.GameCategoryProps`
    """
    def __init__(self, id: str, name: str, description: str, game_category_id: str, no_comment_from_buyer: bool,
                 instruction_for_buyer: str | None, instruction_for_seller: str | None, sequence: int, fee_multiplier: float,
                 agreements: list[GameCategoryAgreement], props: GameCategoryProps):
        self.id: str = id
        """ ID способа. """
        self.name: str = name
        """ Название способа. """
        self.description: str = description
        """ Описание способа. """
        self.game_category_id: str = game_category_id
        """ ID категории игры способа. """
        self.no_comment_from_buyer: bool = no_comment_from_buyer
        """ Без комментария от покупателя? """
        self.instruction_for_buyer: str | None = instruction_for_buyer
        """ Инструкция для покупателя. """
        self.instruction_for_seller: str | None = instruction_for_seller
        """ Инструкция для продавца. """
        self.sequence: int = sequence
        """ Последовательность способа. """
        self.fee_multiplier: float = fee_multiplier
        """ Множитель комиссии. """
        self.agreements: list[GameCategoryAgreement] = agreements
        """ Соглашения покупателя на покупку/продавца на продажу. """
        self.props: GameCategoryProps = props
        """ Пропорции категории. """


class GameCategoryObtainingTypePageInfo:
    """
    Подкласс, описывающий информацию о странице типов (способов) получения предмета в категории.

    :param start_cursor: Курсор начала страницы.
    :type start_cursor: `str`

    :param end_cursor: Курсок конца страницы.
    :type end_cursor: `str`

    :param has_previous_page: Имеет ли предыдущую страницу.
    :type has_previous_page: `bool`

    :param has_next_page: Имеет ли следующую страницу.
    :type has_next_page: `bool`
    """
    def __init__(self, start_cursor: str, end_cursor: str,
                 has_previous_page: bool, has_next_page: bool):
        self.start_cursor: str = start_cursor
        """ Курсор начала страницы. """
        self.end_cursor: str = end_cursor
        """ Курсор конца страницы. """
        self.has_previous_page: bool = has_previous_page
        """ Имеет ли предыдущую страницу. """
        self.has_next_page: bool = has_next_page
        """ Имеет ли следующую страницу. """


class GameCategoryObtainingTypeList:
    """
    Класс, описывающий страницу типов (способов) получения предмета в категории.

    :param obtaining_types: Способы страницы.
    :type obtaining_types: `list[playerokapi.types.GameCategoryObtainingType]`

    :param page_info: Информация о странице.
    :type page_info: `playerokapi.types.GameCategoryObtainingTypePageInfo`

    :param total_count: Всего способов.
    :type total_count: `int`
    """
    def __init__(self, obtaining_types: list[GameCategoryObtainingType], page_info: GameCategoryObtainingTypePageInfo,
                 total_count: int):
        self.obtaining_types: list[GameCategoryObtainingType] = obtaining_types
        """ Соглашения страницы. """
        self.page_info: GameCategoryAgreementPageInfo = page_info
        """ Информация о странице. """
        self.total_count: int = total_count
        """ Всего способов. """


class GameCategoryDataField:
    """
    Подкласс, описывающий поля с данными предмета в категории (которые отправляются после покупки).

    :param id: ID поля с данными.
    :type id: `str`

    :param label: Надпись-название поля.
    :type label: `str`

    :param type: Тип поля с данными.
    :type type: `playerokapi.enums.GameCategoryDataFieldTypes`

    :param input_type: Тип вводимого значения поля.
    :type input_type: `playerokapi.enums.GameCategoryDataFieldInputTypes`

    :param copyable: Разрешено ли копирование значения с поля.
    :type copyable: `bool`

    :param hidden: Скрыты ли данные в поле.
    :type hidden: `bool`

    :param required: Обязательно ли это поле.
    :type required: `bool`

    :param value: Значение данных в поле.
    :type value: `str` or `None`
    """
    def __init__(self, id: str, label: str, type: GameCategoryDataFieldTypes,
                 input_type: GameCategoryDataFieldInputTypes, copyable: bool, 
                 hidden: bool, required: bool, value: str | None):
        self.id: str = id
        """ ID поля с данными. """
        self.label: str = label
        """ Надпись-название поля. """
        self.type: GameCategoryDataFieldTypes = type
        """ Тип поля с данными. """
        self.input_type: GameCategoryDataFieldInputTypes = input_type
        """ Тип вводимого значения поля. """
        self.copyable: bool = copyable
        """ Разрешено ли копирование значения с поля. """
        self.hidden: bool = hidden
        """ Скрыты ли данные в поле. """
        self.required: bool = required
        """ Обязательно ли это поле. """
        self.value: str | None = value
        """ Значение данных в поле. """


class GameCategoryDataFieldPageInfo:
    """
    Подкласс, описывающий информацию о странице полей с данными предмета.

    :param start_cursor: Курсор начала страницы.
    :type start_cursor: `str`

    :param end_cursor: Курсок конца страницы.
    :type end_cursor: `str`

    :param has_previous_page: Имеет ли предыдущую страницу.
    :type has_previous_page: `bool`

    :param has_next_page: Имеет ли следующую страницу.
    :type has_next_page: `bool`
    """
    def __init__(self, start_cursor: str, end_cursor: str,
                 has_previous_page: bool, has_next_page: bool):
        self.start_cursor: str = start_cursor
        """ Курсор начала страницы. """
        self.end_cursor: str = end_cursor
        """ Курсор конца страницы. """
        self.has_previous_page: bool = has_previous_page
        """ Имеет ли предыдущую страницу. """
        self.has_next_page: bool = has_next_page
        """ Имеет ли следующую страницу. """


class GameCategoryDataFieldList:
    """
    Класс, описывающий страницу полей с данными предмета.

    :param data_fields: Поля с данными предмета в категории на странице.
    :type data_fields: `list[playerokapi.types.GameCategoryDataField]`

    :param page_info: Информация о странице.
    :type page_info: `playerokapi.types.GameCategoryDataFieldPageInfo`

    :param total_count: Всего полей с данными.
    :type total_count: `int`
    """
    def __init__(self, data_fields: list[GameCategoryDataField], 
                 page_info: GameCategoryDataFieldPageInfo, total_count: int):
        self.data_fields: list[GameCategoryDataField] = data_fields
        """ Поля с данными предмета в категории на странице. """
        self.page_info: GameCategoryDataFieldPageInfo = page_info
        """ Информация о странице. """
        self.total_count: int = total_count
        """ Всего полей с данными. """


class GameCategoryProps:
    """
    Подкласс, описывающий пропорции категории.

    :param min_reviews: Минимальное количество отзывов.
    :type min_reviews: `int`

    :param min_reviews_for_seller: Минимальное количество отзывов для продавца.
    :type min_reviews_for_seller: `int`
    """
    def __init__(self, min_reviews: int, min_reviews_for_seller: int):
        self.min_reviews: int = min_reviews
        """ Минимальное количество отзывов. """
        self.min_reviews_for_seller: int = min_reviews_for_seller
        """ Минимальное количество отзывов для продавца. """


class GameCategoryOption:
    """
    Подкласс, описывающий опцию категории.

    :param id: ID опции.
    :type id: `str`

    :param group: Группа опции.
    :type group: `str`

    :param label: Надпись-название опции.
    :type label: `str`

    :param type: Тип опции.
    :type type: `playerokapi.enums.GameCategoryOptionTypes`

    :param field: Название поля (для payload запроса на сайт).
    :type field: `str`

    :param value: Значение поля (для payload запроса на сайт).
    :type value: `str`

    :param value_range_limit: Лимит разброса по значению.
    :type value_range_limit: `int` or `None`
    """
    def __init__(self, id: str, group: str, label: str, type: GameCategoryOptionTypes,
                 field: str, value: str, value_range_limit: int | None):
        self.id: str = id
        """ ID опции. """
        self.group: str = group
        """ Группа опции. """
        self.label: str = label
        """ Надпись-название опции. """
        self.type: GameCategoryOptionTypes = type
        """ Тип опции. """
        self.field: str = field
        """ Название поля (для payload запроса на сайт). """
        self.value: str = value
        """ Значение поля (для payload запроса на сайт). """
        self.value_range_limit: int | None = value_range_limit
        """ Лимит разброса по значению. """


class GameCategoryInstruction:
    """
    Подкласс, описывающий информацию о странице инструкии по продаже/покупке в категории.

    :param id: ID инструкции.
    :type id: `str`

    :param text: Текст инструкции.
    :type text: `str`
    """
    def __init__(self, id: str, text: str):
        self.id: str = id
        """ ID инструкции. """
        self.text: str = text
        """ Текст инструкции. """


class GameCategoryInstructionPageInfo:
    """
    Подкласс, описывающий инструкцию по продаже/покупке в категории.

    :param start_cursor: Курсор начала страницы.
    :type start_cursor: `str`

    :param end_cursor: Курсок конца страницы.
    :type end_cursor: `str`

    :param has_previous_page: Имеет ли предыдущую страницу.
    :type has_previous_page: `bool`

    :param has_next_page: Имеет ли следующую страницу.
    :type has_next_page: `bool`
    """
    def __init__(self, start_cursor: str, end_cursor: str,
                 has_previous_page: bool, has_next_page: bool):
        self.start_cursor: str = start_cursor
        """ Курсор начала страницы. """
        self.end_cursor: str = end_cursor
        """ Курсор конца страницы. """
        self.has_previous_page: bool = has_previous_page
        """ Имеет ли предыдущую страницу. """
        self.has_next_page: bool = has_next_page
        """ Имеет ли следующую страницу. """


class GameCategoryInstructionList:
    """
    Класс, описывающий страницу инструкций по продаже/покупке в категории.

    :param instructions: Инструкции страницы.
    :type instructions: `list[playerokapi.types.GameCategoryInstruction]`

    :param page_info: Информация о странице.
    :type page_info: `playerokapi.types.GameCategoryInstructionPageInfo`

    :param total_count: Всего инструкций.
    :type total_count: `int`
    """
    def __init__(self, instructions: list[GameCategoryInstruction], page_info: GameCategoryInstructionPageInfo,
                 total_count: int):
        self.instructions: list[GameCategoryInstruction] = instructions
        """ Соглашения страницы. """
        self.page_info: GameCategoryInstructionPageInfo = page_info
        """ Информация о странице. """
        self.total_count: int = total_count
        """ Всего инструкций. """


class GameCategory:
    """
    Объект категории игры/приложения.

    :param id: ID категории.
    :type id: `str`

    :param slug: Имя страницы категории.
    :type slug: `str`

    :param name: Название категории.
    :type name: `str`

    :param category_id: ID родительской категории.
    :type category_id: `str` or `None`

    :param game_id: ID игры категории.
    :type game_id: `str` or `None`

    :param obtaining: Тип получения.
    :type obtaining: `str` or `None` or `None`

    :param options: Опции категории.
    :type options: `list[playerokapi.types.GameCategoryOption]` or `None`

    :param props: Пропорции категории.
    :type props: `playerokapi.types.GameCategoryProps` or `None`

    :param no_comment_from_buyer: Без комментария от покупателя?
    :type no_comment_from_buyer: `bool` or `None`

    :param instruction_for_buyer: Инструкция для покупателя.
    :type instruction_for_buyer: `str` or `None`

    :param instruction_for_seller: Инструкция для продавца.
    :type instruction_for_seller: `str` or `None`

    :param use_custom_obtaining: Используется ли кастомное получение.
    :type use_custom_obtaining: `bool`

    :param auto_confirm_period: Период авто-подтверждения сделки этой категории.
    :type auto_confirm_period: `playerokapi.enums.GameCategoryAutoConfirmPeriods` or `None`

    :param auto_moderation_mode: Включена ли автоматическая модерация.
    :type auto_moderation_mode: `bool` or `None`

    :param agreements: Соглашения покупателя.
    :type agreements: `list[playerokapi.types.GameCategoryAgreement]` or `None`

    :param fee_multiplier: Множитель комиссии.
    :type fee_multiplier: `float` or `None`
    """
    def __init__(self, id: str, slug: str, name: str, category_id: str | None, game_id: str | None,
                 obtaining: str | None, options: list[GameCategoryOption] | None, props: GameCategoryProps | None, 
                 no_comment_from_buyer: bool | None, instruction_for_buyer: str | None, instruction_for_seller: str | None, 
                 use_custom_obtaining: bool, auto_confirm_period: GameCategoryAutoConfirmPeriods | None, 
                 auto_moderation_mode: bool | None, agreements: list[GameCategoryAgreement] | None, fee_multiplier: float | None):
        self.id: str = id
        """ ID категории. """
        self.slug: str = slug
        """ Имя страницы категории. """
        self.name: str = name
        """ Название категории. """
        self.category_id: str | None = category_id
        """ ID родительской категории. """
        self.game_id: str | None = game_id
        """ ID игры категории. """
        self.obtaining: str | None = obtaining
        """ Тип получения. """
        self.options: list[GameCategoryOption] | None = options
        """ Опции категории. """
        self.props: str | None = props
        """ Пропорции категории. """
        self.no_comment_from_buyer: bool | None = no_comment_from_buyer
        """ Без комментария от покупателя? """
        self.instruction_for_buyer: str | None = instruction_for_buyer
        """ Инструкция для покупателя. """
        self.instruction_for_seller: str | None = instruction_for_seller
        """ Инструкция для продавца. """
        self.use_custom_obtaining: bool = use_custom_obtaining
        """ Используется ли кастомное получение. """
        self.auto_confirm_period: GameCategoryAutoConfirmPeriods | None = auto_confirm_period
        """ Период авто-подтверждения сделки этой категории. """
        self.auto_moderation_mode: bool | None = auto_moderation_mode
        """ Включена ли автоматическая модерация. """
        self.agreements: list[GameCategoryAgreement] | None = agreements
        """ Соглашения покупателя. """
        self.fee_multiplier: float | None = fee_multiplier
        """ Множитель комиссии. """


class Game:
    """
    Объект игры/приложения.

    :param id: ID игры/приложения.
    :type id: `str`

    :param slug: Имя страницы игры/приложения.
    :type slug: `str`

    :param name: Название игры/приложения.
    :type name: `str`

    :param type: Тип: игра или приложение.
    :type type: `playerokapi.enums.GameTypes`

    :param logo: Лого игры/приложения.
    :type logo: `playerokapi.types.FileObject`

    :param banner: Баннер игры/приложения.
    :type banner: `FileObject`

    :param categories: Список категорий игры/приложения.
    :type categories: `list[playerokapi.types.GameCategory]`

    :param created_at: Дата создания.
    :type created_at: `str`
    """
    def __init__(self, id: str, slug: str, name: str, type: GameTypes, 
                 logo: FileObject, banner: FileObject, categories: list[GameCategory], 
                 created_at: str):
        self.id: str = id
        """ ID игры/приложения. """
        self.slug: str = slug
        """ Имя страницы игры/приложения. """
        self.name: str = name
        """ Название игры/приложения. """
        self.type: GameTypes = type
        """ Тип: игра или приложение. """
        self.logo: FileObject = logo
        """ Лого игры/приложения. """
        self.banner: FileObject = banner
        """ Баннер игры/приложения. """
        self.categories: list[GameCategory] = categories
        """ Список категорий игры/приложения. """
        self.created_at: str = created_at
        """ Дата создания. """


class GameProfile:
    """
    Профиль игры/приложения.

    :param id: ID игры/приложения.
    :type id: `str`

    :param slug: Имя страницы игры/приложения.
    :type slug: `str`

    :param name: Название игры/приложения.
    :type name: `str`

    :param type: Тип: игра или приложение.
    :type type: `playerokapi.types.GameTypes`

    :param logo: Лого игры/приложения.
    :type logo: `playerokapi.types.FileObject`
    """
    def __init__(self, id: str, slug: str, name: str, 
                 type: GameTypes, logo: FileObject):
        self.id: str = id
        """ ID игры/приложения. """
        self.slug: str = slug
        """ Имя страницы игры/приложения. """
        self.name: str = name
        """ Название игры/приложения. """
        self.type: GameTypes = id
        """ Тип: игра или приложение. """
        self.logo: FileObject = logo
        """ Лого игры/приложения. """


class GamePageInfo:
    """
    Подкласс, описывающий информацию о странице игр.

    :param start_cursor: Курсор начала страницы.
    :type start_cursor: `str`

    :param end_cursor: Курсок конца страницы.
    :type end_cursor: `str`

    :param has_previous_page: Имеет ли предыдущую страницу.
    :type has_previous_page: `bool`

    :param has_next_page: Имеет ли следующую страницу.
    :type has_next_page: `bool`
    """
    def __init__(self, start_cursor: str, end_cursor: str,
                 has_previous_page: bool, has_next_page: bool):
        self.start_cursor: str = start_cursor
        """ Курсор начала страницы. """
        self.end_cursor: str = end_cursor
        """ Курсор конца страницы. """
        self.has_previous_page: bool = has_previous_page
        """ Имеет ли предыдущую страницу. """
        self.has_next_page: bool = has_next_page
        """ Имеет ли следующую страницу. """


class GameList:
    """
    Класс, описывающий страницу игр.

    :param games: Игры/приложения страницы.
    :type games: `list[playerokapi.types.Game]`

    :param page_info: Информация о странице.
    :type page_info: `playerokapi.types.ChatPageInfo`

    :param total_count: Всего игр.
    :type total_count: `int`
    """
    def __init__(self, games: list[Game], page_info: GamePageInfo,
                 total_count: int):
        self.games: list[Game] = games
        """ Игры/приложения страницы. """
        self.page_info: ChatPageInfo = page_info
        """ Информация о странице. """
        self.total_count: int = total_count
        """ Всего игр. """


class ItemPriorityStatusPriceRange:
    """
    Подкласс, описывающий ценовой диапазон предмета, подходящего для опред. статуса приоритета.

    :param min: Минимальная цена предмета.
    :type min: `int`

    :param max: Максимальная цена предмета.
    :type max: `int`
    """
    def __init__(self, min: int, max: str):
        self.min: int = min
        """ Минимальная цена предмета (в рублях). """
        self.max: int = max
        """ Максимальная цена предмета (в рублях). """


class ItemPriorityStatus:
    """
    Класс, описывающий статус приоритета предмета.

    :param id: ID статуса приоритета.
    :type id: `str`

    :param price: Цена статуса (в рублях).
    :type price: `int`

    :param name: Название статуса.
    :type name: `str`

    :param type: Тип статуса.
    :type type: `playerokapi.enums.PriorityTypes`

    :param period: Длительность статуса (в днях).
    :type period: `str`

    :param price_range: Ценовой диапазон предмета статуса.
    :type price_range: `playerokapi.types.ItemPriorityStatusPriceRange`
    """
    def __init__(self, id: str, price: int, name: str, type: PriorityTypes,
                 period: int, price_range: ItemPriorityStatusPriceRange):
        self.id: str = id
        """ ID статуса приоритета. """
        self.price: int = price
        """ Цена статуса (в рублях). """
        self.name: str = name
        """ Название статуса. """
        self.type: PriorityTypes = type
        """ Тип статуса. """
        self.period: int = period
        """ Длительность статуса (в днях). """
        self.price_range: ItemPriorityStatusPriceRange = price_range
        """ Ценовой диапазон предмета статуса. """


class ItemLog:
    """
    Подкласс, описывающий лог действия с предметом.
    
    :param id: ID лога.
    :type id: `str`
    
    :param event: Событие лога.
    :type event: `playerokapi.enums.ItemLogEvents`
    
    :param created_at: Дата создания лога.
    :type created_at: `str`
    
    :param user: Профиль пользователя, совершившего лог.
    :type user: `playerokapi.types.UserProfile`
    """
    def __init__(self, id: str, event: ItemLogEvents, created_at: str,
                 user: UserProfile):
        self.id: str = id
        """ ID лога. """
        self.event: ItemLogEvents = event
        """ Событие лога. """
        self.created_at: str = created_at
        """ Дата создания лога. """
        self.user: UserProfile = user
        """ Профиль пользователя, совершившего лог. """


class Item:
    """
    Объект предмета.

    :param id: ID предмета.
    :type id: `str`

    :param name: Название предмета.
    :type name: `str`

    :param description: Описание предмета.
    :type description: `str`

    :param status: Статус предмета.
    :type status: `playerokapi.enums.ItemStatuses`

    :param obtaining_type: Способ получения.
    :type obtaining_type: `playerokapi.types.GameCategoryObtainingType` or `None`

    :param price: Цена предмета.
    :type price: `int`

    :param raw_price: Цена без учёта скидки.
    :type raw_price: `int`

    :param priority_position: Приоритетная позиция.
    :type priority_position: `int`

    :param attachments: Файлы-приложения.
    :type attachments: `list[playerokapi.types.FileObject]`

    :param attributes: Аттрибуты предмета.
    :type attributes: `dict`

    :param category: Категория игры предмета.
    :type category: `playerokapi.types.GameCategory`

    :param comment: Комментарий предмета.
    :type comment: `str` or `None`

    :param data_fields: Поля данных предмета.
    :type data_fields: `list[playerokapi.types.GameCategoryDataField]` or `None`

    :param fee_multiplier: Множитель комиссии.
    :type fee_multiplier: `float`

    :param game: Профиль игры предмета.
    :type game: `playerokapi.types.GameProfile`

    :param seller_type: Тип продавца.
    :type seller_type: `playerokapi.enums.UserTypes`

    :param slug: Имя страницы предмета.
    :type slug: `str`

    :param user: Профиль продавца.
    :type user: `playerokapi.types.UserProfile`
    """
    def __init__(self, id: str, slug: str, name: str, description: str, obtaining_type: GameCategoryObtainingType | None, price: int, raw_price: int, priority_position: int,
                 attachments: list[FileObject], attributes: dict, category: GameCategory, comment: str | None, data_fields: list[GameCategoryDataField] | None, 
                 fee_multiplier: float, game: GameProfile, seller_type: UserTypes, status: ItemStatuses, user: UserProfile):
        self.id: str = id
        """ ID предмета. """
        self.slug: str = slug
        """ Имя страницы предмета. """
        self.name: str = name
        """ Название предмета. """
        self.description: str = description
        """ Описание предмета. """
        self.obtaining_type: GameCategoryObtainingType | None = obtaining_type
        """ Способ получения. """
        self.price: int = price
        """ Цена предмета. """
        self.raw_price: int = raw_price
        """ Цена без учёта скидки. """
        self.priority_position: int = priority_position
        """ Приоритетная позиция. """
        self.attachments: list[FileObject] = attachments
        """ Файлы-приложения. """
        self.attributes: dict = attributes
        """ Аттрибуты предмета. """
        self.category: GameCategory = category
        """ Категория игры предмета. """
        self.comment: str | None = comment
        """ Комментарий предмета. """
        self.data_fields: list[GameCategoryDataField] | None = data_fields
        """ Поля данных предмета. """
        self.fee_multiplier: float = fee_multiplier
        """ Множитель комиссии. """
        self.game: GameProfile = game
        """ Профиль игры предмета. """
        self.seller_type: UserTypes = seller_type
        """ Тип продавца. """
        self.slug: str = slug
        """ Имя страницы предмета. """
        self.status: ItemStatuses = status
        """ Статус предмета. """
        self.user: UserProfile = user
        """ Профиль продавца. """


class MyItem:
    """
    Объект своего предмета.

    :param id: ID предмета.
    :type id: `str`

    :param slug: Имя страницы предмета.
    :type slug: `str`

    :param name: Название предмета.
    :type name: `str`

    :param description: Описание предмета.
    :type description: `str`

    :param status: Статус предмета.
    :type status: `playerokapi.enums.ItemStatuses`

    :param obtaining_type: Способ получения.
    :type obtaining_type: `playerokapi.types.GameCategoryObtainingType` or `None`

    :param price: Цена предмета.
    :type price: `int`

    :param prev_price: Предыдущая цена.
    :type prev_price: `int`

    :param raw_price: Цена без учёта скидки.
    :type raw_price: `int`

    :param priority_position: Приоритетная позиция.
    :type priority_position: `int`

    :param attachments: Файлы-приложения.
    :type attachments: `list[playerokapi.types.FileObject]`

    :param attributes: Аттрибуты предмета.
    :type attributes: `dict`

    :param category: Категория игры предмета.
    :type category: `playerokapi.types.GameCategory`

    :param comment: Комментарий предмета.
    :type comment: `str` or `None`

    :param data_fields: Поля данных предмета.
    :type data_fields: `list[playerokapi.types.GameCategoryDataField]` or `None`

    :param fee_multiplier: Множитель комиссии.
    :type fee_multiplier: `float`

    :param prev_fee_multiplier: Предыдущий множитель комиссии.
    :type prev_fee_multiplier: `float`

    :param seller_notified_about_fee_change: Оповещён ли продавец о смене комиссии.
    :type seller_notified_about_fee_change: `bool`

    :param game: Профиль игры предмета.
    :type game: `playerokapi.types.GameProfile`

    :param seller_type: Тип продавца.
    :type seller_type: `playerokapi.enums.UserTypes`

    :param user: Профиль продавца.
    :type user: `playerokapi.types.UserProfile`

    :param buyer: Профиль продавца.
    :type user: `playerokapi.types.UserProfile`

    :param priority: Статус приоритета предмета.
    :type priority: `playerokapi.types.PriorityTypes`

    :param priority_price: Цены статуса приоритета.
    :type priority_price: `int`

    :param status_expiration_date: Дата истечения статуса приоритета.
    :type status_expiration_date: `str` or `None`

    :param status_description: Описание статуса приоритета.
    :type status_description: `str` or `None`

    :param status_payment: Платёж статуса (транзакция).
    :type status_payment: `playerokapi.types.Transaction` or `None`

    :param views_counter: Количество просмотров предмета.
    :type views_counter: `int`

    :param is_editable: Можно ли редактировать товар.
    :type is_editable: `bool`

    :param approval_date: Дата публикации товара.
    :type approval_date: `str` or `None`

    :param deleted_at: Дата удаления товара.
    :type deleted_at: `str` or `None`

    :param updated_at: Дата последнего обновления товара.
    :type updated_at: `str` or `None`

    :param created_at: Дата создания товара.
    :type created_at: `str` or `None`
    """
    def __init__(self, id: str, slug: str, name: str, description: str, obtaining_type: GameCategoryObtainingType | None, price: int, raw_price: int, priority_position: int,
                 attachments: list[FileObject], attributes: dict, buyer: UserProfile, category: GameCategory, comment: str | None,
                 data_fields: list[GameCategoryDataField] | None, fee_multiplier: float, game: GameProfile, seller_type: UserTypes, status: ItemStatuses,
                 user: UserProfile, prev_price: int, prev_fee_multiplier: float, seller_notified_about_fee_change: bool, 
                 priority: PriorityTypes, priority_price: int, status_expiration_date: str | None, status_description: str | None,
                 status_payment: Transaction | None, views_counter: int, is_editable: bool, approval_date: str | None, deleted_at: str | None, 
                 updated_at: str | None, created_at: str | None):
        self.id: str = id
        """ ID предмета. """
        self.slug: str = slug
        """ Имя страницы предмета. """
        self.name: str = name
        """ Название предмета. """
        self.status: ItemStatuses = status
        """ Статус предмета. """
        self.description: str = description
        """ Описание предмета. """
        self.obtaining_type: GameCategoryObtainingType | None = obtaining_type
        """ Способ получения. """
        self.price: int = price
        """ Цена предмета. """
        self.prev_price: int = prev_price
        """ Предыдущая цена. """
        self.raw_price: int = raw_price
        """ Цена без учёта скидки. """
        self.priority_position: int = priority_position
        """ Приоритетная позиция. """
        self.attachments: list[FileObject] = attachments
        """ Файлы-приложения. """
        self.attributes: dict = attributes
        """ Аттрибуты предмета. """
        self.category: GameCategory = category
        """ Категория игры предмета. """
        self.comment: str | None = comment
        """ Комментарий предмета. """
        self.data_fields: list[GameCategoryDataField] | None = data_fields
        """ Поля данных предмета. """
        self.fee_multiplier: float = fee_multiplier
        """ Множитель комиссии. """
        self.prev_fee_multiplier: float = prev_fee_multiplier
        """ Предыдущий множитель комиссии. """
        self.seller_notified_about_fee_change: bool = seller_notified_about_fee_change
        """ Оповещён ли продавец о смене комиссии. """
        self.game: GameProfile = game
        """ Профиль игры предмета. """
        self.seller_type: UserTypes = seller_type
        """ Тип продавца. """
        self.user: UserProfile = user
        """ Профиль продавца. """
        self.buyer: UserProfile = buyer
        """ Профиль покупателя предмета (если продан). """
        self.priority: PriorityTypes = priority
        """ Статус приоритета предмета. """
        self.priority_price: int = priority_price
        """ Цены статуса приоритета. """
        self.status_expiration_date: str | None = status_expiration_date
        """ Дата истечения статуса приоритета. """
        self.status_description: str | None = status_description
        """ Описание статуса приоритета. """
        self.status_payment: str | None = status_payment
        """ Платёж статуса (транзакция). """
        self.views_counter: int = views_counter
        """ Количество просмотров предмета. """
        self.is_editable: bool = is_editable
        """ Можно ли редактировать товар. """
        self.approval_date: str | None = approval_date
        """ Дата публикации товара. """
        self.deleted_at: str | None = deleted_at
        """ Дата удаления товара. """
        self.updated_at: str | None = updated_at
        """ Дата последнего обновления товара. """
        self.created_at: str | None = created_at
        """ Дата создания товара. """


class ItemProfile:
    """
    Профиль предмета.

    :param id: ID предмета.
    :type id: `str`

    :param slug: Имя страницы предмета.
    :type slug: `str`

    :param priority: Приоритет предмета.
    :type priority: `playerokapi.enums.PriorityTypes`

    :param status: Статус предмета.
    :type status: `playerokapi.enums.ItemStatuses`

    :param name: Название предмета.
    :type name: `str`

    :param price: Цена предмета.
    :type price: `int`

    :param raw_price: Цена без учёта скидки.
    :type raw_price: `int`

    :param seller_type: Тип продавца.
    :type seller_type: `playerokapi.enums.UserTypes`

    :param attachment: Файл-приложение.
    :type attachment: `playerokapi.types.FileObject`

    :param user: Профиль продавца.
    :type user: `playerokapi.types.UserProfile`

    :param approval_date: Дата одобрения.
    :type approval_date: `str`

    :param priority_position: Приоритетная позиция.
    :type priority_position: `int`

    :param views_counter: Количество просмотров.
    :type views_counter: `int` or `None`

    :param fee_multiplier: Множитель комиссии.
    :type fee_multiplier: `float`

    :param created_at: Дата создания.
    :type created_at: `str`
    """
    def __init__(self, id: str, slug: str, priority: PriorityTypes, status: ItemStatuses,
                 name: str, price: int, raw_price: int, seller_type: UserTypes, attachment: FileObject,
                 user: UserProfile, approval_date: str, priority_position: int, views_counter: int | None, 
                 fee_multiplier: float, created_at: str):
        self.id: str = id
        """ ID предмета. """
        self.slug: str = slug
        """ Имя страницы предмета. """
        self.priority: PriorityTypes = priority
        """ Приоритет предмета. """
        self.status: ItemStatuses = status
        """ Статус предмета. """
        self.name: str = name
        """ Название предмета. """
        self.price: int = price
        """ Цена предмета. """
        self.raw_price: int = raw_price
        """ Цена без учёта скидки. """
        self.seller_type: UserTypes = seller_type
        """ Тип продавца. """
        self.attachment: FileObject = attachment
        """ Файл-приложение. """
        self.user: UserProfile = user
        """ Профиль продавца. """
        self.approval_date: str = approval_date
        """ Дата одобрения. """
        self.priority_position: int = priority_position
        """ Приоритетная позиция. """
        self.views_counter: int | None = views_counter
        """ Количество просмотров. """
        self.fee_multiplier: float = fee_multiplier
        """ Множитель комиссии. """
        self.created_at: str = created_at
        """ Дата создания. """


class ItemProfilePageInfo:
    """
    Подкласс, описывающий информацию о странице предметов.

    :param start_cursor: Курсор начала страницы.
    :type start_cursor: `str`

    :param end_cursor: Курсок конца страницы.
    :type end_cursor: `str`

    :param has_previous_page: Имеет ли предыдущую страницу.
    :type has_previous_page: `bool`

    :param has_next_page: Имеет ли следующую страницу.
    :type has_next_page: `bool`
    """
    def __init__(self, start_cursor: str, end_cursor: str,
                 has_previous_page: bool, has_next_page: bool):
        self.start_cursor: str = start_cursor
        """ Курсор начала страницы. """
        self.end_cursor: str = end_cursor
        """ Курсор конца страницы. """
        self.has_previous_page: bool = has_previous_page
        """ Имеет ли предыдущую страницу. """
        self.has_next_page: bool = has_next_page
        """ Имеет ли следующую страницу. """


class ItemProfileList:
    """
    Профиль страницы предметов.

    :param items: Предметы страницы.
    :type items: `list[playerokapi.types.Item]`

    :param page_info: Информация о странице.
    :type page_info: `playerokapi.types.ItemProfilePageInfo`

    :param total_count: Всего предметов.
    :type total_count: `int`
    """
    def __init__(self, items: list[ItemProfile], page_info: ItemProfilePageInfo,
                 total_count: int):
        self.items: list[ItemProfile] = items
        """ Предметы страницы. """
        self.page_info: ItemProfilePageInfo = page_info
        """ Информация о странице. """
        self.total_count: int = total_count
        """ Всего предметов. """


class SBPBankMember:
    """
    Объект членов СБП банка.

    :param id: ID.
    :type id: `str`

    :param name: Название.
    :type name: `str`

    :param icon: URL иконки.
    :type icon: `str`
    """
    def __init__(self, id: str, name: str, icon: str):
        self.id: str = id
        """ ID. """
        self.name: str = name
        """ Название. """
        self.icon: str = icon
        """ URL иконки. """


class TransactionPaymentMethod:
    """
    Платёжный метод транзакции.

    :param id: ID метода.
    :type id: `playerokapi.types.TransactionPaymentMethodIds`

    :param name: Название метода.
    :type name: `str`

    :param fee: Комиссия метода.
    :type fee: `int`

    :param provider_id: ID провайдера транзакции.
    :type provider_id: `playerokapi.types.TransactionProviderIds`

    :param account: Аккаунт метода (?).
    :type account: `AccountProfile` or `None`

    :param props: Параметры провайдера транзакции.
    :type props: `playerokapi.types.TransactionProviderProps`

    :param limits: Лимиты провайдера транзакции.
    :type limits: `playerokapi.types.TransactionProviderLimits`
    """
    def __init__(self, id: TransactionPaymentMethodIds, name: str, fee: int, provider_id: TransactionProviderIds,
                 account: AccountProfile | None, props: TransactionProviderProps, limits: TransactionProviderLimits):
        self.id: TransactionPaymentMethodIds = id
        """ ID метода. """
        self.name: str = name
        """ Названиие метода. """
        self.fee: int = fee
        """ Комиссия метода. """
        self.provider_id: TransactionProviderIds = provider_id
        """ ID провайдера транзакции. """
        self.account: AccountProfile | None = account
        """ Аккаунт метода (?). """
        self.props: TransactionProviderProps = props
        """ Параметры провайдера транзакции. """
        self.limits: TransactionProviderLimits = limits
        """ Лимиты провайдера транзакции. """


class TransactionProviderLimitRange:
    """
    Диапозон лимитов провайдера транзакции.

    :param min: Минимальная сумма (в рублях).
    :type min: `int`

    :param max: Максимальная сумма (в рублях).
    :type max: `int`
    """
    def __init__(self, min: int, max: int):
        self.min: int = min
        """ Минимальная сумма (в рублях). """
        self.max: int = max
        """ Максимальная сумма (в рублях). """


class TransactionProviderLimits:
    """
    Лимиты провайдера транзакции.

    :param incoming: На пополнение.
    :type incoming: `playerokapi.types.TransactionProviderLimitRange`

    :param outgoing: На вывод.
    :type outgoing: `playerokapi.types.TransactionProviderLimitRange`
    """
    def __init__(self, incoming: TransactionProviderLimitRange, outgoing: TransactionProviderLimitRange):
        self.incoming: TransactionProviderLimitRange = incoming
        """ На пополнение. """
        self.outgoing: TransactionProviderLimitRange = outgoing
        """ На вывод. """


class TransactionProviderRequiredUserData:
    """
    Обязательные пользовательские данные провайдера транзакции.

    :param email: Обязательно ли указывать EMail?
    :type email: `bool`

    :param phone_number: Обязательно ли указывать номер телефона?
    :type phone_number: `bool`

    :param erip_account_number: Обязательно ли указывать номер аккаунта ЕРИП?
    :type erip_account_number: `bool` or `None`
    """
    def __init__(self, email: bool, phone_number: bool, 
                 erip_account_number: bool | None):
        self.email: bool = email
        """ Обязательно ли указывать EMail? """
        self.phone_number: bool = phone_number
        """ Обязательно ли указывать номер телефона? """
        self.erip_account_number: bool | None = erip_account_number
        """ Обязательно ли указывать номер аккаунта ЕРИП? """


class TransactionProviderProps:
    """
    Параметры провайдера транзакции.

    :param required_user_data: Обязательные пользовательские данные.
    :type required_user_data: `playerokapi.types.TransactionProviderRequiredUserData`

    :param tooltip: Подсказка.
    :type tooltip: `str` or `None`
    """
    def __init__(self, required_user_data: TransactionProviderRequiredUserData,
                 tooltip: str | None):
        self.required_user_data: TransactionProviderRequiredUserData = required_user_data
        """ Обязательные пользовательские данные. """
        self.tooltip: str | None = tooltip
        """ Подсказка. """


class TransactionProvider:
    """
    Объект провайдера транзакции.

    :param id: ID провайдера.
    :type id: `playerokapi.enums.TransactionProviderIds`

    :param name: Название провайдера.
    :type name: `str`

    :param fee: Комиссия провайдера.
    :type fee: `int`

    :param min_fee_amount: Минимальная комиссия.
    :type min_fee_amount: `int` or `None`

    :param description: Описание провайдера.
    :type description: `str` or `None`

    :param account: Аккаунт провайдера (?).
    :type account: `playerokapi.types.AccountProfile` or `None`

    :param props: Параметры провайдера.
    :type props: `playerokapi.types.TransactionProviderProps`

    :param limits: Лимиты провайдера.
    :type limits: `playerokapi.types.TransactionProviderLimits`

    :param payment_methods: Платёжные методы.
    :type payment_methods: `list` of `playerokapi.types.TransactionPaymentMethod`
    """
    def __init__(self, id: TransactionProviderIds, name: str, fee: int, min_fee_amount: int | None, 
                 description: str | None, account: AccountProfile | None, props: TransactionProviderProps, 
                 limits: TransactionProviderLimits, payment_methods: list[TransactionPaymentMethod]):
        self.id: TransactionProviderIds = id
        """ ID провайдера. """
        self.name: str = name
        """ Название провайдера. """
        self.fee: int = fee
        """ Комиссия провайдера. """
        self.min_fee_amount: int | None = min_fee_amount
        """ Минимальная комиссия. """
        self.description: str | None = description
        """ Описание провайдера. """
        self.account: AccountProfile | None = account
        """ Аккаунт провайдера (?). """
        self.props: TransactionProviderProps = props
        """ Параметры провайдера. """
        self.limits: TransactionProviderLimits = limits
        """ Лимиты провайдера. """
        self.payment_methods: list[TransactionPaymentMethod] = payment_methods
        """ Платёжные методы. """


class Transaction:
    """
    Объект транзакции.

    :param id: ID транзакции.
    :type id: `str`

    :param operation: Тип выполненной операции.
    :type operation: `playerokapi.enums.TransactionOperations`

    :param direction: Направление транзакции.
    :type direction: `playerokapi.enums.TransactionDirections`

    :param provider_id: ID платёжного провайдера.
    :type provider_id: `playerokapi.enums.TransactionProviderIds`

    :param provider: Объект провайдера транзакции.
    :type provider: `playerokapi.types.TransactionProvider`

    :param user: Объект пользователя-совершателя транзакции.
    :type user: `playerokapi.types.UserProfile`

    :param creator: Объект пользователя-создателя транзакции.
    :type creator: `playerokapi.types.UserProfile` or `None`

    :param status: Статус обработки транзакции.
    :type status: `playerokapi.enums.TransactionStatuses`

    :param status_description: Описание статуса.
    :type status_description: `str` or `None`

    :param status_expiration_date: Дата истечения статуса.
    :type status_expiration_date: `str` or `None`

    :param value: Сумма транзакции.
    :type value: `int`

    :param fee: Комиссия транзакции.
    :type fee: `int`

    :param created_at: Дата создания транзакции.
    :type created_at: `str`

    :param verified_at: Дата подтверждения транзакции.
    :type verified_at: `str` or `None`

    :param verified_by: Объект пользователя, подтвердившего транзакцию.
    :type verified_by: `playerokapi.types.UserProfile` or `None`

    :param completed_at: Дата выполнения транзакции.
    :type completed_at: `str` or `None`

    :param completed_by: Объект пользователя, выполнившего транзакцию.
    :type completed_by: `playerokapi.types.UserProfile` or `None`

    :param payment_method_id: ID способа оплаты.
    :type payment_method_id: `str` or `None`

    :param is_suspicious: Подозрительная ли транзакция.
    :type is_suspicious: `bool` or `None`

    :param sbp_bank_name: Название банка СБП (если транзакция была совершена с помощью СБП).
    :type sbp_bank_name: `str` or `None`
    """
    def __init__(self, id: str, operation: TransactionOperations, direction: TransactionDirections, provider_id: TransactionProviderIds, 
                 provider: TransactionProvider, user: UserProfile, creator: UserProfile, status: TransactionStatuses, status_description: str | None, 
                 status_expiration_date: str | None, value: int, fee: int, created_at: str, verified_at: str | None, verified_by: UserProfile | None, 
                 completed_at: str | None, completed_by: UserProfile | None, payment_method_id: str | None, is_suspicious: bool | None, sbp_bank_name: str | None):
        self.id: str = id
        """ ID транзакции. """
        self.operation: TransactionOperations = operation
        """ Тип выполненной операции. """
        self.direction: TransactionDirections = direction
        """ Направление транзакции. """
        self.provider_id: TransactionProviderIds = provider_id
        """ ID платёжного провайдера. """
        self.provider: TransactionProvider = provider
        """ Объект провайдера транзакции. """
        self.user: UserProfile = user
        """ Объект пользователя-совершателя транзакции. """
        self.creator: UserProfile | None = creator
        """ Объект пользователя-создателя транзакции. """
        self.status: TransactionStatuses = status
        """ Статус обработки транзакции. """
        self.status_description: str | None = status_description
        """ Описание статуса. """
        self.status_expiration_date: str | None = status_expiration_date
        """ Дата истечения статуса. """
        self.value: int = value
        """ Сумма транзакции. """
        self.fee: int = fee
        """ Комиссия транзакции. """
        self.created_at: str = created_at
        """ Дата создания транзакции. """
        self.verified_at: str | None = verified_at
        """ Дата подтверждения транзакции. """
        self.verified_by: UserProfile | None = verified_by
        """ Объект пользователя, подтвердившего транзакцию. """
        self.completed_at: str | None = completed_at
        """ Дата выполнения транзакции. """
        self.completed_by: UserProfile | None = completed_by
        """ Объект пользователя, выполнившего транзакцию. """
        self.payment_method_id: str | None = payment_method_id
        """ ID способа оплаты. """
        self.is_suspicious: bool | None = is_suspicious
        """ Подозрительная ли транзакция. """
        self.sbp_bank_name: str | None = sbp_bank_name
        """ Название банка СБП (если транзакция была совершена с помощью СБП). """


class TransactionPageInfo:
    """
    Подкласс, описывающий информацию о странице транзакций.

    :param start_cursor: Курсор начала страницы.
    :type start_cursor: `str`

    :param end_cursor: Курсок конца страницы.
    :type end_cursor: `str`

    :param has_previous_page: Имеет ли предыдущую страницу.
    :type has_previous_page: `bool`

    :param has_next_page: Имеет ли следующую страницу.
    :type has_next_page: `bool`
    """
    def __init__(self, start_cursor: str, end_cursor: str,
                 has_previous_page: bool, has_next_page: bool):
        self.start_cursor: str = start_cursor
        """ Курсор начала страницы. """
        self.end_cursor: str = end_cursor
        """ Курсор конца страницы. """
        self.has_previous_page: bool = has_previous_page
        """ Имеет ли предыдущую страницу. """
        self.has_next_page: bool = has_next_page
        """ Имеет ли следующую страницу. """


class TransactionList:
    """
    Класс, описывающий страницу сообщений чата.

    :param transactions: Транзакции страницы.
    :type transactions: `list[playerokapi.types.Transaction]`

    :param page_info: Информация о странице.
    :type page_info: `playerokapi.types.TransactionPageInfo`

    :param total_count: Всего транзакций на странице.
    :type total_count: `int`
    """
    def __init__(self, transactions: list[Transaction], page_info: TransactionPageInfo,
                 total_count: int):
        self.transactions: list[Transaction] = transactions
        """ Транзакции страницы. """
        self.page_info: TransactionPageInfo = page_info
        """ Информация о странице. """
        self.total_count: int = total_count
        """ Всего транзакций на странице. """


class UserBankCard:
    """
    Объект банковской карты пользователя.

    :param id: ID карты.
    :type id: `str`

    :param card_first_six: Первые шесть цифр карты.
    :type card_first_six: `str`

    :param card_last_four: Последние четыре цифры карты.
    :type card_last_four: `str`

    :param card_type: Тип банковской карты.
    :type card_type: `playerokapi.enums.BankCardTypes`

    :param is_chosen: Выбрана ли эта карта как по умолчанию?
    :type is_chosen: `bool`
    """
    def __init__(self, id: str, card_first_six: str, card_last_four: str,
                 card_type: BankCardTypes, is_chosen: bool):
        self.id: str = id
        """ ID карты. """
        self.card_first_six: str = card_first_six
        """ Первые шесть цифр карты. """
        self.card_last_four: str = card_last_four
        """ Последние четыре цифры карты. """
        self.card_type: BankCardTypes = card_type
        """ Тип банковской карты. """
        self.is_chosen: bool = is_chosen
        """ Выбрана ли эта карта как по умолчанию? """


class UserBankCardPageInfo:
    """
    Подкласс, описывающий информацию о странице банковских карт пользователя.

    :param start_cursor: Курсор начала страницы.
    :type start_cursor: `str`

    :param end_cursor: Курсок конца страницы.
    :type end_cursor: `str`

    :param has_previous_page: Имеет ли предыдущую страницу.
    :type has_previous_page: `bool`

    :param has_next_page: Имеет ли следующую страницу.
    :type has_next_page: `bool`
    """
    def __init__(self, start_cursor: str, end_cursor: str,
                 has_previous_page: bool, has_next_page: bool):
        self.start_cursor: str = start_cursor
        """ Курсор начала страницы. """
        self.end_cursor: str = end_cursor
        """ Курсор конца страницы. """
        self.has_previous_page: bool = has_previous_page
        """ Имеет ли предыдущую страницу. """
        self.has_next_page: bool = has_next_page
        """ Имеет ли следующую страницу. """


class UserBankCardList:
    """
    Класс, описывающий страницу банковских карт пользователя.

    :param bank_cards: Банковские карты страницы.
    :type bank_cards: `list[playerokapi.types.UserBankCard]`

    :param page_info: Информация о странице.
    :type page_info: `playerokapi.types.UserBankCardPageInfo`

    :param total_count: Всего банковских карт на странице.
    :type total_count: `int`
    """
    def __init__(self, bank_cards: list[UserBankCard], 
                 page_info: UserBankCardPageInfo, total_count: int):
        self.bank_cards: list[UserBankCard] = bank_cards
        """ Банковские карты страницы. """
        self.page_info: UserBankCardPageInfo = page_info
        """ Информация о странице. """
        self.total_count: int = total_count
        """ Всего банковских карт на странице. """


class Moderator:
    # TODO: Сделать класс модератора Moderator

    def __init__(self):
        pass


class ChatMessageButton:
    """
    Объект кнопки сообщения.

    :param type: Тип кнопки.
    :type type: `playerokapi.types.ChatMessageButtonTypes`

    :param url: URL кнопки.
    :type url: `str` or None

    :param text: Текст кнопки.
    :type text: `str`
    """
    def __init__(self, type: ChatMessageButtonTypes, 
                 url: str | None, text: str,):
        self.type: ChatMessageButtonTypes = type
        """ Тип кнопки. """
        self.url: str | None = url
        """ URL кнопки. """
        self.text: str = text
        """ Текст кнопки. """


class ChatMessage:
    """
    Класс, описывающий сообщение в чате.

    :param id: ID сообщения.
    :type id: `str`

    :param text: Текст сообщения.
    :type text: `str`

    :param created_at: Дата создания сообщения.
    :type created_at: `str`

    :param deleted_at: Дата удаления сообщения.
    :type deleted_at: `str` or `None`

    :param is_read: Прочитано ли сообщение.
    :type is_read: `bool`

    :param is_suspicious: Подозрительное ли сообщение.
    :type is_suspicious: `bool`

    :param is_bulk_messaging: Массовая ли это рассылка.
    :type is_bulk_messaging: `bool`

    :param game: Игра, к которой относится сообщение.
    :type game: `str` or `None`

    :param file: Файл, прикреплённый к сообщению.
    :type file: `playerokapi.types.FileObject` or `None`

    :param user: Пользователь, который отправил сообщение.
    :type user: `playerokapi.types.UserProfile`

    :param deal: Сделка, к которой относится сообщение.
    :type deal: `playerokapi.types.Deal` or `None`

    :param item: Предмет, к которому относится сообщение (обычно передаётся только сама сделка в переменную deal).
    :type item: `playerokapi.types.Item` or `None`

    :param transaction: Транзакция сообщения.
    :type transaction: `playerokapi.types.Transaction` or `None`

    :param moderator: Модератор сообщения.
    :type moderator: `playerokapi.types.Moderator`

    :param event_by_user: Ивент от пользователя.
    :type event_by_user: `playerokapi.types.UserProfile` or `None`

    :param event_to_user: Ивент для пользователя.
    :type event_to_user: `playerokapi.types.UserProfile` or `None`

    :param is_auto_response: Авто-ответ ли это.
    :type is_auto_response: `bool`

    :param event: Ивент сообщения.
    :type event: `playerokapi.types.Event` or `None`

    :param buttons: Кнопки сообщения.
    :type buttons: `list[playerokapi.types.MessageButton]`
    """
    def __init__(self, id: str, text: str, created_at: str, deleted_at: str | None, is_read: bool, 
                 is_suspicious: bool, is_bulk_messaging: bool, game: Game | None, file: FileObject | None,
                 user: UserProfile, deal: ItemDeal | None, item: ItemProfile | None, transaction: Transaction | None,
                 moderator: Moderator | None, event_by_user: UserProfile | None, event_to_user: UserProfile | None, 
                 is_auto_response: bool, event: Event | None, buttons: list[ChatMessageButton]):
        self.id: str = id
        """ ID сообщения. """
        self.text: str = text
        """ Текст сообщения. """
        self.created_at: str = created_at
        """ Дата создания сообщения. """
        self.deleted_at: str | None = deleted_at
        """ Дата удаления сообщения. """
        self.is_read: bool = is_read
        """ Прочитано ли сообщение. """
        self.is_suspicious: bool = is_suspicious
        """ Подозрительное ли сообщение. """
        self.is_bulk_messaging: bool = is_bulk_messaging
        """ Массовая ли это рассылка. """
        self.game: Game | None  = game
        """ Игра, к которой относится сообщение. """
        self.file: FileObject | None  = file
        """ Файл, прикреплённый к сообщению. """
        self.user: UserProfile = user
        """ Пользователь, который отправил сообщение. """
        self.deal: ItemDeal | None = deal
        """ Сделка, к которой относится сообщение. """
        self.item: ItemProfile | None = item
        """ Предмет, к которому относится сообщение (обычно передаётся только сама сделка в переменную deal). """
        self.transaction: Transaction | None = transaction
        """ Транзакция сообщения. """
        self.moderator: Moderator = moderator
        """ Модератор сообщения. """
        self.event_by_user: UserProfile | None = event_by_user
        """ Ивент от пользователя. """
        self.event_to_user: UserProfile | None = event_to_user
        """ Ивент для пользователя. """
        self.is_auto_response: bool = is_auto_response
        """ Авто-ответ ли это. """
        self.event: Event | None = event
        """ Ивент сообщения. """
        self.buttons: list[ChatMessageButton] = buttons
        """ Кнопки сообщения. """


class ChatMessagePageInfo:
    """
    Подкласс, описывающий информацию о странице сообщений.

    :param start_cursor: Курсор начала страницы.
    :type start_cursor: `str`

    :param end_cursor: Курсок конца страницы.
    :type end_cursor: `str`

    :param has_previous_page: Имеет ли предыдущую страницу.
    :type has_previous_page: `bool`

    :param has_next_page: Имеет ли следующую страницу.
    :type has_next_page: `bool`
    """
    def __init__(self, start_cursor: str, end_cursor: str,
                 has_previous_page: bool, has_next_page: bool):
        self.start_cursor: str = start_cursor
        """ Курсор начала страницы. """
        self.end_cursor: str = end_cursor
        """ Курсор конца страницы. """
        self.has_previous_page: bool = has_previous_page
        """ Имеет ли предыдущую страницу. """
        self.has_next_page: bool = has_next_page
        """ Имеет ли следующую страницу. """


class ChatMessageList:
    """
    Класс, описывающий страницу сообщений чата.

    :param messages: Сообщения страницы.
    :type messages: `list[playerokapi.types.ChatMessage]`

    :param page_info: Информация о странице.
    :type page_info: `playerokapi.types.ChatMessagePageInfo`

    :param total_count: Всего сообщений в чате.
    :type total_count: `int`
    """
    def __init__(self, messages: list[ChatMessage], page_info: ChatMessagePageInfo,
                 total_count: int):
        self.messages: list[ChatMessage] = messages
        """ Сообщения страницы. """
        self.page_info: ChatMessagePageInfo = page_info
        """ Информация о странице. """
        self.total_count: int = total_count
        """ Всего сообщений в чате. """


class Chat:
    """
    Объект чата.

    :param id: ID чата.
    :type id: `str`

    :param type: Тип чата.
    :type type: `playerokapi.enums.ChatTypes`

    :param status: Статус чата.
    :type status: `playerokapi.enums.ChatStatuses` or `None`

    :param unread_messages_counter: Количество непрочитанных сообщений.
    :type unread_messages_counter: `int`

    :param bookmarked: В закладках ли чат.
    :type bookmarked: `bool` or `None`

    :param is_texting_allowed: Разрешено ли писать в чат.
    :type is_texting_allowed: `bool` or `None`

    :param owner: Владелец чата (только если это чат с ботом).
    :type owner: `bool` or `None`

    :param deals: Сделки в чате.
    :type deals: `list[playerokapi.types.ItemDeal]` or `None`

    :param last_message: Объект последнего сообщения в чате
    :type last_message: `playerokapi.types.ChatMessage` or `None`

    :param users: Участники чата.
    :type users: `list[UserProfile]`

    :param started_at: Дата начала диалога.
    :type started_at: `str` or `None`

    :param finished_at: Дата завершения диалога.
    :type finished_at: `str` or `None`
    """
    def __init__(self, id: str, type: ChatTypes, status: ChatStatuses | None, unread_messages_counter: int, 
                 bookmarked: bool | None, is_texting_allowed: bool | None, owner: UserProfile | None, deals: list[ItemDeal] | None,
                 started_at: str | None, finished_at: str | None, last_message: ChatMessage | None, users: list[UserProfile]):
        self.id: str = id
        """ ID чата. """
        self.type: ChatTypes = type
        """ Тип чата. """
        self.status: ChatStatuses | None = status
        """ Статус чата. """
        self.unread_messages_counter: int = unread_messages_counter
        """ Количество непрочитанных сообщений. """
        self.bookmarked: bool | None = bookmarked
        """ В закладках ли чат. """
        self.is_texting_allowed: bool | None = is_texting_allowed
        """ Разрешено ли писать в чат. """
        self.owner: UserProfile = owner
        """ Владелец чата. """
        self.deals: list[ItemDeal] | None = deals
        """ Сделки в чате. """
        self.last_message: ChatMessage | None = last_message
        """ Объект последнего сообщения в чате. """
        self.users: list[UserProfile] = users
        """ Участники чата. """
        self.started_at: str | None = started_at
        """ Дата начала диалога. """
        self.finished_at: str | None = finished_at
        """ Дата завершения диалога. """


class ChatPageInfo:
    """
    Подкласс, описывающий информацию о странице чатов.

    :param start_cursor: Курсор начала страницы.
    :type start_cursor: `str`

    :param end_cursor: Курсок конца страницы.
    :type end_cursor: `str`

    :param has_previous_page: Имеет ли предыдущую страницу.
    :type has_previous_page: `bool`

    :param has_next_page: Имеет ли следующую страницу.
    :type has_next_page: `bool`
    """
    def __init__(self, start_cursor: str, end_cursor: str,
                 has_previous_page: bool, has_next_page: bool):
        self.start_cursor: str = start_cursor
        """ Курсор начала страницы. """
        self.end_cursor: str = end_cursor
        """ Курсор конца страницы. """
        self.has_previous_page: bool = has_previous_page
        """ Имеет ли предыдущую страницу. """
        self.has_next_page: bool = has_next_page
        """ Имеет ли следующую страницу. """


class ChatList:
    """
    Класс, описывающий страницу чатов.

    :param chats: Чаты страницы.
    :type chats: `list[playerokapi.types.Chat]`

    :param page_info: Информация о странице.
    :type page_info: `playerokapi.types.ChatPageInfo`

    :param total_count: Всего чатов.
    :type total_count: `int`
    """
    def __init__(self, chats: list[Chat], page_info: ChatPageInfo,
                 total_count: int):
        self.chats: list[Chat] = chats
        """ Чаты страницы. """
        self.page_info: ChatPageInfo = page_info
        """ Информация о странице. """
        self.total_count: int = total_count
        """ Всего чатов. """


class Review:
    """
    Объект отзыва.

    :param id: ID отзыва.
    :type id: `str`

    :param status: Статус отзыва.
    :type status: `playerokapi.enums.ReviewStatuses`

    :param text: Текст отзыва.
    :type text: `str` or `None`

    :param rating: Рейтинг отзыва.
    :type rating: `int`

    :param created_at: Дата создания отзыва.
    :type created_at: `str`

    :param updated_at: Дата изменения отзыва.
    :type updated_at: `str`

    :param deal: Сделка, связанная с отзывом.
    :type deal: `Deal`

    :param creator: Профиль создателя отзыва.
    :type creator: `UserProfile`

    :param moderator: Модератор, обработавший отзыв.
    :type moderator: `Moderator` or `None`

    :param user: Профиль продавца, к которому относится отзыв.
    :type user: `UserProfile`
    """
    def __init__(self, id: str, status: ReviewStatuses, text: str | None, rating: int,
                 created_at: str, updated_at: str, deal: ItemDeal, creator: UserProfile, 
                 moderator: Moderator | None, user: UserProfile):
        self.id: str = id
        """ ID отзыва. """
        self.status: ReviewStatuses = status
        """ Статус отзыва. """
        self.text: str | None = text
        """ Текст отзыва. """
        self.rating: int = rating
        """ Рейтинг отзыва. """
        self.created_at: str = created_at
        """ Дата создания отзыва. """
        self.updated_at: str = updated_at
        """ Дата изменения отзыва. """
        self.deal: ItemDeal = deal
        """ Сделка, связанная с отзывом. """
        self.creator: UserProfile = creator
        """ Профиль создателя отзыва. """
        self.moderator: Moderator | None = moderator
        """ Модератор, обработавший отзыв. """
        self.user: UserProfile = user
        """ Профиль продавца, к которому относится отзыв. """


class ReviewPageInfo:
    """
    Подкласс, описывающий информацию о странице отзывов.

    :param start_cursor: Курсор начала страницы.
    :type start_cursor: `str`

    :param end_cursor: Курсок конца страницы.
    :type end_cursor: `str`

    :param has_previous_page: Имеет ли предыдущую страницу.
    :type has_previous_page: `bool`

    :param has_next_page: Имеет ли следующую страницу.
    :type has_next_page: `bool`
    """
    def __init__(self, start_cursor: str, end_cursor: str,
                 has_previous_page: bool, has_next_page: bool):
        self.start_cursor: str = start_cursor
        """ Курсор начала страницы. """
        self.end_cursor: str = end_cursor
        """ Курсор конца страницы. """
        self.has_previous_page: bool = has_previous_page
        """ Имеет ли предыдущую страницу. """
        self.has_next_page: bool = has_next_page
        """ Имеет ли следующую страницу. """


class ReviewList:
    """
    Класс, описывающий страницу отзывов.

    :param reviews: Отзывы страницы.
    :type reviews: `list[playerokapi.types.Review]`

    :param page_info: Информация о странице.
    :type page_info: `playerokapi.types.ReviewPageInfo`

    :param total_count: Всего отзывов.
    :type total_count: `int`
    """
    def __init__(self, reviews: list[Review], page_info: ReviewPageInfo,
                 total_count: int):
        self.reviews: list[Review] = reviews
        """ Отзывы страницы. """
        self.page_info: ReviewPageInfo = page_info
        """ Информация о странице. """
        self.total_count: int = total_count
        """ Всего отзывов. """