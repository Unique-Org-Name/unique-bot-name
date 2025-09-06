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
