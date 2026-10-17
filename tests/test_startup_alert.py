import copy
import unittest

from startup_alert import (
    deliver_startup_alert, deliver_playerok_alert, deliver_restart_started,
    deliver_playerok_connected, deliver_playerok_reconnected,
)


class StartupAlertTests(unittest.TestCase):
    def setUp(self):
        self.config = {
            "telegram": {
                "api": {
                    "token": "test-token",
                    "proxy": "socks5://user:pass@127.0.0.1:1080",
                    "custom_api_url": "",
                },
                "bot": {"signed_users": [123]},
            },
            "playerok": {"notifications": {"chat_id": ""}},
        }

    def test_falls_back_to_direct_telegram_without_changing_config(self):
        calls = []
        original = copy.deepcopy(self.config)

        class Response:
            ok = True

            def json(self):
                return {"ok": True}

        def send(url, **kwargs):
            calls.append(kwargs)
            if kwargs["proxies"] is not None:
                raise OSError("proxy unavailable")
            return Response()

        self.assertTrue(deliver_startup_alert(self.config, "test failure", send=send))
        self.assertEqual(self.config, original)
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0]["proxies"]["https"], "socks5h://user:pass@127.0.0.1:1080")
        self.assertIsNone(calls[1]["proxies"])

    def test_no_recipient_exits_without_sending(self):
        self.config["telegram"]["bot"]["signed_users"] = []
        self.assertFalse(deliver_startup_alert(self.config, "test failure", send=lambda *_args, **_kwargs: self.fail("unexpected send")))

    def test_retries_until_notification_is_delivered(self):
        self.config["telegram"]["api"]["proxy"] = ""
        attempts = []
        pauses = []

        class Response:
            ok = True

            def json(self):
                return {"ok": True}

        def send(_url, **_kwargs):
            attempts.append(1)
            if len(attempts) == 1:
                raise OSError("network unavailable")
            return Response()

        self.assertTrue(deliver_startup_alert(self.config, "test failure", send=send, pause=pauses.append))
        self.assertEqual(len(attempts), 2)
        self.assertEqual(pauses, [60])

    def test_restart_messages_report_playerok_separately(self):
        self.config["telegram"]["api"]["proxy"] = ""
        messages = []

        class Response:
            ok = True

            def json(self):
                return {"ok": True}

        def send(_url, **kwargs):
            messages.append(kwargs["json"]["text"])
            return Response()

        self.assertTrue(deliver_restart_started(self.config, send=send))
        self.assertTrue(deliver_playerok_alert(self.config, "Прокси Playerok не отвечает.", send=send))
        self.assertTrue(deliver_playerok_reconnected(self.config, send=send))
        self.assertTrue(deliver_playerok_connected(self.config, send=send))

        self.assertEqual(messages[0], "✅ Бот был успешно перезагружен.\n⏳ Проверяю подключение к Playerok…")
        self.assertIn("автоматически повторит подключение", messages[1])
        self.assertNotIn("/restart", messages[1])
        self.assertEqual(messages[2], "✅ Playerok подключён. Работа восстановлена, /restart не требуется.")
        self.assertEqual(messages[3], "✅ Playerok подключён.")

    def test_playerok_notice_keeps_telegram_available_without_retry_loop(self):
        self.config["telegram"]["api"]["proxy"] = ""
        messages = []

        class Response:
            ok = True

            def json(self):
                return {"ok": True}

        def send(_url, **kwargs):
            messages.append(kwargs["json"]["text"])
            return Response()

        self.assertTrue(deliver_playerok_alert(self.config, "Прокси не отвечает", send=send))
        self.assertIn("Telegram-бот продолжает работать", messages[0])
        self.assertIn("/restart", messages[0])


if __name__ == "__main__":
    unittest.main()
