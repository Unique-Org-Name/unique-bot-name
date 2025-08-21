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

load_dotenv()

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
ASSETS_FOLDER = "assets"
CAMERA_ROLL_FOLDER = os.path.join(ASSETS_FOLDER, "camera_roll")
SPECIAL_IMAGE_PATH = os.path.join(ASSETS_FOLDER, "man_horse.jpg")
SPECIAL_IMAGE_CHANCE = 0.1  # 0.1% chance for special image
allowed_bots = ["966695034340663367"]
not_really_trusted_list = ["1056952213056004118"]
spamthing1 = 0
goofy_gifs = {1: "https://tenor.com/view/finally-yeah-boy-nice-yes-fridge-gif-4687827172351383981",
                  2: "https://cdn.discordapp.com/attachments/773986571434721320/1400123591323812023/5D81CCCE-B4E0-4E3E-9678-193BBE70F7C5.gif",
                  3: "https://cdn.discordapp.com/attachments/773986571434721320/1400123345747316817/C40E3939-8BA1-43E9-9AE5-F48F44F6D3C6.gif",
                  4: "https://tenor.com/view/toilet-shark-toilet-freaky-shark-sitting-shark-goofy-ahh-gif-6628307483075639751",
                  5: "https://tenor.com/view/quandale-quandale-dingle-gif-25093205",
                  6: "https://cdn.discordapp.com/attachments/802977594860503042/1378916194165460992/IMG_0114.gif",
                  7: "https://tenor.com/view/tyler-the-creator-homer-simpson-dance-freaky-dont-tap-the-glass-gif-18219729817367897576",
                  8: "https://cdn.discordapp.com/attachments/1121521105316880384/1393451576638570666/33c1e68ee2acb13e1c11a271006b28ca1online-video-cutter.com-ezgif.com-video-to-gif-converter.gif",
                  9: "https://tenor.com/view/goober-kitty-crazy-cat-cat-goober-warning-gif-24871108",
                  10: "https://cdn.discordapp.com/attachments/1105948808388550749/1313144853013598319/caption-6.gif",
                  11: "https://tenor.com/view/griddy-devious-diabolical-malicious-devil-gif-26915799",
                  12: "https://tenor.com/view/mustard-among-us-among-us-amogus-gif-22939641",
                  13: "https://tenor.com/view/spongebob-crying-geometry-dash-sad-spunch-agony-god-i-love-trampolining-gif-25250082",
                  14: "https://imgur.com/3SvtVR8",
                  15: "https://tenor.com/view/damn-bird-pukeko-chick-chicken-gif-16186129570004356645",
                  16: "https://tenor.com/view/you-wont-believe-this-digs-digging-loop-gif-19998502",
                  17: "https://tenor.com/view/pigeon-lebron-james-meme-funny-gif-3425517799009042574",
                  18: "https://tenor.com/view/cat-meme-cat-cats-cat-hug-cat-love-gif-9176149428765300540",
                  19: "https://imgur.com/gallery/IsWDJWa",
                  20: "https://tenor.com/view/mango-cat-dance-ai-dancing-cat-gif-4373280976266621514",
                  21: "https://tenor.com/view/whatever-go-my-whatever-go-my-vrad-vrad-vradexe-interloper-gif-2623316526149241953",
                  22: "https://tenor.com/view/theres-so-much-theres-so-much-sog-ted-2-ted-so-much-sog-gif-10316726644461251151",
                  23: "https://media.discordapp.net/attachments/735670248715583528/1148768418678460467/togif.gif",
                  24: "https://cdn.discordapp.com/attachments/1205760412507840572/1382867848552124488/1x.webp",
                  25: "https://tenor.com/view/download-carmen-winstead-quandale-dingle-gif-25824098"}
hi_vars = ["hi", "Hi", "HI", "hello", "Hello", "HELLO"]
last_spawn_time = None
timer_task = None

# ------- STUFF --------
def load_achievements():
    try:
        with open("achievements.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("achievements.json not found!")
        return {}


async def update_server_count():
    """Update the bot's presence with current server count"""
    try:
        server_count = len(bot.guilds)

        await bot.change_presence(
            status=discord.Status.dnd,  # Keep DND status
            activity=discord.Streaming(
                name=f"radio or smth | I am in {server_count} Discord servers!",  # Your existing name + server count
                url="https://www.youtube.com/watch?v=dTS_aNfpbIM"  # Your existing URL
            )
        )

        print(f"Updated server count in presence: {server_count} servers")

    except Exception as e:
        print(f"Error updating presence: {e}")

@tasks.loop(minutes=1)
async def server_count_updater():
    """Background task that updates server count every minute"""
    await update_server_count()

@server_count_updater.before_loop
async def before_server_count_updater():
    """Wait for bot to be ready before starting updates"""
    await bot.wait_until_ready()


# ---- OTHER -----

# Function to create achievements
# Load achievements from JSON file
def load_achievements():
    try:
        with open("achievements.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("achievements.json not found!")
        return {}

# Initialize achievements database
def init_achievements_db():
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()

    # Create achievements table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_achievements (
            user_id INTEGER,
            achievement_id TEXT,
            unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, achievement_id)
        )
    ''')

    # Create user profiles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            total_achievements INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

# Get or create user profile
def get_or_create_profile(user_id, username):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()

    # Check if profile exists
    cursor.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,))
    profile = cursor.fetchone()

    if not profile:
        # Create new profile
        cursor.execute('''
            INSERT INTO user_profiles (user_id, username, total_achievements)
            VALUES (?, ?, 0)
        ''', (user_id, username))
        conn.commit()
    else:
        # Update username if changed
        cursor.execute('''
            UPDATE user_profiles
            SET username = ?, last_updated = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (username, user_id))
        conn.commit()

    conn.close()

# Check if user has achievement
def has_achievement(user_id, achievement_id):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM user_achievements WHERE user_id = ? AND achievement_id = ?',
                   (user_id, achievement_id))
    result = cursor.fetchone()
    conn.close()
    return result is not None

# Unlock achievement for user
def unlock_achievement(user_id, username, achievement_id):
    if has_achievement(user_id, achievement_id):
        return False  # Already has achievement

    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()

    try:
        # Add achievement
        cursor.execute('''
            INSERT INTO user_achievements (user_id, achievement_id)
            VALUES (?, ?)
        ''', (user_id, achievement_id))

        # Update user profile achievement count
        cursor.execute('''
            UPDATE user_profiles
            SET total_achievements = (
                SELECT COUNT(*) FROM user_achievements WHERE user_id = ?
            ),
            last_updated = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (user_id, user_id))

        conn.commit()
        return True  # Successfully unlocked
    except Exception as e:
        print(f"Error unlocking achievement: {e}")
        return False
    finally:
        conn.close()

# Get user's unlocked achievements
def get_user_achievements(user_id):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT achievement_id, unlocked_at
        FROM user_achievements
        WHERE user_id = ?
        ORDER BY unlocked_at DESC
    ''', (user_id,))
    achievements = cursor.fetchall()
    conn.close()
    return achievements

# Get user profile data
def get_user_profile(user_id):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,))
    profile = cursor.fetchone()
    conn.close()
    return profile

# Send achievement notification
async def send_achievement_notification(channel, user, achievement_id, achievement_data):
    embed = discord.Embed(
        title="<:normal:1402996994883977237>👍 Achievement Unlocked!",
        description=f"**{achievement_data['title']}**\n{achievement_data['description']}",
        color=discord.Color.gold(),
        timestamp=datetime.now()
    )

    embed.set_author(
        name=f"{user.display_name}",
        icon_url=user.avatar.url if user.avatar else user.default_avatar.url
    )

    # Add category color coding
    category_colors = {
        "common": discord.Color.green(),
        "uncommon": discord.Color.blue(),
        "epic": discord.Color.purple(),
        "legendary": discord.Color.orange()
    }

    if achievement_data['category'] in category_colors:
        embed.color = category_colors[achievement_data['category']]

    embed.set_footer(text=f"Category: {achievement_data['category'].title()}")

    await channel.send(f"{user.mention}", embed=embed)
async def check_and_give_achievement(user, achievement_id, channel):
    """Helper function to check and give achievements"""
    all_achievements = load_achievements()
    if achievement_id in all_achievements:
        get_or_create_profile(user.id, user.display_name)
        if unlock_achievement(user.id, user.display_name, achievement_id):
            achievement_data = all_achievements[achievement_id]
            await send_achievement_notification(channel, user, achievement_id, achievement_data)
"""
def create_achievement(achievement_id, name, description, category):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO achievement_definitions
        (achievement_id, name, description, category)
        VALUES (?, ?, ?, ?)
    ''', (achievement_id, name, description, category))
    conn.commit()
    conn.close()

# Create all achievements
def init_achievements():
    # Catching achievements
    create_achievement("first_taco", "First Bite", "Catch your first taco", "catching")
    create_achievement("taco_10", "Taco Enthusiast", "Catch 10 tacos", "catching")
    create_achievement("taco_50", "Taco Collector", "Catch 50 tacos", "catching")
    create_achievement("taco_100", "Taco Master", "Catch 100 tacos", "catching")
    create_achievement("taco_500", "Taco Legend", "Catch 500 tacos", "catching")
    create_achievement("taco_1000", "Taco God", "Catch 1000 tacos", "catching")

# Function to unlock achievement
def unlock_achievement(user_id, achievement_id):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO achievements (user_id, achievement_id)
            VALUES (?, ?)
        ''', (user_id, achievement_id))
        conn.commit()
        return cursor.rowcount > 0  # True if newly unlocked
    finally:
        conn.close()

# Check if user has achievement
def has_achievement(user_id, achievement_id):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM achievements WHERE user_id = ? AND achievement_id = ?',
                   (user_id, achievement_id))
    result = cursor.fetchone()
    conn.close()
    return result is not None

# Get user's achievements
def get_user_achievements(user_id):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.achievement_id, ad.name, ad.icon, ad.points, a.unlocked_at
        FROM achievements a
        JOIN achievement_definitions ad ON a.achievement_id = ad.achievement_id
        WHERE a.user_id = ?
        ORDER BY a.unlocked_at DESC
    ''', (user_id,))
    achievements = cursor.fetchall()
    conn.close()
    return achievements

# Get achievement info
def get_achievement_info(achievement_id):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM achievement_definitions WHERE achievement_id = ?',
                   (achievement_id,))
    achievement = cursor.fetchone()
    conn.close()
    return achievement
"""
def query_ollama_with_vision(prompt, system_prompt=None, image_data=None):
    """Query the Ollama API for AI responses"""
    if not ai_config.get("AI_ENABLED", True):
        return "AI is currently disabled."

    model_name = ai_config["VISION_MODEL_NAME"] if image_data else ai_config["MODEL_NAME"]
    
    data = {
        "model": model_name,
        "prompt": prompt,
        "stream": False if image_data else True,
        "options": {
        "num_ctx": 4080,
        "num_predict": 350,
        "temperature": 0.7,
        "top_p": 0.9,
        "num_thread": 4
    }
}
    if system_prompt:
        data["system"] = system_prompt

    if image_data:
        data["images"] = [image_data]

    try:
        response = requests.post(ai_config["MODEL_API_URL"], json=data, timeout=None)
    except Exception as e:
        print(f"AI Error: {e}")
        return ai_config["ERROR_RESPONSE"]

    if response.status_code == 200:
        if image_data:
            try:
                result = response.json()
                return result.get("response", "").strip()[:ai_config["MAX_RESPONSE_LENGTH"]]
            except json.JSONDecodeError as e:
                print(f"json decode error: {e}")
                return ai_config["ERROR_RESPONSE"]
        else:
            full_response = ""
            try:
                for line in response.iter_lines():
                    if line:
                        chunk = line.decode("utf-8")
                        try:
                            json_chunk = json.loads(chunk)
                            full_response += json_chunk.get("response", "")
                            if json_chunk.get("done", False):
                                break
                        except json.JSONDecodeError:
                            print("JSON Decode Error:", chunk)
            finally:
                response.close()
            return full_response[:ai_config["MAX_RESPONSE_LENGTH"]]
    else:
        print(f"api error: {response.status_code}")
        return ai_config["ERROR_RESPONSE"]

async def process_image_for_ai(attachment):
    try:
        if not attachment.content_type or not attachment.content_type.startswith('image/'):
            return None
        if attachment.size > 10 * 1024 * 1024:
            return None

        image_data = await attachment.read()
        base64_image = base64.b64encode(image_data).decode('utf-8')

        return base64_image
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def update_conversation_memory(channel_id, user_name, message_content, bot_response=None):
    """Update conversation memory for a channel"""
    if channel_id not in conversation_memory:
        conversation_memory[channel_id] = []

    # Add user message
    conversation_memory[channel_id].append(f"{user_name}: {message_content}")

    # Add bot response if provided
    if bot_response:
        conversation_memory[channel_id].append(f"{ai_config['BOT_NAME']}: {bot_response}")

    # Keep only last MAX_MEMORY_LENGTH messages
    if len(conversation_memory[channel_id]) > MAX_MEMORY_LENGTH * 2:  # *2 for user + bot messages
        conversation_memory[channel_id] = conversation_memory[channel_id][-(MAX_MEMORY_LENGTH * 2):]

def get_conversation_context(channel_id):
    """Get conversation context for a channel"""
    if channel_id not in conversation_memory:
        return ""
    return "\n".join(conversation_memory[channel_id])

# Add this to your init_database() function - replace the existing function
# Update your init_database() function to include all the new limit columns
def init_database():
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()

    # Create table for user cooldowns with original columns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_cooldowns (
            user_id INTEGER PRIMARY KEY,
            ping_count INTEGER DEFAULT 0,
            ping_cooldown_end REAL DEFAULT 0,
            embed_fail_count INTEGER DEFAULT 0,
            embed_fail_cooldown_end REAL DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Add new columns if they don't exist (migration)
    new_columns = [
        ('amethyst_count', 'INTEGER DEFAULT 0'),
        ('amethyst_cooldown_end', 'REAL DEFAULT 0'),
        ('slaughterhouse_count', 'INTEGER DEFAULT 0'),
        ('slaughterhouse_cooldown_end', 'REAL DEFAULT 0'),
        ('hi_count', 'INTEGER DEFAULT 0'),
        ('hi_cooldown_end', 'REAL DEFAULT 0'),
        ('jet2_count', 'INTEGER DEFAULT 0'),
        ('jet2_cooldown_end', 'REAL DEFAULT 0'),
        ('tidal_wave_count', 'INTEGER DEFAULT 0'),
        ('tidal_wave_cooldown_end', 'REAL DEFAULT 0'),
        ('apple_count', 'INTEGER DEFAULT 0'),
        ('apple_cooldown_end', 'REAL DEFAULT 0'),
        ('yeah_ok_bro_count', 'INTEGER DEFAULT 0'),
        ('yeah_ok_bro_cooldown_end', 'REAL DEFAULT 0')
    ]

    for column_name, column_def in new_columns:
        try:
            cursor.execute(f'ALTER TABLE user_cooldowns ADD COLUMN {column_name} {column_def}')
            print(f"Added column: {column_name}")
        except sqlite3.OperationalError:
            # Column already exists, skip
            pass

    # Create table for bot statistics (optional)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bot_stats (
            stat_name TEXT PRIMARY KEY,
            stat_value TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create table for news channels
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news_channels (
            guild_id INTEGER,
            channel_id INTEGER,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (guild_id, channel_id)
        )
    ''')
    """cursor.execute('''
        CREATE TABLE IF NOT EXISTS achievements (
            user_id INTEGER,
            achievement_id TEXT,
            unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, achievement_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS achievement_definitions (
            achievement_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            icon TEXT,
            points INTEGER DEFAULT 0,
            category TEXT DEFAULT 'general'
        )
    ''')"""
    conn.commit()
    conn.close()
# Initialize database when bot starts

def get_user_data(user_id):
    """Get user cooldown data from database"""
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT ping_count, ping_cooldown_end, embed_fail_count, embed_fail_cooldown_end,
               amethyst_count, amethyst_cooldown_end, slaughterhouse_count, slaughterhouse_cooldown_end,
               hi_count, hi_cooldown_end, jet2_count, jet2_cooldown_end,
               tidal_wave_count, tidal_wave_cooldown_end, apple_count, apple_cooldown_end,
               yeah_ok_bro_count, yeah_ok_bro_cooldown_end
        FROM user_cooldowns WHERE user_id = ?
    ''', (user_id,))

    result = cursor.fetchone()
    conn.close()

    if result:
        return {
            'ping_count': result[0],
            'ping_cooldown_end': result[1],
            'embed_fail_count': result[2],
            'embed_fail_cooldown_end': result[3],
            'amethyst_count': result[4],
            'amethyst_cooldown_end': result[5],
            'slaughterhouse_count': result[6],
            'slaughterhouse_cooldown_end': result[7],
            'hi_count': result[8],
            'hi_cooldown_end': result[9],
            'jet2_count': result[10],
            'jet2_cooldown_end': result[11],
            'tidal_wave_count': result[12],
            'tidal_wave_cooldown_end': result[13],
            'apple_count': result[14],
            'apple_cooldown_end': result[15],
            'yeah_ok_bro_count': result[16],
            'yeah_ok_bro_cooldown_end': result[17]
        }
    else:
        return {
            'ping_count': 0, 'ping_cooldown_end': 0,
            'embed_fail_count': 0, 'embed_fail_cooldown_end': 0,
            'amethyst_count': 0, 'amethyst_cooldown_end': 0,
            'slaughterhouse_count': 0, 'slaughterhouse_cooldown_end': 0,
            'hi_count': 0, 'hi_cooldown_end': 0,
            'jet2_count': 0, 'jet2_cooldown_end': 0,
            'tidal_wave_count': 0, 'tidal_wave_cooldown_end': 0,
            'apple_count': 0, 'apple_cooldown_end': 0,
            'yeah_ok_bro_count': 0, 'yeah_ok_bro_cooldown_end': 0
        }

# Update update_user_data function to handle all fields
def update_user_data(user_id, **kwargs):
    """Update user cooldown data in database"""
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()

    # Get current data first
    current_data = get_user_data(user_id)

    # Update with new values or keep current ones
    for key in current_data:
        if key not in kwargs:
            kwargs[key] = current_data[key]

    cursor.execute('''
        INSERT OR REPLACE INTO user_cooldowns
        (user_id, ping_count, ping_cooldown_end, embed_fail_count, embed_fail_cooldown_end,
         amethyst_count, amethyst_cooldown_end, slaughterhouse_count, slaughterhouse_cooldown_end,
         hi_count, hi_cooldown_end, jet2_count, jet2_cooldown_end,
         tidal_wave_count, tidal_wave_cooldown_end, apple_count, apple_cooldown_end,
         yeah_ok_bro_count, yeah_ok_bro_cooldown_end, last_updated)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (user_id, kwargs['ping_count'], kwargs['ping_cooldown_end'],
          kwargs['embed_fail_count'], kwargs['embed_fail_cooldown_end'],
          kwargs['amethyst_count'], kwargs['amethyst_cooldown_end'],
          kwargs['slaughterhouse_count'], kwargs['slaughterhouse_cooldown_end'],
          kwargs['hi_count'], kwargs['hi_cooldown_end'],
          kwargs['jet2_count'], kwargs['jet2_cooldown_end'],
          kwargs['tidal_wave_count'], kwargs['tidal_wave_cooldown_end'],
          kwargs['apple_count'], kwargs['apple_cooldown_end'],
          kwargs['yeah_ok_bro_count'], kwargs['yeah_ok_bro_cooldown_end']))

    conn.commit()
    conn.close()

# Updated reset function
def reset_user_cooldown(user_id, cooldown_type):
    """Reset specific cooldown for a user"""
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()

    reset_fields = {
        'ping': 'ping_count = 0, ping_cooldown_end = 0',
        'embed_fail': 'embed_fail_count = 0, embed_fail_cooldown_end = 0',
        'amethyst': 'amethyst_count = 0, amethyst_cooldown_end = 0',
        'slaughterhouse': 'slaughterhouse_count = 0, slaughterhouse_cooldown_end = 0',
        'hi': 'hi_count = 0, hi_cooldown_end = 0',
        'jet2': 'jet2_count = 0, jet2_cooldown_end = 0',
        'tidal_wave': 'tidal_wave_count = 0, tidal_wave_cooldown_end = 0',
        'apple': 'apple_count = 0, apple_cooldown_end = 0',
        'yeah_ok_bro': 'yeah_ok_bro_count = 0, yeah_ok_bro_cooldown_end = 0'
    }

    if cooldown_type in reset_fields:
        cursor.execute(f'''
            UPDATE user_cooldowns
            SET {reset_fields[cooldown_type]}, last_updated = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (user_id,))

    conn.commit()
    conn.close()

# Helper function to check and handle cooldowns
def check_and_handle_cooldown(user_data, current_time, trigger_type, limit=5, cooldown_duration=60):
    """
    Check if user is on cooldown and handle counting
    Returns: (should_respond, new_count, cooldown_end_time)
    """
    count_key = f"{trigger_type}_count"
    cooldown_key = f"{trigger_type}_cooldown_end"

    # Check if user is on cooldown
    if current_time < user_data[cooldown_key]:
        return False, user_data[count_key], user_data[cooldown_key]

    # Reset if cooldown expired
    if user_data[cooldown_key] > 0:
        return True, 0, 0  # Reset and allow response

    # Increment count
    new_count = user_data[count_key] + 1

    # Check if limit reached
    if new_count >= limit:
        cooldown_end = current_time + cooldown_duration
        return True, new_count, cooldown_end  # Allow this response but set cooldown

    return True, new_count, 0  # Allow response, no cooldown yet

def add_news_channel(guild_id, channel_id):
    """Add a news channel to the database"""
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT OR IGNORE INTO news_channels (guild_id, channel_id)
            VALUES (?, ?)
        ''', (guild_id, channel_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding news channel: {e}")
        return False
    finally:
        conn.close()

def remove_news_channel(guild_id, channel_id):
    """Remove a specific news channel"""
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            DELETE FROM news_channels
            WHERE guild_id = ? AND channel_id = ?
        ''', (guild_id, channel_id))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error removing news channel: {e}")
        return False
    finally:
        conn.close()

def remove_all_news_channels(guild_id):
    """Remove all news channels for a guild"""
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            DELETE FROM news_channels
            WHERE guild_id = ?
        ''', (guild_id,))
        conn.commit()
        return cursor.rowcount
    except Exception as e:
        print(f"Error removing all news channels: {e}")
        return 0
    finally:
        conn.close()

def get_guild_news_channels(guild_id):
    """Get all news channels for a guild"""
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT channel_id FROM news_channels
            WHERE guild_id = ?
        ''', (guild_id,))
        return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        print(f"Error getting guild news channels: {e}")
        return []
    finally:
        conn.close()

def get_all_news_channels():
    """Get all news channels from all guilds"""
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT guild_id, channel_id FROM news_channels
        ''')
        return cursor.fetchall()
    except Exception as e:
        print(f"Error getting all news channels: {e}")
        return []
    finally:
        conn.close()

def count_guild_news_channels(guild_id):
    """Count how many news channels a guild has"""
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT COUNT(*) FROM news_channels
            WHERE guild_id = ?
        ''', (guild_id,))
        return cursor.fetchone()[0]
    except Exception as e:
        print(f"Error counting guild news channels: {e}")
        return 0
    finally:
        conn.close()


async def cat_timer():
    """Timer that runs every 14 minutes"""
    global last_spawn_time, timer_task

    while True:
        try:
            await asyncio.sleep(14 * 60)  # 14 minutes in seconds

            # Get the specific channel
            channel = bot.get_channel(1390518132606636094)
            if channel:
                # 5% chance to send the slash command
                if random.randint(1, 100) <= 5:
                    await channel.send("/cat type: egirl")
                    print(f"Sent /cat command at {datetime.now()}")

        except asyncio.CancelledError:
            print("Timer cancelled")
            break
        except Exception as e:
            print(f"Error in timer: {e}")

class CatPicBot:
    def __init__(self):
        self.all_images = []
        self.catapi_images = []
        self.user_images = []
        self.camera_roll_images = []
        self.special_image = None
        self.setup_assets_folder()

    def setup_assets_folder(self):
        """Create assets folder if it doesn't exist"""
        Path(ASSETS_FOLDER).mkdir(exist_ok=True)
        Path(CAMERA_ROLL_FOLDER).mkdir(exist_ok=True)
        print(f"Assets folder ready: {ASSETS_FOLDER}/")
        print(f"Camera roll folder ready: {CAMERA_ROLL_FOLDER}/")

    def scan_existing_images(self):
        """Scan assets folder for existing images and categorize them"""
        self.all_images = []
        self.catapi_images = []
        self.user_images = []
        self.camera_roll_images = []
        self.special_image = None

        # Get all image files in assets folder (main folder)
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp']
        for ext in image_extensions:
            for filepath in glob.glob(os.path.join(ASSETS_FOLDER, ext)):
                filename = os.path.basename(filepath)

                # Check if it's the special image
                if filepath == SPECIAL_IMAGE_PATH:
                    self.special_image = filepath
                    continue

                # Check if it's from The Cat API (our naming convention)
                if filename.startswith('catapi_'):
                    self.catapi_images.append(filepath)
                else:
                    # It's a user-added image
                    self.user_images.append(filepath)

                self.all_images.append(filepath)

        # Get all images from camera roll folder
        for ext in image_extensions:
            for filepath in glob.glob(os.path.join(CAMERA_ROLL_FOLDER, ext)):
                self.camera_roll_images.append(filepath)
                self.all_images.append(filepath)

        print(f"Found images: {len(self.user_images)} user images, {len(self.catapi_images)} Cat API images, {len(self.camera_roll_images)} camera roll images")
        if self.special_image:
            print("Special 'MAN' image found!")

    def calculate_image_distribution(self):
        """Calculate how many Cat API images we need for balanced distribution"""
        # Reserve percentage for special image
        available_percentage = 100.0 - SPECIAL_IMAGE_CHANCE

        # If we have user images, they get equal share with Cat API images
        total_user_images = len(self.user_images) + len(self.camera_roll_images)

        if total_user_images == 0:
            # No user images, all available percentage goes to Cat API
            needed_catapi_images = 100  # Default to 100 Cat API images
        else:
            # Each image should get equal percentage
            # If we want each image to have ~1% chance:
            target_percentage_per_image = 1.0

            # Calculate how many Cat API images we need
            # Total images = user_images + catapi_images
            # Each gets: available_percentage / total_images

            # If user images exist, balance so each image gets roughly equal chance
            if available_percentage / (total_user_images + 1) >= 0.5:
                # We can add Cat API images while keeping reasonable percentages
                needed_catapi_images = min(100, max(1, int(available_percentage - total_user_images)))
            else:
                # Too many user images, use minimal Cat API images
                needed_catapi_images = max(1, int(available_percentage * 0.1))

        return needed_catapi_images

    async def rebalance_images(self):
        """Remove old Cat API images and download new ones to balance percentages"""
        needed_catapi_images = self.calculate_image_distribution()
        current_catapi_images = len(self.catapi_images)

        print(f"Current Cat API images: {current_catapi_images}")
        print(f"Needed Cat API images: {needed_catapi_images}")

        # Remove existing Cat API images if we have too many or need to refresh
        if current_catapi_images != needed_catapi_images:
            print("Removing old Cat API images...")
            for img_path in self.catapi_images:
                try:
                    os.remove(img_path)
                    print(f"Removed: {os.path.basename(img_path)}")
                except Exception as e:
                    print(f"Failed to remove {img_path}: {e}")

            self.catapi_images.clear()

        # Download new Cat API images
        if needed_catapi_images > 0:
            await self.download_cat_images(needed_catapi_images)

    async def download_cat_images(self, count):
        """Download specified number of cat images from The Cat API"""
        print(f"Downloading {count} cat images from The Cat API...")

        async with aiohttp.ClientSession() as session:
            for i in range(count):
                try:
                    # Get random cat image data from API
                    async with session.get("https://api.thecatapi.com/v1/images/search") as response:
                        if response.status == 200:
                            cat_data = await response.json()
                            image_url = cat_data[0]['url']
                            image_id = cat_data[0]['id']

                            # Determine file extension
                            file_extension = image_url.split('.')[-1].lower()
                            if file_extension not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                                file_extension = 'jpg'

                            # Download the actual image with our naming convention
                            async with session.get(image_url) as img_response:
                                if img_response.status == 200:
                                    filename = f"catapi_{i+1:03d}_{image_id}.{file_extension}"
                                    filepath = os.path.join(ASSETS_FOLDER, filename)

                                    # Save image
                                    async with aiofiles.open(filepath, 'wb') as f:
                                        await f.write(await img_response.read())

                                    self.catapi_images.append(filepath)
                                    print(f"Downloaded {i+1}/{count}: {filename}")

                                    # Small delay to be respectful
                                    await asyncio.sleep(0.1)

                except Exception as e:
                    print(f"Failed to download image {i+1}: {e}")
                    continue

        print(f"Download complete! {len(self.catapi_images)} Cat API images ready.")

    def get_image_stats(self):
        """Get current image distribution statistics"""
        total_regular_images = len(self.all_images)

        if total_regular_images == 0:
            return {
                'total_images': 0,
                'user_images': 0,
                'catapi_images': 0,
                'special_image': bool(self.special_image),
                'percentage_per_regular': 0,
                'special_percentage': SPECIAL_IMAGE_CHANCE
            }

        available_percentage = 100.0 - SPECIAL_IMAGE_CHANCE
        percentage_per_regular = available_percentage / total_regular_images

        return {
            'total_images': total_regular_images,
            'user_images': len(self.user_images),
            'camera_roll_images': len(self.camera_roll_images),
            'catapi_images': len(self.catapi_images),
            'special_image': bool(self.special_image),
            'percentage_per_regular': percentage_per_regular,
            'special_percentage': SPECIAL_IMAGE_CHANCE
        }

    def get_random_image(self):
        """Get a random image with weighted probability"""
        # Generate random number from 1 to 1000
        roll = random.randint(1, 1000)

        # 1 in 1000 chance for special image (0.1%)
        if roll == 1 and self.special_image and os.path.exists(self.special_image):
            return self.special_image, "special"

        # Otherwise, return random image from all available images
        if self.all_images:
            selected_image = random.choice(self.all_images)

            # Determine image type
            if selected_image in self.catapi_images:
                return selected_image, "catapi"
            elif selected_image in self.camera_roll_images:
                return selected_image, "camera_roll"
            else:
                return selected_image, "user"

        return None, None

# Initialize bot instance
cat_bot = CatPicBot()

@bot.event
async def on_ready():
    """Bot startup event"""
    print(f'{bot.user} has landed on Discord!')
    print("=" * 50)

    # Scan existing images
    cat_bot.scan_existing_images()

    # Get current stats
    stats = cat_bot.get_image_stats()
    print(f"Current distribution:")
    print(f"  User images: {stats['user_images']}")
    print(f"  Camera roll images: {stats['camera_roll_images']}")
    print(f"  Cat API images: {stats['catapi_images']}")
    print(f"  Special image: {'✅' if stats['special_image'] else '❌'}")
    print(f"  Percentage per regular image: {stats['percentage_per_regular']:.2f}%")

    # Rebalance if needed
    await cat_bot.rebalance_images()

    # Update stats after rebalancing
    cat_bot.scan_existing_images()
    final_stats = cat_bot.get_image_stats()

    print("\nFinal distribution:")
    print(f"  User images: {final_stats['user_images']} ({final_stats['percentage_per_regular']:.2f}% each)")
    print(f"  Camera roll images: {final_stats['camera_roll_images']} ({final_stats['percentage_per_regular']:.2f}% each)")
    print(f"  Cat API images: {final_stats['catapi_images']} ({final_stats['percentage_per_regular']:.2f}% each)")
    print(f"  Special image: {final_stats['special_percentage']}% chance")
    print(f"  Total regular images: {final_stats['total_images']}")

    print("\nBot is ready to serve cat pics!")
    print("=" * 50)
    """init_database()
    init_achievements()"""
    if not server_count_updater.is_running():
        server_count_updater.start()
        print("Started server count updater")
    await update_server_count()
    async def setup_achievements():
        init_achievements_db()
        print("Achievement system initialized!")
    await setup_achievements()
    if ai_config.get("AI_ENABLED", True):
        print(f"AI Chat enabled using model: {ai_config['MODEL_NAME']}")
    else:
        print("AI Chat is disabled")
    timer_task = asyncio.create_task(cat_timer())
    """await bot.change_presence(
        status=discord.Status.dnd,
        activity=discord.Streaming(
            name="radio or smth",
            url="https://www.youtube.com/watch?v=dTS_aNfpbIM"
        )
    )"""

    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")


@bot.event
async def on_message(message):
    global last_spawn_time, timer_task
    if message.author == bot.user and message.author.id not in allowed_bots:
        return

    user_id = message.author.id
    current_time = time.time()
    user_data = get_user_data(user_id)

    # Track what needs to be updated
    updates = {}
    async def check_and_give_achievement(user, achievement_id, channel):
        """Helper function to check and give achievements"""
        all_achievements = load_achievements()
        if achievement_id in all_achievements:
            get_or_create_profile(user.id, user.display_name)
            if unlock_achievement(user.id, user.display_name, achievement_id):
                achievement_data = all_achievements[achievement_id]
                await send_achievement_notification(channel, user, achievement_id, achievement_data)
    if message.content == bot.user.mention:
        await check_and_give_achievement(message.author, "tf_you_want", message.channel)
    # Handle bot mention (ping) - existing logic
    if bot.user.mentioned_in(message) and ai_config.get("AI_ENABLED", True):
        # Remove the mention from the message content
        clean_content = message.content.replace(f'<@{bot.user.id}>', '').strip()
        image_data = None
        if message.attachments:
            for attachment in message.attachments:
                image_data = await process_image_for_ai(attachment)
                if image_data:
                    break
        if clean_content or image_data:
                # Only respond if there's actual content after the mention
            async with message.channel.typing():
                try:
                    # Get conversation context
                    context = get_conversation_context(message.channel.id)
                    if len(context) > 800:
                        context = context[-800:]

                    if image_data:
                        system_prompt = f"""You are {ai_config['BOT_NAME']}, a Discord bot with vision capabilities. You can see and analyze images that users send. Be descriptive when needed to describe images. You understand internet culture and memes."""
                        if clean_content:
                            prompt = f"{message.author.name} sent an image and asked: {clean_content}"
                        else:
                            prompt = f"{message.author.name} sent an image. Please describe what you see."
                        if context:
                            prompt = f"Recent chat: {context}\n\n{prompt}"
                    else:
# Build the promp
                        system_prompt = f"""You are {ai_config['BOT_NAME']}. {ai_config['PROMPT_MAIN']}
{ai_config['KNOWLEDGE']}
{ai_config['PERSONALITY']}
Keep responses concise and natural for Discord chat."""

                    # Include context if available
                        if context:
                            prompt = f"Previous conversation:\n{context}\n\n{message.author.name}: {clean_content}"
                        else:
                            prompt = f"{message.author.name}: {clean_content}"

                    # Get AI response
                    ai_response = await asyncio.wait_for(
                        asyncio.to_thread(query_ollama_with_vision, prompt, system_prompt, image_data),
                        timeout=None
                    )
                    # Send response
                    if ai_response and ai_response != ai_config["ERROR_RESPONSE"]:
                        # Split long responses if needed
                        if len(ai_response) > 2000:
                            chunks = [ai_response[i:i+2000] for i in range(0, len(ai_response), 2000)]
                            for chunk in chunks:
                                await message.reply(chunk, allowed_mentions=discord.AllowedMentions.none())
                        else:
                            await message.reply(ai_response, allowed_mentions=discord.AllowedMentions.none())

                        # Update conversation memory
                        memory_content = clean_content if clean_content else "[sent an image]"
                        update_conversation_memory(message.channel.id, message.author.name, memory_content, ai_response)
                    else:
                        await message.reply("Sorry, I'm having trouble thinking right now. Try again later!")
                except asyncio.TimeoutError:
                    await message.reply("That's taking too long to process, Try smaller image or shorter msg.")
                except Exception as e:
                    print(f"AI Error: {e}")
                    await message.reply("Sorry, something went wrong! Please try again.")

    # Handle embed fail
    if 'embed fail' in message.content or message.content == "embed fail ig?":
        should_respond, new_count, cooldown_end = check_and_handle_cooldown(
            user_data, current_time, 'embed_fail', limit=3, cooldown_duration=60
        )

        if should_respond:
            await message.channel.send("https://cdn.discordapp.com/attachments/1321992659384012901/1401969285164826697/watermark.gif")
            updates['embed_fail_count'] = new_count
            if cooldown_end > 0:
                updates['embed_fail_cooldown_end'] = cooldown_end
                await message.channel.send(f"{message.author.mention} wait 1 min before saying that again")
        else:
            await message.channel.send("you need to wait 1 min before saying that again")
            return

    # Handle amethyst
    if 'amethyst' in message.content or 'Amethyst' in message.content or 'AMETHYST' in message.content:
        should_respond, new_count, cooldown_end = check_and_handle_cooldown(
            user_data, current_time, 'amethyst', limit=3, cooldown_duration=120
        )

        if should_respond:
            await message.channel.send("https://tenor.com/view/amethyst-alpha-react-geometry-dash-gif-7140286725926478147")
            updates['amethyst_count'] = new_count
            if cooldown_end > 0:
                updates['amethyst_cooldown_end'] = cooldown_end
                await message.channel.send(f"{message.author.mention} wait 2 min before mentioning amethyst again")
        else:
            await message.channel.send("wait 2 min before mentioning amethyst again")
            return

    # Handle slaughterhouse
    if 'slaughterhouse' in message.content or 'Slaughterhouse' in message.content or 'SLAUGHTERHOUSE' in message.content:
        should_respond, new_count, cooldown_end = check_and_handle_cooldown(
            user_data, current_time, 'slaughterhouse', limit=2, cooldown_duration=180
        )

        if should_respond:
            await message.channel.send("https://tenor.com/view/slaughterhouse-gd-cracked-drops-phone-phone-gif-504258885114218717")
            updates['slaughterhouse_count'] = new_count
            if cooldown_end > 0:
                updates['slaughterhouse_cooldown_end'] = cooldown_end
                await message.channel.send(f"{message.author.mention} wait 3 min before mentioning slaughterhouse again")
        else:
            await message.channel.send("wait 3 min before mentioning slaughterhouse again")
            return

    # Handle hi variations
    if message.content in hi_vars:
        should_respond, new_count, cooldown_end = check_and_handle_cooldown(
            user_data, current_time, 'hi', limit=4, cooldown_duration=90
        )

        if should_respond:
            await message.channel.send("https://cdn.discordapp.com/attachments/1401656227540500541/1401927914269839600/IMG_1136.png")
            await check_and_give_achievement(message.author, "welcome", message.channel)
            updates['hi_count'] = new_count
            if cooldown_end > 0:
                updates['hi_cooldown_end'] = cooldown_end
                await message.channel.send(f"{message.author.mention} wait 1.5 min before saying hi again")
        else:
            await message.channel.send("wait 1.5 min before saying hi again")
            return

    # Handle Jet2 holiday
    if (message.content.startswith("DARLING HOLD MY HAND! Nothing beats a Jet2 Holiday") or
        message.content.startswith("jet2 holiday") or message.content.startswith("Jet2 holiday") or
        message.content.startswith("Jet2 Holiday")):

        should_respond, new_count, cooldown_end = check_and_handle_cooldown(
            user_data, current_time, 'jet2', limit=2, cooldown_duration=180
        )

        if should_respond:
            reactionbc = await message.channel.send("DARLING HOLD MY HAND! Nothing beats a Jet2 Holiday and right you can save 50 pounds per person! That's 200 pounds off for a family of four!")
            await message.add_reaction("✈️")
            updates['jet2_count'] = new_count
            if cooldown_end > 0:
                updates['jet2_cooldown_end'] = cooldown_end
                await message.channel.send(f"{message.author.mention} wait 3 min before mentioning Jet2 again")
        else:
            await message.channel.send("wait 3 min before mentioning Jet2 again")
            return

    # Handle tidal wave
    if ('tidal wave' in message.content or message.content.startswith('tidal wave') or
        'Tidal wave' in message.content or 'Tidal Wave' in message.content or 'TIDAL WAVE' in message.content):

        should_respond, new_count, cooldown_end = check_and_handle_cooldown(
            user_data, current_time, 'tidal_wave', limit=3, cooldown_duration=120
        )

        if should_respond:
            await message.channel.send(">>>TIDAL>>>\n<<<WAVE<<<")
            updates['tidal_wave_count'] = new_count
            if cooldown_end > 0:
                updates['tidal_wave_cooldown_end'] = cooldown_end
                await message.channel.send(f"{message.author.mention} wait 2 min before mentioning tidal wave again")
        else:
            await message.channel.send("wait 2 min before mentioning tidal wave again")
            return

    # Handle apple (reaction only, lighter limit)
    if 'apple' in message.content or 'Apple' in message.content or 'APPLE' in message.content:
        should_respond, new_count, cooldown_end = check_and_handle_cooldown(
            user_data, current_time, 'apple', limit=8, cooldown_duration=60
        )

        if should_respond:
            await message.add_reaction("<:appol:1399818634108473495>")
            updates['apple_count'] = new_count
            if cooldown_end > 0:
                updates['apple_cooldown_end'] = cooldown_end
        # No message for apple cooldown since it's just a reaction

    # Handle "yeah ok bro"
    if message.content == "yeah ok bro":
        should_respond, new_count, cooldown_end = check_and_handle_cooldown(
            user_data, current_time, 'yeah_ok_bro', limit=3, cooldown_duration=180
        )

        if should_respond:
            await message.channel.send(f"i agree with {message.author.mention}.")
            updates['yeah_ok_bro_count'] = new_count
            if cooldown_end > 0:
                updates['yeah_ok_bro_cooldown_end'] = cooldown_end
                await message.channel.send(f"{message.author.mention} wait 3 min before saying that again")
        else:
            await message.channel.send("wait 3 min before saying that again")
            return

    # Update database if there are changes
    if updates:
        update_user_data(user_id, **updates)

    # Handle non-limited triggers (these don't have cooldowns)
    if message.guild is None:
        await message.channel.send("u gay shall be")
        await check_and_give_achievement(message.author, "u_gay_shall_be", message.channel)

    # Handle bot interactions and timers (existing logic)
    if message.author == bot.user and message.author.id in allowed_bots and 'cat has spawned out of nowhere!! Say  "cat" to catch it!' in message.content:
        await message.channel.send("cat")

    if (message.author.id == 1402195680830685330 and
        'has spawned out of nowhere!! Say "cat" to catch it!' in message.content):
        print(f"Spawn message detected at {datetime.now()}")
        last_spawn_time = datetime.now()
        if timer_task and not timer_task.done():
            timer_task.cancel()
            print("Timer reset!")
        timer_task = asyncio.create_task(cat_timer())

    if "skibidi" in message.content.lower():
        await check_and_give_achievement(message.author, "brainrotted", message.channel)
    if "❤️" in message.content or "💖" in message.content or ":heart:" in message.content or ":mending_heart:" in message.content:
        await check_and_give_achievement(message.author, "i_love_you", message.channel)
@bot.tree.command(name="info", description="yeah ok bro")
async def info_command(interaction: discord.Interaction):
    await interaction.response.send_message('**BOT INFO**\n*This is a bot specifically made for Unique Server Name.*\nThis bot was coded by lampyt and the ideas are from not_0ne and some of Unique Server Name.\nThis bot does very random stuff like show cat pics, says hi to you and more goofy things <:okcool:1394047147246223401>, including achievements and AI based on qwen2.5 and taco catching coming soon.\nTacos made by not_0ne <:normal:1402996994883977237>👍\n-# llama3.2 AI based on QT-AI by @mari2')

@bot.tree.command(name="roll", description="Roll a dice for GL achievement")
@app_commands.describe(guess="Your guess (1-6)")
async def roll_command(interaction: discord.Interaction, guess: int):
    if guess < 1 or guess > 6:
        await interaction.response.send_message("Please guess a number between 1 and 6!", ephemeral=True)
        return

    roll_result = random.randint(1, 6)

    if guess == roll_result:
        await interaction.response.send_message(f"🎲 Rolled: **{roll_result}**\n🎉 Success! 100XP")
        await check_and_give_achievement(interaction.user, "gl", interaction.channel)
    else:
        await interaction.response.send_message(f"🎲 Rolled: **{roll_result}**\n❌ Not sigma! You guessed {guess}.")

@bot.tree.command(name="achievements", description="View your achievements")
async def achievements_command(interaction: discord.Interaction, user: discord.Member = None):
    target_user = user if user else interaction.user
    await check_and_give_achievement(target_user, "the_grand_list", interaction.channel)
    # Ensure user has profile
    get_or_create_profile(target_user.id, target_user.display_name)

    # Load all achievements
    all_achievements = load_achievements()
    user_achievements = get_user_achievements(target_user.id)
    unlocked_ids = [ach[0] for ach in user_achievements]

    # Create main embed
    embed = discord.Embed(
        title=f"🏆 {target_user.display_name}'s Achievements",
        description=f"**Achievements unlocked: {len(unlocked_ids)}/{len(all_achievements)}**",
        color=discord.Color.gold(),
        timestamp=datetime.now()
    )

    embed.set_thumbnail(url=target_user.avatar.url if target_user.avatar else target_user.default_avatar.url)

    # Group achievements by category
    categories = {}
    for ach_id, ach_data in all_achievements.items():
        category = ach_data['category']
        if category not in categories:
            categories[category] = []
        categories[category].append((ach_id, ach_data))

    # Add achievements to embed by category
    for category, achievements in categories.items():
        achievement_list = []
        for ach_id, ach_data in achievements:
            if ach_id in unlocked_ids:
                achievement_list.append(f"✅ **{ach_data['title']}**\n└ {ach_data['description']}")
            else:
                achievement_list.append(f"🔒 **{ach_data['title']}**\n└ {ach_data['description']}")

        embed.add_field(
            name=f"{category.title()} ({sum(1 for ach_id, _ in achievements if ach_id in unlocked_ids)}/{len(achievements)})",
            value="\n\n".join(achievement_list),
            inline=False
        )

    embed.set_footer(text="Complete challenges to unlock more achievements!")
    await interaction.response.send_message(embed=embed)

# Give achievement command (Admin only)
@bot.tree.command(name="giveachievement", description="Give an achievement to a user (Admin only)")
@app_commands.describe(
    user="The user to give the achievement to",
    achievement_id="The achievement ID to give"
)
async def give_achievement_command(interaction: discord.Interaction, user: discord.Member, achievement_id: str):
    # Check permissions
    if interaction.user.id != 1056952213056004118 and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You don't have permission to use this command!", ephemeral=True)
        return

    # Load achievements
    all_achievements = load_achievements()

    if achievement_id not in all_achievements:
        available_achievements = "\n".join([f"`{ach_id}` - {ach_data['title']}" for ach_id, ach_data in all_achievements.items()])
        await interaction.response.send_message(
            f"Invalid achievement ID! Available achievements:\n{available_achievements}",
            ephemeral=True
        )
        return

    # Ensure user has profile
    get_or_create_profile(user.id, user.display_name)

    # Try to unlock achievement
    if unlock_achievement(user.id, user.display_name, achievement_id):
        achievement_data = all_achievements[achievement_id]
        await interaction.response.send_message(
            f"✅ Successfully gave **{achievement_data['title']}** to {user.mention}!"
        )

        # Send achievement notification
        await send_achievement_notification(interaction.channel, user, achievement_id, achievement_data)
    else:
        await interaction.response.send_message(
            f"❌ {user.mention} already has this achievement or an error occurred!",
            ephemeral=True
        )


# Enhanced announce command with embed customization options
@bot.tree.command(name="announce", description="Send announcement to all news channels with custom embed")
@app_commands.describe(
    announcement="The main announcement message",
    title="Custom title for the embed (optional)",
    color="Embed color: red, blue, green, purple, orange, yellow, or hex code like #FF0000 (optional)",
    thumbnail="URL for thumbnail image (optional)",
    image="URL for main image (optional)",
    footer="Custom footer text (optional)",
    ping_everyone="Whether to ping @everyone (default: False)",
    urgent="Mark as urgent with special styling (default: False)",
    timestamp_format="Timestamp format (optional)"
)
@app_commands.choices(
    color=[
        app_commands.Choice(name="Red", value="red"),
        app_commands.Choice(name="Blue", value="blue"),
        app_commands.Choice(name="Green", value="green"),
        app_commands.Choice(name="Purple", value="purple"),
        app_commands.Choice(name="Orange", value="orange"),
        app_commands.Choice(name="Yellow", value="yellow"),
        app_commands.Choice(name="Random", value="random")
    ],
    timestamp_format=[
        app_commands.Choice(name="Discord Default (Today at 2:30 PM)", value="discord"),
        app_commands.Choice(name="Date Format (05/08/2025 at 2:30 PM)", value="date"),
        app_commands.Choice(name="ISO Format (2025-08-05 14:30)", value="iso"),
        app_commands.Choice(name="Long Format (August 5, 2025 at 2:30 PM)", value="long"),
        app_commands.Choice(name="Short Format (Aug 5, 2:30 PM)", value="short"),
        app_commands.Choice(name="No Timestamp", value="none")
    ]
)
async def announce_command(
    interaction: discord.Interaction,
    announcement: str,
    title: str = None,
    color: str = "blue",
    thumbnail: str = None,
    image: str = None,
    footer: str = None,
    ping_everyone: bool = False,
    urgent: bool = False,
    timestamp_format: str = "discord"
):
    # Check if user has permission
    if interaction.user.id != 1056952213056004118:  # Your user ID
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    # Process newlines in announcement text
    announcement = announcement.replace('\\n', '\n')
    # Get all news channels
    news_channels = get_all_news_channels()

    if not news_channels:
        await interaction.followup.send("No news channels are configured.", ephemeral=True)
        return

    # Parse color
    embed_color = discord.Color.blue()  # default
    if color:
        color_map = {
            "red": discord.Color.red(),
            "blue": discord.Color.blue(),
            "green": discord.Color.green(),
            "purple": discord.Color.purple(),
            "orange": discord.Color.orange(),
            "yellow": discord.Color.yellow(),
            "random": discord.Color.random()
        }

        if color in color_map:
            embed_color = color_map[color]
        elif color.startswith('#') and len(color) == 7:
            try:
                # Convert hex to discord color
                hex_value = int(color[1:], 16)
                embed_color = discord.Color(hex_value)
            except ValueError:
                embed_color = discord.Color.blue()  # fallback

    # Create embed
    if urgent:
        embed_title = f"🚨 URGENT: {title}" if title else "🚨 URGENT ANNOUNCEMENT"
        embed_color = discord.Color.red()  # Override color for urgent
    else:
        embed_title = title if title else "📢 Announcement"

    # Handle timestamp based on format choice
    if timestamp_format == "none":
        embed = discord.Embed(
            title=embed_title,
            description=announcement,
            color=embed_color
        )
    else:
        embed = discord.Embed(
            title=embed_title,
            description=announcement,
            color=embed_color,
            timestamp=datetime.now()
        )

    # Add optional elements
    if thumbnail:
        try:
            embed.set_thumbnail(url=thumbnail)
        except:
            pass  # Invalid URL, skip

    if image:
        try:
            embed.set_image(url=image)
        except:
            pass  # Invalid URL, skip

    # Set footer with custom timestamp format
    current_time = datetime.now()

    if footer:
        footer_text = footer
    elif urgent:
        footer_text = "⚠️ Urgent Bot Announcement"
    else:
        footer_text = "Bot Announcement System"

    # Add custom timestamp to footer if not using Discord's default
    if timestamp_format == "date":
        footer_text += f" • {current_time.strftime('%d/%m/%Y at %I:%M %p')}"
    elif timestamp_format == "iso":
        footer_text += f" • {current_time.strftime('%Y-%m-%d %H:%M')}"
    elif timestamp_format == "long":
        footer_text += f" • {current_time.strftime('%B %d, %Y at %I:%M %p')}"
    elif timestamp_format == "short":
        footer_text += f" • {current_time.strftime('%b %d, %I:%M %p')}"
    elif timestamp_format == "none":
        footer_text += f" • {current_time.strftime('%d/%m/%Y at %I:%M %p')}"
    # For "discord" format, we let Discord handle it with the embed timestamp

    embed.set_footer(text=footer_text)

    # Don't add author section anymore - removed as requested

    successful_sends = 0
    failed_sends = 0
    failed_channels = []

    # Send announcement to all channels
    for guild_id, channel_id in news_channels:
        try:
            channel = bot.get_channel(channel_id)
            if channel:
                # Prepare message content
                message_content = ""
                if ping_everyone:
                    message_content = "<@&1392328926696706089>"
                elif urgent:
                    message_content = "⚠️ **URGENT ANNOUNCEMENT** ⚠️"

                # Send the message
                if message_content:
                    await channel.send(content=message_content, embed=embed)
                else:
                    await channel.send(embed=embed)

                successful_sends += 1
            else:
                failed_sends += 1
                failed_channels.append(f"Channel {channel_id} (not found)")
        except discord.Forbidden:
            failed_sends += 1
            failed_channels.append(f"Channel {channel_id} (no permissions)")
        except Exception as e:
            print(f"Failed to send to channel {channel_id}: {e}")
            failed_sends += 1
            failed_channels.append(f"Channel {channel_id} (error: {str(e)[:50]})")

    # Create summary embed
    summary_embed = discord.Embed(
        title="📊 Announcement Summary",
        color=discord.Color.green() if failed_sends == 0 else discord.Color.orange(),
        timestamp=datetime.now()
    )

    summary_embed.add_field(
        name="✅ Successful Sends",
        value=str(successful_sends),
        inline=True
    )

    summary_embed.add_field(
        name="❌ Failed Sends",
        value=str(failed_sends),
        inline=True
    )

    summary_embed.add_field(
        name="📈 Success Rate",
        value=f"{(successful_sends / (successful_sends + failed_sends) * 100):.1f}%" if (successful_sends + failed_sends) > 0 else "0%",
        inline=True
    )

    # Add failed channels if any
    if failed_channels:
        failed_list = "\n".join(failed_channels[:10])  # Limit to 10 to avoid embed limits
        if len(failed_channels) > 10:
            failed_list += f"\n... and {len(failed_channels) - 10} more"
        summary_embed.add_field(
            name="Failed Channels",
            value=f"```{failed_list}```",
            inline=False
        )

    summary_embed.set_footer(text="Announcement completed")

    await interaction.followup.send(embed=summary_embed, ephemeral=True)

@bot.event
async def on_guild_join(guild):
    """Update server count immediately when bot joins a server"""
    print(f"Joined server: {guild.name}")
    await update_server_count()

@bot.event
async def on_guild_remove(guild):
    """Update server count immediately when bot leaves a server"""
    print(f"Left server: {guild.name}")
    await update_server_count()

# Optional: Add a preview command to test embed appearance
""""@bot.tree.command(name="preview_announcement", description="Preview how your announcement will look")
@app_commands.describe(
    announcement="The main announcement message",
    title="Custom title for the embed (optional)",
    color="Embed color (optional)",
    thumbnail="URL for thumbnail image (optional)",
    image="URL for main image (optional)",
    footer="Custom footer text (optional)",
    urgent="Mark as urgent with special styling (default: False)",
    timestamp_format="Timestamp format (optional)"
)
@app_commands.choices(
    color=[
        app_commands.Choice(name="Red", value="red"),
        app_commands.Choice(name="Blue", value="blue"),
        app_commands.Choice(name="Green", value="green"),
        app_commands.Choice(name="Purple", value="purple"),
        app_commands.Choice(name="Orange", value="orange"),
        app_commands.Choice(name="Yellow", value="yellow"),
        app_commands.Choice(name="Random", value="random")
    ],
    timestamp_format=[
        app_commands.Choice(name="Discord Default (Today at 2:30 PM)", value="discord"),
        app_commands.Choice(name="Date Format (05/08/2025 at 2:30 PM)", value="date"),
        app_commands.Choice(name="ISO Format (2025-08-05 14:30)", value="iso"),
        app_commands.Choice(name="Long Format (August 5, 2025 at 2:30 PM)", value="long"),
        app_commands.Choice(name="Short Format (Aug 5, 2:30 PM)", value="short"),
        app_commands.Choice(name="No Timestamp", value="none")
    ]
)
async def preview_announcement_command(
    interaction: discord.Interaction,
    announcement: str,
    title: str = None,
    color: str = "blue",
    thumbnail: str = None,
    image: str = None,
    footer: str = None,
    urgent: bool = False,
    timestamp_format: str = "discord"
):
    # Check if user has permission
    if interaction.user.id != 1056952213056004118:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    # Parse color (same logic as announce command)
    embed_color = discord.Color.blue()
    if color:
        color_map = {
            "red": discord.Color.red(),
            "blue": discord.Color.blue(),
            "green": discord.Color.green(),
            "purple": discord.Color.purple(),
            "orange": discord.Color.orange(),
            "yellow": discord.Color.yellow(),
            "random": discord.Color.random()
        }

        if color in color_map:
            embed_color = color_map[color]
        elif color.startswith('#') and len(color) == 7:
            try:
                hex_value = int(color[1:], 16)
                embed_color = discord.Color(hex_value)
            except ValueError:
                embed_color = discord.Color.blue()

    # Create embed (same logic as announce command)
    if urgent:
        embed_title = f"🚨 URGENT: {title}" if title else "🚨 URGENT ANNOUNCEMENT"
        embed_color = discord.Color.red()
    else:
        embed_title = title if title else "📢 Announcement"

    # Handle timestamp based on format choice
    if timestamp_format == "none":
        embed = discord.Embed(
            title=embed_title,
            description=announcement,
            color=embed_color
        )
    else:
        embed = discord.Embed(
            title=embed_title,
            description=announcement,
            color=embed_color,
            timestamp=datetime.now()
        )

    if thumbnail:
        try:
            embed.set_thumbnail(url=thumbnail)
        except:
            pass

    if image:
        try:
            embed.set_image(url=image)
        except:
            pass

    # Set footer with custom timestamp format (same logic as announce command)
    current_time = datetime.now()

    if footer:
        footer_text = footer
    elif urgent:
        footer_text = "⚠️ Urgent Bot Announcement"
    else:
        footer_text = "Bot Announcement System"

    # Add custom timestamp to footer if not using Discord's default
    if timestamp_format == "date":
        footer_text += f" • {current_time.strftime('%d/%m/%Y at %I:%M %p')}"
    elif timestamp_format == "iso":
        footer_text += f" • {current_time.strftime('%Y-%m-%d %H:%M')}"
    elif timestamp_format == "long":
        footer_text += f" • {current_time.strftime('%B %d, %Y at %I:%M %p')}"
    elif timestamp_format == "short":
        footer_text += f" • {current_time.strftime('%b %d, %I:%M %p')}"
    elif timestamp_format == "none":
        footer_text += f" • {current_time.strftime('%d/%m/%Y at %I:%M %p')}"

    embed.set_footer(text=footer_text)

    # Add preview notice
    preview_embed = discord.Embed(
        title="📋 Announcement Preview",
        description="This is how your announcement will look:",
        color=discord.Color.yellow()
    )

    await interaction.response.send_message(
        content="**PREVIEW MODE** - This announcement was NOT sent to news channels:",
        embeds=[preview_embed, embed],
        ephemeral=True
    )"""
@bot.tree.command(name="news", description="Manage news channels")
@app_commands.describe(
    action="What to do (set/remove/disable/list)",
    channel="Channel to add or remove (optional for disable/list)"
)
@app_commands.choices(action=[
    app_commands.Choice(name="set", value="set"),
    app_commands.Choice(name="remove", value="remove"),
    app_commands.Choice(name="disable", value="disable"),
    app_commands.Choice(name="list", value="list")
])
async def news_command(interaction: discord.Interaction, action: str, channel: discord.TextChannel = None):
    # Check if user has manage_channels permission
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("You need the 'Manage Channels' permission to use this command.", ephemeral=True)
        return

    guild_id = interaction.guild.id

    if action == "set":
        if not channel:
            await interaction.response.send_message("Please specify a channel to set as news channel.", ephemeral=True)
            return

        # Check if guild already has 2 news channels
        current_count = count_guild_news_channels(guild_id)
        if current_count >= 2:
            await interaction.response.send_message("This server already has the maximum of 2 news channels. Remove one first.", ephemeral=True)
            return

        # Check if channel is already a news channel
        current_channels = get_guild_news_channels(guild_id)
        if channel.id in current_channels:
            await interaction.response.send_message(f"{channel.mention} is already set as a news channel.", ephemeral=True)
            return

        # Add the channel
        if add_news_channel(guild_id, channel.id):
            await interaction.response.send_message(f"✅ {channel.mention} has been set as a news channel!")
        else:
            await interaction.response.send_message("Failed to add news channel. Please try again.", ephemeral=True)

    elif action == "remove":
        if not channel:
            await interaction.response.send_message("Please specify a channel to remove from news channels.", ephemeral=True)
            return

        if remove_news_channel(guild_id, channel.id):
            await interaction.response.send_message(f"✅ {channel.mention} has been removed from news channels.")
        else:
            await interaction.response.send_message(f"{channel.mention} was not set as a news channel.", ephemeral=True)

    elif action == "disable":
        removed_count = remove_all_news_channels(guild_id)
        if removed_count > 0:
            await interaction.response.send_message(f"✅ Removed {removed_count} news channel(s) from this server.")
        else:
            await interaction.response.send_message("This server has no news channels to remove.", ephemeral=True)

    elif action == "list":
        current_channels = get_guild_news_channels(guild_id)
        if not current_channels:
            await interaction.response.send_message("This server has no news channels configured.", ephemeral=True)
            return

        channel_mentions = []
        for channel_id in current_channels:
            channel_obj = bot.get_channel(channel_id)
            if channel_obj:
                channel_mentions.append(channel_obj.mention)
            else:
                channel_mentions.append(f"<#{channel_id}> (channel not found)")

        embed = discord.Embed(
            title="📰 News Channels",
            description=f"This server has {len(current_channels)}/2 news channels:\n" + "\n".join(channel_mentions),
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="goofygif", description="my name is quindile dingle hehehehehehehehe")
async def goofygif_command(interaction: discord.Interaction):
    random_num = random.randint(1, 25)
    print(goofy_gifs[random_num])  # debugging stuff
    goofy_gif = goofy_gifs[random_num]

    if random_num == 3:
        await interaction.response.send_message("btw @qualitymaxxmemes is <@1056952213056004118>'s nickname in Kingsammelot Kingdom Server.")
        await interaction.followup.send(goofy_gif)
    elif random_num == 14:
        await interaction.response.send_message("oh look! this one has sound, also it isn't really goofy, i just wanted to add it since it had sound somehow.")
        await interaction.followup.send(goofy_gif)
    elif random_num == 19:
        await interaction.response.send_message("crazy that the entire shrek movie became a video on imgur that could be embedded on discord wow.")
        await interaction.followup.send(goofy_gif)
    else:
        await interaction.response.send_message(goofy_gif)

@bot.tree.command(name="catpic", description="Get a random cat picture!")
async def catpic_command(interaction: discord.Interaction):
    """Slash command to send a random cat picture"""
    try:
        image_path, image_type = cat_bot.get_random_image()

        if image_path and os.path.exists(image_path):
            filename = os.path.basename(image_path)

            # Create embed based on image type
            if image_type == "special":
                embed = discord.Embed(
                    title="_ _",
                    color=discord.Color.random()
                )
            elif image_type == "catapi":
                embed = discord.Embed(
                    title="_ _",
                    color=discord.Color.random()
                )
            elif image_type == "camera_roll":
                embed = discord.Embed(
                    title="_ _",
                    color=discord.Color.random()
                )
            else:  # user image
                embed = discord.Embed(
                    title="_ _",
                    color=discord.Color.random()
                )

            # Send image with embed
            with open(image_path, 'rb') as f:
                file = discord.File(f, filename=filename)
                embed.set_image(url=f"attachment://{filename}")
                await interaction.response.send_message(embed=embed, file=file)

        else:
            # Fallback if no images available
            embed = discord.Embed(
                title="Error.",
                description="No cat pics currently available.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)

    except Exception as e:
        print(f"Error in catpic command: {e}")
        await interaction.response.send_message("An error occured.", ephemeral=True)

@bot.tree.command(name="rebalancecatpics", description="Rebalance image distribution (Admin only)")
async def rebalance_command(interaction: discord.Interaction):
    """Admin command to rebalance images"""
    if not interaction.user.guild_permissions.administrator or interaction.user.id != "1056952213056004118":
        await interaction.response.send_message("You need administrator permissions to use this command!", ephemeral=True)
        return

    await interaction.response.send_message("Rebalancing image distribution... This may take a moment!", ephemeral=True)

    try:
        # Rescan and rebalance
        cat_bot.scan_existing_images()
        await cat_bot.rebalance_images()
        cat_bot.scan_existing_images()

        stats = cat_bot.get_image_stats()


        await interaction.followup.send("Rebalancing complete.")

    except Exception as e:
        print(f"Error in rebalance command: {e}")
        await interaction.followup.send("Failed to rebalance images. Check console for errors.")

# Setup instructions
def main():
    """Main function with setup instructions"""
    print("=== Dynamic Cat Pic Discord Bot ===")
    print("Features:")
    print("- Automatically balances image percentages")
    print("- Supports user-added images in assets/ folder")
    print("- Special 'MAN' image with 0.1% chance")
    print("- Dynamic Cat API image management")
    print("\nSetup:")
    print("1. pip install discord.py aiohttp aiofiles requests")
    print("2. Place 'MAN' horse image as 'assets/man_horse.jpg'")
    print("3. Add your own cat images to 'assets/' folder")
    print("4. Add camera roll images to 'assets/camera_roll/' folder")
    print("5. Set bot token and run!")
    print("\nThe bot will automatically:")
    print("- Scan for existing images")
    print("- Calculate needed Cat API images")
    print("- Download/remove Cat API images to balance percentages")
    print("=" * 50)

    # Replace with your bot token
    BOT_TOKEN = str(os.getenv("TOKEN"))

    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("\n❌ ERROR: Please set your bot token in the BOT_TOKEN variable!")
        print("Get your token from: https://discord.com/developers/applications")
        return

    bot.run(BOT_TOKEN)

if __name__ == "__main__":
    main()

bot.tree.clear_commands(guild=None)
