import asyncio
from aiogram import types, Router, F
from aiogram.filters import BaseFilter, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.dispatcher.event.bases import SkipHandler

from settings import Settings as sett
from core import startup
from core.access import is_signed
from utils import (
    check_cookies,
    is_user_agent_valid,
    is_proxy_valid,
    is_proxy_alive,
    normalize_proxy,
    diagnose_playerok
)

from .. import templates as templ
from .. import states
from ..helpful import throw_float_message, extract_lines


router = Router()

# в режиме настройки эти кнопки работают как обычно: закрыть, отчёт об ошибке, запрос доступа
PASS_CALLBACKS = ("destroy", "null_answer", "booterr:", "accreq:")


class SetupMode(BaseFilter):
    async def __call__(self, event) -> bool:
        user = getattr(event, "from_user", None)
        return startup.is_setup_mode() and user is not None and is_signed(user.id)


router.message.filter(SetupMode())
router.callback_query.filter(SetupMode())


async def render_setup(message: types.Message, state: FSMContext, callback: types.CallbackQuery = None, placeholder: str = None, send: bool = False):
    await state.set_state(None)
    await throw_float_message(
        state=state,
        message=message,
        text=templ.setup_text(startup.get_problem(), placeholder),
        reply_markup=templ.setup_kb(),
        callback=callback,
        send=send
    )


async def ask_cookies(message: types.Message, state: FSMContext, callback: types.CallbackQuery = None, error: str = None, intro: str = None):
    data = await state.get_data()
    await state.set_state(states.SetupStates.waiting_for_cookies)
    text = templ.setup_cookies_text(1 if data.get("setup_wizard") else None, error)
    await throw_float_message(
        state=state,
        message=message,
        text=f"{intro}\n\n{text}" if intro else text,
        reply_markup=templ.setup_input_kb(skip=False),
        callback=callback,
        send=bool(intro)
    )


async def ask_user_agent(message: types.Message, state: FSMContext, callback: types.CallbackQuery = None, error: str = None):
    data = await state.get_data()
    await state.set_state(states.SetupStates.waiting_for_user_agent)
    await throw_float_message(
        state=state,
        message=message,
        text=templ.setup_user_agent_text(2 if data.get("setup_wizard") else None, error),
        reply_markup=templ.setup_input_kb(skip=bool(data.get("setup_wizard"))),
        callback=callback
    )


async def ask_proxy(message: types.Message, state: FSMContext, callback: types.CallbackQuery = None, error: str = None):
    data = await state.get_data()
    await state.set_state(states.SetupStates.waiting_for_proxy)
    await throw_float_message(
        state=state,
        message=message,
        text=templ.setup_proxy_text(3 if data.get("setup_wizard") else None, error),
        reply_markup=templ.setup_input_kb(skip=bool(data.get("setup_wizard"))),
        callback=callback
    )


async def open_home(message: types.Message, state: FSMContext, welcome: bool = False):
    await state.set_state(None)

    if not startup.is_setup_mode():
        text = templ.menu_text()
        if welcome:
            text = templ.owner_welcome_text() + "\n\n" + text
        return await throw_float_message(state=state, message=message, text=text, reply_markup=templ.menu_kb(), send=True)

    problem = startup.get_problem() or {}
    if problem.get("code") == "no_cookies": # свежая установка — ведём по шагам
        await state.update_data(setup_wizard=True)
        return await ask_cookies(message, state, intro=templ.owner_welcome_text() if welcome else "👋 Осталось подключить аккаунт Playerok")
    await state.update_data(setup_wizard=False)
    await render_setup(message, state, send=True)


async def run_check(message: types.Message, state: FSMContext, callback: types.CallbackQuery = None):
    await state.set_state(None)
    await state.update_data(setup_wizard=False)

    if startup.is_launching():
        return await throw_float_message(
            state=state,
            message=message,
            text=templ.setup_float_text("⏳ Бот уже запускается, подождите немного..."),
            callback=callback
        )

    await throw_float_message(
        state=state,
        message=message,
        text=templ.setup_float_text("⏳ Проверяю подключение к Playerok — это может занять пару минут..."),
        callback=callback
    )
    problem = await asyncio.to_thread(diagnose_playerok)
    if problem:
        startup.set_problem(problem)
        return await render_setup(message, state)

    await throw_float_message(
        state=state,
        message=message,
        text=templ.setup_float_text("✅ Playerok отвечает — запускаю бота, это займёт до минуты...")
    )
    data = await state.get_data()
    startup.launch(message.chat.id, data.get("accent_message_id"))


async def _next_step(message: types.Message, state: FSMContext, after: str, callback: types.CallbackQuery = None):
    data = await state.get_data()
    if not data.get("setup_wizard"):
        return await run_check(message, state, callback)
    if after == "cookies":
        return await ask_user_agent(message, state, callback)
    if after == "user_agent":
        return await ask_proxy(message, state, callback)
    return await run_check(message, state, callback)


async def _is_command(message: types.Message, state: FSMContext) -> bool:
    # в шагах мастера команда — не ввод: /restart работает как обычно, остальные возвращают на экран настройки
    if not (message.text or "").startswith("/"):
        return False
    if message.text.startswith("/restart"):
        raise SkipHandler()
    await render_setup(message, state)
    return True


def _set_api(key: str, value: str):
    config = sett.get("config")
    config["playerok"]["api"][key] = value
    sett.set("config", config)


@router.callback_query(F.data == "setup_open")
async def callback_setup_open(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(setup_wizard=False)
    await render_setup(callback.message, state, callback)


@router.callback_query(F.data == "setup_cookies")
async def callback_setup_cookies(callback: types.CallbackQuery, state: FSMContext):
    await ask_cookies(callback.message, state, callback)


@router.callback_query(F.data == "setup_user_agent")
async def callback_setup_user_agent(callback: types.CallbackQuery, state: FSMContext):
    await ask_user_agent(callback.message, state, callback)


@router.callback_query(F.data == "setup_proxy")
async def callback_setup_proxy(callback: types.CallbackQuery, state: FSMContext):
    await ask_proxy(callback.message, state, callback)


@router.callback_query(F.data == "setup_remove_proxy")
async def callback_setup_remove_proxy(callback: types.CallbackQuery, state: FSMContext):
    _set_api("proxy", "")
    await run_check(callback.message, state, callback)


@router.callback_query(F.data == "setup_skip")
async def callback_setup_skip(callback: types.CallbackQuery, state: FSMContext):
    current = await state.get_state()
    after = "user_agent" if current == states.SetupStates.waiting_for_user_agent.state else "proxy"
    await _next_step(callback.message, state, after, callback)


@router.callback_query(F.data == "setup_check")
async def callback_setup_check(callback: types.CallbackQuery, state: FSMContext):
    await run_check(callback.message, state, callback)


@router.message(states.SetupStates.waiting_for_cookies)
async def handler_setup_cookies(message: types.Message, state: FSMContext):
    if await _is_command(message, state):
        return
    try:
        str_cookies = "".join(await extract_lines(message)).strip()
    except Exception as e:
        return await ask_cookies(message, state, error=e)
    finally:
        try: # куки — это доступ к аккаунту, в истории чата им не место
            await message.delete()
        except Exception:
            pass

    if not check_cookies(str_cookies):
        return await ask_cookies(
            message, state,
            error="❌ Это не похоже на Cookie-данные Playerok — нужен формат Header String, в нём обязательно есть token=..."
        )

    _set_api("cookies", str_cookies)
    await _next_step(message, state, "cookies")


@router.message(states.SetupStates.waiting_for_user_agent, F.text)
async def handler_setup_user_agent(message: types.Message, state: FSMContext):
    if await _is_command(message, state):
        return
    user_agent = message.text.strip()
    if not is_user_agent_valid(user_agent):
        return await ask_user_agent(message, state, error="❌ Неверный формат User Agent — в нём не должно быть русских символов")

    _set_api("user_agent", user_agent)
    await _next_step(message, state, "user_agent")


@router.message(states.SetupStates.waiting_for_proxy, F.text)
async def handler_setup_proxy(message: types.Message, state: FSMContext):
    if await _is_command(message, state):
        return
    proxy = normalize_proxy(message.text)
    if not is_proxy_valid(proxy):
        return await ask_proxy(message, state, error="❌ Неверный формат прокси")

    await throw_float_message(state=state, message=message, text=templ.setup_float_text("⏳ Проверяю прокси..."))
    if not await asyncio.to_thread(is_proxy_alive, proxy):
        return await ask_proxy(message, state, error="❌ Прокси не отвечает — нет подключения к playerok.com через него")

    _set_api("proxy", proxy)
    await _next_step(message, state, "proxy")


@router.message(StateFilter(None))
async def handler_setup_any(message: types.Message, state: FSMContext):
    if message.text and message.text.startswith("/restart"):
        raise SkipHandler()
    await render_setup(message, state)


@router.callback_query()
async def callback_setup_any(callback: types.CallbackQuery, state: FSMContext):
    if (callback.data or "").startswith(PASS_CALLBACKS):
        raise SkipHandler()
    await render_setup(callback.message, state, callback)
