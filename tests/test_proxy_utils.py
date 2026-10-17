import unittest

from proxy_utils import ProxyCheckState, normalize_proxy, parse_proxy, requests_proxy, websocket_proxy_options


class ProxyUtilsTests(unittest.TestCase):
    def test_legacy_http_proxy(self):
        proxy = "user:pass@127.0.0.1:8080"
        self.assertEqual(normalize_proxy(proxy), "http://user:pass@127.0.0.1:8080")
        self.assertEqual(requests_proxy(proxy), "http://user:pass@127.0.0.1:8080")
        self.assertEqual(websocket_proxy_options(proxy), {
            "http_proxy_host": "127.0.0.1",
            "http_proxy_port": 8080,
            "proxy_type": "http",
            "http_proxy_auth": ("user", "pass"),
        })

    def test_socks5_proxy_all_transports(self):
        proxy = "socks5://user:pa%3Ass@proxy.example:1080"
        self.assertEqual(parse_proxy(proxy).scheme, "socks5")
        self.assertEqual(requests_proxy(proxy), "socks5h://user:pa%3Ass@proxy.example:1080")
        self.assertEqual(websocket_proxy_options(proxy), {
            "http_proxy_host": "proxy.example",
            "http_proxy_port": 1080,
            "proxy_type": "socks5h",
            "http_proxy_auth": ("user", "pa:ss"),
        })

    def test_socks5_without_auth(self):
        self.assertEqual(websocket_proxy_options("SOCKS5://127.0.0.1:1080"), {
            "http_proxy_host": "127.0.0.1",
            "http_proxy_port": 1080,
            "proxy_type": "socks5h",
        })

    def test_proxy_check_state_recovers_and_can_alert_again(self):
        state = ProxyCheckState()
        self.assertIsNone(state.record(False, 3))
        self.assertIsNone(state.record(False, 3))
        self.assertEqual(state.record(False, 3), "unavailable")
        self.assertTrue(state.unavailable)
        self.assertIsNone(state.record(False, 3))
        self.assertEqual(state.record(True, 3), "recovered")
        self.assertFalse(state.unavailable)
        self.assertEqual(state.failures, 0)
        self.assertIsNone(state.record(True, 3))
        self.assertIsNone(state.record(False, 3))
        self.assertIsNone(state.record(False, 3))
        self.assertEqual(state.record(False, 3), "unavailable")

    def test_invalid_proxy_is_rejected(self):
        for proxy in ("ftp://host:21", "socks5://host", "socks5://host:70000", "http://user@host:80", "http://host:80/path", "http://host:80 invalid"):
            with self.subTest(proxy=proxy), self.assertRaises(ValueError):
                parse_proxy(proxy)


if __name__ == "__main__":
    unittest.main()
