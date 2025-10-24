import re
import traceback
from logging import getLogger
from typing import TYPE_CHECKING
from colorama import Fore
from threading import Thread

from playerokapi.listener.events import *
from playerokapi.enums import *
from playerokapi.account import *

from ..meta import PREFIX, NAME
from ..data import Data as data
from ..settings import Settings as sett
from ..settings import DATA
from plbot.playerokbot import get_playerok_bot

if TYPE_CHECKING:
    from plbot.playerokbot import PlayerokBot


logger = getLogger(f"{NAME}.playerok")
config = sett.get("config")
messages = sett.get("messages")

new_forms = data.get("new_forms")
forms = data.get("forms")


def msg(message_name: str, exclude_watermark: bool = False, **kwargs) -> str | None:
    return get_playerok_bot().msg(message_name, exclude_watermark, "messages", DATA, **kwargs)

def is_fullname_valid(fullname: str) -> bool:
    pattern = r'^[А-Яа-яЁё]+ [А-Яа-яЁё]+ [А-Яа-яЁё]+$'
    return bool(re.match(pattern, fullname.strip()))

def is_age_valid(age: str) -> bool:
    return age.isdigit()

def is_hobby_valid(hobby: str) -> bool:
    pattern = r'^[А-Яа-яЁё\s\-]+$'
    return bool(re.match(pattern, hobby.strip()))

async def handle_cmds(plbot: 'PlayerokBot', event: NewMessageEvent):
    global new_forms
    if event.message.text.lower() == "!мояанкета":
        form = forms.get(event.message.user.username)
        if not form:
            plbot.send_message(event.chat.id, msg("cmd_myform_error", reason="Ваша анкета не была найдена.\nИспользуйте команду !заполнить, чтобы заполнить анкету."))
            return
        plbot.send_message(event.chat.id, msg("cmd_myform", fullname=form["fullname"], age=form["age"], hobby=form["hobby"]))
    elif event.message.text.lower() == "!заполнить":
        new_forms[event.message.user.username] = {
            "fullname": "",
            "age": "",
            "hobby": "",
            "state": "waiting_for_fullname"
        }
        plbot.send_message(event.chat.id, msg("cmd_writein"))

async def handle_new_form_waiting_for_fullname(plbot: 'PlayerokBot', event: NewMessageEvent):
    global new_forms
    fullname = event.message.text.strip()
    if not is_fullname_valid(fullname):
        plbot.send_message(event.chat.id, msg("entering_fullname_error"))
        return
    fullname = " ".join([f"{part[0].upper()}{part[1:]}" for part in fullname.split(" ")])
    new_forms[event.message.user.username]["fullname"] = fullname
    new_forms[event.message.user.username]["state"] = "waiting_for_age"
    if config["playerok"]["bot"]["log_states"]:
        logger.info(f"{PREFIX} {Fore.LIGHTWHITE_EX}{event.message.user.username} {Fore.WHITE}указал в анкете ФИО: {Fore.LIGHTWHITE_EX}{fullname}")
    plbot.send_message(event.chat.id, msg("enter_age"))

async def handle_new_form_waiting_for_age(plbot: 'PlayerokBot', event: NewMessageEvent):
    global new_forms
    age = event.message.text.strip()
    if not is_age_valid(age):
        plbot.send_message(event.chat.id, msg("entering_age_error"))
        return
    new_forms[event.message.user.username]["age"] = int(age)
    new_forms[event.message.user.username]["state"] = "waiting_for_hobby"
    if config["playerok"]["bot"]["log_states"]:
        logger.info(f"{PREFIX} {Fore.LIGHTWHITE_EX}{event.message.user.username} {Fore.WHITE}указал в анкете возраст: {Fore.LIGHTWHITE_EX}{age}")
    plbot.send_message(event.chat.id, msg("enter_hobby"))

async def handle_new_form_waiting_for_hobby(plbot: 'PlayerokBot', event: NewMessageEvent):
    global new_forms, forms
    hobby = event.message.text.strip()
    if not is_hobby_valid(hobby):
        plbot.send_message(event.chat.id, msg("entering_hobby_error"))
        return
    new_forms[event.message.user.username]["hobby"] = hobby
    forms[event.message.user.username] = {
        "fullname": new_forms[event.message.user.username]["fullname"],
        "age": new_forms[event.message.user.username]["age"],
        "hobby": new_forms[event.message.user.username]["hobby"]
    }
    del new_forms[event.message.user.username]
    if config["playerok"]["bot"]["log_states"]:
        logger.info(f"{PREFIX} {Fore.LIGHTWHITE_EX}{event.message.user.username} {Fore.WHITE}указал в анкете хобби: {Fore.LIGHTWHITE_EX}{hobby}")
    plbot.send_message(event.chat.id, msg("form_filled_out", fullname=forms[event.message.user.username]["fullname"], age=forms[event.message.user.username]["age"], hobby=forms[event.message.user.username]["hobby"]))
    
async def handle_new_form(plbot: 'PlayerokBot', event: NewMessageEvent):
    if event.message.user.username not in new_forms:
        return
    if new_forms[event.message.user.username]["state"] == "waiting_for_fullname":
        await handle_new_form_waiting_for_fullname(plbot, event)
    elif new_forms[event.message.user.username]["state"] == "waiting_for_age":
        await handle_new_form_waiting_for_age(plbot, event)
    elif new_forms[event.message.user.username]["state"] == "waiting_for_hobby":
        await handle_new_form_waiting_for_hobby(plbot, event)
    else:
        return

def on_playerok_bot_init(plbot: 'PlayerokBot'):

    def endless_loop(cycle_delay=5):
        global config, messages, new_forms, forms
        while True:
            if sett.get("config") != config: config = sett.get("config")
            if sett.get("messages") != messages: messages = sett.get("messages")
            if data.get("new_forms") != new_forms: data.set("new_forms", new_forms)
            if data.get("forms") != forms: data.set("forms", forms)
            time.sleep(cycle_delay)

    Thread(target=endless_loop, daemon=True).start()

async def on_new_message(plbot: 'PlayerokBot', event: NewMessageEvent):
    try:
        if event.message.text is None:
            return
        if event.message.user.id != plbot.playerok_account.id:
            await handle_new_form(plbot, event)
            await handle_cmds(plbot, event)
    except Exception:
        logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При обработке ивента новых сообщений произошла ошибка: {Fore.WHITE}")
        traceback.print_exc()