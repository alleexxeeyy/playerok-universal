import os
from data import (
    Data as data,
    DataFile
)


NEW_FORMS = DataFile(
    name="new_forms",
    path=os.path.join(os.path.dirname(__file__), "module_data", "new_forms.json"),
    default={}
)

FORMS = DataFile(
    name="forms",
    path=os.path.join(os.path.dirname(__file__), "module_data", "forms.json"),
    default={}
)

DATA = [NEW_FORMS, FORMS]


class Data:

    @staticmethod
    def get(name: str) -> dict:
        return data.get(name, DATA)

    @staticmethod
    def set(name: str, new: list | dict) -> dict:
        return data.set(name, new, DATA)