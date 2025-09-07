import sqlite3

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

# Get or create user profile
def upsert_profile(user_id, username):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()

    # Check if profile exists
    cursor.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,))
    profile = cursor.fetchone()

    # upsert profile
    if not profile:
        # Create new profile
        cursor.execute('''
            INSERT INTO user_profiles (user_id, username, total_achievements)
            VALUES (?, ?, 0)
        ''', (user_id, username))
    else:
        # Update username if changed
        cursor.execute('''
            UPDATE user_profiles
            SET username = ?, last_updated = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (username, user_id))
    
    conn.commit()
    conn.close()

# Get user profile data
def get_user_profile(user_id):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,))
    profile = cursor.fetchone()
    conn.close()
    return profile


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