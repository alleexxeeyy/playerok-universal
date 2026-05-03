from dataclasses import dataclass
import pytz
from datetime import datetime

from playerokapi.enums import (
    ChatTypes,
    ChatStatuses,
    ItemDealStatuses,
    UserTypes
)
from playerokapi.types import (
    AccountProfile, 
    UserProfile, 
    Item, 
    ItemDeal, 
    ChatMessage,
    Chat
)


@dataclass
class MsgAccount:
    id: str
    username: str
    email: str
    role: str
    avatar_url: str
    rating: int
    reviews_count: int
    created_at: str


def msg_account(data: AccountProfile) -> MsgAccount:
    if not data:
        return None
    
    role = "-"
    if data.role == UserTypes.USER:
        role = "Пользователь"
    elif data.role == UserTypes.MODERATOR:
        role = "Модератор"
    elif data.role == UserTypes.BOT:
        role = "Бот"
    elif data.role == UserTypes.CHECKER:
        role = "Проверяющий"

    cr_at = "-"
    iso_dt = data.created_at

    if iso_dt:
        if iso_dt.endswith("Z"):
            iso_dt = iso_dt[:-1] + "+00:00"

        dt = datetime.fromisoformat(iso_dt).astimezone(pytz.timezone("Europe/Moscow"))
        cr_at = dt.strftime("%d.%m %H:%M:%S")

    return MsgAccount(
        id=data.id or "-",
        username=data.username or "-",
        email=data.email or "-",
        role=role,
        avatar_url=data.avatar_url or "-",
        rating=data.rating or "-",
        reviews_count=data.reviews_count or "-",
        created_at=cr_at
    )


@dataclass
class MsgUser:
    id: str
    username: str
    role: str
    avatar_url: str
    is_online: str
    is_blocked: str
    rating: int
    reviews_count: int
    created_at: str


def msg_user(data: UserProfile) -> MsgUser:
    if not data:
        return None
    
    role = "-"
    if data.role == UserTypes.USER:
        role = "Пользователь"
    elif data.role == UserTypes.MODERATOR:
        role = "Модератор"
    elif data.role == UserTypes.BOT:
        role = "Бот"
    elif data.role == UserTypes.CHECKER:
        role = "Проверяющий"

    cr_at = "-"
    iso_dt = data.created_at

    if iso_dt:
        if iso_dt.endswith("Z"):
            iso_dt = iso_dt[:-1] + "+00:00"

        dt = datetime.fromisoformat(iso_dt).astimezone(pytz.timezone("Europe/Moscow"))
        cr_at = dt.strftime("%d.%m %H:%M:%S")

    return MsgUser(
        id=data.id or "-",
        username=data.username or "-",
        role=role,
        avatar_url=data.avatar_url or "-",
        is_online="Онлайн" if data.is_online else "Оффлайн",
        is_blocked="Заблокирован" if data.is_blocked else "Свободен",
        rating=data.rating or "-",
        reviews_count=data.reviews_count or "-",
        created_at=cr_at
    )


def msg_user_from_chat(data: Chat) -> MsgUser:
    if data is None:
        return
    
    from plbot.playerokbot import get_playerok_bot as plbot
    user = next((
        u for u in data.users if u.id != plbot().account.id
    ), None)
    
    return msg_user(user)


@dataclass
class MsgItem:
    id: str
    slug: str
    name: str
    description: str
    price: int
    raw_price: str
    game: str
    category: str


def msg_item(data: Item) -> MsgItem:
    if not data:
        return None

    return MsgItem(
        id=data.id or "-",
        slug=data.slug or "-",
        name=data.name or "-",
        description=data.description or "-",
        price=data.price or "-",
        raw_price=data.raw_price or "-",
        game=data.game.name if data.game and data.game.name else "-",
        category=data.category.name if data.category and data.category.name else "-"
    )


@dataclass
class MsgDeal:
    id: str
    status: str
    user: MsgUser
    item: MsgItem
    created_at: str
    completed_at: str


def msg_deal(data: ItemDeal) -> MsgDeal:
    if not data:
        return None
    
    status = "-"
    if data.status == ItemDealStatuses.PAID:
        status = "Оплачено"
    elif data.status == ItemDealStatuses.PENDING:
        status = "В ожидании"
    elif data.status == ItemDealStatuses.SENT:
        status = "Товар отправлен"
    elif data.status == ItemDealStatuses.CONFIRMED:
        status = "Выполнено"
    elif data.status == ItemDealStatuses.CONFIRMED_AUTOMATICALLY:
        status = "Подтверждено автоматически"
    elif data.status == ItemDealStatuses.ROLLED_BACK:
        status = "Возврат"

    cr_at = "-"
    iso_dt = data.created_at
    
    if iso_dt:
        if iso_dt.endswith("Z"):
            iso_dt = iso_dt[:-1] + "+00:00"

        dt = datetime.fromisoformat(iso_dt).astimezone(pytz.timezone("Europe/Moscow"))
        cr_at = dt.strftime("%d.%m %H:%M:%S")

    co_at = "-"
    iso_dt = data.completed_at

    if iso_dt:
        if iso_dt.endswith("Z"):
            iso_dt = iso_dt[:-1] + "+00:00"

        dt = datetime.fromisoformat(iso_dt).astimezone(pytz.timezone("Europe/Moscow"))
        co_at = dt.strftime("%d.%m %H:%M:%S")

    return MsgDeal(
        id=data.id or "-",
        status=status,
        user=msg_user(data.user) if data.user else "-",
        item=msg_item(data.item) if data.item else "-",
        created_at=cr_at,
        completed_at=co_at
    )


@dataclass
class MsgChat:
    id: str
    type: str
    status: str
    user: MsgUser
    last_message: str


def msg_chat(data: Chat) -> MsgChat:
    if not data:
        return None
    
    type = "-"
    if data.type == ChatTypes.PM:
        type = "Приватный"
    elif data.type == ChatTypes.NOTIFICATIONS:
        type = "Уведомления"
    elif data.type == ChatTypes.SUPPORT:
        type = "Поддержка"

    status = "-"
    if data.status == ChatStatuses.NEW:
        status = "Новый"
    elif data.status == ChatStatuses.FINISHED:
        status = "Активный"

    from plbot.playerokbot import get_playerok_bot as plbot
    user = next((u for u in data.users if u.id != plbot().account.id), None)

    return MsgChat(
        id=data.id or "-",
        type=type,
        status=status,
        user=msg_user(user) if user else "-",
        last_message=data.last_message.text if data.last_message and data.last_message.text else "-"
    )