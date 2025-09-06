
@bot.tree.command(name="rebalancecatpics", description="Rebalance image distribution (Admin only)")
async def rebalance_command(interaction: discord.Interaction):
    """Admin command to rebalance images"""
    if not interaction.user.guild_permissions.administrator or interaction.user.id != "1056952213056004118":
        await interaction.response.send_message("You need administrator permissions to use this command!", ephemeral=True)
        return

    await interaction.response.send_message("Rebalancing image distribution... This may take a moment!", ephemeral=True)

    try:
        # Rescan and rebalance
        cat_bot.scan_existing_images()
        await cat_bot.rebalance_images()
        cat_bot.scan_existing_images()

        stats = cat_bot.get_image_stats()


        await interaction.followup.send("Rebalancing complete.")

    except Exception as e:
        print(f"Error in rebalance command: {e}")
        await interaction.followup.send("Failed to rebalance images. Check console for errors.")
