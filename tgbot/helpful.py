from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, Message, CallbackQuery
from aiogram.exceptions import TelegramAPIError

from . import templates as templ


async def do_auth(message: Message, state: FSMContext):
    """
    Начинает процесс авторизации в боте (запрашивает пароль, указанный в конфиге).

    :param message: Исходное сообщение.
    :type message: `aiogram.types.Message`

    :param state: Исходное состояние.
    :type state: `aiogram.fsm.context.FSMContext`
    """
    from . import states
    await state.set_state(states.SystemStates.entering_password)
    return await throw_float_message(state=state,
                                     message=message,
                                     text=templ.sign_text('🔑 Введите ключ-пароль, указанный вами в конфиге бота ↓\n\n<span class="tg-spoiler">Если вы забыли, его можно посмотреть напрямую в конфиге по пути bot_settings/config.json, параметр password в разделе telegram.bot</span>'),
                                     reply_markup=templ.destroy_kb())

async def throw_float_message(state: FSMContext, message: Message, text: str, 
                              reply_markup: InlineKeyboardMarkup = None,
                              callback: CallbackQuery = None,
                              send: bool = False) -> Message | None:
    """
    Изменяет плавающее сообщение (изменяет текст акцентированного сообщения) или родительское сообщение бота, переданное в аргумент `message`.\n
    Если не удалось найти акцентированное сообщение, или это сообщения - команда, отправит новое акцентированное сообщение.

    :param state: Состояние бота.
    :type state: `aiogram.fsm.context.FSMContext`
    
    :param message: Переданный в handler объект сообщения.
    :type message: `aiogram.types.Message`

    :param text: Текст сообщения.
    :type text: `str`

    :param reply_markup: Клавиатура сообщения, _опционально_.
    :type reply_markup: `aiogram.typesInlineKeyboardMarkup.`

    :param callback: CallbackQuery хендлера, для ответа пустой AnswerCallbackQuery, _опционально_.
    :type callback: `aiogram.types.CallbackQuery` or `None`

    :param send: Отправить ли новое акцентированное сообщение, _опционально_.
    :type send: `bool`
    """
    from .telegrambot import get_telegram_bot
    try:
        bot = get_telegram_bot().bot
        data = await state.get_data()
        accent_message_id = message.message_id
        if message.from_user and message.from_user.id != bot.id:
            accent_message_id = data.get("accent_message_id")
        mess = None
        new_mess_cond = False

        if not send:
            if message.text is not None:
                new_mess_cond = message.from_user.id != bot.id and message.text.startswith('/')

            if accent_message_id is not None and not new_mess_cond:
                try:
                    if message.from_user.id != bot.id: 
                        await bot.delete_message(message.chat.id, message.message_id)
                    mess = await bot.edit_message_text(text=text, reply_markup=reply_markup, 
                                                    chat_id=message.chat.id, message_id=accent_message_id, parse_mode="HTML")
                except TelegramAPIError as e:
                    if "message to edit not found" in e.message.lower():
                        accent_message_id = None
                    elif "message is not modified" in e.message.lower():
                        await bot.answer_callback_query(callback.id, show_alert=False, cache_time=0)
                        pass
                    else:
                        raise e
        if callback:
            await bot.answer_callback_query(callback.id, show_alert=False, cache_time=0)
        if accent_message_id is None or new_mess_cond or send:
            mess = await bot.send_message(chat_id=message.chat.id, text=text, 
                                          reply_markup=reply_markup, parse_mode="HTML")
    except Exception as e:
        import traceback
        traceback.print_exc()
        try:
            mess = await bot.edit_message_text(chat_id=message.chat.id, reply_markup=templ.destroy_kb(),
                                               text=templ.error_text(e), message_id=accent_message_id, parse_mode="HTML")
        except Exception as e:
            mess = await bot.send_message(chat_id=message.chat.id, reply_markup=templ.destroy_kb(),
                                          text=templ.error_text(e), parse_mode="HTML")
    finally:
        if mess: await state.update_data(accent_message_id=mess.message_id)
    return mess