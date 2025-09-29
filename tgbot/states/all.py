from aiogram.fsm.state import State, StatesGroup


class ActionsStates(StatesGroup):
    entering_message_text = State()

class SystemStates(StatesGroup):
    entering_password = State()


class SettingsStates(StatesGroup):
    entering_token = State()
    entering_user_agent = State()
    entering_requests_timeout = State()
    entering_listener_requests_delay = State()
    entering_proxy = State()
    entering_tg_logging_chat_id = State()
    entering_messages_watermark = State()


class MessagesStates(StatesGroup):
    entering_page = State()

class MessagePageStates(StatesGroup):
    entering_message_text = State()


class CustomCommandsStates(StatesGroup):
    entering_page = State()
    entering_new_custom_command = State()
    entering_new_custom_command_answer = State()

class CustomCommandPageStates(StatesGroup):
    entering_custom_command_answer = State()


class AutoDeliveriesStates(StatesGroup):
    entering_page = State()
    entering_new_auto_delivery_keyphrases = State()
    entering_new_auto_delivery_message = State()

class AutoDeliveryPageStates(StatesGroup):
    entering_auto_delivery_keyphrases = State()
    entering_auto_delivery_message = State()


class ActiveOrdersStates(StatesGroup):
    entering_page = State()