import asyncio
import traceback
from colorama import Fore, init as init_colorama
from logging import getLogger

from __init__ import ACCENT_COLOR, VERSION
from settings import Settings as sett
from core.utils import (
    set_title, 
    setup_logger, 
    install_requirements, 
    patch_requests, 
    init_main_loop, 
    run_async_in_thread,
    is_token_valid,
    is_pl_account_working,
    is_pl_account_banned,
    is_user_agent_valid,
    is_proxy_valid,
    is_proxy_working,
    is_tg_token_valid,
    is_tg_bot_exists,
    is_password_valid
)
from core.modules import (
    load_modules, 
    set_modules, 
    connect_modules
)
from core.handlers import call_bot_event
from updater import check_for_updates


logger = getLogger("universal")

try:
    main_loop = asyncio.get_running_loop()
except RuntimeError:
    main_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(main_loop)

init_colorama()
init_main_loop(main_loop)


async def start_telegram_bot():
    from tgbot.telegrambot import TelegramBot
    run_async_in_thread(TelegramBot().run_bot)


async def start_playerok_bot():
    from plbot.playerokbot import PlayerokBot
    await PlayerokBot().run_bot()


def check_and_configure_config():
    config = sett.get("config")
    
    while not config["playerok"]["api"]["token"]:
        while not config["playerok"]["api"]["token"]:
            print(
                f"\n{Fore.WHITE}Введите {Fore.LIGHTBLUE_EX}токен {Fore.WHITE}вашего Playerok аккаунта. Его можно узнать из Cookie-данных, воспользуйтесь расширением Cookie-Editor."
                f"\n  {Fore.WHITE}· Пример: eyJhbGciOiJIUzI1NiIsInR5cCI1IkpXVCJ9.eyJzdWIiOiIxZWUxMzg0Ni..."
            )
            token = input(f"  {Fore.WHITE}↳ {Fore.LIGHTWHITE_EX}").strip()
            if is_token_valid(token):
                config["playerok"]["api"]["token"] = token
                sett.set("config", config)
                print(f"\n{Fore.GREEN}Токен успешно сохранён в конфиг.")
            else:
                print(f"\n{Fore.LIGHTRED_EX}Похоже, что вы ввели некорректный токен. Убедитесь, что он соответствует формату и попробуйте ещё раз.")

        while not config["playerok"]["api"]["user_agent"]:
            print(
                f"\n{Fore.WHITE}Введите {Fore.LIGHTMAGENTA_EX}User Agent {Fore.WHITE}вашего браузера. Его можно скопировать на сайте {Fore.LIGHTWHITE_EX}https://whatmyuseragent.com. Или вы можете пропустить этот параметр, нажав Enter."
                f"\n  {Fore.WHITE}· Пример: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
            )
            user_agent = input(f"  {Fore.WHITE}↳ {Fore.LIGHTWHITE_EX}").strip()
            if not user_agent:
                print(f"\n{Fore.YELLOW}Вы пропустили ввод User Agent. Учтите, что в таком случае бот может работать нестабильно.")
                break
            if is_user_agent_valid(user_agent):
                config["playerok"]["api"]["user_agent"] = user_agent
                sett.set("config", config)
                print(f"\n{Fore.GREEN}User Agent успешно сохранён в конфиг.")
            else:
                print(f"\n{Fore.LIGHTRED_EX}Похоже, что вы ввели некорректный User Agent. Убедитесь, что в нём нет русских символов и попробуйте ещё раз.")
        
        while not config["playerok"]["api"]["proxy"]:
            print(
                f"\n{Fore.WHITE}Введите {Fore.LIGHTBLUE_EX}IPv4 Прокси {Fore.WHITE}в формате user:password@ip:port или ip:port, если он без авторизации. Если вы не знаете что это, или не хотите устанавливать прокси - пропустите этот параметр, нажав Enter."
                f"\n  {Fore.WHITE}· Пример: DRjcQTm3Yc:m8GnUN8Q9L@46.161.30.187:8000"
            )
            proxy = input(f"  {Fore.WHITE}↳ {Fore.LIGHTWHITE_EX}").strip()
            if not proxy:
                print(f"\n{Fore.WHITE}Вы пропустили ввод прокси.")
                break
            if is_proxy_valid(proxy):
                config["playerok"]["api"]["proxy"] = proxy
                sett.set("config", config)
                print(f"\n{Fore.GREEN}Прокси успешно сохранён в конфиг.")
            else:
                print(f"\n{Fore.LIGHTRED_EX}Похоже, что вы ввели некорректный Прокси. Убедитесь, что он соответствует формату и попробуйте ещё раз.")

    while not config["telegram"]["api"]["token"]:
        print(
            f"\n{Fore.WHITE}Введите {Fore.CYAN}токен вашего Telegram бота{Fore.WHITE}. Бота нужно создать у @BotFather."
            f"\n  {Fore.WHITE}· Пример: 7257913369:AAG2KjLL3-zvvfSQFSVhaTb4w7tR2iXsJXM"
        )
        token = input(f"  {Fore.WHITE}↳ {Fore.LIGHTWHITE_EX}").strip()
        if is_tg_token_valid(token):
            config["telegram"]["api"]["token"] = token
            sett.set("config", config)
            print(f"\n{Fore.GREEN}Токен Telegram бота успешно сохранён в конфиг.")
        else:
            print(f"\n{Fore.LIGHTRED_EX}Похоже, что вы ввели некорректный токен. Убедитесь, что он соответствует формату и попробуйте ещё раз.")

    while not config["telegram"]["bot"]["password"]:
        print(
            f"\n{Fore.WHITE}Придумайте и введите {Fore.YELLOW}пароль для вашего Telegram бота{Fore.WHITE}. Бот будет запрашивать этот пароль при каждой новой попытке взаимодействия чужого пользователя с вашим Telegram ботом."
            f"\n  {Fore.WHITE}· Пароль должен быть сложным, длиной не менее 6 и не более 64 символов."
        )
        password = input(f"  {Fore.WHITE}↳ {Fore.LIGHTWHITE_EX}").strip()
        if is_password_valid(password):
            config["telegram"]["bot"]["password"] = password
            sett.set("config", config)
            print(f"\n{Fore.GREEN}Пароль успешно сохранён в конфиг.")
        else:
            print(f"\n{Fore.LIGHTRED_EX}Ваш пароль не подходит. Убедитесь, что он соответствует формату и не является лёгким и попробуйте ещё раз.")

    if config["playerok"]["api"]["proxy"] and not is_proxy_working(config["playerok"]["api"]["proxy"]):
        print(f"\n{Fore.LIGHTRED_EX}Похоже, что указанный вами прокси не работает. Пожалуйста, проверьте его и введите снова.")
        config["playerok"]["api"]["token"] = ""
        config["playerok"]["api"]["user_agent"] = ""
        config["playerok"]["api"]["proxy"] = ""
        sett.set("config", config)
        return check_and_configure_config()
    elif config["playerok"]["api"]["proxy"]:
        logger.info(f"{Fore.WHITE}Прокси успешно работает.")

    if not is_pl_account_working():
        print(f"\n{Fore.LIGHTRED_EX}Не удалось подключиться к вашему Playerok аккаунту. Пожалуйста, убедитесь, что у вас указан верный токен и введите его снова.")
        config["playerok"]["api"]["token"] = ""
        config["playerok"]["api"]["user_agent"] = ""
        config["playerok"]["api"]["proxy"] = ""
        sett.set("config", config)
        return check_and_configure_config()
    else:
        logger.info(f"{Fore.WHITE}Playerok аккаунт успешно авторизован.")

    if is_pl_account_banned():
        print(f"{Fore.LIGHTRED_EX}\nВаш Playerok аккаунт забанен! Увы, я не могу запустить бота на заблокированном аккаунте...")
        config["playerok"]["api"]["token"] = ""
        config["playerok"]["api"]["user_agent"] = ""
        config["playerok"]["api"]["proxy"] = ""
        sett.set("config", config)
        return check_and_configure_config()

    if not is_tg_bot_exists():
        print(f"\n{Fore.LIGHTRED_EX}Не удалось подключиться к вашему Telegram боту. Пожалуйста, убедитесь, что у вас указан верный токен и введите его снова.")
        config["telegram"]["api"]["token"] = ""
        sett.set("config", config)
        return check_and_configure_config()
    else:
        logger.info(f"{Fore.WHITE}Telegram бот успешно работает.")


if __name__ == "__main__":
    try:
        install_requirements("requirements.txt") # установка недостающих зависимостей, если таковые есть
        patch_requests()
        setup_logger()
        
        set_title(f"Playerok Universal v{VERSION} by @alleexxeeyy")
        print(
            f"\n\n"
            f"\n   {ACCENT_COLOR}Playerok Universal {Fore.WHITE}v{Fore.LIGHTWHITE_EX}{VERSION}"
            f"\n"
            f"\n   {Fore.YELLOW}Наши ссылки:"
            f"\n   {Fore.WHITE}· TG бот: {Fore.LIGHTWHITE_EX}https://t.me/alexey_production_bot"
            f"\n   {Fore.WHITE}· TG канал: {Fore.LIGHTWHITE_EX}https://t.me/alexeyproduction"
            f"\n   {Fore.WHITE}· GitHub: {Fore.LIGHTWHITE_EX}https://github.com/alleexxeeyy/playerok-universal"
            f"\n\n\n"
        )
        
        check_for_updates()
        check_and_configure_config()

        modules = load_modules()
        set_modules(modules)
        asyncio.run(connect_modules(modules))

        main_loop.run_until_complete(start_telegram_bot())
        main_loop.run_until_complete(start_playerok_bot())

        asyncio.run(call_bot_event("ON_INIT"))
        
        main_loop.run_forever()
    except Exception as e:
        traceback.print_exc()
        print(
            f"\n{Fore.LIGHTRED_EX}Ваш бот словил непредвиденную ошибку и был выключен."
            f"\n\n{Fore.WHITE}Пожалуйста, попробуйте найти свою проблему в нашей статье, в которой собраны все самые частые ошибки.",
            f"\nСтатья: {Fore.LIGHTWHITE_EX}https://telegra.ph/FunPay-Universal--chastye-oshibki-i-ih-resheniya-08-26 {Fore.WHITE}(CTRL + Клик ЛКМ)\n"
        )