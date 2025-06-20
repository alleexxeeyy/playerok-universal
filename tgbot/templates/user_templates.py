from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import math
from datetime import datetime

import tgbot.callback_datas.user_callback_datas as CallbackDatas

from settings import Config, Messages, CustomCommands, AutoDeliveries

from bot_settings.app import CURRENT_VERSION
from plbot.utils.stats import get_stats
from plbot import get_playerok_bot

from core.modules_manager import ModulesManager, Module
from uuid import UUID

from playerokapi import types as plapi_types
        
class System:
    """ Шаблоны системных сообщений """
    class Error:
        def text(error_text) -> str:
            msg = f"❌ Произошла ошибка: <b>{error_text}</b>"
            return msg

class Navigation:
    """ Шаблоны навигации по боту """

    class MenuNavigation:
        class Default:
            def text() -> str:
                msg = f"🏠 <b>Главное меню</b>" \
                    f"\n" \
                    f"\n<b>Playerok UNIVERSAL</b> v{CURRENT_VERSION} " \
                    f"\nБот-помощник для Playerok" \
                    f"\n" \
                    f"\n<b>Ссылки:</b>" \
                    f"\n→ <b>@alleexxeeyy</b> — главный и единственный разработчик" \
                    f"\n→ <b>@alexeyproduction</b> — канал, где публикуются новости" \
                    f"\n→ <b>@alexey_production_bot</b> — бот для покупки официальных модулей" \
                    f"\n" \
                    f"\nПеремещайтесь по разделам ниже ↓"
                return msg
                
            def kb() -> InlineKeyboardMarkup:
                btn1 = InlineKeyboardButton(
                    text="⚙️ Настройки бота",
                    callback_data=CallbackDatas.SettingsNavigation(
                        to="default"
                    ).pack()
                )
                btn2 = InlineKeyboardButton(
                    text="📊 Статистика",
                    callback_data=CallbackDatas.MenuNavigation(
                        to="stats"
                    ).pack()
                )
                btn3 = InlineKeyboardButton(
                    text="👤 Мой профиль",
                    callback_data=CallbackDatas.MenuNavigation(
                        to="profile"
                    ).pack()
                )
                btn4 = InlineKeyboardButton(
                    text="🔌 Модули",
                    callback_data=CallbackDatas.ModulesPagination(
                        page=0
                    ).pack()
                )
                btn5 = InlineKeyboardButton(
                    text="📖 Инструкция",
                    callback_data=CallbackDatas.InstructionNavigation(
                        to="default"
                    ).pack()
                )
                btn6 = InlineKeyboardButton(
                    text="👨‍💻 Разработчик",
                    url="https://t.me/alleexxeeyy",
                )
                btn7 = InlineKeyboardButton(
                    text="📢 Наш канал",
                    url="https://t.me/alexeyproduction",
                )
                btn8 = InlineKeyboardButton(
                    text="⚙️ Наш бот",
                    url="https://t.me/alexey_production_bot",
                )
                rows = [[btn1, btn2], [btn3, btn4], [btn5], [btn6, btn7, btn8]]
                markup = InlineKeyboardMarkup(inline_keyboard=rows)
                return markup
                
        class Stats:
            class Error:
                def text() -> str:
                    msg = "📊 <b>Статистика Playerok бота</b>" \
                        f"\n" \
                        f"\n→ Дата запуска: <i>не удалось загрузить</i>" \
                        f"\n" \
                        f"\n→ Продаж: <i>не удалось загрузить</i>" \
                        f"\n→ Активных: <i>не удалось загрузить</i>" \
                        f"\n→ Возвратов: <i>не удалось загрузить</i>" \
                        f"\n→ Заработано: <i>не удалось загрузить</i>" \
                        f"\n" \
                        f"\nВыберите действие ↓"
                    return msg

            class Loading:
                def text() -> str:
                    msg = "📊 <b>Статистика Playerok бота</b>" \
                        f"\n" \
                        f"\n→ Дата запуска: <i>загрузка</i>" \
                        f"\n" \
                        f"\n→ Продаж: <i>загрузка</i>" \
                        f"\n→ Активных: <i>загрузка</i>" \
                        f"\n→ Возвратов: <i>загрузка</i>" \
                        f"\n→ Заработано: <i>загрузка</i>" \
                        f"\n" \
                        f"\nВыберите действие ↓"
                    return msg
                
            class Default:
                def text() -> str:
                    stats = get_stats()
                    msg = "📊 <b>Статистика Playerok бота</b>" \
                        f"\n" \
                        f"\n→ Дата запуска: <code>{stats['bot_launch_time'].strftime('%d.%m.%Y %H:%M:%S')}</code>" \
                        f"\n" \
                        f"\n→ Продаж: <code>{stats['orders_completed']}</code>" \
                        f"\n→ Активных: <code>{stats['active_orders']}</code>" \
                        f"\n→ Возвратов: <code>{stats['orders_refunded']}</code>" \
                        f"\n→ Заработано: <code>{stats['earned_money']}</code> р." \
                        f"\n" \
                        f"\nВыберите действие ↓"
                    return msg
                    
                def kb() -> InlineKeyboardMarkup:
                    btn_refresh = InlineKeyboardButton(
                        text="🔄️ Обновить",
                        callback_data=CallbackDatas.MenuNavigation(
                            to="stats"
                        ).pack()
                    )
                    btn_back = InlineKeyboardButton(
                        text="⬅️ Назад",
                        callback_data=CallbackDatas.MenuNavigation(
                            to="default"
                        ).pack()
                    )
                    rows = [[btn_refresh], [btn_back]]
                    markup = InlineKeyboardMarkup(inline_keyboard=rows)
                    return markup
            
        class Profile:
            class Error:
                def text() -> str:
                    msg = "👤 <b>Мой профиль</b>" \
                        f"\n" \
                        f"\n→ ID: <i>не удалось загрузить</i>" \
                        f"\n→ Никнейм: <i>не удалось загрузить</i>" \
                        f"\n→ Email: <i>не удалось загрузить</i>" \
                        f"\n→ Роль: <i>не удалось загрузить</i>" \
                        f"\n" \
                        f"\n→ Рейтинг: <i>не удалось загрузить</i>" \
                        f"\n→ Кол-во отзывов: <i>не удалось загрузить</i>" \
                        f"\n" \
                        f"\n→ Баланс:" \
                        f"\n  ┕ Всего: <i>не удалось загрузить</i>" \
                        f"\n  ┕ Доступно: <i>не удалось загрузить</i>" \
                        f"\n  ┕ Заморожено: <i>не удалось загрузить</i>" \
                        f"\n" \
                        f"\n→ Статистика:" \
                        f"\n  ┕ Предметы: " \
                        f"\n      ┕ Всего: <i>не удалось загрузить</i>" \
                        f"\n      ┕ Истёкших: <i>не удалось загрузить</i>" \
                        f"\n  ┕ Сделки: " \
                        f"\n      ┕ Всего входящих: <i>не удалось загрузить</i>" \
                        f"\n      ┕ Завершено входящих: <i>не удалось загрузить</i>" \
                        f"\n      ┕ Всего исходящих: <i>не удалось загрузить</i>" \
                        f"\n      ┕ Завершено исходящих: <i>не удалось загрузить</i>" \
                        f"\n" \
                        f"\n→ Дата создания: <i>не удалось загрузить</i>" \
                        f"\n" \
                        f"\nВыберите действие ↓"
                    return msg

            class Loading:
                def text() -> str:
                    msg = "👤 <b>Мой профиль</b>" \
                        f"\n" \
                        f"\n→ ID: <i>загрузка</i>" \
                        f"\n→ Никнейм: <i>загрузка</i>" \
                        f"\n→ Email: <i>загрузка</i>" \
                        f"\n→ Роль: <i>загрузка</i>" \
                        f"\n" \
                        f"\n→ Рейтинг: <i>загрузка</i>" \
                        f"\n→ Кол-во отзывов: <i>загрузка</i>" \
                        f"\n" \
                        f"\n→ Баланс:" \
                        f"\n  ┕ Всего: <i>загрузка</i>" \
                        f"\n  ┕ Доступно: <i>загрузка</i>" \
                        f"\n  ┕ Заморожено: <i>загрузка</i>" \
                        f"\n" \
                        f"\n→ Статистика:" \
                        f"\n  ┕ Предметы: " \
                        f"\n      ┕ Всего: <i>загрузка</i>" \
                        f"\n      ┕ Истёкших: <i>загрузка</i>" \
                        f"\n  ┕ Сделки: " \
                        f"\n      ┕ Всего входящих: <i>загрузка</i>" \
                        f"\n      ┕ Завершено входящих: <i>загрузка</i>" \
                        f"\n      ┕ Всего исходящих: <i>загрузка</i>" \
                        f"\n      ┕ Завершено исходящих: <i>загрузка</i>" \
                        f"\n" \
                        f"\n→ Дата создания: <i>загрузка</i>" \
                        f"\n" \
                        f"\nВыберите действие ↓"
                    return msg
                
            class Default:
                def text() -> str:
                    playerokbot = get_playerok_bot()
                    profile = playerokbot.playerok_account.profile
                    msg = "👤 <b>Мой профиль</b>" \
                        f"\n" \
                        f"\n→ ID: <code>{profile.id}</code>" \
                        f"\n→ Никнейм: <b>{profile.username}</b>" \
                        f"\n→ Email: <b>{profile.email}</b>" \
                        f"\n→ Роль: <b>{profile.role.name}</b>" \
                        f"\n" \
                        f"\n→ Рейтинг: <b>{profile.rating}</b>" \
                        f"\n→ Кол-во отзывов: <b>{profile.reviews_count}</b>" \
                        f"\n" \
                        f"\n→ Баланс:" \
                        f"\n  ┕ Всего: <b>{profile.balance.value}</b>" \
                        f"\n  ┕ Доступно: <b>{profile.balance.available}</b>" \
                        f"\n  ┕ Заморожено: <b>{profile.balance.frozen}</b>" \
                        f"\n" \
                        f"\n→ Статистика:" \
                        f"\n  ┕ Предметы: " \
                        f"\n      ┕ Всего: <b>{profile.stats.items.total}</b>" \
                        f"\n      ┕ Истёкших: <b>{profile.stats.items.finished}</b>" \
                        f"\n  ┕ Сделки: " \
                        f"\n      ┕ Всего входящих: <b>{profile.stats.deals.incoming.total}</b>" \
                        f"\n      ┕ Завершено входящих: <b>{profile.stats.deals.incoming.finished}</b>" \
                        f"\n      ┕ Всего исходящих: <b>{profile.stats.deals.outgoing.total}</b>" \
                        f"\n      ┕ Завершено исходящих: <b>{profile.stats.deals.outgoing.finished}</b>" \
                        f"\n" \
                        f"\n→ Дата создания: <b>{datetime.fromisoformat(profile.created_at).strftime('%d.%m.%Y %H:%M:%S')}</b>" \
                        f"\n" \
                        f"\nВыберите действие ↓"
                    return msg
                    
                def kb() -> InlineKeyboardMarkup:
                    btn_refresh = InlineKeyboardButton(
                        text="🔄️ Обновить",
                        callback_data=CallbackDatas.MenuNavigation(
                            to="profile"
                        ).pack()
                    )
                    btn_back = InlineKeyboardButton(
                        text="⬅️ Назад",
                        callback_data=CallbackDatas.MenuNavigation(
                            to="default"
                        ).pack()
                    )
                    rows = [[btn_refresh], [btn_back]]
                    markup = InlineKeyboardMarkup(inline_keyboard=rows)
                    return markup
                
    class InstructionNavigation:
        class Default:
            def text() -> str:
                msg = "📖 <b>Инструкция</b>" \
                    "\nВ этом разделе описаны инструкции по работе с ботом" \
                    "\n" \
                    "\nПеремещайтесь по разделам ниже ↓"
                return msg
                
            def kb() -> InlineKeyboardMarkup:
                btn1 = InlineKeyboardButton(
                    text="⌨️ Команды",
                    callback_data=CallbackDatas.InstructionNavigation(
                        to="commands"
                    ).pack()
                )
                btn_back = InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data=CallbackDatas.MenuNavigation(
                        to="default"
                    ).pack()
                )
                rows = [[btn1], [btn_back]]
                markup = InlineKeyboardMarkup(inline_keyboard=rows)
                return markup
            
        class Commands:
            def text() -> str:
                msg = "📖 <b>Инструкция → ⌨️ Команды</b>" \
                    "\n" \
                    "\n<b>Команды покупателя:</b>" \
                    "\n→ <code>!команды</code> — отображает меню с доступными для покупателя командами" \
                    "\n→ <code>!продавец</code> — уведомляет и вызывает продавца в диалог с покупателем (пишет вам в Telegram сообщение с просьбой о помощи)" \
                    "\n" \
                    "\nВыберите действие ↓"
                return msg
            
            def kb() -> InlineKeyboardMarkup:
                btn_back = InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data=CallbackDatas.MenuNavigation(
                        to="instruction"
                    ).pack()
                )
                rows = [[btn_back]]
                markup = InlineKeyboardMarkup(inline_keyboard=rows)
                return markup

    class Settings:
        class Default:
            class Loading:
                def text() -> str:
                    msg = f"⚙️ <b>Настройки бота</b>" \
                        f"\n" \
                        f"\n<b>Основные настройки:</b>" \
                        f"\n→ Токен аккаунта: <i>загрузка</i>" \
                        f"\n→ Юзер агент: <i>загрузка</i>" \
                        f"\n" \
                        f"\nПеремещайтесь по разделам ниже, чтобы изменить значения параметров ↓"
                    return msg
                
            class Error:
                def text() -> str:
                    msg = f"⚙️ <b>Настройки бота</b>" \
                        f"\n" \
                        f"\n<b>Основные настройки:</b>" \
                        f"\n→ Токен аккаунта: <i>не удалось загрузить</i>" \
                        f"\n→ Юзер агент: <i>не удалось загрузить</i>" \
                        f"\n" \
                        f"\nПеремещайтесь по разделам ниже, чтобы изменить значения параметров ↓"
                    return msg
                
            class Default:
                def text() -> str:
                    config = Config.get()
                    token = (config["token"][:3] + "*" * (len(config["token"]) - 3))[:32] if config["token"] else "❌ Не задано"
                    user_agent = config["user_agent"] if config["user_agent"] else "❌ Не задано"
                    msg = f"⚙️ <b>Настройки бота</b>" \
                        f"\n" \
                        f"\n<b>Основные настройки</b>:" \
                        f"\n→ Токен аккаунта: <code>{token}</code>" \
                        f"\n→ Юзер агент: <code>{user_agent}</code>" \
                        f"\n" \
                        f"\nПеремещайтесь по разделам ниже, чтобы изменить значения параметров ↓"
                    return msg
                
                def kb() -> InlineKeyboardMarkup:
                    btn1 = InlineKeyboardButton(
                        text="🔑 Авторизация",
                        callback_data=CallbackDatas.BotSettingsNavigation(
                            to="authorization"
                        ).pack()
                    )
                    btn2 = InlineKeyboardButton(
                        text="📶 Соединение",
                        callback_data=CallbackDatas.BotSettingsNavigation(
                            to="connection"
                        ).pack()
                    )
                    btn3 = InlineKeyboardButton(
                        text="📦 Предметы",
                        callback_data=CallbackDatas.BotSettingsNavigation(
                            to="items"
                        ).pack()
                    )
                    btn4 = InlineKeyboardButton(
                        text="✉️ Сообщения",
                        callback_data=CallbackDatas.MessagesPagination(
                            page=0
                        ).pack()
                    )
                    btn5 = InlineKeyboardButton(
                        text="⌨️ Пользовательские команды",
                        callback_data=CallbackDatas.CustomCommandsPagination(
                            page=0
                        ).pack()
                    )
                    btn6 = InlineKeyboardButton(
                        text="🚀 Автоматическая выдача",
                        callback_data=CallbackDatas.AutoDeliveriesPagination(
                            page=0
                        ).pack()
                    )
                    btn7 = InlineKeyboardButton(
                        text="🔧 Прочее",
                        callback_data=CallbackDatas.BotSettingsNavigation(
                            to="other"
                        ).pack()
                    )
                    btn_refresh = InlineKeyboardButton(
                        text="🔄️ Обновить",
                        callback_data=CallbackDatas.BotSettingsNavigation(
                            to="default"
                        ).pack()
                    )
                    btn_back = InlineKeyboardButton(
                        text="⬅️ Назад",
                        callback_data=CallbackDatas.MenuNavigation(
                            to="default"
                        ).pack()
                    )
                    rows = [[btn1, btn2], [btn3, btn4], [btn5], [btn6], [btn7], [btn_refresh], [btn_back]]
                    markup = InlineKeyboardMarkup(inline_keyboard=rows)
                    return markup
            
        class Authorization:
            class Error:
                def text() -> str:
                    msg = f"⚙️ <b>Настройки бота → 🔑 Авторизация</b>"\
                            f"\n" \
                            f"\n→ Токен: <i>не удалось загрузить</i>" \
                            f"\n→ Юзер агент: <i>не удалось загрузить</i>" \
                            f"\n" \
                            f"\nВыберите параметр для изменения ↓"
                    return msg
                
            class Loading:
                def text() -> str:
                    msg = f"⚙️ <b>Настройки бота → 🔑 Авторизация</b>"\
                            f"\n" \
                            f"\n→ Токен: <i>загрузка</i>" \
                            f"\n→ Юзер агент: <i>загрузка</i>" \
                            f"\n" \
                            f"\nВыберите параметр для изменения ↓"
                    return msg
                    
            class Default:
                def text() -> str:
                    config = Config.get()
                    user_agent = config["user_agent"] if config["user_agent"] else "❌ Не задано"
                    token = (config["token"][:3] + "*" * (len(config['token']) - 3))[:32] if config["token"] else "❌ Не задано"
                    msg = f"⚙️ <b>Настройки бота → 🔑 Авторизация</b>"\
                            f"\n" \
                            f"\n→ Токен: <code>{token}</code>" \
                            f"\n→ Юзер агент: <code>{user_agent}</code>" \
                            f"\n" \
                            f"\nВыберите параметр для изменения ↓"
                    return msg
                
                def kb() -> InlineKeyboardMarkup:
                    config = Config.get()
                    user_agent = config["user_agent"] if config["user_agent"] else "❌ Не задано"
                    token = (config["token"][:3] + "*" * (len(config['token']) - 3))[:32] if config["token"] else "❌ Не задано"
                    btn1 = InlineKeyboardButton(
                        text=f"🔑 Токен: {token}",
                        callback_data="enter_token"
                    )
                    btn2 = InlineKeyboardButton(
                        text=f"🎩 Юзер агент: {user_agent}",
                        callback_data="enter_user_agent"
                    )
                    btn_refresh = InlineKeyboardButton(
                        text="🔄️ Обновить",
                        callback_data=CallbackDatas.BotSettingsNavigation(
                            to="authorization"
                        ).pack()
                    )
                    btn_back = InlineKeyboardButton(
                        text="⬅️ Назад",
                        callback_data=CallbackDatas.BotSettingsNavigation(
                            to="default"
                        ).pack()
                    )
                    rows = [[btn1, btn2], [btn_refresh], [btn_back]]
                    markup = InlineKeyboardMarkup(inline_keyboard=rows)
                    return markup
                
            class EnterToken:
                def text() -> str:
                    config = Config.get()
                    msg = f"🔑 <b>Введите новый токен вашего Playerok аккаунта ↓</b>" \
                            f"\nТекущее значение: <code>{config['token']}</code>"
                    return msg
                
            class TokenChanged:
                def text(new):
                    msg = f"✅ <b>Токен аккаунта</b> был успешно изменён на <code>{new}</code>"
                    return msg
                
            class EnterUserAgent:
                def text() -> str:
                    config = Config.get()
                    user_agent = config["user_agent"] if config["user_agent"] != "" else "❌ Не задано"
                    msg = f"🎩 <b>Введитe новый юзер агент вашего браузера ↓</b>" \
                            f"\nТекущее значение: <code>{user_agent}</code>"
                    return msg
                
            class UserAgentChanged:
                def text(new):
                    msg = f"✅ <b>Юзе агент</b> был успешно изменён на <code>{new}</code>"
                    return msg
                
        class Connection:
            class Error:
                def text() -> str:
                    msg = f"⚙️ <b>Настройки бота → 📶 Соединение</b>"\
                            f"\n" \
                            f"\n→ Таймаут подключения к playerok.com: <i>не удалось загрузить</i>" \
                            f"\n→ Периодичность запросов к playerok.com: <i>не удалось загрузить</i>" \
                            f"\n" \
                            f"\n<b>Что такое таймаут подключения к playerok.com?</b>" \
                            f"\nЭто максимальное время, за которое должен прийти ответ на запрос с сайта Playerok. " \
                            f"Если время истекло, а ответ не пришёл - бот выдаст ошибку. Если у вас слабый интернет, " \
                            f"указывайте значение больше" \
                            f"\n" \
                            f"\n<b>Что такое периодичность запросов к playerok.com?</b>" \
                            f"\nС какой периодичностью будут отправляться запросы на Playerok для получения событий. " \
                            f"Не рекомендуем ставить ниже 4 секунд, так как Playerok попросту может забанить ваш IP " \
                            f"адрес, и вы уже не сможете отправлять с него запросы" \
                            f"\n" \
                            f"\nВыберите параметр для изменения ↓"
                    return msg

            class Loading:
                def text() -> str:
                    msg = f"⚙️ <b>Настройки бота → 📶 Соединение</b>"\
                            f"\n" \
                            f"\n→ Таймаут подключения к playerok.com: <i>загрузка</i>" \
                            f"\n→ Периодичность запросов к playerok.com: <i>загрузка</i>" \
                            f"\n" \
                            f"\n<b>Что такое таймаут подключения к playerok.com?</b>" \
                            f"\nЭто максимальное время, за которое должен прийти ответ на запрос с сайта Playerok. " \
                            f"Если время истекло, а ответ не пришёл - бот выдаст ошибку. Если у вас слабый интернет, " \
                            f"указывайте значение больше" \
                            f"\n" \
                            f"\n<b>Что такое периодичность запросов к playerok.com?</b>" \
                            f"\nС какой периодичностью будут отправляться запросы на Playerok для получения событий. " \
                            f"Не рекомендуем ставить ниже 4 секунд, так как Playerok попросту может забанить ваш IP " \
                            f"адрес, и вы уже не сможете отправлять с него запросы" \
                            f"\n" \
                            f"\nВыберите параметр для изменения ↓"
                    return msg

            class Default:
                def text() -> str:
                    config = Config.get()
                    msg = f"⚙️ <b>Настройки бота → 📶 Соединение</b>"\
                            f"\n" \
                            f"\n→ Таймаут подключения к playerok.com: <code>{config['playerokapi_requests_timeout']}</code> сек." \
                            f"\n→ Периодичность запросов к playerok.com: <code>{config['playerokapi_listener_requests_delay']}</code> сек." \
                            f"\n" \
                            f"\n<b>Что такое таймаут подключения к playerok.com?</b>" \
                            f"\nЭто максимальное время, за которое должен прийти ответ на запрос с сайта Playerok. " \
                            f"Если время истекло, а ответ не пришёл - бот выдаст ошибку. Если у вас слабый интернет, " \
                            f"указывайте значение больше" \
                            f"\n" \
                            f"\n<b>Что такое периодичность запросов к playerok.com?</b>" \
                            f"\nС какой периодичностью будут отправляться запросы на Playerok для получения событий. " \
                            f"Не рекомендуем ставить ниже 4 секунд, так как Playerok попросту может забанить ваш IP " \
                            f"адрес, и вы уже не сможете отправлять с него запросы" \
                            f"\n" \
                            f"\nВыберите параметр для изменения ↓"
                    return msg

                def kb() -> InlineKeyboardMarkup:
                    config = Config.get()
                    playerokapi_requests_timeout = config["playerokapi_requests_timeout"] if config["playerokapi_requests_timeout"] else "❌ Не задано"
                    playerokapi_listener_requests_delay = config["playerokapi_listener_requests_delay"] if config["playerokapi_listener_requests_delay"] else "❌ Не задано"
                    btn1 = InlineKeyboardButton(
                        text=f"🛜 Таймаут подключения: {playerokapi_requests_timeout}",
                        callback_data="enter_playerokapi_requests_timeout"
                    )
                    btn2 = InlineKeyboardButton(
                        text=f"⏱️ Периодичность запросов: {playerokapi_listener_requests_delay}",
                        callback_data="enter_playerokapi_listener_requests_delay"
                    )
                    btn_update = InlineKeyboardButton(
                        text="🔄️ Обновить",
                        callback_data=CallbackDatas.BotSettingsNavigation(
                            to="connection"
                        ).pack()
                    )
                    btn_back = InlineKeyboardButton(
                        text="← Назад",
                        callback_data=CallbackDatas.BotSettingsNavigation(
                            to="default"
                        ).pack()
                    )
                    rows = [[btn1, btn2], [btn_update], [btn_back]]
                    markup = InlineKeyboardMarkup(inline_keyboard=rows)
                    return markup
            
            class EnterPlayerokApiRequestsTimeout:
                def text() -> str:
                    config = Config.get()
                    msg = f"🛜 <b>Введите новый таймаут подключения к playerok.com ↓</b>" \
                            f"\nТекущее значение: <code>{config['playerokapi_requests_timeout']}</code> сек."
                    return msg
                
            class PlayerokApiRequestsTimeoutChanged:
                def text(new):
                    msg = f"✅ <b>Таймаут подключения к playerok.com</b> был успешно изменён на <code>{new}</code> сек."
                    return msg
            
            class EnterPlayerokApiListenerRequestsDelay:
                def text() -> str:
                    config = Config.get()
                    msg = f"⏱️ <b>Введите новую периодичность запросов к playerok.com ↓</b>" \
                            f"\nТекущее значение: <code>{config['playerokapi_listener_requests_delay']}</code> сек."
                    return msg
                
            class PlayerokApiListenerRequestsDelayChanged:
                def text(new):
                    msg = f"✅ <b>Периодичность запросов к playerok.com</b> была успешно изменена на <code>{new}</code> сек."
                    return msg

        class Items:
            class Error:
                def text() -> str:
                    msg = f"⚙️ <b>Настройки бота → 📦 Предметы</b>"\
                            f"\n" \
                            f"\n→ Автоматическое восстановление предметов: <i>не удалось загрузить</i>" \
                            f"\n→ Статус приоритета для восстановленных предметов: <i>не удалось загрузить</i>" \
                            f"\n" \
                            f"\n<b>Что такое автоматическое восстановление предметов?</b>" \
                            f"\nКак только кто-то купит ваш предмет на Playerok, он сразу же пропадёт из активных " \
                            f"на сайте. Эта функция позволит автоматически \"поднимать на ноги\" предмет, который " \
                            f"только что купили, чтобы он снова был в продаваемых." \
                            f"\n" \
                            f"\n<b>Что такое cтатус приоритета для восстановленных предметов?</b>" \
                            f"\nС каким статусом будет выставлять на продажу предмет, который был автоматически восстановлен. " \
                            f"Учтите, что за премиум статус нужно платить, и если у вас не будет денег на балансе аккаунта для " \
                            f"этого, товар будет выставляен по бесплатному приоритету." \
                            f"\n" \
                            f"\nВыберите параметр для изменения ↓"
                    return msg

            class Loading:
                def text() -> str:
                    msg = f"⚙️ <b>Настройки бота → 📦 Предметы</b>"\
                            f"\n" \
                            f"\n→ Автоматическое восстановление лотов: <i>загрузка</i>" \
                            f"\n→ Статус приоритета для восстановленных предметов: <i>загрузка</i>" \
                            f"\n" \
                            f"\n<b>Что такое автоматическое восстановление предметов?</b>" \
                            f"\nКак только кто-то купит ваш предмет на Playerok, он сразу же пропадёт из активных " \
                            f"на сайте. Эта функция позволит автоматически \"поднимать на ноги\" предмет, который " \
                            f"только что купили, чтобы он снова был в продаваемых." \
                            f"\n" \
                            f"\n<b>Что такое cтатус приоритета для восстановленных предметов?</b>" \
                            f"\nС каким статусом будет выставлять на продажу предмет, который был автоматически восстановлен. " \
                            f"Учтите, что за премиум статус нужно платить, и если у вас не будет денег на балансе аккаунта для " \
                            f"этого, товар будет выставляен по бесплатному приоритету." \
                            f"\n" \
                            f"\nВыберите параметр для изменения ↓"
                    return msg

            class Default:
                def text() -> str:
                    config = Config.get()
                    auto_restore_items_enabled = "🟢 Включено" if config.get("auto_restore_items_enabled") == True else "🔴 Выключено"
                    if config.get("auto_restore_items_priority_status") == "DEFAULT": auto_restore_items_priority_status = "🆓 Бесплатный"
                    elif config.get("auto_restore_items_priority_status") == "PREMIUM": auto_restore_items_priority_status = "⚡ Премиум"
                    else: auto_restore_items_priority_status = "❌ Не задано"
                    msg = f"⚙️ <b>Настройки бота → 📦 Предметы</b>"\
                            f"\n" \
                            f"\n→ Автоматическое восстановление предметов: <code>{auto_restore_items_enabled}</code>" \
                            f"\n→ Статус приоритета для восстановленных предметов: <code>{auto_restore_items_priority_status}</code>" \
                            f"\n" \
                            f"\n<b>Что такое автоматическое восстановление предметов?</b>" \
                            f"\nКак только кто-то купит ваш предмет на Playerok, он сразу же пропадёт из активных " \
                            f"на сайте. Эта функция позволит автоматически \"поднимать на ноги\" предмет, который " \
                            f"только что купили, чтобы он снова был в продаваемых." \
                            f"\n" \
                            f"\n<b>Что такое cтатус приоритета для восстановленных предметов?</b>" \
                            f"\nС каким статусом будет выставлять на продажу предмет, который был автоматически восстановлен. " \
                            f"Учтите, что за премиум статус нужно платить, и если у вас не будет денег на балансе аккаунта для " \
                            f"этого, товар будет выставляен по бесплатному приоритету." \
                            f"\n" \
                            f"\nВыберите параметр для изменения ↓" 
                    return msg

                def kb() -> InlineKeyboardMarkup:
                    config = Config.get()
                    auto_restore_items_enabled = "🟢 Включено" if config["auto_restore_items_enabled"] == True else "🔴 Выключено"
                    if config.get("auto_restore_items_priority_status") == "DEFAULT": auto_restore_items_priority_status = "🆓 Бесплатный"
                    elif config.get("auto_restore_items_priority_status") == "PREMIUM": auto_restore_items_priority_status = "⚡ Премиум"
                    else: auto_restore_items_priority_status = "❌ Не задано"
                    btn1 = InlineKeyboardButton(
                        text=f"⬆️ Автовосстановление предметов: {auto_restore_items_enabled}",
                        callback_data="disable_auto_restore_items" if config.get("auto_restore_items_enabled") else "enable_auto_restore_items"
                    )
                    btn2 = InlineKeyboardButton(
                        text=f"⭐ Статус приоритета: {auto_restore_items_priority_status}",
                        callback_data="premium_auto_restore_items_priority_status" if config.get("auto_restore_items_priority_status") == "DEFAULT" else "default_auto_restore_items_priority_status"
                    )
                    btn_refresh = InlineKeyboardButton(
                        text="🔄️ Обновить",
                        callback_data=CallbackDatas.BotSettingsNavigation(
                            to="items"
                        ).pack()
                    )
                    btn_back = InlineKeyboardButton(
                        text="⬅️ Назад",
                        callback_data=CallbackDatas.BotSettingsNavigation(
                            to="default"
                        ).pack()
                    )
                    rows = [[btn1], [btn2], [btn_refresh], [btn_back]]
                    markup = InlineKeyboardMarkup(inline_keyboard=rows)
                    return markup
                
        class CustomCommands:
            class Pagination:
                def text() -> str:
                    custom_commands = CustomCommands.get()
                    msg = f"⚙️ <b>Настройки бота</b> → ⌨️ <b>Пользовательские команды</b>" \
                            f"\nВсего <b>{len(custom_commands.keys())}</b> пользовательских команд в конфиге" \
                            f"\n\nПеремещайтесь по разделам ниже. Нажмите на команду, чтобы перейти в её редактирование ↓"
                    return msg
                
                def kb(page: int = 0) -> InlineKeyboardMarkup:
                    custom_commands = CustomCommands.get()

                    rows = []
                    items_per_page = 7
                    total_pages = math.ceil(len(custom_commands.keys())/items_per_page)
                    total_pages = total_pages if total_pages > 0 else 1

                    if page < 0:
                        page = 0
                    elif page >= total_pages:
                        page = total_pages-1

                    start_offset = page * items_per_page
                    end_offset = start_offset + items_per_page

                    for command in list(custom_commands.keys())[start_offset:end_offset]:
                        command_text = "\n".join(custom_commands[command])
                        btn = InlineKeyboardButton(
                            text=f'{command} → {command_text}',
                            callback_data=CallbackDatas.CustomCommandPage(
                                command=command
                            ).pack()
                        )
                        rows.append([btn])
                        
                    buttons_row = []
                    if page > 0:
                        btn_back = InlineKeyboardButton(
                            text="←",
                            callback_data=CallbackDatas.CustomCommandsPagination(
                                page=page-1
                            ).pack()
                        )
                    else:
                        btn_back = InlineKeyboardButton(
                            text="🛑",
                            callback_data="123"
                        )
                    buttons_row.append(btn_back)
                        
                    btn_pages = InlineKeyboardButton(
                        text=f"{page+1}/{total_pages}",
                        callback_data="enter_custom_command_page"
                    )
                    buttons_row.append(btn_pages)
                    
                    if page < total_pages-1:
                        btn_next = InlineKeyboardButton(
                            text="→",
                            callback_data=CallbackDatas.CustomCommandsPagination(
                                page=page+1
                            ).pack()
                        )
                    else:
                        btn_next = InlineKeyboardButton(
                            text="🛑",
                            callback_data="123"
                        )
                    buttons_row.append(btn_next)
                    rows.append(buttons_row)

                    btn1 = InlineKeyboardButton(
                        text="➕⌨️ Добавить пользовательскую команду",
                        callback_data="enter_custom_command"
                    )
                    rows.append([btn1])
                    btn2 = InlineKeyboardButton(
                        text="🚪 Выход",
                        callback_data=CallbackDatas.BotSettingsNavigation(
                            to="default"
                        ).pack()
                    )
                    rows.append([btn2])
                    markup = InlineKeyboardMarkup(inline_keyboard=rows)
                    return markup
                
            class Page:
                class Error:
                    def text() -> str:
                        msg = f"✏️ <b>Редактирование пользовательской команды</b>" \
                            f"\n" \
                            f"\n→ Команда: <i>не удалось загрузить</i>" \
                            f"\n→ Ответ: <i>не удалось загрузить</i>" \
                            f"\n" \
                            f"\nВыберите параметр для изменения ↓"
                        return msg

                class Loading:
                    def text() -> str:
                        msg = f"✏️ <b>Редактирование пользовательской команды</b>" \
                            f"\n" \
                            f"\n→ Команда: <i>загрузка</i>" \
                            f"\n→ Ответ: <i>загрузка</i>" \
                            f"\n" \
                            f"\nВыберите параметр для изменения ↓"
                        return msg

                class Default:
                    def text(command: str) -> str:
                        custom_commands = CustomCommands.get()
                        command_text = "\n".join(custom_commands[command])
                        msg = f"✏️ <b>Редактирование пользовательской команды</b>" \
                            f"\n" \
                            f"\n→ Команда: <code>{command}</code>" \
                            f"\n→ Ответ: \n<blockquote>{command_text}</blockquote>" \
                            f"\n" \
                            f"\nВыберите параметр для изменения ↓"
                        return msg
                    
                    def kb(command, page) -> InlineKeyboardMarkup:
                        custom_commands = CustomCommands.get()
                        command_text = "\n".join(custom_commands[command]) if custom_commands[command] else "❌ Не задано"
                        btn1 = InlineKeyboardButton(
                            text=f"✍️ Текст ответа: {command_text}",
                            callback_data="enter_new_custom_command_answer"
                        )
                        btn2 = InlineKeyboardButton(
                            text="🗑️ Удалить команду",
                            callback_data="confirm_deleting_custom_command"
                        )
                        btn_refresh = InlineKeyboardButton(
                            text="🔄️ Обновить",
                            callback_data=CallbackDatas.CustomCommandPage(
                                command=command
                            ).pack()
                        )
                        btn_back = InlineKeyboardButton(
                            text="⬅️ Назад",
                            callback_data=CallbackDatas.CustomCommandsPagination(
                                page=page
                            ).pack()
                        )
                        rows = [[btn1, btn2], [btn_refresh], [btn_back]]
                        markup = InlineKeyboardMarkup(inline_keyboard=rows)
                        return markup
                
            class EnterCustomCommandsPage:
                def text() -> str:
                    msg = f"📃 Введите номер страницы для перехода ↓" 
                    return msg
                
            class EnterCustomCommand:
                def text() -> str:
                    msg = f"⌨️ <b>Введите название команды ↓</b>" \
                            f"\nТекст, который должен будет вводить покупатель, чтобы ему выдался ответ"
                    return msg
                
            class EnterCustomCommandAnswer:
                def text() -> str:
                    msg = f"✍️ <b>Введите ответ команды ↓</b>" \
                            f"\nТекст, который будет выдавать покупателю после ввода команды"
                    return msg
                
            class ConfirmAddingCustomCommand:
                def text(command, command_answer) -> str:
                    msg = f"➕⌨️ <b>Подтвердите добавление новой пользовательской команды</b>" \
                            f"\nКоманда: <code>{command}</code>" \
                            f"\nОтвет: <blockquote>{command_answer}</blockquote>"
                    return msg

                def kb() -> InlineKeyboardMarkup:
                    btn1 = InlineKeyboardButton(
                        text="✅ Подтвердить",
                        callback_data="add_custom_command"
                    )
                    btn2 = InlineKeyboardButton(
                        text="❌ Отменить",
                        callback_data="destroy"
                    )
                    rows = [[btn1, btn2]]
                    markup = InlineKeyboardMarkup(inline_keyboard=rows)
                    return markup
                
            class CustomCommandAdded:
                def text(command) -> str:
                    msg = f"✅ Пользовательская команда <code>{command}</code> <b>была успешно добавлена</b>" 
                    return msg
                
            class EnterNewCustomCommandAnswer:
                def text(command) -> str:
                    custom_commands = CustomCommands.get()
                    command_answer = "\n".join(custom_commands[command])
                    msg = f"✍️ <b>Введите новый текст ответа ↓</b>" \
                            f"\nКоманда: <code>{command}</code>" \
                            f"\nТекущий ответ: <blockquote>{command_answer}</blockquote>"
                    return msg
                
            class CustomCommandAnswerChanged:
                def text(new, command) -> str:
                    msg = f"✅ Текст ответа команды <code>{command}</code> <b>был успешно изменён</b> на:\n<blockquote>{new}</blockquote>" 
                    return msg
                
            class ConfirmDeletingCustomCommand:
                def text(command) -> str:
                    msg = f"🗑️ <b>Подтвердите удаление пользовательской команды</b>" \
                        f"\nЭто действие удалит пользовательскую команду <code>{command}</code>" 
                    return msg

                def kb() -> InlineKeyboardMarkup:
                    btn1 = InlineKeyboardButton(
                        text="✅ Подтвердить",
                        callback_data="delete_custom_command"
                    )
                    btn2 = InlineKeyboardButton(
                        text="❌ Отменить",
                        callback_data="destroy"
                    )
                    rows = [[btn1, btn2]]
                    markup = InlineKeyboardMarkup(inline_keyboard=rows)
                    return markup
                
            class CustomComandDeleted:
                def text(command) -> str:
                    msg = f"✅ Пользовательская команда <code>{command}</code> <b>была успешно удалена</b>" 
                    return msg
                
        class AutoDeliveries:
            class Pagination:
                def text() -> str:
                    auto_deliveries: list = AutoDeliveries.get()
                    msg = f"⚙️ <b>Настройки бота</b> → 🚀 <b>Автоматическая выдача</b>" \
                            f"\nВсего <b>{len(auto_deliveries)}</b> настроенных авто-выдач в конфиге" \
                            f"\n\nПеремещайтесь по разделам ниже. Нажмите на нужную авто-выдачу, чтобы перейти в её редактирование ↓"
                    return msg
                
                def kb(page: int = 0) -> InlineKeyboardMarkup:
                    auto_deliveries: list = AutoDeliveries.get()

                    rows = []
                    items_per_page = 7
                    total_pages = math.ceil(len(auto_deliveries)/items_per_page)
                    total_pages = total_pages if total_pages > 0 else 1

                    if page < 0:
                        page = 0
                    elif page >= total_pages:
                        page = total_pages-1

                    start_offset = page * items_per_page
                    end_offset = start_offset + items_per_page

                    for auto_delivery in list(auto_deliveries)[start_offset:end_offset]:
                        keywords = ", ".join(auto_delivery.get("keywords")) or "❌ Не задано"
                        message = "\n".join(auto_delivery.get("message")) or "❌ Не задано"
                        btn = InlineKeyboardButton(
                            text=f'{keywords[:32]} → {message}',
                            callback_data=CallbackDatas.AutoDeliveryPage(
                                index=auto_deliveries.index(auto_delivery)
                            ).pack()
                        )
                        rows.append([btn])
                        
                    buttons_row = []
                    if page > 0:
                        btn_back = InlineKeyboardButton(
                            text="←",
                            callback_data=CallbackDatas.AutoDeliveriesPagination(
                                page=page-1
                            ).pack()
                        )
                    else:
                        btn_back = InlineKeyboardButton(
                            text="🛑",
                            callback_data="123"
                        )
                    buttons_row.append(btn_back)
                        
                    btn_pages = InlineKeyboardButton(
                        text=f"{page+1}/{total_pages}",
                        callback_data="enter_auto_deliveries_page"
                    )
                    buttons_row.append(btn_pages)
                    
                    if page < total_pages-1:
                        btn_next = InlineKeyboardButton(
                            text="→",
                            callback_data=CallbackDatas.AutoDeliveriesPagination(
                                page=page+1
                            ).pack()
                        )
                    else:
                        btn_next = InlineKeyboardButton(
                            text="🛑",
                            callback_data="123"
                        )
                    buttons_row.append(btn_next)
                    rows.append(buttons_row)

                    btn1 = InlineKeyboardButton(
                        text="➕🚀 Добавить авто-выдачу",
                        callback_data="enter_auto_delivery_keywords"
                    )
                    rows.append([btn1])
                    btn_exit = InlineKeyboardButton(
                        text="🚪 Выход",
                        callback_data=CallbackDatas.BotSettingsNavigation(
                            to="default"
                        ).pack()
                    )
                    rows.append([btn_exit])
                    markup = InlineKeyboardMarkup(inline_keyboard=rows)
                    return markup
                    
            class Page:
                class Error:
                    def text() -> str:
                        msg = f"✏️ <b>Редактирование авто-выдачи</b>" \
                            f"\n" \
                            f"\n→ Ключевые слова: <i>не удалось загрузить</i>" \
                            f"\n→ Сообщение после покупки: <i>не удалось загрузить</i>" \
                            f"\n" \
                            f"\nВыберите параметр для изменения ↓"
                        return msg

                class Loading:
                    def text() -> str:
                        msg = f"✏️ <b>Редактирование авто-выдачи</b>" \
                            f"\n" \
                            f"\n→ Ключевые слова: <i>загрузка</i>" \
                            f"\n→ Сообщение после покупки: <i>загрузка</i>" \
                            f"\n" \
                            f"\nВыберите параметр для изменения ↓"
                        return msg

                class Default:
                    def text(index: int) -> str:
                        auto_deliveries = AutoDeliveries.get()
                        auto_delivery: dict = auto_deliveries[index]
                        keywords = "</code>, <code>".join(auto_delivery.get("keywords")) or "❌ Не задано"
                        message = "\n".join(auto_delivery.get("message")) or "❌ Не задано"

                        msg = f"✏️ <b>Редактирование авто-выдачи</b>" \
                            f"\n" \
                            f"\n→ Ключевые слова: \n<code>{keywords}</code>" \
                            f"\n→ Сообщение после покупки: \n<blockquote>{message}</blockquote>" \
                            f"\n" \
                            f"\nВыберите параметр для изменения ↓"
                        return msg
                    
                    def kb(index: int, page: int = 0) -> InlineKeyboardMarkup:
                        auto_deliveries = AutoDeliveries.get()
                        auto_delivery: dict = auto_deliveries[index]
                        keywords = ", ".join(auto_delivery.get("keywords")) or "❌ Не задано"
                        message = "\n".join(auto_delivery.get("message")) or "❌ Не задано"

                        btn1 = InlineKeyboardButton(
                            text=f"🔑 Ключевые слова: {keywords}",
                            callback_data="enter_new_auto_delivery_keywords"
                        )
                        btn2 = InlineKeyboardButton(
                            text=f"✍️ Сообщение после покупки: {message}",
                            callback_data="enter_new_auto_delivery_message"
                        )
                        btn3 = InlineKeyboardButton(
                            text="🗑️ Удалить авто-выдачу",
                            callback_data="confirm_deleting_auto_delivery"
                        )
                        btn_refresh = InlineKeyboardButton(
                            text="🔄️ Обновить",
                            callback_data=CallbackDatas.AutoDeliveryPage(
                                index=index
                            ).pack()
                        )
                        btn_back = InlineKeyboardButton(
                            text="⬅️ Назад",
                            callback_data=CallbackDatas.AutoDeliveriesPagination(
                                page=page
                            ).pack()
                        )
                        rows = [[btn1], [btn2], [btn3], [btn_refresh], [btn_back]]
                        markup = InlineKeyboardMarkup(inline_keyboard=rows)
                        return markup
                
            class EnterAutoDeliveryPage:
                def text() -> str:
                    msg = f"📃 Введите номер страницы для перехода ↓" 
                    return msg
                
            class EnterAutoDeliveryKeywords:
                def text() -> str:
                    msg = f"🔑 <b>Введите ключевые слова названия предмета авто-выдачи ↓</b>" \
                            f"\nВводятся через запятую" \
                            f"\nАвтовыдача привяжется ко всем предметам, в названии которых будут указанные вами ключевые слова"
                    return msg
                
            class EnterAutoDeliveryMessage:
                def text() -> str:
                    msg = f"✉️ <b>Введите сообщение после покупки ↓</b>" \
                            f"\nТекст, который будет выдавать покупателю после покупки этого предмета"
                    return msg
                
            class ConfirmAddingAutoDelivery:
                def text(keywords, message) -> str:
                    keywords = ", ".join(keywords)
                    msg = f"➕🚀 <b>Подтвердите добавление новой авто-выдачи</b>" \
                            f"\nКлючевые слова: <code>{keywords}</code>" \
                            f"\nСообщение после покупки: <blockquote>{message}</blockquote>"
                    return msg

                def kb() -> InlineKeyboardMarkup:
                    btn1 = InlineKeyboardButton(
                        text="✅ Подтвердить",
                        callback_data="add_auto_delivery"
                    )
                    btn2 = InlineKeyboardButton(
                        text="❌ Отменить",
                        callback_data="destroy"
                    )
                    rows = [[btn1, btn2]]
                    markup = InlineKeyboardMarkup(inline_keyboard=rows)
                    return markup
                
            class AutoDeliveryAdded:
                def text(keywords) -> str:
                    keywords = ", ".join(keywords)
                    msg = f"✅ Авто-выдача с ключевыми словами <code>{keywords}</code> <b>была успешно добавлена</b>" 
                    return msg
                
            class EnterNewAutoDeliveryKeywords:
                def text(index: int) -> str:
                    auto_deliveries = AutoDeliveries.get()
                    keywords = ", ".join(auto_deliveries[index].get("keywords")) or "❌ Не задано"
                    msg = f"🔑 <b>Введите новые ключевые слова названия предмета ↓</b>" \
                            f"\nВводить нужно через запятую" \
                            f"\nТекущее значение: <code>{keywords}</code>"
                    return msg
                
            class AutoDeliveryKeywordsChanged:
                def text(new) -> str:
                    msg = f"✅ Ключевые слова авто-выдачи <b>были успешно изменены</b> на:\n<code>{new}</code>" 
                    return msg
                
            class EnterNewAutoDeliveryMessage:
                def text(index: int) -> str:
                    auto_deliveries = AutoDeliveries.get()
                    message = "\n".join(auto_deliveries[index].get("message")) or "❌ Не задано"
                    msg = f"✍️ <b>Введите новое сообщение после покупки ↓</b>" \
                            f"\nТекущее сообщение: <blockquote>{message}</blockquote>"
                    return msg
                
            class AutoDeliveryMessageChanged:
                def text(new) -> str:
                    msg = f"✅ Сообщение после покупки <b>было успешно изменено</b> на:\n<blockquote>{new}</blockquote>" 
                    return msg
                
            class ConfirmDeletingAutoDelivery:
                def text(index: int) -> str:
                    auto_deliveries = AutoDeliveries.get()
                    keywords = auto_deliveries[index].get("keywords") or "❌ Не задано"
                    msg = f"🗑️ <b>Подтвердите удаление авто-выдачи</b>" \
                            f"\nЭто действие удалит авто-выдачу для ключевых слов:\n<code>{keywords}</code>" 
                    return msg

                def kb() -> InlineKeyboardMarkup:
                    btn1 = InlineKeyboardButton(
                        text="✅ Подтвердить",
                        callback_data="delete_auto_delivery"
                    )
                    btn2 = InlineKeyboardButton(
                        text="❌ Отменить",
                        callback_data="destroy"
                    )
                    rows = [[btn1, btn2]]
                    markup = InlineKeyboardMarkup(inline_keyboard=rows)
                    return markup
                
            class AutoDeliveryDeleted:
                def text(index: int) -> str:
                    auto_deliveries = AutoDeliveries.get()
                    keywords = auto_deliveries[index].get("keywords") or "❌ Не задано"
                    msg = f"✅ Авто-выдача для ключевых слов <code>{keywords}</code> <b>была успешно удалена</b>" 
                    return msg
            
        class Messages:
            class Pagination:
                def text() -> str:
                    messages = Messages.get()
                    if not messages:
                        raise Exception("В конфиге нет ни одного сообщения")
                    msg = f"⚙️ <b>Настройки бота</b> → ✉️ <b>Сообщения</b>" \
                            f"\nВсего <b>{len(messages.keys())}</b> настраиваемых сообщений в конфиге" \
                            f"\n\nПеремещайтесь по разделам ниже. Нажмите на сообщение, чтобы перейти в его редактирование ↓"
                    return msg
                
                def kb(page: int = 0) -> InlineKeyboardMarkup:
                    messages = Messages.get()
                    if not messages:
                        raise Exception("В конфиге нет ни одного сообщения")

                    rows = []
                    items_per_page = 8
                    total_pages = math.ceil(len(messages.keys())/items_per_page)
                    total_pages = total_pages if total_pages > 0 else 1

                    if page < 0:
                        page = 0
                    elif page >= total_pages:
                        page = total_pages-1

                    start_offset = page * items_per_page
                    end_offset = start_offset + items_per_page

                    for message_id in list(messages.keys())[start_offset:end_offset]:
                        btn = InlineKeyboardButton(
                            text=message_id,
                            callback_data=CallbackDatas.MessagePage(
                                message_id=message_id
                            ).pack()
                        )
                        rows.append([btn])
                        
                    buttons_row = []
                    if page > 0:
                        btn_back = InlineKeyboardButton(
                            text="←",
                            callback_data=CallbackDatas.MessagesPagination(
                                page=page-1
                            ).pack()
                        )
                    else:
                        btn_back = InlineKeyboardButton(
                            text="🛑",
                            callback_data="123"
                        )
                    buttons_row.append(btn_back)

                        
                    btn_pages = InlineKeyboardButton(
                        text=f"{page+1}/{total_pages}",
                        callback_data="enter_messages_page"
                    )
                    buttons_row.append(btn_pages)
                    
                    if page < total_pages-1:
                        btn_next = InlineKeyboardButton(
                            text="→",
                            callback_data=CallbackDatas.MessagesPagination(
                                page=page+1
                            ).pack()
                        )
                    else:
                        btn_next = InlineKeyboardButton(
                            text="🛑",
                            callback_data="123"
                        )
                    buttons_row.append(btn_next)
                    rows.append(buttons_row)

                    btn1 = InlineKeyboardButton(
                        text="🚪 Выход",
                        callback_data=CallbackDatas.BotSettingsNavigation(
                            to="default"
                        ).pack()
                    )
                    rows.append([btn1])
                    markup = InlineKeyboardMarkup(inline_keyboard=rows)
                    return markup
                
            class Page:
                class Error:
                    def text() -> str:
                        msg = f"✒️ <b>Редактирование сообщения</b>" \
                            f"\n" \
                            f"\n→ ID сообщения: <i>не удалось загрузить</i>" \
                            f"\n→ Текст сообщения: <i>не удалось загрузить</i>" \
                            f"\n" \
                            f"\nВыберите параметр для изменения ↓"
                        return msg

                class Loading:
                    def text() -> str:
                        msg = f"✒️ <b>Редактирование сообщения</b>" \
                            f"\n" \
                            f"\n→ ID сообщения: <i>загрузка</i>" \
                            f"\n→ Текст сообщения: <i>загрузка</i>" \
                            f"\n" \
                            f"\nВыберите параметр для изменения ↓"
                        return msg

                class Default:
                    def text(message_id) -> str:
                        messages = Messages.get()
                        message_text = "\n".join(messages[message_id]) if messages[message_id] else "❌ Не задано"
                        msg = f"✒️ <b>Редактирование сообщения</b>" \
                            f"\n" \
                            f"\n→ ID сообщения: <code>{message_id}</code>" \
                            f"\n→ Текст сообщения: \n<blockquote>{message_text}</blockquote>" \
                            f"\n" \
                            f"\nВыберите параметр для изменения ↓"
                        return msg
                    
                    def kb(message_id, page) -> InlineKeyboardMarkup:
                        messages = Messages.get()
                        message_text = "\n".join(messages[message_id]) if messages[message_id] else "❌ Не задано"
                        btn1 = InlineKeyboardButton(
                            text=f"✍️ Текст сообщения: {message_text}",
                            callback_data="enter_message_text"
                        )
                        btn_refresh = InlineKeyboardButton(
                            text="🔄️ Обновить",
                            callback_data=CallbackDatas.MessagePage(
                                message_id=message_id
                            ).pack()
                        )
                        btn_back = InlineKeyboardButton(
                            text="⬅️ Назад",
                            callback_data=CallbackDatas.MessagesPagination(
                                page=page
                            ).pack()
                        )
                        rows = [[btn1], [btn_refresh], [btn_back]]
                        markup = InlineKeyboardMarkup(inline_keyboard=rows)
                        return markup
                
            class EnterMessagesPage:
                def text() -> str:
                    msg = f"📃 Введите номер страницы для перехода ↓" 
                    return msg
                
            class EnterMessageText:
                def text(message_id) -> str:
                    messages = Messages.get()
                    message_text = "\n".join(messages[message_id]) if messages[message_id] else "❌ Не задано"
                    msg = f"✍️ <b>Введите новый текст сообщения ↓</b>" \
                            f"\nID сообщения: \n<code>{message_id}</code>" \
                            f"\nТекущий текст: \n<blockquote>{message_text}</blockquote>"
                    return msg
                
            class MessageTextChanged:
                def text(new, message_id) -> str:
                    msg = f"✅ Текст сообщения <code>{message_id}</code> <b>был успешно изменён</b> на:\n<blockquote>{new}</blockquote>" 
                    return msg
                
        class Other:
            class Error:
                def text() -> str:
                    msg = f"⚙️ <b>Настройки бота → 🔧 Прочее</b>" \
                            f"\n" \
                            f"\n→ Читать чат перед отправкой сообщения: <i>не удалось загрузить</i>" \
                            f"\n→ Автоподтверждение выполнения заказов: <i>не удалось загрузить</i>" \
                            f"\n→ Приветственное сообщение: <i>не удалось загрузить</i>" \
                            f"\n→ Пользовательские команды: <i>не удалось загрузить</i>" \
                            f"\n→ Автоматическая выдача: <i>не удалось загрузить</i>" \
                            f"\n" \
                            f"\n→ Водяной знак под сообщениями: <i>не удалось загрузить</i>" \
                            f"\n→ Водяной знак: <i>не удалось загрузить</i>" \
                            f"\n" \
                            f"\nВыберите параметр для изменения ↓" 
                    return msg

            class Loading:
                def text() -> str:
                    msg = f"⚙️ <b>Настройки бота → 🔧 Прочее</b>" \
                            f"\n" \
                            f"\n→ Читать чат перед отправкой сообщения: <i>загрузка</i>" \
                            f"\n→ Автоподтверждение выполнения заказов: <i>загрузка</i>" \
                            f"\n→ Приветственное сообщение: <i>загрузка</i>" \
                            f"\n→ Пользовательские команды: <i>загрузка</i>" \
                            f"\n→ Автоматическая выдача: <i>загрузка</i>" \
                            f"\n" \
                            f"\n→ Водяной знак под сообщениями: <i>загрузка</i>" \
                            f"\n→ Водяной знак: <i>загрузка</i>" \
                            f"\n" \
                            f"\nВыберите параметр для изменения ↓" 
                    return msg

            class Default:
                def text() -> str:
                    config = Config.get()
                    read_chat_before_sending_message_enabled = "🟢 Включено" if config["read_chat_before_sending_message_enabled"] else "🔴 Выключено"
                    auto_complete_deals_enabled = "🟢 Включено" if config["auto_complete_deals_enabled"] else "🔴 Выключено"
                    first_message_enabled = "🟢 Включено" if config["first_message_enabled"] else "🔴 Выключено"
                    custom_commands_enabled = "🟢 Включено" if config["custom_commands_enabled"] else "🔴 Выключено"
                    auto_deliveries_enabled = "🟢 Включено" if config["auto_deliveries_enabled"] else "🔴 Выключено"
                    messages_watermark_enabled = "🟢 Включено" if config["messages_watermark_enabled"] else "🔴 Выключено"
                    messages_watermark = config["messages_watermark"] if config["messages_watermark"] else "❌ Не задано"
                    msg = f"⚙️ <b>Настройки бота → 🔧 Прочее</b>" \
                            f"\n" \
                            f"\n→ Читать чат перед отправкой сообщения: <code>{read_chat_before_sending_message_enabled}</code>" \
                            f"\n→ Автоподтверждение выполнения заказов: <code>{auto_complete_deals_enabled}</code>" \
                            f"\n→ Приветственное сообщение: <code>{first_message_enabled}</code>" \
                            f"\n→ Пользовательские команды: <code>{custom_commands_enabled}</code>" \
                            f"\n→ Автоматическая выдача: <code>{auto_deliveries_enabled}</code>" \
                            f"\n" \
                            f"\n→ Водяной знак под сообщениями: <code>{messages_watermark_enabled}</code>" \
                            f"\n→ Водяной знак: <code>{messages_watermark}</code>" \
                            f"\n" \
                            f"\nВыберите параметр для изменения ↓" 
                    return msg
                
                def kb() -> InlineKeyboardMarkup:
                    config = Config.get()
                    read_chat_before_sending_message_enabled = "🟢 Включено" if config["read_chat_before_sending_message_enabled"] else "🔴 Выключено"
                    auto_complete_deals_enabled = "🟢 Включено" if config["auto_complete_deals_enabled"] else "🔴 Выключено"
                    first_message_enabled = "🟢 Включено" if config["first_message_enabled"] else "🔴 Выключено"
                    custom_commands_enabled = "🟢 Включено" if config["custom_commands_enabled"] else "🔴 Выключено"
                    auto_deliveries_enabled = "🟢 Включено" if config["auto_deliveries_enabled"] else "🔴 Выключено"
                    messages_watermark_enabled = "🟢 Включено" if config["messages_watermark_enabled"] else "🔴 Выключено"
                    messages_watermark = config["messages_watermark"] if config["messages_watermark"] else "❌ Не задано"
                    btn1 = InlineKeyboardButton(
                        text=f"👀 Читать чат перед отправкой: {read_chat_before_sending_message_enabled}",
                        callback_data="disable_read_chat_before_sending_message" if config["read_chat_before_sending_message_enabled"] else "enable_read_chat_before_sending_message"
                    )
                    btn2 = InlineKeyboardButton(
                        text=f"☑️ Автоподтверждение выполнения заказов: {auto_complete_deals_enabled}",
                        callback_data="disable_auto_complete_deals" if config["auto_complete_deals_enabled"] else "enable_auto_complete_deals"
                    )
                    btn3 = InlineKeyboardButton(
                        text=f"👋 Приветственное сообщение: {first_message_enabled}",
                        callback_data="disable_first_message" if config["first_message_enabled"] else "enable_first_message"
                    )
                    btn4 = InlineKeyboardButton(
                        text=f"🔧 Пользовательские команды: {custom_commands_enabled}",
                        callback_data="disable_custom_commands" if config["custom_commands_enabled"] else "enable_custom_commands"
                    )
                    btn5 = InlineKeyboardButton(
                        text=f"🚀 Автоматическая выдача: {auto_deliveries_enabled}",
                        callback_data="disable_auto_delivery" if config["auto_deliveries_enabled"] else "enable_auto_delivery"
                    )
                    btn6 = InlineKeyboardButton(
                        text=f"©️ Водяной знак под сообщениями: {messages_watermark_enabled}",
                        callback_data="disable_messages_watermark" if config["messages_watermark_enabled"] else "enable_messages_watermark"
                    )
                    btn7 = InlineKeyboardButton(
                        text=f"✍️©️ Водяной знак: {messages_watermark}",
                        callback_data="enter_messages_watermark"
                    )
                    btn_refresh = InlineKeyboardButton(
                        text="🔄️ Обновить",
                        callback_data=CallbackDatas.BotSettingsNavigation(
                            to="other"
                        ).pack()
                    )
                    btn_back = InlineKeyboardButton(
                        text="⬅️ Назад",
                        callback_data=CallbackDatas.BotSettingsNavigation(
                            to="default"
                        ).pack()
                    )
                    rows = [[btn1], [btn2], [btn3], [btn4], [btn5], [btn6], [btn7], [btn_refresh], [btn_back]]
                    markup = InlineKeyboardMarkup(inline_keyboard=rows)
                    return markup

            class EnterMessagesWatermark:
                def text() -> str:
                    msg = f"✍️©️ <b>Введите новый водянок знак под сообщениями ↓</b>" \
                          f"\nЭтот водяной знак будет под каждым сообщением, отправленным ботом"
                    return msg

            class MessagesWatermarkChanged:
                def text(new) -> str:
                    msg = f"✅ Водяной знак под сообщениями <b>был успешно изменён</b> на <code>{new}</code>"
                    return msg
            
    class Modules:
        class Pagination:
            def text() -> str:
                modules = ModulesManager.get_modules()
                msg = f"🔌 <b>Модули</b>" \
                        f"\nВсего <b>{len(modules)}</b> загруженных модулей" \
                        f"\n\nПеремещайтесь по разделам ниже. Нажмите на название модуля, чтобы перейти в его управление ↓"
                return msg
            
            def kb(page: int = 0) -> InlineKeyboardMarkup:
                modules = ModulesManager.get_modules()

                rows = []
                items_per_page = 7
                total_pages = math.ceil(len(modules)/items_per_page)
                total_pages = total_pages if total_pages > 0 else 1

                if page < 0:
                    page = 0
                elif page >= total_pages:
                    page = total_pages-1

                start_offset = page * items_per_page
                end_offset = start_offset + items_per_page

                for module in list(modules)[start_offset:end_offset]:
                    btn = InlineKeyboardButton(
                        text=module.meta.name,
                        callback_data=CallbackDatas.ModulePage(
                            uuid=module.uuid
                        ).pack()
                    )
                    rows.append([btn])
                    
                buttons_row = []
                if page > 0:
                    btn_back = InlineKeyboardButton(
                        text="←",
                        callback_data=CallbackDatas.ModulesPagination(
                            page=page-1
                        ).pack()
                    )
                else:
                    btn_back = InlineKeyboardButton(
                        text="🛑",
                        callback_data="123"
                    )
                buttons_row.append(btn_back)
                    
                btn_pages = InlineKeyboardButton(
                    text=f"{page+1}/{total_pages}",
                    callback_data="enter_modules_page"
                )
                buttons_row.append(btn_pages)
                
                if page < total_pages-1:
                    btn_next = InlineKeyboardButton(
                        text="→",
                        callback_data=CallbackDatas.ModulesPagination(
                            page=page+1
                        ).pack()
                    )
                else:
                    btn_next = InlineKeyboardButton(
                        text="🛑",
                        callback_data="123"
                    )
                buttons_row.append(btn_next)
                rows.append(buttons_row)

                btn2 = InlineKeyboardButton(
                    text="🚪 Выход",
                    callback_data=CallbackDatas.MenuNavigation(
                        to="default"
                    ).pack()
                )
                rows.append([btn2])
                markup = InlineKeyboardMarkup(inline_keyboard=rows)
                return markup
            
        class Page:
            class Error:
                def text() -> str:
                    msg = f"🔧 <b>Управление модулем</b>" \
                        f"\n" \
                        f"\n→ Состояние: <i>не удалось загрузить</i>" \
                        f"\n" \
                        f"\n→ UUID: <i>не удалось загрузить</i>" \
                        f"\n→ Название: <i>не удалось загрузить</i>" \
                        f"\n→ Версия: <i>не удалось загрузить</i>" \
                        f"\n→ Описание: <i>не удалось загрузить</i>" \
                        f"\n" \
                        f"\n→ Авторы: <i>не удалось загрузить</i>" \
                        f"\n→ Ссылки: <i>не удалось загрузить</i>" \
                        f"\n" \
                        f"\nВыберите действие для управвления ↓"
                    return msg

            class Loading:
                def text() -> str:
                    msg = f"🔧 <b>Управлением модулем</b>" \
                        f"\n" \
                        f"\n→ Состояние: <i>загрузка</i>" \
                        f"\n" \
                        f"\n→ UUID: <i>загрузка</i>" \
                        f"\n→ Название: <i>загрузка</i>" \
                        f"\n→ Версия: <i>загрузка</i>" \
                        f"\n→ Описание: <i>загрузка</i>" \
                        f"\n" \
                        f"\n→ Авторы: <i>загрузка</i>" \
                        f"\n→ Ссылки: <i>загрузка</i>" \
                        f"\n" \
                        f"\nВыберите действие для управвления ↓"
                    return msg

            class Default:
                def text(module_uuid: UUID) -> str:
                    module: Module = ModulesManager.get_module_by_uuid(module_uuid)
                    if not module:
                        raise Exception("Не удалось найти модуль")
                    
                    enabled = "🟢 Включен" if module.enabled else "🔴 Выключен"
                    msg = f"🔧 <b>Управлением модулем</b>" \
                        f"\n" \
                        f"\n→ Состояние: <code>{enabled}</code>" \
                        f"\n" \
                        f"\n→ UUID: <code>{module.uuid}</code>" \
                        f"\n→ Название: <code>{module.meta.name}</code>" \
                        f"\n→ Версия: <code>{module.meta.version}</code>" \
                        f"\n→ Описание: <blockquote>{module.meta.description}</blockquote>" \
                        f"\n" \
                        f"\n→ Авторы: <code>{module.meta.authors}</code>" \
                        f"\n→ Ссылки: <code>{module.meta.links}</code>" \
                        f"\n" \
                        f"\nВыберите действие для управвления ↓"
                    return msg
                
                def kb(module_uuid: UUID, page: int) -> InlineKeyboardMarkup:
                    module: Module = ModulesManager.get_module_by_uuid(module_uuid)
                    if not module:
                        raise Exception("Не удалось найти модуль")
                    
                    rows = []
                    if module.enabled:
                        btn_disable = InlineKeyboardButton(
                            text="🔴 Отключить модуль",
                            callback_data="disable_module"
                        )
                        rows.append([btn_disable])
                    else:
                        btn_enable = InlineKeyboardButton(
                            text="🟢 Подключить модуль",
                            callback_data="enable_module"
                        )
                        rows.append([btn_enable])
                    btn_refresh = InlineKeyboardButton(
                        text="🔄️ Обновить",
                        callback_data=CallbackDatas.ModulePage(
                            uuid=module_uuid
                        ).pack()
                    )
                    rows.append([btn_refresh])
                    btn_back = InlineKeyboardButton(
                        text="⬅️ Назад",
                        callback_data=CallbackDatas.ModulesPagination(
                            page=page
                        ).pack()
                    )
                    rows.append([btn_back])
                    markup = InlineKeyboardMarkup(inline_keyboard=rows)
                    return markup
              
class Callbacks:
    class CallSeller:
        def text(calling_name, chat_link) -> str:
            msg = f"🆘 <b>{calling_name}</b> требуется ваша помощь!" \
                  f"\n{chat_link}"
            return msg