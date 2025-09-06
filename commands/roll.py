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
