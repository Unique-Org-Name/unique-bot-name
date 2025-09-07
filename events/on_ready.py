import asyncio
from utils.cat_timer import cat_timer
from utils.achievements import init_achievements_db

async def setup(bot):
    @bot.event
    async def on_ready():
        bot.remove_command('help')  # Remove default help command
        """Bot startup event"""
        print(f'{bot.user} has landed on Discord!')
        print("=" * 50)

        # Cat bot functionality temporarily disabled
        # cat_bot.scan_existing_images()
        # stats = cat_bot.get_image_stats()
        # print(f"Current distribution:")
        # print(f"  User images: {stats['user_images']}")
        # print(f"  Camera roll images: {stats['camera_roll_images']}")
        # print(f"  Cat API images: {stats['catapi_images']}")
        # print(f"  Special image: {'✅' if stats['special_image'] else '❌'}")
        # print(f"  Percentage per regular image: {stats['percentage_per_regular']:.2f}%")
        # await cat_bot.rebalance_images()
        # cat_bot.scan_existing_images()
        # final_stats = cat_bot.get_image_stats()
        # print("\nFinal distribution:")
        # print(f"  User images: {final_stats['user_images']} ({final_stats['percentage_per_regular']:.2f}% each)")
        # print(f"  Camera roll images: {final_stats['camera_roll_images']} ({final_stats['percentage_per_regular']:.2f}% each)")
        # print(f"  Cat API images: {final_stats['catapi_images']} ({final_stats['percentage_per_regular']:.2f}% each)")
        # print(f"  Special image: {final_stats['special_percentage']}% chance")
        # print(f"  Total regular images: {final_stats['total_images']}")
        # print("\nBot is ready to serve cat pics!")
        print("=" * 50)
        
        # Initialize achievements
        async def setup_achievements():
            init_achievements_db()
            print("Achievement system initialized!")
        
        await setup_achievements()
        
        # Start server count updater if it exists
        if hasattr(bot, 'server_count_updater'):
            if not bot.server_count_updater.is_running():
                bot.server_count_updater.start()
                print("Started server count updater")
            if hasattr(bot, 'update_server_count'):
                await bot.update_server_count()
        
        # Initialize AI if enabled
        if hasattr(bot, 'ai_config') and bot.ai_config.get("AI_ENABLED", True):
            print(f"AI Chat enabled using model: {bot.ai_config['MODEL_NAME']}")
        else:
            print("AI Chat is disabled")
        
        # Start cat timer
        asyncio.create_task(cat_timer(bot))
        
        # Sync slash commands once after the bot is ready
        if not getattr(bot, "_commands_synced", False):
            try:
                await asyncio.sleep(1)
                synced = await bot.tree.sync()
                print(f"Synced {len(synced)} command(s)")
                bot._commands_synced = True
            except Exception as e:
                print(f"Failed to sync commands: {e}")
    """await bot.change_presence(
        status=discord.Status.dnd,
        activity=discord.Streaming(
            name="radio or smth",
            url="https://www.youtube.com/watch?v=dTS_aNfpbIM"
        )
    )"""

