import os
import asyncio

import discord
from discord.ext import commands
from discord import app_commands

from dotenv import load_dotenv

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone

from config import (
    CHANNEL_ID,
    GUILD_ID,
    TIMEZONE,
)

from sheets import load_birthdays
from birthday import morning_messages, evening_messages


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

if TOKEN is None:
    raise RuntimeError("DISCORD_TOKEN is missing in .env")


# ============================================================
# DISCORD
# ============================================================

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

guild = discord.Object(id=GUILD_ID)

scheduler = AsyncIOScheduler(
    timezone=timezone(TIMEZONE)
)


# ============================================================
# HELPERS
# ============================================================

async def send_messages(messages):

    channel = bot.get_channel(CHANNEL_ID)

    if channel is None:
        print("ERROR: Channel not found.")
        return

    if len(messages) == 0:
        print("No reminders to send.")
        return

    print(f"Sending {len(messages)} reminder(s)...")

    for mention, message in messages:

        await channel.send(
            f"{mention}\n\n{message}"
        )

        await asyncio.sleep(1)

    print("Finished sending reminders.")


# ============================================================
# MORNING JOB
# ============================================================

async def run_morning():

    print("Running morning reminders...")

    people = load_birthdays()

    messages = morning_messages(people)

    await send_messages(messages)


# ============================================================
# EVENING JOB
# ============================================================

async def run_evening():

    print("Running evening reminders...")

    people = load_birthdays()

    messages = evening_messages(people)

    await send_messages(messages)


# ============================================================
# READY
# ============================================================

@bot.event
async def on_ready():

    print(f"Logged in as {bot.user}")

    try:

        bot.tree.copy_global_to(guild=guild)

        synced = await bot.tree.sync(guild=guild)

        print(f"Synced {len(synced)} guild commands.")

    except Exception as e:

        print(e)

    if not scheduler.running:

        scheduler.add_job(
            lambda: asyncio.create_task(run_morning()),
            trigger="cron",
            hour=9,
            minute=0
        )

        scheduler.add_job(
            lambda: asyncio.create_task(run_evening()),
            trigger="cron",
            hour=20,
            minute=0
        )

        scheduler.start()

        print("Scheduler started.")

# ============================================================
# SLASH COMMANDS
# ============================================================

@bot.tree.command(
    name="birthdaycount",
    description="Show the number of birthdays loaded.",
    guild=guild,
)
async def birthdaycount(interaction: discord.Interaction):

    people = load_birthdays()

    await interaction.response.send_message(
        f"✅ Loaded **{len(people)}** birthdays.",
        ephemeral=True
    )


@bot.tree.command(
    name="testmorning",
    description="Run the morning reminder immediately.",
    guild=guild,
)
async def testmorning(interaction: discord.Interaction):

    await interaction.response.defer(ephemeral=True)

    await run_morning()

    await interaction.followup.send(
        "✅ Morning reminders sent.",
        ephemeral=True
    )


@bot.tree.command(
    name="testevening",
    description="Run the evening reminder immediately.",
    guild=guild,
)
async def testevening(interaction: discord.Interaction):

    await interaction.response.defer(ephemeral=True)

    await run_evening()

    await interaction.followup.send(
        "✅ Evening reminders sent.",
        ephemeral=True
    )


@bot.tree.command(
    name="today",
    description="Show today's birthdays.",
    guild=guild,
)
async def today(interaction: discord.Interaction):

    from datetime import datetime

    people = load_birthdays()

    today = datetime.now()

    birthdays = []

    for person in people:

        if (
            person["birthday"].day == today.day
            and person["birthday"].month == today.month
        ):

            birthdays.append(
                f"• {person['name']} ({person['department']}) - Gen {person['gen']}"
            )

    if birthdays:

        await interaction.response.send_message(
            "# 🎂 Today's Birthdays\n\n" + "\n".join(birthdays),
            ephemeral=True
        )

    else:

        await interaction.response.send_message(
            "No birthdays today.",
            ephemeral=True
        )


# ============================================================
# START BOT
# ============================================================

bot.run(TOKEN)