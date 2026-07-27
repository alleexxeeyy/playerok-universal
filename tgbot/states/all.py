from aiogram.fsm.state import State, StatesGroup


class SystemStates(StatesGroup):
    waiting_for_password = State()
    waiting_for_current_password = State()
    waiting_for_new_password = State()


class ActionsStates(StatesGroup):
    waiting_for_chats_search_value = State()
    waiting_for_fast_answer_message = State()
    waiting_for_chat_answer_message = State()

    waiting_for_fast_problem_description = State()
    waiting_for_deal_problem_description = State()

    waiting_for_items_game_name = State()

    waiting_for_trans_min_value = State()
    waiting_for_trans_max_value = State()
    waiting_for_trans_from_date = State()
    waiting_for_trans_to_date = State()

    waiting_for_reviews_game_name = State()
    waiting_for_reviews_min_item_price = State()
    waiting_for_reviews_max_item_price = State()


class SettingsStates(StatesGroup):
    waiting_for_cookies = State()
    waiting_for_user_agent = State()

    waiting_for_requests_timeout = State()
    waiting_for_listener_requests_delay = State()
    waiting_for_pl_proxy = State()
    waiting_for_tg_proxy = State()
    waiting_for_tg_custom_api_url = State()

    waiting_for_auto_withdrawal_interval = State()
    waiting_for_sbp_bank_phone_number = State()
    waiting_for_usdt_address = State()

    waiting_for_notifications_chat_id = State()
    waiting_for_watermark_value = State()

    waiting_for_new_fast_reply_text = State()
    waiting_for_fast_reply_text = State()

    waiting_for_logs_max_file_size = State()
    waiting_for_module_file = State()
    waiting_for_config_file = State()


class MessagesStates(StatesGroup):
    waiting_for_page = State()
    waiting_for_message_text = State()


class RestoreItemsStates(StatesGroup):
    waiting_for_new_included_restore_item_keyphrases = State()
    waiting_for_new_excluded_restore_item_keyphrases = State()


class CompleteDealsStates(StatesGroup):
    waiting_for_new_included_complete_deal_keyphrases = State()
    waiting_for_new_excluded_complete_deal_keyphrases = State()


class BumpItemsStates(StatesGroup):
    waiting_for_bump_items_interval = State()
    waiting_for_bump_items_position = State()
    waiting_for_bump_items_cooldown = State()

    waiting_for_bump_items_night_interval = State()
    waiting_for_bump_items_night_position = State()
    waiting_for_bump_items_night_time_from = State()
    waiting_for_bump_items_night_time_to = State()

    waiting_for_new_included_bump_item_keyphrases = State()
    waiting_for_new_excluded_bump_item_keyphrases = State()


class CustomCommandsStates(StatesGroup):
    waiting_for_new_custom_command = State()
    waiting_for_new_custom_command_answer = State()
    
    waiting_for_page = State()
    waiting_for_custom_command_answer = State()


class AutoDeliveriesStates(StatesGroup):
    waiting_for_page = State()
    
    waiting_for_new_auto_delivery_keyphrases = State()
    waiting_for_new_auto_delivery_piece = State()
    waiting_for_new_auto_delivery_message = State()
    waiting_for_new_auto_delivery_goods = State()
    
    waiting_for_auto_delivery_keyphrases = State()
    waiting_for_auto_delivery_piece = State()
    waiting_for_auto_delivery_message = State()
    waiting_for_auto_delivery_goods_add = State()


class DataReplacementStates(StatesGroup):
    waiting_for_page = State()

    waiting_for_new_data_replacement_keyphrases = State()
    waiting_for_new_data_replacement_values = State()

    waiting_for_data_replacement_keyphrases = State()
    waiting_for_data_replacement_separator = State()
    waiting_for_data_replacement_values_add = State()