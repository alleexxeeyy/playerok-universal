import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from tgbot.callback_handlers import pagination


class ChatsTimeoutTests(unittest.IsolatedAsyncioTestCase):
    async def test_chats_show_error_instead_of_waiting_for_all_api_retries(self):
        account = SimpleNamespace(get_chats=lambda **_kwargs: None)
        config = {"playerok": {"api": {"requests_timeout": 1}}}

        async def never_finishes(*_args, **_kwargs):
            await asyncio.sleep(3600)

        with (
            patch("plbot.playerokbot.get_playerok_bot", return_value=SimpleNamespace(account=account, connection_unavailable=False)),
            patch.object(pagination.sett, "get", return_value=config),
            patch.object(pagination, "load_cursor_list", side_effect=never_finishes),
            patch.object(pagination, "show_chats_error", new_callable=AsyncMock) as show_error,
        ):
            await pagination.render_chats(None, None, 0)

        show_error.assert_awaited_once()
        self.assertIn("не ответил за 1 сек", show_error.await_args.args[2])

    async def test_known_outage_does_not_show_loading_spinner(self):
        with (
            patch("plbot.playerokbot.get_playerok_bot", return_value=SimpleNamespace(account=object(), connection_unavailable=True)),
            patch.object(pagination, "load_cursor_list", new_callable=AsyncMock) as load,
            patch.object(pagination, "show_chats_error", new_callable=AsyncMock) as show_error,
        ):
            await pagination.render_chats(None, None, 0)

        load.assert_not_awaited()
        show_error.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()
