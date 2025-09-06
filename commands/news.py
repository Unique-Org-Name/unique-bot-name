
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
