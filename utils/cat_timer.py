# maybe move to catbot?
async def cat_timer():
    """Timer that runs every 14 minutes"""
    global last_spawn_time, timer_task

    while True:
        try:
            await asyncio.sleep(14 * 60)  # 14 minutes in seconds

            # Get the specific channel
            channel = bot.get_channel(1390518132606636094)
            if channel:
                # 5% chance to send the slash command
                if random.randint(1, 100) <= 5:
                    await channel.send("/cat type: egirl")
                    print(f"Sent /cat command at {datetime.now()}")

        except asyncio.CancelledError:
            print("Timer cancelled")
            break
        except Exception as e:
            print(f"Error in timer: {e}")
