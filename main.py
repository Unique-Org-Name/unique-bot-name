import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
import random
import requests
import asyncio
from pathlib import Path
import aiofiles
import aiohttp
import glob
import time
from datetime import datetime
from datetime import datetime, timedelta
import sqlite3
from dotenv import load_dotenv
import json
import re
import base64
from io import BytesIO
from PIL import Image
from utils import catbot
from utils import printStartupMessage

### Global setup ###
load_dotenv()

# Initialize bot instance
cat_bot = catbot.CatPicBot()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')  # Remove default help command
try:
    with open("ai_config.json", "r") as f:
        ai_config = json.load(f)
except FileNotFoundError:
    # Default AI configuration if file doesn't exist
    ai_config = {
        "MODEL_API_URL": "http://localhost:11434/api/generate",
        "MODEL_NAME": "llama3.2",  # Change to your preferred model
        "BOT_NAME": "Assistant Bot",
        "PROMPT_MAIN": "You are a helpful and friendly Discord bot assistant.",
        "KNOWLEDGE": "You can answer questions, have conversations, and help users with various tasks.",
        "PERSONALITY": "Be friendly, helpful, and occasionally playful. Keep responses concise unless asked for details.",
        "ERROR_RESPONSE": "Sorry, I'm having trouble processing that right now. Please try again later.",
        "MAX_RESPONSE_LENGTH": 2000,
        "AI_ENABLED": True
    }
    # Save default config
    with open("ai_config.json", "w") as f:
        json.dump(ai_config, f, indent=2)

# Memory storage for conversations (per channel)
conversation_memory = {}
MAX_MEMORY_LENGTH = 10  # Remember last 10 messages per channel

# Configuration

SPECIAL_IMAGE_CHANCE = 0.1  # 0.1% chance for special image
allowed_bots = ["966695034340663367"]
not_really_trusted_list = ["1056952213056004118"]
spamthing1 = 0
hi_vars = ["hi", "Hi", "HI", "hello", "Hello", "HELLO"]
last_spawn_time = None
timer_task = None

# Setup instructions
def main():
    """Main function with setup instructions"""
    printStartupMessage.printStartupMessage()
    # bot token via .env
    BOT_TOKEN = str(os.getenv("TOKEN"))
    bot.run(BOT_TOKEN)

if __name__ == "__main__":
    main()

bot.tree.clear_commands(guild=None)
