from aiogram.filters.callback_data import CallbackData


class MenuNavigation(CallbackData, prefix="mennav"):
    to: str

class PlaceholdersNavigation(CallbackData, prefix="plhnav"):
    to: str
    by: str

class StatsNavigation(CallbackData, prefix="stnav"):
    to: str

class SettingsNavigation(CallbackData, prefix="senva"):
    to: str

class BotSettingsNavigation(CallbackData, prefix="bsnav"):
    to: str

class ItemsSettingsNavigation(CallbackData, prefix="isnav"):
    to: str