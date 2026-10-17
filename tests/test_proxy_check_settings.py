import copy
import unittest

from settings import CONFIG, restore_config


class ProxyCheckSettingsTests(unittest.TestCase):
    def test_existing_config_keeps_credentials_and_receives_defaults(self):
        old_config = copy.deepcopy(CONFIG.default)
        old_config["playerok"]["api"]["cookies"] = "token=existing"
        old_config["telegram"]["api"]["token"] = "existing-telegram-token"
        for key in ("proxy_check_interval", "proxy_check_timeout", "proxy_check_failures"):
            del old_config["playerok"]["api"][key]

        updated = restore_config(old_config, CONFIG.default)

        self.assertEqual(updated["playerok"]["api"]["cookies"], "token=existing")
        self.assertEqual(updated["telegram"]["api"]["token"], "existing-telegram-token")
        self.assertEqual(updated["playerok"]["api"]["proxy_check_interval"], 60)
        self.assertEqual(updated["playerok"]["api"]["proxy_check_timeout"], 10)
        self.assertEqual(updated["playerok"]["api"]["proxy_check_failures"], 2)
        self.assertNotIn("proxy_check_interval", old_config["playerok"]["api"])


if __name__ == "__main__":
    unittest.main()
