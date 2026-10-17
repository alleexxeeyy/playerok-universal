import asyncio
import unittest
from unittest.mock import AsyncMock, patch

import bot


class StartupRecoveryTests(unittest.IsolatedAsyncioTestCase):
    async def test_failed_startup_retries_and_starts_playerok_when_proxy_recovers(self):
        config = {
            "playerok": {"api": {
                "proxy": "socks5://user:pass@127.0.0.1:1080",
                "proxy_check_interval": 60,
                "proxy_check_timeout": 10,
                "proxy_check_failures": 2,
            }}
        }
        checks = iter((False, True, True))
        sleep_count = 0

        async def controlled_sleep(_seconds):
            nonlocal sleep_count
            sleep_count += 1
            if sleep_count == 4:
                raise asyncio.CancelledError()

        async def run_sync_in_thread(function, *args, **kwargs):
            return function(*args, **kwargs)

        with (
            patch("settings.Settings.get", return_value=config),
            patch("utils.is_proxy_working", side_effect=lambda *_args, **_kwargs: next(checks)),
            patch("bot.asyncio.sleep", side_effect=controlled_sleep),
            patch("bot.asyncio.to_thread", side_effect=run_sync_in_thread),
            patch("bot.start_playerok_bot", new_callable=AsyncMock) as start,
            patch("startup_alert.deliver_playerok_reconnected") as recovered,
        ):
            with self.assertRaises(asyncio.CancelledError):
                await bot.monitor_playerok_proxy(startup_unavailable=True, notified=True)

        start.assert_awaited_once_with(in_thread=True)
        recovered.assert_called_once_with(config)


if __name__ == "__main__":
    unittest.main()
