import asyncio
import json
from collections import defaultdict, deque
from datetime import datetime

import aiohttp
from discord import Intents
from discord.ext import commands
from discord.ext.commands import Bot, Context

import util

MAX_EVENTS: int = 100
WIKIPEDIA_STREAM_URL: str = "https://stream.wikimedia.org/v2/stream/recentchange"

recent_changes: defaultdict = defaultdict(lambda: deque(maxlen=MAX_EVENTS))
daily_stats: defaultdict = defaultdict(int)

default_languages: dict[int, str] = dict()

intents = Intents.default()
intents.message_content = True

bot: Bot = commands.Bot(command_prefix="!", intents=intents)


def process_event(event: dict[str, str | int | float]):
    """
    Given a JSON event from Wikipedia, determine its language and update the in-memory stores.
    """
    global recent_changes, daily_stats

    # We expect a 'wiki' field in the event (e.g. "enwiki" or "eswiki")
    wiki: str = event.get("wiki", "")
    if len(wiki) < 2:
        return

    language: str = wiki[:2].lower()
    # Append the event (keeping only the last MAX_EVENTS events)
    recent_changes[language].append(event)

    # Update daily stats based on the event's timestamp.
    timestamp = event.get("timestamp")
    if timestamp:
        try:
            dt: str = util.get_date_time(timestamp)
            key = (language, dt)
            daily_stats[key] += 1
        except Exception as e:
            print("Error processing timestamp:", e)


async def wikipedia_stream():
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(WIKIPEDIA_STREAM_URL) as resp:
                    print("Connected to Wikipedia stream...")
                    async for line_bytes in resp.content:
                        try:
                            line = line_bytes.decode("utf-8").strip()
                        except Exception as ex:
                            print(ex)
                            continue
                        if not line.startswith("data:"):
                            continue
                        data_str = line[len("data:"):].strip()
                        if not data_str:
                            continue
                        try:
                            event = json.loads(data_str)
                            process_event(event)
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            print("Error in Wikipedia stream:", e)
            await asyncio.sleep(5)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.loop.create_task(wikipedia_stream())


@bot.command()
async def hello(ctx: Context):
    await ctx.send(f'Hello, {ctx.author.name}!')


@bot.command(name="setLang")
async def set_lang(ctx: Context, lang_code: str):
    if not lang_code or len(lang_code) != 2:
        await ctx.send("Please provide a valid two-letter language code (e.g., en, es).")
        return

    key: int = ctx.guild.id if ctx.guild else ctx.author.id
    default_languages[key] = lang_code.lower()
    await ctx.send(f"Default language set to `{lang_code.lower()}` for this session.")


@bot.command(name="recent")
async def recent(ctx: Context, lang_code: str = None):
    """
    Show the most recent changes for a given language.
    If no language is provided, use the default (or default to English).
    Usage: !recent or !recent es
    """
    key: int = ctx.guild.id if ctx.guild else ctx.author.id
    language = (lang_code.lower() if lang_code else default_languages.get(key, "en"))
    events = list(recent_changes.get(language, []))

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
async def stats(ctx: Context, date: str):
    """
    Display the total number of changes for a given date (yyyy-mm-dd)
    using the current session's language (or default to English).
    Usage: !stats 2025-01-31
    """
    # Validate the date format.
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        await ctx.send("Please provide a date in the format yyyy-mm-dd.")
        return

    key: int = ctx.guild.id if ctx.guild else ctx.author.id
    language: str = default_languages.get(key, "en")
    count: int = daily_stats.get((language, date), 0)
    await ctx.send(f"On {date}, there were **{count}** changes for language `{language}`.")


bot.run("MTMzNjAwMTE0MTMwNDk4MzY4Mw.GiztLT.ixuzybWaRKpLTsOSYqFOCnFRCg5ivgiHvVATjU")
