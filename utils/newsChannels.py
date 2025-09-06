
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
