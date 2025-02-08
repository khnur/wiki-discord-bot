import os
import threading
from datetime import datetime

from discord import Intents
from discord.ext import commands
from discord.ext.commands import Bot, Context

import service
import util
from streaming import producer, consumer

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
WIKIPEDIA_STREAM_URL: str = "https://stream.wikimedia.org/v2/stream/recentchange"

lock: threading.Lock = threading.Lock()

intents = Intents.default()
intents.message_content = True

bot: Bot = commands.Bot(command_prefix="!", intents=intents)


def process_event(event: dict[str, str | int | float]):
    print(f"Processing event {event}")
    wiki: str = event.get("wiki", "")
    if len(wiki) < 2:
        return

    language: str = wiki[:2].lower()
    service.append_event(language, event)

    timestamp = event.get("timestamp")
    if timestamp:
        try:
            date: str = util.get_date(timestamp)
            service.increment_daily_stats(language, date)
        except Exception as e:
            print("Error processing timestamp:", e)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

    threading.Thread(target=producer.produce).start()
    print("Producer is running in another thread...")

    threading.Thread(target=consumer.consume, args=[process_event, lock]).start()
    print("Consumer is running in another thread...")


@bot.command()
async def hello(ctx: Context):
    await ctx.send(f'Hello, {ctx.author.name}!')


@bot.command(name="setLang")
async def set_lang(ctx: Context, lang_code: str = None):
    with lock:
        if not lang_code or len(lang_code) != 2:
            await ctx.send("Please provide a valid two-letter language code (e.g., en, es).")
            return

        key: int = ctx.guild.id if ctx.guild else ctx.author.id
        service.update_language(key, lang_code)
        await ctx.send(f"Default language set to `{lang_code.lower()}` for this session.")


@bot.command(name="recent")
async def recent(ctx: Context, lang_code: str = None):
    with lock:
        key: int = ctx.guild.id if ctx.guild else ctx.author.id
        language: str = lang_code.lower() if lang_code else service.get_language_by_key(key)
        events: list = service.get_events(language)

        if not events or len(events) == 0:
            await ctx.send(f"No recent changes found for language `{language}`.")
            return

        recent_events = events[-5:]
        messages = []
        for event in recent_events:
            title = event.get("title", "N/A")
            user = event.get("user", "N/A")
            timestamp = event.get("timestamp")
            dt_str = util.get_date_time(timestamp) if timestamp else "N/A"
            server_url = event.get("server_url", "")
            url = f"{server_url}/wiki/{title.replace(' ', '_')}" if server_url else "N/A"

            messages.append(f"**Title:** {title}\n**User:** {user}\n**Timestamp:** {dt_str} UTC\n**URL:** {url}\n")

        response = "\n".join(messages)
        await ctx.send(f"Recent changes for language `{language}`:\n\n{response}")


@bot.command(name="stats")
async def stats(ctx: Context, date: str = None):
    with lock:
        try:
            if not date or len(date) != 10:
                raise ValueError("Date must be 10 digits.")
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            await ctx.send("Please provide a date in the format yyyy-mm-dd.")
            return

        key: int = ctx.guild.id if ctx.guild else ctx.author.id
        language: str = service.get_language_by_key(key)
        count: int = service.get_daily_stats(language, date)
        await ctx.send(f"On {date}, there were **{count}** changes for language `{language}`.")


bot.run(DISCORD_BOT_TOKEN)
