import re
from html import escape
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from core.blacklist import is_blacklisted, add_to_blacklist

from .. import templates as templ
from .. import states
from .. import callback_datas as calls
from ..helpful import throw_float_message


router = Router()


@router.message(states.BlacklistStates.waiting_for_new_blacklist_username, F.text)
async def handler_waiting_for_new_blacklist_username(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        data = await state.get_data()
        last_page = data.get("last_page", 0)

        username = message.text.strip().lstrip("@")
        if not re.fullmatch(r"[\w.\-]{2,32}", username):
            raise Exception("❌ Некорректный никнейм")
        if is_blacklisted(username):
            raise Exception(f"❌ Покупатель <code>{escape(username)}</code> уже в чёрном списке")

        await state.update_data(new_blacklist_user=username)
        await state.set_state(states.BlacklistStates.waiting_for_new_blacklist_reason)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_blacklist_user_float_text(f"📝 Введите <b>причину</b> добавления <code>{escape(username)}</code> в чёрный список:"),
            reply_markup=templ.new_blacklist_user_reason_kb(calls.BlacklistPagination(page=last_page).pack())
        )
    except Exception as e:
        data = await state.get_data()
        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_blacklist_user_float_text(e),
            reply_markup=templ.back_kb(calls.BlacklistPagination(page=data.get("last_page", 0)).pack())
        )


@router.message(states.BlacklistStates.waiting_for_new_blacklist_reason, F.text)
async def handler_waiting_for_new_blacklist_reason(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        data = await state.get_data()
        last_page = data.get("last_page", 0)
        username = data.get("new_blacklist_user")
        if not username:
            raise Exception("❌ Никнейм покупателя не был найден, повторите процесс с самого начала")

        reason = message.text.strip()
        if len(reason) > 200:
            raise Exception("❌ Слишком длинная причина")

        if not add_to_blacklist(username, reason):
            raise Exception(f"❌ Покупатель <code>{escape(username)}</code> уже в чёрном списке")
        await state.update_data(new_blacklist_user=None)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_blacklist_user_float_text(f"✅ Покупатель <code>{escape(username)}</code> добавлен в чёрный список"),
            reply_markup=templ.back_kb(calls.BlacklistPagination(page=last_page).pack())
        )
    except Exception as e:
        data = await state.get_data()
        await throw_float_message(
            state=state,
            message=message,
            text=templ.new_blacklist_user_float_text(e),
            reply_markup=templ.back_kb(calls.BlacklistPagination(page=data.get("last_page", 0)).pack())
        )


@router.message(states.BlacklistStates.waiting_for_chat_blacklist_reason, F.text)
async def handler_waiting_for_chat_blacklist_reason(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        data = await state.get_data()
        chat_name = data.get("blacklist_chat_user")
        if not chat_name:
            raise Exception("❌ Чат не был найден, повторите процесс с самого начала")

        reason = message.text.strip()
        if len(reason) > 200:
            raise Exception("❌ Слишком длинная причина")

        await state.update_data(chat_blacklist_reason=reason)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.do_action_text(
                f"✔️ Подтвердите <b>добавление</b> <code>{escape(chat_name)}</code> в чёрный список:"
                f"\n\n<b>📝 Причина:</b> {escape(reason)}"
            ),
            reply_markup=templ.confirm_kb(confirm_cb="add_chat_to_blacklist", cancel_cb="destroy")
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.do_action_text(e),
            reply_markup=templ.destroy_kb()
        )
