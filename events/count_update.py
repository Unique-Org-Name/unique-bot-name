# various functions to update count based on events etc

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
