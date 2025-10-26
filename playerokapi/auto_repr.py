class AutoRepr:
    """Добавляет приемлемый вывод в консоль любого объекта"""
    def __repr__(self):
        attrs = ", ".join(
            f"{k}={v!r}" for k, v in self.__dict__.items() if not k.startswith("_")
        )
        return f"{self.__class__.__name__}({attrs})"
