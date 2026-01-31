from aiogram.fsm.state import State, StatesGroup


class SystemStates(StatesGroup):
    waiting_for_password = State()


class ActionsStates(StatesGroup):
    waiting_for_message_text = State()


class SettingsStates(StatesGroup):
    waiting_for_token = State()
    waiting_for_user_agent = State()

    waiting_for_requests_timeout = State()
    waiting_for_listener_requests_delay = State()
    waiting_for_proxy = State()

    waiting_for_auto_withdrawal_interval = State()
    waiting_for_sbp_bank_phone_number = State()
    waiting_for_usdt_address = State()

    waiting_for_tg_logging_chat_id = State()
    waiting_for_watermark_value = State()


class MessagesStates(StatesGroup):
    waiting_for_page = State()
    waiting_for_message_text = State()


class RestoreItemsStates(StatesGroup):
    waiting_for_new_included_restore_item_keyphrases = State()
    waiting_for_new_included_restore_items_keyphrases_file = State()
    waiting_for_new_excluded_restore_item_keyphrases = State()
    waiting_for_new_excluded_restore_items_keyphrases_file = State()


class BumpItemsStates(StatesGroup):
    waiting_for_bump_items_interval = State()
    waiting_for_new_included_bump_item_keyphrases = State()
    waiting_for_new_included_bump_items_keyphrases_file = State()
    waiting_for_new_excluded_bump_item_keyphrases = State()
    waiting_for_new_excluded_bump_items_keyphrases_file = State()


class CustomCommandsStates(StatesGroup):
    waiting_for_page = State()
    waiting_for_new_custom_command = State()
    waiting_for_new_custom_command_answer = State()
    waiting_for_custom_command_answer = State()


class AutoDeliveriesStates(StatesGroup):
    waiting_for_page = State()
    waiting_for_new_auto_delivery_keyphrases = State()
    waiting_for_new_auto_delivery_message = State()
    waiting_for_auto_delivery_keyphrases = State()
    waiting_for_auto_delivery_message = State()