from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from settings import Settings as sett
from utils import is_password_valid

from .. import templates as templ
from .. import states
from .. import callback_datas as calls
from ..helpful import throw_float_message


router = Router()


@router.message(states.SystemStates.waiting_for_password, F.text)
async def handler_waiting_for_password(message: types.Message, state: FSMContext):
    try: 
        await state.set_state(None)
        config = sett.get("config")
        
        if message.text != config["telegram"]["bot"]["password"]:
            raise Exception("❌ Неверный ключ-пароль")
        
        config["telegram"]["bot"]["signed_users"].append(message.from_user.id)
        sett.set("config", config)

        try:
            await throw_float_message(
                state=state,
                message=message,
                text=templ.menu_text(),
                reply_markup=templ.menu_kb()
            )
        except:
            await message.bot.send_message(
                chat_id=message.from_user.id,
                text=templ.menu_text(),
                reply_markup=templ.menu_kb(),
                parse_mode="HTML"
            )

        old_users = config["telegram"]["bot"]["signed_users"]
        old_users.remove(message.from_user.id)

        for user_id in old_users:
            try:
                await message.bot.send_message(
                    chat_id=user_id,
                    text=templ.new_sign_text(message.from_user),
                    reply_markup=templ.destroy_kb(),
                    parse_mode="HTML"
                )
            except:
                pass
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.sign_text(e), 
            reply_markup=templ.destroy_kb()
        )


@router.message(states.SystemStates.waiting_for_current_password, F.text)
async def handler_waiting_for_current_password(message: types.Message, state: FSMContext):
    try: 
        await state.set_state(None)
        config = sett.get("config")

        data = await state.get_data()
        last_page = data.get("last_page", 0)
        
        if message.text != config["telegram"]["bot"]["password"]:
            raise Exception("❌ Неверный ключ-пароль")

        await state.set_state(states.SystemStates.waiting_for_new_password)
        await throw_float_message(
            state=state,
            message=message,
            text=templ.signed_users_float_text("🆕 Введите <b>новый ключ-пароль</b> от бота (не менее 6 и не более 64 символов):"),
            reply_markup=templ.back_kb(calls.SignedUsersPagination(page=last_page).pack())
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.signed_users_float_text(e), 
            reply_markup=templ.back_kb(calls.SignedUsersPagination(page=last_page).pack())
        )


@router.message(states.SystemStates.waiting_for_new_password, F.text)
async def handler_waiting_for_new_password(message: types.Message, state: FSMContext):
    try: 
        await state.set_state(None)

        config = sett.get("config")
        old_passwd = config["telegram"]["bot"]["password"]

        data = await state.get_data()
        last_page = data.get("last_page", 0)
        
        if not is_password_valid(message.text):
            raise Exception("❌ Ваш пароль не подходит. Убедитесь, что он соответствует формату и не является лёгким и попробуйте ещё раз")
        
        new_passwd = message.text
        await state.update_data(new_password=new_passwd)

        await throw_float_message(
            state=state,
            message=message,
            text=templ.signed_users_float_text(
                "✔️ Подтвердите <b>смену пароля</b> для бота:"
                f"\n\n・ <b>Старый:</b> {old_passwd}"
                f"\n・ <b>Новый:</b> {new_passwd}"
            ),
            reply_markup=templ.confirm_kb(
                confirm_cb="change_password",
                cancel_cb=calls.SignedUsersPagination(page=last_page).pack()
            )
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.signed_users_float_text(e), 
            reply_markup=templ.back_kb(calls.SignedUsersPagination(page=last_page).pack())
        )