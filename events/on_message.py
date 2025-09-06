@bot.event
async def on_message(message):
    global last_spawn_time, timer_task
    if message.author == bot.user and message.author.id not in allowed_bots:
        return

    user_id = message.author.id
    current_time = time.time()
    user_data = get_user_data(user_id)

    # Track what needs to be updated
    updates = {}
    async def check_and_give_achievement(user, achievement_id, channel):
        """Helper function to check and give achievements"""
        all_achievements = load_achievements()
        if achievement_id in all_achievements:
            get_or_create_profile(user.id, user.display_name)
            if unlock_achievement(user.id, user.display_name, achievement_id):
                achievement_data = all_achievements[achievement_id]
                await send_achievement_notification(channel, user, achievement_id, achievement_data)
    if message.content == bot.user.mention:
        await check_and_give_achievement(message.author, "tf_you_want", message.channel)
    # Handle bot mention (ping) - existing logic
    if bot.user.mentioned_in(message) and ai_config.get("AI_ENABLED", True):
        # Remove the mention from the message content
        clean_content = message.content.replace(f'<@{bot.user.id}>', '').strip()
        image_data = None
        if message.attachments:
            for attachment in message.attachments:
                image_data = await process_image_for_ai(attachment)
                if image_data:
                    break
        if clean_content or image_data:
                # Only respond if there's actual content after the mention
            async with message.channel.typing():
                try:
                    # Get conversation context
                    context = get_conversation_context(message.channel.id)
                    if len(context) > 800:
                        context = context[-800:]

                    if image_data:
                        system_prompt = f"""You are {ai_config['BOT_NAME']}, a Discord bot with vision capabilities. You can see and analyze images that users send. Be descriptive when needed to describe images. You understand internet culture and memes."""
                        if clean_content:
                            prompt = f"{message.author.name} sent an image and asked: {clean_content}"
                        else:
                            prompt = f"{message.author.name} sent an image. Please describe what you see."
                        if context:
                            prompt = f"Recent chat: {context}\n\n{prompt}"
                    else:
                        # Build the promp
                        system_prompt = f"""You are {ai_config['BOT_NAME']}. {ai_config['PROMPT_MAIN']}
                                        {ai_config['KNOWLEDGE']}
                                        {ai_config['PERSONALITY']}
                                        Keep responses concise and natural for Discord chat."""

                    # Include context if available
                        if context:
                            prompt = f"Previous conversation:\n{context}\n\n{message.author.name}: {clean_content}"
                        else:
                            prompt = f"{message.author.name}: {clean_content}"

                    # Get AI response
                    ai_response = await asyncio.wait_for(
                        asyncio.to_thread(query_ollama_with_vision, prompt, system_prompt, image_data),
                        timeout=None
                    )
                    # Send response
                    if ai_response and ai_response != ai_config["ERROR_RESPONSE"]:
                        # Split long responses if needed
                        if len(ai_response) > 2000:
                            chunks = [ai_response[i:i+2000] for i in range(0, len(ai_response), 2000)]
                            for chunk in chunks:
                                await message.reply(chunk, allowed_mentions=discord.AllowedMentions.none())
                        else:
                            await message.reply(ai_response, allowed_mentions=discord.AllowedMentions.none())

                        # Update conversation memory
                        memory_content = clean_content if clean_content else "[sent an image]"
                        update_conversation_memory(message.channel.id, message.author.name, memory_content, ai_response)
                    else:
                        await message.reply("Sorry, I'm having trouble thinking right now. Try again later!")
                except asyncio.TimeoutError:
                    await message.reply("That's taking too long to process, Try smaller image or shorter msg.")
                except Exception as e:
                    print(f"AI Error: {e}")
                    await message.reply("Sorry, something went wrong! Please try again.")

    # Handle embed fail
    if 'embed fail' in message.content or message.content == "embed fail ig?":
        should_respond, new_count, cooldown_end = check_and_handle_cooldown(
            user_data, current_time, 'embed_fail', limit=3, cooldown_duration=60
        )

        if should_respond:
            await message.channel.send("https://cdn.discordapp.com/attachments/1321992659384012901/1401969285164826697/watermark.gif")
            updates['embed_fail_count'] = new_count
            if cooldown_end > 0:
                updates['embed_fail_cooldown_end'] = cooldown_end
                await message.channel.send(f"{message.author.mention} wait 1 min before saying that again")
        else:
            await message.channel.send("you need to wait 1 min before saying that again")
            return

    # Handle amethyst
    if 'amethyst' in message.content or 'Amethyst' in message.content or 'AMETHYST' in message.content:
        should_respond, new_count, cooldown_end = check_and_handle_cooldown(
            user_data, current_time, 'amethyst', limit=3, cooldown_duration=120
        )

        if should_respond:
            await message.channel.send("https://tenor.com/view/amethyst-alpha-react-geometry-dash-gif-7140286725926478147")
            updates['amethyst_count'] = new_count
            if cooldown_end > 0:
                updates['amethyst_cooldown_end'] = cooldown_end
                await message.channel.send(f"{message.author.mention} wait 2 min before mentioning amethyst again")
        else:
            await message.channel.send("wait 2 min before mentioning amethyst again")
            return

    # Handle slaughterhouse
    if 'slaughterhouse' in message.content or 'Slaughterhouse' in message.content or 'SLAUGHTERHOUSE' in message.content:
        should_respond, new_count, cooldown_end = check_and_handle_cooldown(
            user_data, current_time, 'slaughterhouse', limit=2, cooldown_duration=180
        )

        if should_respond:
            await message.channel.send("https://tenor.com/view/slaughterhouse-gd-cracked-drops-phone-phone-gif-504258885114218717")
            updates['slaughterhouse_count'] = new_count
            if cooldown_end > 0:
                updates['slaughterhouse_cooldown_end'] = cooldown_end
                await message.channel.send(f"{message.author.mention} wait 3 min before mentioning slaughterhouse again")
        else:
            await message.channel.send("wait 3 min before mentioning slaughterhouse again")
            return

    # Handle hi variations
    if message.content in hi_vars:
        should_respond, new_count, cooldown_end = check_and_handle_cooldown(
            user_data, current_time, 'hi', limit=4, cooldown_duration=90
        )

        if should_respond:
            await message.channel.send("https://cdn.discordapp.com/attachments/1401656227540500541/1401927914269839600/IMG_1136.png")
            await check_and_give_achievement(message.author, "welcome", message.channel)
            updates['hi_count'] = new_count
            if cooldown_end > 0:
                updates['hi_cooldown_end'] = cooldown_end
                await message.channel.send(f"{message.author.mention} wait 1.5 min before saying hi again")
        else:
            await message.channel.send("wait 1.5 min before saying hi again")
            return

    # Handle Jet2 holiday
    if (message.content.startswith("DARLING HOLD MY HAND! Nothing beats a Jet2 Holiday") or
        message.content.startswith("jet2 holiday") or message.content.startswith("Jet2 holiday") or
        message.content.startswith("Jet2 Holiday")):

        should_respond, new_count, cooldown_end = check_and_handle_cooldown(
            user_data, current_time, 'jet2', limit=2, cooldown_duration=180
        )

        if should_respond:
            reactionbc = await message.channel.send("DARLING HOLD MY HAND! Nothing beats a Jet2 Holiday and right you can save 50 pounds per person! That's 200 pounds off for a family of four!")
            await message.add_reaction("✈️")
            updates['jet2_count'] = new_count
            if cooldown_end > 0:
                updates['jet2_cooldown_end'] = cooldown_end
                await message.channel.send(f"{message.author.mention} wait 3 min before mentioning Jet2 again")
        else:
            await message.channel.send("wait 3 min before mentioning Jet2 again")
            return

    # Handle tidal wave
    if ('tidal wave' in message.content or message.content.startswith('tidal wave') or
        'Tidal wave' in message.content or 'Tidal Wave' in message.content or 'TIDAL WAVE' in message.content):

        should_respond, new_count, cooldown_end = check_and_handle_cooldown(
            user_data, current_time, 'tidal_wave', limit=3, cooldown_duration=120
        )

        if should_respond:
            await message.channel.send(">>>TIDAL>>>\n<<<WAVE<<<")
            updates['tidal_wave_count'] = new_count
            if cooldown_end > 0:
                updates['tidal_wave_cooldown_end'] = cooldown_end
                await message.channel.send(f"{message.author.mention} wait 2 min before mentioning tidal wave again")
        else:
            await message.channel.send("wait 2 min before mentioning tidal wave again")
            return

    # Handle apple (reaction only, lighter limit)
    if 'apple' in message.content or 'Apple' in message.content or 'APPLE' in message.content:
        should_respond, new_count, cooldown_end = check_and_handle_cooldown(
            user_data, current_time, 'apple', limit=8, cooldown_duration=60
        )

        if should_respond:
            await message.add_reaction("<:appol:1399818634108473495>")
            updates['apple_count'] = new_count
            if cooldown_end > 0:
                updates['apple_cooldown_end'] = cooldown_end
        # No message for apple cooldown since it's just a reaction

    # Handle "yeah ok bro"
    if message.content == "yeah ok bro":
        should_respond, new_count, cooldown_end = check_and_handle_cooldown(
            user_data, current_time, 'yeah_ok_bro', limit=3, cooldown_duration=180
        )

        if should_respond:
            await message.channel.send(f"i agree with {message.author.mention}.")
            updates['yeah_ok_bro_count'] = new_count
            if cooldown_end > 0:
                updates['yeah_ok_bro_cooldown_end'] = cooldown_end
                await message.channel.send(f"{message.author.mention} wait 3 min before saying that again")
        else:
            await message.channel.send("wait 3 min before saying that again")
            return

    # Update database if there are changes
    if updates:
        update_user_data(user_id, **updates)

    # Handle non-limited triggers (these don't have cooldowns)
    if message.guild is None:
        await message.channel.send("u gay shall be")
        await check_and_give_achievement(message.author, "u_gay_shall_be", message.channel)

    # Handle bot interactions and timers (existing logic)
    if message.author == bot.user and message.author.id in allowed_bots and 'cat has spawned out of nowhere!! Say  "cat" to catch it!' in message.content:
        await message.channel.send("cat")

    if (message.author.id == 1402195680830685330 and
        'has spawned out of nowhere!! Say "cat" to catch it!' in message.content):
        print(f"Spawn message detected at {datetime.now()}")
        last_spawn_time = datetime.now()
        if timer_task and not timer_task.done():
            timer_task.cancel()
            print("Timer reset!")
        timer_task = asyncio.create_task(cat_timer())

    if "skibidi" in message.content.lower():
        await check_and_give_achievement(message.author, "brainrotted", message.channel)
    if "❤️" in message.content or "💖" in message.content or ":heart:" in message.content or ":mending_heart:" in message.content:
        await check_and_give_achievement(message.author, "i_love_you", message.channel)
