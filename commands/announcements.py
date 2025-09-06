# Enhanced announce command with embed customization options
@bot.tree.command(name="announce", description="Send announcement to all news channels with custom embed")
@app_commands.describe(
    announcement="The main announcement message",
    title="Custom title for the embed (optional)",
    color="Embed color: red, blue, green, purple, orange, yellow, or hex code like #FF0000 (optional)",
    thumbnail="URL for thumbnail image (optional)",
    image="URL for main image (optional)",
    footer="Custom footer text (optional)",
    ping_everyone="Whether to ping @everyone (default: False)",
    urgent="Mark as urgent with special styling (default: False)",
    timestamp_format="Timestamp format (optional)"
)
@app_commands.choices(
    color=[
        app_commands.Choice(name="Red", value="red"),
        app_commands.Choice(name="Blue", value="blue"),
        app_commands.Choice(name="Green", value="green"),
        app_commands.Choice(name="Purple", value="purple"),
        app_commands.Choice(name="Orange", value="orange"),
        app_commands.Choice(name="Yellow", value="yellow"),
        app_commands.Choice(name="Random", value="random")
    ],
    timestamp_format=[
        app_commands.Choice(name="Discord Default (Today at 2:30 PM)", value="discord"),
        app_commands.Choice(name="Date Format (05/08/2025 at 2:30 PM)", value="date"),
        app_commands.Choice(name="ISO Format (2025-08-05 14:30)", value="iso"),
        app_commands.Choice(name="Long Format (August 5, 2025 at 2:30 PM)", value="long"),
        app_commands.Choice(name="Short Format (Aug 5, 2:30 PM)", value="short"),
        app_commands.Choice(name="No Timestamp", value="none")
    ]
)
async def announce_command(
    interaction: discord.Interaction,
    announcement: str,
    title: str = None,
    color: str = "blue",
    thumbnail: str = None,
    image: str = None,
    footer: str = None,
    ping_everyone: bool = False,
    urgent: bool = False,
    timestamp_format: str = "discord"
):
    # Check if user has permission
    if interaction.user.id != 1056952213056004118:  # Your user ID
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    # Process newlines in announcement text
    announcement = announcement.replace('\\n', '\n')
    # Get all news channels
    news_channels = get_all_news_channels()

    if not news_channels:
        await interaction.followup.send("No news channels are configured.", ephemeral=True)
        return

    # Parse color
    embed_color = discord.Color.blue()  # default
    if color:
        color_map = {
            "red": discord.Color.red(),
            "blue": discord.Color.blue(),
            "green": discord.Color.green(),
            "purple": discord.Color.purple(),
            "orange": discord.Color.orange(),
            "yellow": discord.Color.yellow(),
            "random": discord.Color.random()
        }

        if color in color_map:
            embed_color = color_map[color]
        elif color.startswith('#') and len(color) == 7:
            try:
                # Convert hex to discord color
                hex_value = int(color[1:], 16)
                embed_color = discord.Color(hex_value)
            except ValueError:
                embed_color = discord.Color.blue()  # fallback

    # Create embed
    if urgent:
        embed_title = f"🚨 URGENT: {title}" if title else "🚨 URGENT ANNOUNCEMENT"
        embed_color = discord.Color.red()  # Override color for urgent
    else:
        embed_title = title if title else "📢 Announcement"

    # Handle timestamp based on format choice
    if timestamp_format == "none":
        embed = discord.Embed(
            title=embed_title,
            description=announcement,
            color=embed_color
        )
    else:
        embed = discord.Embed(
            title=embed_title,
            description=announcement,
            color=embed_color,
            timestamp=datetime.now()
        )

    # Add optional elements
    if thumbnail:
        try:
            embed.set_thumbnail(url=thumbnail)
        except:
            pass  # Invalid URL, skip

    if image:
        try:
            embed.set_image(url=image)
        except:
            pass  # Invalid URL, skip

    # Set footer with custom timestamp format
    current_time = datetime.now()

    if footer:
        footer_text = footer
    elif urgent:
        footer_text = "⚠️ Urgent Bot Announcement"
    else:
        footer_text = "Bot Announcement System"

    # Add custom timestamp to footer if not using Discord's default
    if timestamp_format == "date":
        footer_text += f" • {current_time.strftime('%d/%m/%Y at %I:%M %p')}"
    elif timestamp_format == "iso":
        footer_text += f" • {current_time.strftime('%Y-%m-%d %H:%M')}"
    elif timestamp_format == "long":
        footer_text += f" • {current_time.strftime('%B %d, %Y at %I:%M %p')}"
    elif timestamp_format == "short":
        footer_text += f" • {current_time.strftime('%b %d, %I:%M %p')}"
    elif timestamp_format == "none":
        footer_text += f" • {current_time.strftime('%d/%m/%Y at %I:%M %p')}"
    # For "discord" format, we let Discord handle it with the embed timestamp

    embed.set_footer(text=footer_text)

    # Don't add author section anymore - removed as requested

    successful_sends = 0
    failed_sends = 0
    failed_channels = []

    # Send announcement to all channels
    for guild_id, channel_id in news_channels:
        try:
            channel = bot.get_channel(channel_id)
            if channel:
                # Prepare message content
                message_content = ""
                if ping_everyone:
                    message_content = "<@&1392328926696706089>"
                elif urgent:
                    message_content = "⚠️ **URGENT ANNOUNCEMENT** ⚠️"

                # Send the message
                if message_content:
                    await channel.send(content=message_content, embed=embed)
                else:
                    await channel.send(embed=embed)

                successful_sends += 1
            else:
                failed_sends += 1
                failed_channels.append(f"Channel {channel_id} (not found)")
        except discord.Forbidden:
            failed_sends += 1
            failed_channels.append(f"Channel {channel_id} (no permissions)")
        except Exception as e:
            print(f"Failed to send to channel {channel_id}: {e}")
            failed_sends += 1
            failed_channels.append(f"Channel {channel_id} (error: {str(e)[:50]})")

    # Create summary embed
    summary_embed = discord.Embed(
        title="📊 Announcement Summary",
        color=discord.Color.green() if failed_sends == 0 else discord.Color.orange(),
        timestamp=datetime.now()
    )

    summary_embed.add_field(
        name="✅ Successful Sends",
        value=str(successful_sends),
        inline=True
    )

    summary_embed.add_field(
        name="❌ Failed Sends",
        value=str(failed_sends),
        inline=True
    )

    summary_embed.add_field(
        name="📈 Success Rate",
        value=f"{(successful_sends / (successful_sends + failed_sends) * 100):.1f}%" if (successful_sends + failed_sends) > 0 else "0%",
        inline=True
    )

    # Add failed channels if any
    if failed_channels:
        failed_list = "\n".join(failed_channels[:10])  # Limit to 10 to avoid embed limits
        if len(failed_channels) > 10:
            failed_list += f"\n... and {len(failed_channels) - 10} more"
        summary_embed.add_field(
            name="Failed Channels",
            value=f"```{failed_list}```",
            inline=False
        )

    summary_embed.set_footer(text="Announcement completed")

    await interaction.followup.send(embed=summary_embed, ephemeral=True)


# Optional: Add a preview command to test embed appearance
""""@bot.tree.command(name="preview_announcement", description="Preview how your announcement will look")
@app_commands.describe(
    announcement="The main announcement message",
    title="Custom title for the embed (optional)",
    color="Embed color (optional)",
    thumbnail="URL for thumbnail image (optional)",
    image="URL for main image (optional)",
    footer="Custom footer text (optional)",
    urgent="Mark as urgent with special styling (default: False)",
    timestamp_format="Timestamp format (optional)"
)
@app_commands.choices(
    color=[
        app_commands.Choice(name="Red", value="red"),
        app_commands.Choice(name="Blue", value="blue"),
        app_commands.Choice(name="Green", value="green"),
        app_commands.Choice(name="Purple", value="purple"),
        app_commands.Choice(name="Orange", value="orange"),
        app_commands.Choice(name="Yellow", value="yellow"),
        app_commands.Choice(name="Random", value="random")
    ],
    timestamp_format=[
        app_commands.Choice(name="Discord Default (Today at 2:30 PM)", value="discord"),
        app_commands.Choice(name="Date Format (05/08/2025 at 2:30 PM)", value="date"),
        app_commands.Choice(name="ISO Format (2025-08-05 14:30)", value="iso"),
        app_commands.Choice(name="Long Format (August 5, 2025 at 2:30 PM)", value="long"),
        app_commands.Choice(name="Short Format (Aug 5, 2:30 PM)", value="short"),
        app_commands.Choice(name="No Timestamp", value="none")
    ]
)
async def preview_announcement_command(
    interaction: discord.Interaction,
    announcement: str,
    title: str = None,
    color: str = "blue",
    thumbnail: str = None,
    image: str = None,
    footer: str = None,
    urgent: bool = False,
    timestamp_format: str = "discord"
):
    # Check if user has permission
    if interaction.user.id != 1056952213056004118:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    # Parse color (same logic as announce command)
    embed_color = discord.Color.blue()
    if color:
        color_map = {
            "red": discord.Color.red(),
            "blue": discord.Color.blue(),
            "green": discord.Color.green(),
            "purple": discord.Color.purple(),
            "orange": discord.Color.orange(),
            "yellow": discord.Color.yellow(),
            "random": discord.Color.random()
        }

        if color in color_map:
            embed_color = color_map[color]
        elif color.startswith('#') and len(color) == 7:
            try:
                hex_value = int(color[1:], 16)
                embed_color = discord.Color(hex_value)
            except ValueError:
                embed_color = discord.Color.blue()

    # Create embed (same logic as announce command)
    if urgent:
        embed_title = f"🚨 URGENT: {title}" if title else "🚨 URGENT ANNOUNCEMENT"
        embed_color = discord.Color.red()
    else:
        embed_title = title if title else "📢 Announcement"

    # Handle timestamp based on format choice
    if timestamp_format == "none":
        embed = discord.Embed(
            title=embed_title,
            description=announcement,
            color=embed_color
        )
    else:
        embed = discord.Embed(
            title=embed_title,
            description=announcement,
            color=embed_color,
            timestamp=datetime.now()
        )

    if thumbnail:
        try:
            embed.set_thumbnail(url=thumbnail)
        except:
            pass

    if image:
        try:
            embed.set_image(url=image)
        except:
            pass

    # Set footer with custom timestamp format (same logic as announce command)
    current_time = datetime.now()

    if footer:
        footer_text = footer
    elif urgent:
        footer_text = "⚠️ Urgent Bot Announcement"
    else:
        footer_text = "Bot Announcement System"

    # Add custom timestamp to footer if not using Discord's default
    if timestamp_format == "date":
        footer_text += f" • {current_time.strftime('%d/%m/%Y at %I:%M %p')}"
    elif timestamp_format == "iso":
        footer_text += f" • {current_time.strftime('%Y-%m-%d %H:%M')}"
    elif timestamp_format == "long":
        footer_text += f" • {current_time.strftime('%B %d, %Y at %I:%M %p')}"
    elif timestamp_format == "short":
        footer_text += f" • {current_time.strftime('%b %d, %I:%M %p')}"
    elif timestamp_format == "none":
        footer_text += f" • {current_time.strftime('%d/%m/%Y at %I:%M %p')}"

    embed.set_footer(text=footer_text)

    # Add preview notice
    preview_embed = discord.Embed(
        title="📋 Announcement Preview",
        description="This is how your announcement will look:",
        color=discord.Color.yellow()
    )

    await interaction.response.send_message(
        content="**PREVIEW MODE** - This announcement was NOT sent to news channels:",
        embeds=[preview_embed, embed],
        ephemeral=True
    )"""
