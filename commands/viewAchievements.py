import discord
from discord import app_commands
from datetime import datetime
from utils.achievements import load_achievements, get_user_achievements, check_and_give_achievement
from utils.user import upsert_profile

async def achievements_command(interaction: discord.Interaction, user: discord.Member = None):
    target_user = user if user else interaction.user
    await check_and_give_achievement(target_user, "the_grand_list", interaction.channel)
    # Ensure user has profile in the db
    upsert_profile(target_user.id, target_user.display_name)
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

def setup(bot):
    @bot.tree.command(name="achievements", description="View your achievements")
    async def achievements_slash_command(interaction: discord.Interaction, user: discord.Member = None):
        await achievements_command(interaction, user)