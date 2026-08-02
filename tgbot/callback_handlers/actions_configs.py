import os
from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.fsm.context import FSMContext

from utils import escape_html
from core.configs import (
    BACKUPS_DIR,
    BACKUP_COOLDOWN,
    MAX_BACKUPS,
    export_all,
    export_file,
    import_file,
    make_backup,
    recent_backup,
    list_backups,
    clear_export_dir,
    clear_import_dir
)

from .. import templates as templ
from .. import callback_datas as calls
from .. import states
from ..helpful import throw_float_message, notify, answer_callback


router = Router()


async def apply_import(state: FSMContext, message: Message, user_id: int, keep_secrets: bool, callback: CallbackQuery = None):
    """
    Применяет ранее полученный файл конфигов и отправляет отчёт.

    :param user_id: ID пользователя Telegram, который прислал файл.
    :type user_id: `int`

    :param keep_secrets: Оставить текущие секретные данные (Cookie-данные, токены, пароль).
    :type keep_secrets: `bool`
    """
    data = await state.get_data()
    path = data.get("import_config_path")
    await state.update_data(import_config_path=None)

    try:
        if not path or not os.path.exists(path):
            raise Exception("❌ Файл не найден, отправьте его заново")

        applied, skipped, backup = import_file(path, keep_secrets=keep_secrets)

        if applied:
            str_applied = "\n".join(f"・ {escape_html(name)}" for name in applied)
            report = (
                f"✅ <b>Импортировано ({len(applied)}):</b>"
                f"\n<blockquote>{str_applied}</blockquote>"
            )
        else:
            report = "❌ <b>Не удалось импортировать ни один конфиг</b>"

        if skipped:
            str_skipped = "\n".join(
                f"・ {escape_html(name)} — {escape_html(reason)}" for name, reason in skipped
            )
            report += (
                f"\n\n⚠️ <b>Пропущено ({len(skipped)}):</b>"
                f"\n<blockquote>{str_skipped}</blockquote>"
            )

        if backup:
            report += (
                f"\n\n💾 <b>Бэкап прошлых конфигов:</b>"
                f"\n<blockquote>{escape_html(backup)}</blockquote>"
            )
        elif applied:
            report += "\n\n⚠️ <b>Бэкап прошлых конфигов создать не удалось</b> — подробности в логах"

        if applied:
            report += "\n\n❗ Чтобы изменения применились полностью, <b>перезагрузите бота</b> — /restart"

        await throw_float_message(
            state=state,
            message=message,
            text=templ.configs_float_text(report),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="configs").pack()),
            callback=callback
        )
    except Exception as e:
        await throw_float_message(
            state=state,
            message=message,
            text=templ.configs_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="configs").pack()),
            callback=callback
        )
    finally:
        clear_import_dir(user_id)


async def send_export(callback: CallbackQuery, state: FSMContext, path: str):
    await callback.message.answer_document(
        document=FSInputFile(path),
        caption="❗ В файле лежат ваши <b>Cookie-данные, токен Telegram бота и ключ-пароль</b> — не пересылайте его третьим лицам",
        parse_mode="HTML",
        reply_markup=templ.destroy_kb()
    )
    await answer_callback(callback.bot, callback)

    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.configs_text(),
        reply_markup=templ.configs_kb()
    )


async def run_export(callback: CallbackQuery, state: FSMContext, make_path: callable):
    await state.set_state(None)
    user_id = callback.from_user.id

    try:
        await send_export(callback, state, make_path(user_id))
    except Exception as e:
        await throw_float_message(
            state=state,
            message=callback.message,
            text=templ.configs_float_text(e),
            reply_markup=templ.back_kb(calls.MenuNavigation(to="configs").pack())
        )
    finally:
        clear_export_dir(user_id)


@router.callback_query(F.data == "export_main_config")
async def callback_export_main_config(callback: CallbackQuery, state: FSMContext):
    await run_export(callback, state, lambda uid: export_file(uid, "config"))


@router.callback_query(F.data == "export_all_configs")
async def callback_export_all_configs(callback: CallbackQuery, state: FSMContext):
    await run_export(callback, state, lambda uid: export_all(uid))


@router.callback_query(F.data == "export_full_configs")
async def callback_export_full_configs(callback: CallbackQuery, state: FSMContext):
    await run_export(callback, state, lambda uid: export_all(uid, with_data=True))


@router.callback_query(F.data == "make_config_backup")
async def callback_make_config_backup(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)

    # свежий бэкап переиспользуем: иначе повторные нажатия забьют все слоты
    # одинаковыми копиями и вытеснят бэкапы, снятые перед импортом
    backup = recent_backup()
    reused = bool(backup)
    if not backup:
        backup = make_backup()

    if not backup:
        await notify(callback, "❌ Не удалось создать бэкап")
        report = "❌ <b>Не удалось создать бэкап</b> — подробности в логах"
    else:
        if reused:
            await notify(callback, "💾 Свежий бэкап уже есть")
            report = (
                f"💾 <b>Свежий бэкап уже есть:</b>"
                f"\n<blockquote>{escape_html(os.path.basename(backup))}</blockquote>"
                f"\n\nНовая копия не создана — прошлая снята меньше {BACKUP_COOLDOWN} сек. назад."
                f" Так повторные нажатия не вытесняют бэкапы, снятые перед импортом"
            )
        else:
            await notify(callback, "💾 Бэкап создан")
            report = (
                f"💾 <b>Бэкап создан:</b>"
                f"\n<blockquote>{escape_html(os.path.basename(backup))}</blockquote>"
            )

        backups = list_backups()
        if backups:
            str_backups = "\n".join(f"・ {escape_html(name)}" for name in backups)
            report += (
                f"\n\n🗄 <b>Хранится копий ({len(backups)} из {MAX_BACKUPS}):</b>"
                f"\n<blockquote>{str_backups}</blockquote>"
            )

        report += (
            f"\n\n<b>(?)</b> Бэкапы лежат в папке <b>{BACKUPS_DIR}</b> на этом устройстве."
            f" Когда копий становится больше {MAX_BACKUPS}, <b>самая старая удаляется</b>"
        )

    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.configs_float_text(report),
        reply_markup=templ.back_kb(calls.MenuNavigation(to="configs").pack()),
        callback=callback
    )


@router.callback_query(F.data == "send_config_file")
async def callback_send_config_file(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SettingsStates.waiting_for_config_file)
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.configs_float_text(
            "🗂 Отправьте <b>файл конфига или данных</b> (config.json, messages.json, cached_orders.json и т.д.)"
            " или <b>архив</b> с ними (форматы: zip, rar):"
        ),
        reply_markup=templ.back_kb(calls.MenuNavigation(to="configs").pack()),
        callback=callback
    )


@router.callback_query(F.data == "import_config_keep_secrets")
async def callback_import_config_keep_secrets(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    await apply_import(
        state, callback.message, callback.from_user.id, keep_secrets=True, callback=callback
    )


@router.callback_query(F.data == "import_config_take_secrets")
async def callback_import_config_take_secrets(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    await apply_import(
        state, callback.message, callback.from_user.id, keep_secrets=False, callback=callback
    )


@router.callback_query(F.data == "import_config_cancel")
async def callback_import_config_cancel(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    await state.update_data(import_config_path=None)
    clear_import_dir(callback.from_user.id)

    await notify(callback, "❌ Импорт отменён")
    await throw_float_message(
        state=state,
        message=callback.message,
        text=templ.configs_text(),
        reply_markup=templ.configs_kb(),
        callback=callback
    )
