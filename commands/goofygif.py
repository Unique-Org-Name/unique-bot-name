import discord
from discord import app_commands
import random

goofy_gifs = {
    1: "https://tenor.com/view/finally-yeah-boy-nice-yes-fridge-gif-4687827172351383981",
    2: "https://cdn.discordapp.com/attachments/773986571434721320/1400123591323812023/5D81CCCE-B4E0-4E3E-9678-193BBE70F7C5.gif",
    3: "https://cdn.discordapp.com/attachments/773986571434721320/1400123345747316817/C40E3939-8BA1-43E9-9AE5-F48F44F6D3C6.gif",
    4: "https://tenor.com/view/toilet-shark-toilet-freaky-shark-sitting-shark-goofy-ahh-gif-6628307483075639751",
    5: "https://tenor.com/view/quandale-quandale-dingle-gif-25093205",
    6: "https://cdn.discordapp.com/attachments/802977594860503042/1378916194165460992/IMG_0114.gif",
    7: "https://tenor.com/view/tyler-the-creator-homer-simpson-dance-freaky-dont-tap-the-glass-gif-18219729817367897576",
    8: "https://cdn.discordapp.com/attachments/1121521105316880384/1393451576638570666/33c1e68ee2acb13e1c11a271006b28ca1online-video-cutter.com-ezgif.com-video-to-gif-converter.gif",
    9: "https://tenor.com/view/goober-kitty-crazy-cat-cat-goober-warning-gif-24871108",
    10: "https://cdn.discordapp.com/attachments/1105948808388550749/1313144853013598319/caption-6.gif",
    11: "https://tenor.com/view/griddy-devious-diabolical-malicious-devil-gif-26915799",
    12: "https://tenor.com/view/mustard-among-us-among-us-amogus-gif-22939641",
    13: "https://tenor.com/view/spongebob-crying-geometry-dash-sad-spunch-agony-god-i-love-trampolining-gif-25250082",
    14: "https://imgur.com/3SvtVR8",
    15: "https://tenor.com/view/damn-bird-pukeko-chick-chicken-gif-16186129570004356645",
    16: "https://tenor.com/view/you-wont-believe-this-digs-digging-loop-gif-19998502",
    17: "https://tenor.com/view/pigeon-lebron-james-meme-funny-gif-3425517799009042574",
    18: "https://tenor.com/view/cat-meme-cat-cats-cat-hug-cat-love-gif-9176149428765300540",
    19: "https://imgur.com/gallery/IsWDJWa",
    20: "https://tenor.com/view/mango-cat-dance-ai-dancing-cat-gif-4373280976266621514",
    21: "https://tenor.com/view/whatever-go-my-whatever-go-my-vrad-vrad-vradexe-interloper-gif-2623316526149241953",
    22: "https://tenor.com/view/theres-so-much-theres-so-much-sog-ted-2-ted-so-much-sog-gif-10316726644461251151",
    23: "https://media.discordapp.net/attachments/735670248715583528/1148768418678460467/togif.gif",
    24: "https://cdn.discordapp.com/attachments/1205760412507840572/1382867848552124488/1x.webp",
    25: "https://tenor.com/view/download-carmen-winstead-quandale-dingle-gif-25824098"
}

async def goofygif_command(interaction: discord.Interaction):
    random_num = random.randint(1, 25)
    print(goofy_gifs[random_num])  # debugging stuff
    goofy_gif = goofy_gifs[random_num]

    if random_num == 3:
        await interaction.response.send_message("btw @qualitymaxxmemes is <@1056952213056004118>'s nickname in Kingsammelot Kingdom Server.")
        await interaction.followup.send(goofy_gif)
    elif random_num == 14:
        await interaction.response.send_message("oh look! this one has sound, also it isn't really goofy, i just wanted to add it since it had sound somehow.")
        await interaction.followup.send(goofy_gif)
    elif random_num == 19:
        await interaction.response.send_message("crazy that the entire shrek movie became a video on imgur that could be embedded on discord wow.")
        await interaction.followup.send(goofy_gif)
    else:
        await interaction.response.send_message(goofy_gif)

def setup(bot):
    @bot.tree.command(name="goofygif", description="my name is quindile dingle hehehehehehehehe")
    async def goofygif_slash_command(interaction: discord.Interaction):
        await goofygif_command(interaction)