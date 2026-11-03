from html import escape
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    KeyboardButtonRequestUsers
)

from core.access import CONFIRM_WORD
from .. import callback_datas as calls


PICK_USER_REQUEST_ID = 1
PICK_USER_CANCEL = "❌ Отмена"


def user_title(user_id: int, username: str | None = None, name: str | None = None) -> str:
    if username:
        return f"@{escape(username)}"
    if name:
        return f"<b>{escape(name)}</b> (<code>{user_id}</code>)"
    return f"<code>{user_id}</code>"


def not_linked_text():
    return (
        "<b>🔒 Бот не привязан к владельцу</b>"
        "\n\n<blockquote><b>(?)</b> Если это ваш бот — откройте ссылку, которую он показал в консоли при запуске. "
        "Она одноразовая и делает вас владельцем.</blockquote>"
    )


def access_denied_text(user_id: int, requested: bool):
    if requested:
        status = "✉️ Владельцу отправлен <b>запрос на доступ</b> — если он его одобрит, вам придёт сообщение"
    else:
        status = "⏳ Запрос владельцу <b>уже отправлен</b> — повторно запросить доступ можно через сутки"
    return (
        "<b>🔒 Нет доступа к боту</b>"
        f"\n\n{status}"
        f"\n\n<b>🆔 Ваш ID:</b> <code>{user_id}</code>"
    )


def access_request_text(user_id: int, username: str | None, name: str | None, placeholder: str = None):
    txt = (
        "<b>👤 Запрос доступа к боту</b>"
        f"\n\n<b>📛 Имя:</b> {escape(name) if name else '—'}"
        f"\n<b>🔗 Юзернейм:</b> {'@' + escape(username) if username else '—'}"
        f"\n<b>🆔 ID:</b> <code>{user_id}</code>"
        "\n\n<blockquote><b>(?)</b> Этот человек сможет управлять ботом и вашим аккаунтом Playerok. "
        "Пускайте только тех, кого знаете.</blockquote>"
    )
    if placeholder:
        txt += f"\n\n{placeholder}"
    return txt


def access_request_kb(user_id: int):
    rows = [[
        InlineKeyboardButton(text="✅ Пустить", callback_data=calls.AccessRequest(id=user_id, do="allow").pack()),
        InlineKeyboardButton(text="❌ Отклонить", callback_data=calls.AccessRequest(id=user_id, do="deny").pack())
    ]]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def access_confirm_text(user_id: int, username: str | None, name: str | None):
    return (
        "<b>👤 Запрос доступа к боту</b>"
        f"\n\n✍️ Чтобы пустить {user_title(user_id, username, name)}, напишите слово <b>{CONFIRM_WORD}</b>"
        "\n\n<blockquote><b>(?)</b> Так бот убедится, что вы не нажали «Пустить» случайно.</blockquote>"
    )


def access_confirm_kb(user_id: int):
    rows = [[InlineKeyboardButton(text="❌ Отмена", callback_data=calls.AccessRequest(id=user_id, do="cancel").pack())]]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def access_granted_text():
    return "<b>✅ Вам открыли доступ к боту</b>\n\nНажмите /start, чтобы открыть меню"


def owner_welcome_text():
    return "<b>👋 Готово, вы — владелец бота!</b>\n\nДругих людей можно добавить в разделе «🔑 Авторизации»"


def pick_user_text():
    return (
        "<b>🔑 Авторизации</b>"
        "\n\n👤 Нажмите кнопку <b>«Выбрать пользователя»</b> внизу экрана и выберите человека из своих чатов"
        "\n\n<blockquote><b>(?)</b> Бот сразу получит его ID и откроет ему доступ.</blockquote>"
    )


def pick_user_kb():
    rows = [
        [KeyboardButton(
            text="👤 Выбрать пользователя",
            request_users=KeyboardButtonRequestUsers(
                request_id=PICK_USER_REQUEST_ID,
                user_is_bot=False,
                max_quantity=1,
                request_name=True,
                request_username=True
            )
        )],
        [KeyboardButton(text=PICK_USER_CANCEL)]
    ]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, one_time_keyboard=True)
