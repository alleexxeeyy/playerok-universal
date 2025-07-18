from enum import Enum

class EventTypes(Enum):
    """
    Типы событий.
    """
    CHAT_INITIALIZED = 0
    """ Чат инициализирован. """
    NEW_MESSAGE = 1
    """ Новое сообщение в чате. """
    NEW_DEAL = 2
    """ Создана новая сделка (когда покупатель оплатил товар). """
    DEAL_CONFIRMED = 3
    """ Сделка подтверждена (покупатель подтвердил получение предмета). """
    DEAL_CONFIRMED_AUTOMATICALLY = 4
    """ Сделка подтверждена автоматически (если покупатель долго не выходит на связь). """
    DEAL_ROLLED_BACK = 5
    """ Продавец оформил возврат сделки. """
    DEAL_HAS_PROBLEM = 6
    """ Пользователь сообщил о проблеме в сделке. """
    DEAL_PROBLEM_RESOLVED = 7
    """ Проблема в сделке решена. """
    DEAL_STATUS_CHANGED = 8
    """ Статус сделки изменён. """
    ITEM_PAID = 9
    """ Пользователь оплатил предмет. """
    ITEM_SENT = 10
    """ Предмет отправлен (продавец подтвердил выполнение сделки). """

class ItemLogEvents(Enum):
    """
    События логов предмета.
    """
    PAID = 0
    """ Продавец подтвердил выполнение сделки. """
    SENT = 1
    """ Товар сделки отправлен. """
    DEAL_CONFIRMED = 2
    """ Сделка подтверждена. """
    DEAL_ROLLED_BACK = 3
    """ Сделка возвращена. """
    PROBLEM_REPORTED = 4
    """ Отправлена жалоба (создана проблема). """
    PROBLEM_RESOLVED = 5
    """ Проблема решена. """

class TransactionOperations(Enum):
    """
    Операции транзакций.
    """
    BUY = 0
    """ Оплата. """
    SELL = 1
    """ Продажа. """

class TransactionDirections(Enum):
    """
    Операции транзакций.
    """
    IN = 0
    """ Входящая. """
    OUT = 1
    """ Исходящая. """

class TransactionStatuses(Enum):
    """
    Статусы транзакций.
    """
    #TODO: Доделать все статусы транзакций
    PENDING = 0
    """ В ожидании (транзакция оплачена, но деньги за неё ещё не поступили на баланс). """
    CONFIRMED = 1
    """ Транзакция подтверждена. """

class TransactionProviderIds(Enum):
    """
    Айди провайдеров транзакции.
    """
    #TODO: Доделать все id провайдеров транзакций
    LOCAL = 0
    """ Локальная транзакция. """

class ItemDealStatuses(Enum):
    """
    Состояния сделки.
    """
    PAID = 0
    """ Сделка оплачена. """
    PENDING = 1
    """ Сделка в ожидании отправки товара. """
    SENT = 2
    """ Продавец подтвердил выполнение сделки. """
    CONFIRMED = 3
    """ Сделка подтверждена. """
    ROLLED_BACK = 4
    """ Сделка возвращена. """

class ItemDealDirections(Enum):
    """
    Направления сделки.
    """
    IN = 0
    """ Покупка. """
    OUT = 1
    """ Продажа. """

class GameTypes(Enum):
    """
    Типы игр.
    """
    GAME = 0
    """ Игра. """
    APPLICATION = 1
    """ Приложение. """

class UserTypes(Enum):
    """
    Типы пользователей.
    """
    USER = 0
    """ Обычный пользователь. """
    MODERATOR = 1
    """ Модератор. """
    BOT = 2
    """ Бот. """

class ChatTypes(Enum):
    """
    Типы чатов.
    """
    PM = 0
    """ Приватный чат (диалог с пользователем). """
    NOTIFICATIONS = 1
    """ Чат уведомлений. """
    SUPPORT = 2
    """ Чат поддержки. """

class ChatStatuses(Enum):
    """
    Статусы чатов.
    """
    NEW = 0
    """ Новый чат (в нём нет ни единого прочитанного сообщения). """
    FINISHED = 1
    """ Чат доступен, в нём сейчас можно переписываться. """

class ChatMessageButtonTypes(Enum):
    """
    Типы кнопок сообщений.
    """
    # TODO: Доделать все типы кнопок сообщения
    REDIRECT = 0
    """ Перенаправляет на ссылку. """
    LOTTERY = 1
    """ Перенаправляет на розыгрыш/акцию. """

class ItemStatuses(Enum):
    """
    Статусы предметов.
    """
    PENDING_APPROVAL = 0
    """ Ожидает принятия (на проверке модерацией). """
    APPROVED = 1
    """ Активный (принятый модерацией). """
    DECLINED = 2
    """ Отклонённый. """
    BLOCKED = 3
    """ Заблокированный. """
    EXPIRED = 4
    """ Истёкший. """
    SOLD = 5
    """ Проданный. """
    DRAFT = 6
    """ Черновик (если предмет не выставлен на продажу). """

class ReviewStatuses(Enum):
    """
    Статусы отзывов.
    """
    APPROVED = 0
    """ Активный. """
    DELETED = 1
    """ Удалённый. """

class SortDirections(Enum):
    """
    Типы сортировки.
    """
    DESC = 0
    """ По убыванию. """
    ASC = 1
    """ По возрастанию. """

class PriorityTypes(Enum):
    """
    Типы приоритетов.
    """
    DEFAULT = 0
    """ Стандартный приоритет. """
    PREMIUM = 1
    """ Премиум приоритет. """

class GameCategoryAgreementIconTypes(Enum):
    """
    Типы иконок соглашения покупателя в определённой категории.
    """
    # TODO: Доделать все типы иконок соглашений
    RESTRICTION = 0
    """ Ограничение. """
    CONFIRMATION = 0
    """ Подтверждение. """

class GameCategoryOptionTypes(Enum):
    """
    Типы опции категории.
    """
    # TODO: Доделать все типы опций категории
    SELECTOR = 0
    """ Выбор типа. """
    SWITCH = 1
    """ Переключатель. """

class GameCategoryDataFieldTypes(Enum):
    """
    Типы полей с данными категории игры.
    """
    ITEM_DATA = 0
    """ Данные предмета. """
    OBTAINING_DATA = 1
    """ Получаемые данные (после покупки предмета). """

class GameCategoryDataFieldInputTypes(Enum):
    """
    Типы вводимых полей с данными категории игры.
    """
    # TODO: Доделать все типы вводимых дата-полей
    INPUT = 0
    """ Вводимое значение (вводится покупателем при оформлении предмета). """

class GameCategoryAutoConfirmPeriods(Enum):
    """
    Периоды автоматического подтверждения сделки в категории игры.
    """
    # TODO: Доделать все периоды авто-подтверждения
    SEVEN_DEYS = 0
    """ Семь дней. """

class GameCategoryInstructionTypes(Enum):
    """
    Типы инструкций категории.
    """
    FOR_SELLER = 0
    """ Для продавца. """
    FOR_BUYER = 1
    """ Для покупателя. """