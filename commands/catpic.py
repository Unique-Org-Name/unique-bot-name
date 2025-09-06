@bot.tree.command(name="catpic", description="Get a random cat picture!")
async def catpic_command(interaction: discord.Interaction):
    """Slash command to send a random cat picture"""
    try:
        image_path, image_type = cat_bot.get_random_image()

        if image_path and os.path.exists(image_path):
            filename = os.path.basename(image_path)

            # Create embed based on image type
            if image_type == "special":
                embed = discord.Embed(
                    title="_ _",
                    color=discord.Color.random()
                )
            elif image_type == "catapi":
                embed = discord.Embed(
                    title="_ _",
                    color=discord.Color.random()
                )
            elif image_type == "camera_roll":
                embed = discord.Embed(
                    title="_ _",
                    color=discord.Color.random()
                )
            else:  # user image
                embed = discord.Embed(
                    title="_ _",
                    color=discord.Color.random()
                )

            # Send image with embed
            with open(image_path, 'rb') as f:
                file = discord.File(f, filename=filename)
                embed.set_image(url=f"attachment://{filename}")
                await interaction.response.send_message(embed=embed, file=file)

        else:
            # Fallback if no images available
            embed = discord.Embed(
                title="Error.",
                description="No cat pics currently available.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)

    except Exception as e:
        print(f"Error in catpic command: {e}")
        await interaction.response.send_message("An error occured.", ephemeral=True)
