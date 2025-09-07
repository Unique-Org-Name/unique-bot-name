from utils.user import upsert_profile
import json
import sqlite3

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

# load achievements from json file
def load_achievements():
    try:
        with open("./achievements.json", "r") as f:
            return json.loads(f.read())
    except FileNotFoundError:
        print("achievements.json not found!")
        return {}


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
# old definition, keep for now, def unlock_achievement(user_id, username, achievement_id):
def unlock_achievement(user_id, achievement_id):
    # ensure the user doesnt already have the achievement
    if has_achievement(user_id, achievement_id):
        return False
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

# Send achievement notification
async def send_achievement_notification(channel, user, achievement_data):
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
        upsert_profile(user.id, user.display_name)
        if unlock_achievement(user.id, achievement_id):
            achievement_data = all_achievements[achievement_id]
            await send_achievement_notification(channel, user, achievement_data)



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
