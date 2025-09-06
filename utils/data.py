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
