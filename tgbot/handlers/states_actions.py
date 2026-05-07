from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from tempfile import NamedTemporaryFile
import os
import asyncio

from .. import templates as templ
from .. import states
from ..helpful import throw_float_message

from ..callback_handlers.page import callback_chat_page
from ..callback_handlers.actions_other import (
    callback_transactions_filter,
    callback_change_transactions_filter,
    callback_change_reviews_filter
)
from .. import callback_datas as calls

from utils import parse_date


router = Router()


async def _send_mess(message: types.Message, state: FSMContext):
    data = await state.get_data()
    chat_id = data.get("chat_id")

    from plbot.playerokbot import get_playerok_bot as plbot
    acc = plbot().account
    chat = plbot().get_chat_by_id(chat_id)

    sent_msg = ""

    text = None
    if message.text:
        if len(message.text) <= 0:
            raise Exception("❌ Слишком короткий текст")

        text = message.text
        sent_msg += message.text

    photo_paths = []
    if message.photo:
        photos_messages = [message]

        if message.media_group_id:
            await asyncio.sleep(1)
            data = await state.get_data()
            photos_messages = data.get("album_messages", []) + [message]
            await state.update_data(album_messages=photos_messages)

        for msg in photos_messages:
            photo = msg.photo[-1]

            with NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                await message.bot.download(photo, destination=tmp.name)
                photo_paths.append(tmp.name)

        if message.caption:
            text = message.caption
            sent_msg += message.caption
            await asyncio.sleep(1)

        sent_msg += f", <b>Изображения ({len(photo_paths)})</b>"

    acc.send_message(
        chat_id=chat.id, 
        text=text,
        photo_file_paths=photo_paths
    )
    
    for path in photo_paths:
        try: os.remove(path)
        except: pass

    return acc, chat, sent_msg


@router.message(states.ActionsStates.waiting_for_fast_answer_message, F.text | F.photo)
async def handler_waiting_for_fast_answer_message(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        await throw_float_message(state, message, "⌛")

        acc, chat, sent_msg = await _send_mess(message, state)
        username = next((u.username for u in chat.users if u.id != acc.id), "???")

        await throw_float_message(
            state=state,
            message=message,
            text=templ.do_action_text(
                f"✅ Сообщение отправлено: <blockquote>{sent_msg}</blockquote>"
            ),
            reply_markup=templ.destroy_kb()
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.do_action_text(e),
            reply_markup=templ.destroy_kb()
        )


@router.message(states.ActionsStates.waiting_for_chat_answer_message, F.text | F.photo)
async def handler_waiting_for_chat_answer_message(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        await throw_float_message(state, message, "⌛")

        data = await state.get_data()
        chat = data.get("chat")
        
        callback = data.get("callback")
        
        _, _, sent_msg = await _send_mess(message, state)

        try:
            await callback_chat_page(
                callback,
                calls.ChatPage(id=chat.id),
                state
            )
        except:
            await throw_float_message(
                state=state,
                message=message,
                text=templ.chat_float_text(
                    chat,
                    f"✅ Сообщение <b>успешно отправлено</b>: <blockquote>{sent_msg}</blockquote>"
                ),
                reply_markup=templ.back_kb(calls.ChatPage(id=chat.id).pack())
            )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.chat_float_text(chat, e),
            reply_markup=templ.back_kb(calls.ChatPage(id=chat.id).pack())
        )


@router.message(states.ActionsStates.waiting_for_fast_problem_description, F.text | F.photo)
async def handler_waiting_for_fast_problem_description(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        data = await state.get_data()

        deal_id = data.get("deal_id")
        mt_str = data.get("mt_str")

        problem_desc = message.text
        if len(problem_desc) < 6:
            raise Exception("❌ Слишком короткое описание проблемы. Минимум 6 символов")
        
        await state.update_data(problem_desc=problem_desc)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.do_action_text(
                f"✔️ Подтвердите <b>создание проблемы</b>:"
                f"\n・ Категория: <blockquote>{mt_str}</blockquote>"
                f"\n・ Описание: <blockquote>{problem_desc}</blockquote>"
            ),
            reply_markup=templ.confirm_kb(
                confirm_cb=calls.FastReportDealProblem(id=deal_id).pack(),
                cancel_cb="destroy"
            )
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.do_action_text(e),
            reply_markup=templ.destroy_kb()
        )


@router.message(states.ActionsStates.waiting_for_deal_problem_description, F.text)
async def handler_waiting_for_problem_description(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        data = await state.get_data()

        deal_id = data.get("deal_id")
        mt_str = data.get("mt_str")

        problem_desc = message.text
        if len(problem_desc) < 6:
            raise Exception("❌ Слишком короткое описание проблемы. Минимум 6 символов")
        
        await state.update_data(problem_desc=problem_desc)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.deal_float_text(
                f"✔️ Подтвердите <b>создание проблемы</b>:"
                f"\n・ Категория: <blockquote>{mt_str}</blockquote>"
                f"\n・ Описание: <blockquote>{problem_desc}</blockquote>"
            ),
            reply_markup=templ.confirm_kb(
                confirm_cb=calls.ReportDealProblem(id=deal_id).pack(),
                cancel_cb=calls.DealPage(id=deal_id).pack()
            )
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.deal_float_text(e),
            reply_markup=templ.back_kb(calls.DealPage(id=deal_id).pack())
        )


@router.message(states.ActionsStates.waiting_for_items_game_name, F.text)
async def handler_waiting_for_items_game_name(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        
        name = message.text
        await state.update_data(game_name=name)

        from plbot.playerokbot import get_playerok_bot as plbot
        games = plbot().account.get_games(name=name).games
        await state.update_data(games=games)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.items_float_text(
                f"🔍 Найдено <b>{len(games)} игр</b>:"
            ),
            reply_markup=templ.items_filter_games_kb(
                games=games, page=0
            )
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.items_float_text(e),
            reply_markup=templ.back_kb("items_filter")
        )


@router.message(states.ActionsStates.waiting_for_trans_min_value, F.text)
async def handler_waiting_for_trans_min_value(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)

        data = await state.get_data()
        callback = data.get("callback")
        
        if not message.text.isdigit() or not (1 <= int(message.text) <= 999999):
            raise Exception("❌ Вы должны ввести числовое значение")
        
        await message.bot.delete_message(message.chat.id, message.message_id)
        await callback_change_transactions_filter(
            callback, calls.ChangeTransactionsFilter(min_val=int(message.text)), state
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.transactions_float_text(e),
            reply_markup=templ.back_kb("transactions_filter")
        )


@router.message(states.ActionsStates.waiting_for_trans_max_value, F.text)
async def handler_waiting_for_trans_max_value(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)

        data = await state.get_data()
        callback = data.get("callback")
        
        if not message.text.isdigit() or not (1 <= int(message.text) <= 999999):
            raise Exception("❌ Вы должны ввести числовое значение")
        
        await message.bot.delete_message(message.chat.id, message.message_id)
        await callback_change_transactions_filter(
            callback, calls.ChangeTransactionsFilter(max_val=int(message.text)), state
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.transactions_float_text(e),
            reply_markup=templ.back_kb("transactions_filter")
        )


@router.message(states.ActionsStates.waiting_for_trans_from_date, F.text)
async def handler_waiting_for_trans_from_date(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)

        data = await state.get_data()
        callback = data.get("callback")
        
        if not parse_date(message.text):
            raise Exception("❌ Неверный формат даты. Пример: 01.05.2026")
        
        await message.bot.delete_message(message.chat.id, message.message_id)
        try:
            await callback_change_transactions_filter(
                callback, calls.ChangeTransactionsFilter(from_dt=message.text), state
            )
        except:
            await callback_transactions_filter(callback, state)
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.transactions_float_text(e),
            reply_markup=templ.back_kb("transactions_filter")
        )


@router.message(states.ActionsStates.waiting_for_trans_to_date, F.text)
async def handler_waiting_for_trans_to_date(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)

        data = await state.get_data()
        callback = data.get("callback")
        
        if not parse_date(message.text):
            raise Exception("❌ Неверный формат даты. Пример: 01.05.2026")
        
        await message.bot.delete_message(message.chat.id, message.message_id)
        try:
            await callback_change_transactions_filter(
                callback, calls.ChangeTransactionsFilter(to_dt=message.text), state
            )
        except:
            await callback_transactions_filter(callback, state)
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.transactions_float_text(e),
            reply_markup=templ.back_kb("transactions_filter")
        )


@router.message(states.ActionsStates.waiting_for_reviews_game_name, F.text)
async def handler_waiting_for_reviews_game_name(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)
        
        name = message.text
        await state.update_data(game_name=name)

        from plbot.playerokbot import get_playerok_bot as plbot
        games = plbot().account.get_games(name=name).games
        await state.update_data(games=games)
        
        await throw_float_message(
            state=state,
            message=message,
            text=templ.reviews_float_text(
                f"🔍 Найдено <b>{len(games)} игр</b>:"
            ),
            reply_markup=templ.reviews_filter_games_kb(
                games=games, page=0
            )
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.reviews_float_text(e),
            reply_markup=templ.back_kb("reviews_filter")
        )


@router.message(states.ActionsStates.waiting_for_reviews_min_item_price, F.text)
async def handler_waiting_for_reviews_min_item_price(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)

        data = await state.get_data()
        callback = data.get("callback")
        
        if not message.text.isdigit() or not (1 <= int(message.text) <= 999999):
            raise Exception("❌ Вы должны ввести числовое значение")
        
        await message.bot.delete_message(message.chat.id, message.message_id)
        await callback_change_reviews_filter(
            callback, calls.ChangeReviewsFilter(min_pr=int(message.text)), state
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.reviews_float_text(e),
            reply_markup=templ.back_kb("reviews_filter")
        )


@router.message(states.ActionsStates.waiting_for_reviews_max_item_price, F.text)
async def handler_waiting_for_reviews_max_item_price(message: types.Message, state: FSMContext):
    try:
        await state.set_state(None)

        data = await state.get_data()
        callback = data.get("callback")
        
        if not message.text.isdigit() or not (1 <= int(message.text) <= 999999):
            raise Exception("❌ Вы должны ввести числовое значение")
        
        await message.bot.delete_message(message.chat.id, message.message_id)
        await callback_change_reviews_filter(
            callback, calls.ChangeReviewsFilter(max_pr=int(message.text)), state
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.reviews_float_text(e),
            reply_markup=templ.back_kb("reviews_filter")
        )