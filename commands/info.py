import discord
from discord import app_commands

async def info_command(interaction: discord.Interaction):
    await interaction.response.send_message('This is a unique bot that can do some cool stuff like cat pics, catbot ripoff but tacos 👍 and some achievements.\nFor more info go to https://uniqueweb.site/')

def setup(bot):
    @bot.tree.command(name="info", description="yeah ok bro")
    async def info_slash_command(interaction: discord.Interaction):
        await info_command(interaction)