import unittest
from unittest.mock import patch, MagicMock, AsyncMock

from src import main


class TestProcessEvent(unittest.TestCase):
    def test_process_event_with_valid_wiki_and_timestamp(self):
        with (
            patch("main.service.append_event") as mock_append,
            patch("main.util.get_date", return_value="2025-01-01") as mock_get_date,
            patch("main.service.increment_daily_stats") as mock_increment
        ):
            event: dict = {"wiki": "enwiki", "timestamp": 1600000000}
            main.process_event(event)
            mock_append.assert_called_once_with("en", event)
            mock_get_date.assert_called_once_with(1600000000)
            mock_increment.assert_called_once_with("en", "2025-01-01")

    def test_process_event_with_short_wiki(self):
        with patch("main.service.append_event") as mock_append:
            main.process_event({"wiki": "e"})
            mock_append.assert_not_called()

    def test_process_event_with_no_timestamp(self):
        with (
            patch("main.service.append_event") as mock_append,
            patch("main.util.get_date") as mock_get_date,
            patch("main.service.increment_daily_stats") as mock_increment
        ):
            event: dict = {"wiki": "enwiki"}
            main.process_event(event)
            mock_append.assert_called_once_with("en", event)
            mock_get_date.assert_not_called()
            mock_increment.assert_not_called()

    def test_process_event_with_invalid_timestamp(self):
        with (
            patch("main.service.append_event") as mock_append,
            patch("main.util.get_date", side_effect=ValueError("bad date")) as mock_get_date,
            patch("main.service.increment_daily_stats") as mock_increment
        ):
            event: dict = {"wiki": "enwiki", "timestamp": "invalid"}
            main.process_event(event)
            mock_append.assert_called_once_with("en", event)
            mock_get_date.assert_called_once_with("invalid")
            mock_increment.assert_not_called()


class TestCommands(unittest.IsolatedAsyncioTestCase):
    async def test_hello_command(self):
        ctx = MagicMock()
        ctx.author.name = "TestUser"
        ctx.send = AsyncMock()

        hello_cmd = main.bot.get_command("hello")
        await hello_cmd.callback(ctx)

        ctx.send.assert_called_once_with("Hello, TestUser!")

    async def test_set_lang_invalid(self):
        ctx = MagicMock()
        ctx.guild = MagicMock()
        ctx.guild.id = 1234
        ctx.send = AsyncMock()

        set_lang_cmd = main.bot.get_command("setLang")
        await set_lang_cmd.callback(ctx, None)
        ctx.send.assert_called_once_with(
            "Please provide a valid two-letter language code (e.g., en, es)."
        )

    @patch("main.service.update_language")
    async def test_set_lang_valid(self, mock_update_language):
        ctx = MagicMock()
        ctx.guild = MagicMock()
        ctx.guild.id = 1234
        ctx.send = AsyncMock()

        set_lang_cmd = main.bot.get_command("setLang")
        await set_lang_cmd.callback(ctx, "EN")

        mock_update_language.assert_called_once_with(1234, "EN")
        ctx.send.assert_called_once_with(
            "Default language set to `en` for this session."
        )

    @patch("main.service.get_language_by_key", return_value="en")
    @patch("main.service.get_events")
    async def test_recent_no_events(self, mock_get_events, mock_get_language):
        mock_get_events.return_value = []
        ctx = MagicMock()
        ctx.guild = MagicMock()
        ctx.guild.id = 1234
        ctx.send = AsyncMock()

        recent_cmd = main.bot.get_command("recent")
        await recent_cmd.callback(ctx)
        ctx.send.assert_called_once_with("No recent changes found for language `en`.")

    @patch("main.util.get_date_time", return_value="2025-01-01 00:00:00")
    @patch("main.service.get_language_by_key", return_value="en")
    @patch("main.service.get_events")
    async def test_recent_with_events(self, mock_get_events, mock_get_language, mock_get_date_time):
        events = []
        for i in range(6):
            events.append({
                "title": f"Page {i}",
                "user": f"User {i}",
                "timestamp": 1600000000 + i,
                "server_url": "https://en.wikipedia.org",
            })
        mock_get_events.return_value = events
        ctx = MagicMock()
        ctx.guild = MagicMock()
        ctx.guild.id = 1234
        ctx.send = AsyncMock()

        recent_cmd = main.bot.get_command("recent")
        await recent_cmd.callback(ctx)

        messages = []
        for event in events[-5:]:
            title = event.get("title", "N/A")
            user = event.get("user", "N/A")
            dt_str = "2025-01-01 00:00:00"  # our patched return value
            server_url = event.get("server_url", "")
            url = f"{server_url}/wiki/{title.replace(' ', '_')}" if server_url else "N/A"
            messages.append(
                f"**Title:** {title}\n**User:** {user}\n**Timestamp:** {dt_str} UTC\n**URL:** {url}\n"
            )
        expected_response = f"Recent changes for language `en`:\n\n" + "\n".join(messages)
        ctx.send.assert_called_once_with(expected_response)

    async def test_stats_invalid_date(self):
        ctx = MagicMock()
        ctx.guild = MagicMock()
        ctx.guild.id = 1234
        ctx.send = AsyncMock()

        stats_cmd = main.bot.get_command("stats")
        await stats_cmd.callback(ctx, "20250101")
        ctx.send.assert_called_once_with(
            "Please provide a date in the format yyyy-mm-dd."
        )

    @patch("main.service.get_daily_stats", return_value=42)
    @patch("main.service.get_language_by_key", return_value="en")
    async def test_stats_valid_date(self, mock_get_language, mock_get_daily_stats):
        ctx = MagicMock()
        ctx.guild = MagicMock()
        ctx.guild.id = 1234
        ctx.send = AsyncMock()

        stats_cmd = main.bot.get_command("stats")
        await stats_cmd.callback(ctx, "2025-01-01")
        mock_get_language.assert_called_once_with(1234)
        mock_get_daily_stats.assert_called_once_with("en", "2025-01-01")
        ctx.send.assert_called_once_with(
            "On 2025-01-01, there were **42** changes for language `en`."
        )


class TestOnReady(unittest.IsolatedAsyncioTestCase):
    @patch("main.threading.Thread")
    async def test_on_ready(self, mock_thread):
        mock_thread1 = MagicMock()
        mock_thread2 = MagicMock()
        mock_thread.side_effect = [mock_thread1, mock_thread2]
        with patch("main.producer.produce") as mock_producer, \
                patch("main.consumer.consume") as mock_consumer:
            await main.on_ready()
            self.assertEqual(mock_thread.call_count, 2)
            first_call = mock_thread.call_args_list[0]
            self.assertEqual(first_call[1]["target"], mock_producer)

            second_call = mock_thread.call_args_list[1]
            self.assertEqual(second_call[1]["target"], mock_consumer)
            self.assertEqual(second_call[1]["args"], [main.process_event, main.lock])

            mock_thread1.start.assert_called_once()
            mock_thread2.start.assert_called_once()


if __name__ == "__main__":
    unittest.main()
