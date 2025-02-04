import asyncio
import json
from datetime import datetime

import aiohttp
from discord import Intents
from discord.ext import commands
from discord.ext.commands import Bot, Context

import service
import util
import threading

WIKIPEDIA_STREAM_URL: str = "https://stream.wikimedia.org/v2/stream/recentchange"

lock: threading.Lock = threading.Lock()

intents = Intents.default()
intents.message_content = True

bot: Bot = commands.Bot(command_prefix="!", intents=intents)


def process_event(event: dict[str, str | int | float]):
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


async def wikipedia_stream():
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(WIKIPEDIA_STREAM_URL) as resp:
                    print("Connected to Wikipedia stream...")
                    async for line_bytes in resp.content:
                        if lock.locked():
                            continue
                        with lock:
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
    # await bot.loop.create_task(wikipedia_stream())


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


bot.run("MTMzNjAwMTE0MTMwNDk4MzY4Mw.GiztLT.ixuzybWaRKpLTsOSYqFOCnFRCg5ivgiHvVATjU")
