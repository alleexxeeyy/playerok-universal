from datetime import datetime
import os
from data import *


DATA = {
    "new_forms": {
        "path": os.path.join(os.path.dirname(__file__), 'module_data', 'new_forms.json'),
        "default": {}
    },
    "forms": {
        "path": os.path.join(os.path.dirname(__file__), 'module_data', 'forms.json'),
        "default": {}
    }
}


class Data:

    @staticmethod
    def get(name) -> dict:
        return get_json(DATA[name]["path"], DATA[name]["default"])

    @staticmethod
    def set(name, new) -> dict:
        set_json(DATA[name]["path"], new)