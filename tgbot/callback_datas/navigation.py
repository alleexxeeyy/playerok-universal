from aiogram.filters.callback_data import CallbackData


class MenuNavigation(CallbackData, prefix="menpag"):
    to: str


class SettingsNavigation(CallbackData, prefix="sepag"):
    to: str


class BotSettingsNavigation(CallbackData, prefix="bspag"):
    to: str


class ItemsSettingsNavigation(CallbackData, prefix="ispag"):
    to: str


class InstructionNavigation(CallbackData, prefix="inspag"):
    to: str