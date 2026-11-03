import asyncio
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from settings import Settings as sett
from core import access

from .. import templates as templ
from .. import states
from .. import callback_datas as calls
from ..helpful import throw_float_message, do_auth, notify_access_granted
from .setup import open_home


router = Router()


async def _render_signed_users(message: types.Message, state: FSMContext, page: int, placeholder: str = None, send: bool = False):
    await throw_float_message(
        state=state,
        message=message,
        text=templ.signed_users_float_text(placeholder) if placeholder else templ.signed_users_text(),
        reply_markup=templ.back_kb(calls.SignedUsersPagination(page=page).pack()) if placeholder else await templ.signed_users_kb(page),
        send=send
    )


@router.message(states.SystemStates.waiting_for_password, F.text)
async def handler_waiting_for_password(message: types.Message, state: FSMContext):
    await state.set_state(None)

    if not access.is_legacy_password_login(): # вход по паролю отключён — владелец уже есть
        return await do_auth(message, state)

    if message.text != sett.get("config")["telegram"]["bot"]["password"]:
        await asyncio.sleep(2) # тормозим перебор пароля
        await state.set_state(states.SystemStates.waiting_for_password)
        return await throw_float_message(
            state=state,
            message=message,
            text=templ.sign_text("❌ Неверный ключ-пароль, попробуйте ещё раз"),
            reply_markup=templ.destroy_kb()
        )

    access.add_signed_user(message.from_user.id)
    await open_home(message, state, welcome=True)


@router.message(states.SystemStates.waiting_for_access_confirm, F.text)
async def handler_waiting_for_access_confirm(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.set_state(None)

    user_id = data.get("access_user_id")
    request = data.get("access_request") or {}
    if not user_id or not access.is_signed(message.from_user.id):
        return

    username, name = request.get("username"), request.get("name")
    if message.text.strip().lower() != access.CONFIRM_WORD:
        return await throw_float_message(
            state=state,
            message=message,
            text=templ.access_request_text(
                user_id, username, name,
                "❌ Слово не совпало — доступ не выдан. Если всё-таки хотите пустить, нажмите «Пустить» ещё раз"
            ),
            reply_markup=templ.access_request_kb(user_id)
        )

    access.add_signed_user(user_id)
    await throw_float_message(
        state=state,
        message=message,
        text=templ.access_request_text(user_id, username, name, "✅ Доступ выдан"),
        reply_markup=templ.destroy_kb()
    )
    await notify_access_granted(message.bot, user_id)


@router.message(states.SystemStates.waiting_for_signed_user_id, F.text)
async def handler_waiting_for_signed_user_id(message: types.Message, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    await state.set_state(None)
    if not access.is_signed(message.from_user.id):
        return

    text = message.text.strip()
    if not text.isdigit():
        placeholder = "❌ ID — это число, например <code>123456789</code>"
    elif not access.add_signed_user(int(text)):
        placeholder = f"❌ У пользователя <code>{text}</code> уже есть доступ"
    else:
        placeholder = f"✅ Доступ выдан пользователю <code>{text}</code>"
        await notify_access_granted(message.bot, int(text))

    await _render_signed_users(message, state, last_page, placeholder)


@router.message(states.SystemStates.waiting_for_shared_user, F.users_shared)
async def handler_waiting_for_shared_user(message: types.Message, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    await state.set_state(None)
    if not access.is_signed(message.from_user.id):
        return

    added = []
    for user in message.users_shared.users:
        if access.add_signed_user(user.user_id):
            added.append(templ.user_title(user.user_id, user.username, user.first_name))
            await notify_access_granted(message.bot, user.user_id)

    await message.answer(
        f"✅ Доступ выдан: {', '.join(added)}" if added else "❌ У этого пользователя уже есть доступ",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML"
    )
    await _render_signed_users(message, state, last_page, send=True)


@router.message(states.SystemStates.waiting_for_shared_user)
async def handler_waiting_for_shared_user_cancel(message: types.Message, state: FSMContext):
    data = await state.get_data()
    last_page = data.get("last_page", 0)
    await state.set_state(None)

    await message.answer("✖️ Выбор пользователя отменён", reply_markup=ReplyKeyboardRemove())
    await _render_signed_users(message, state, last_page, send=True)
