import requests


class CloudflareDetectedException(Exception):
    """
    Ошибка обнаружения Cloudflare защиты при отправке запроса.

    :param response: Объект ответа.
    :type response: `requests.Response`
    """

    def __init__(self, response: requests.Response):
        self.response = response
        self.status_code = self.response.status_code
        self.html_text = self.response.text

    def __str__(self):
        msg = (
            f"Ошибка: CloudFlare заметил подозрительную активность при отправке запроса на сайт Playerok."
            f"\nКод ошибки: {self.status_code}"
            f"\nОтвет: {self.html_text}"
        )
        return msg


class RequestFailedError(Exception):
    """
    Исключение, которое возбуждается, если код ответа не равен 200.

    :param response: Объект ответа.
    :type response: `requests.Response`
    """

    def __init__(self, response: requests.Response):
        self.response = response
        self.status_code = self.response.status_code
        self.html_text = self.response.text

    def __str__(self):
        msg = (
            f"Ошибка запроса к {self.response.url}"
            f"\nКод ошибки: {self.status_code}"
            f"\nОтвет: {self.html_text}"
        )
        return msg


class RequestPlayerokError(Exception):
    """
    Исключение, которое возбуждается, если возникла ошибка запроса на стороне Playerok.

    :param response: Объект ответа.
    :type response: `requests.Response`
    """

    def __init__(self, response: requests.Response):
        self.response = response
        self.json = response.json()
        self.error_code = self.json["errors"][0]["extensions"]["code"]
        self.error_message = self.json["errors"][0]["message"]

    def __str__(self):
        msg = (
            f"Ошибка запроса к {self.response.url}"
            f"\nКод ошибки: {self.error_code}"
            f"\nСообщение: {self.error_message}"
        )
        return self.error_message or msg


class RequestSendingError(Exception):
    """
    Исключение, которое возбуждается, если не удалось отправить запрос за несколько попыток.

    :param url: URL запроса.
    :type url: `str`

    :param error: Текст ошибки.
    :type error: `str`
    """

    def __init__(self, url: str, error: str):
        self.url = url
        self.error = error

    def __str__(self):
        msg = (
            f"Ошибка при попытке отправить запрос к {self.response.url}"
            f"\nТекст ошибки: {self.error}"
        )
        return msg


class UnauthorizedError(Exception):
    """Исключение, которое возбуждается, если не удалось авторизоваться в аккаунте Playerok."""

    def __str__(self):
        return "Не удалось подключиться к аккаунту Playerok. Может вы указали неверный token?"
