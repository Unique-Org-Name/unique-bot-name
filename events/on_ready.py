@bot.event
async def on_ready():
    """Bot startup event"""
    print(f'{bot.user} has landed on Discord!')
    print("=" * 50)

    # Scan existing images
    cat_bot.scan_existing_images()

    # Get current stats
    stats = cat_bot.get_image_stats()
    print(f"Current distribution:")
    print(f"  User images: {stats['user_images']}")
    print(f"  Camera roll images: {stats['camera_roll_images']}")
    print(f"  Cat API images: {stats['catapi_images']}")
    print(f"  Special image: {'✅' if stats['special_image'] else '❌'}")
    print(f"  Percentage per regular image: {stats['percentage_per_regular']:.2f}%")

    # Rebalance if needed
    await cat_bot.rebalance_images()

    # Update stats after rebalancing
    cat_bot.scan_existing_images()
    final_stats = cat_bot.get_image_stats()

    print("\nFinal distribution:")
    print(f"  User images: {final_stats['user_images']} ({final_stats['percentage_per_regular']:.2f}% each)")
    print(f"  Camera roll images: {final_stats['camera_roll_images']} ({final_stats['percentage_per_regular']:.2f}% each)")
    print(f"  Cat API images: {final_stats['catapi_images']} ({final_stats['percentage_per_regular']:.2f}% each)")
    print(f"  Special image: {final_stats['special_percentage']}% chance")
    print(f"  Total regular images: {final_stats['total_images']}")

    print("\nBot is ready to serve cat pics!")
    print("=" * 50)
    """init_database()
    init_achievements()"""
    if not server_count_updater.is_running():
        server_count_updater.start()
        print("Started server count updater")
    await update_server_count()
    async def setup_achievements():
        init_achievements_db()
        print("Achievement system initialized!")
    await setup_achievements()
    if ai_config.get("AI_ENABLED", True):
        print(f"AI Chat enabled using model: {ai_config['MODEL_NAME']}")
    else:
        print("AI Chat is disabled")
    timer_task = asyncio.create_task(cat_timer())
    """await bot.change_presence(
        status=discord.Status.dnd,
        activity=discord.Streaming(
            name="radio or smth",
            url="https://www.youtube.com/watch?v=dTS_aNfpbIM"
        )
    )"""

    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
