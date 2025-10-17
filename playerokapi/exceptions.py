import requests


class CloudflareDetectedException(Exception):
    """
    Ошибка обнаружения Cloudflare защиты при отправке запроса.

    :param response: Объект ответа.
    :type response: `Response`
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
    Ошибка, которая возбуждается, если код ответа не равен 200.

    :param response: Объект ответа.
    :type response: `Response`
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


class RequestError(Exception):
    """
    Ошибка, которая возбуждается, если возникла ошибка при отправке запроса.

    :param response: Объект ответа.
    :type response: `Response`
    """

    def __init__(self, response: requests.Response):
        self.response = response
        self.json = response.json() or None
        self.error_code = self.json["errors"][0]["extensions"]["code"]
        self.error_message = self.json["errors"][0]["message"]

    def __str__(self):
        msg = (
            f"Ошибка запроса к {self.response.url}"
            f"\nКод ошибки: {self.error_code}"
            f"\nСообщение: {self.error_message}"
        )
        return msg


class UnauthorizedError(Exception):
    """
    Ошибка, которая возбуждается, если не удалось подключиться к аккаунту Playerok.
    """

    def __str__(self):
        return "Не удалось подключиться к аккаунту Playerok. Может вы указали неверный token?"
