import discord
from discord.ext import commands
from discord import app_commands

from config import TOKEN, GUILD_ID
from api import ImageAPI
from views import ImageView
from cache import get_cache, set_cache

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

guild = discord.Object(id=GUILD_ID)

@bot.event
async def on_ready():
    print(f"{bot.user} online")

    synced = await bot.tree.sync()

    print("Synced commands:", synced)


async def send_random_image(interaction, tag):

    cache_key = f"tag:{tag}"

    posts = get_cache(cache_key)

    if not posts:
        url = f"https://danbooru.donmai.us/posts.json?tags={tag}&limit=50"

        posts = await ImageAPI.fetch_images(url)

        set_cache(cache_key, posts)

    post = ImageAPI.pick_random(posts)

    if not post:
        await interaction.followup.send("Không tìm thấy ảnh.")
        return

    image = (
        post.get("file_url")
        or post.get("large_file_url")
        or post.get("preview_file_url")
    )

    if not image:
        await interaction.followup.send("Ảnh không hợp lệ.")
        return

    embed = discord.Embed(
        title=f"Image: {tag}",
        color=0x2b2d31
    )

    embed.set_image(url=image)
    embed.set_author(name=tag)
    embed.set_footer(text="Powered by Danbooru", icon_url="https://danbooru.donmai.us/favicon.ico")

    view = ImageView(lambda i: send_random_image(i, tag))

    if interaction.response.is_done():
        await interaction.edit_original_response(embed=embed, view=view)
    else:
        await interaction.response.send_message(embed=embed, view=view)

async def tag_autocomplete(
    interaction: discord.Interaction,
    current: str
):
    tags = [
        "waifu",
        "neko",
        "milf",
        "cosplay",
        "marin_kitagawa",
        "raiden_shogun",
        "hatsune_miku",
        "rem_(re_zero)",
        "zero_two"
    ]

    return [
        app_commands.Choice(name=tag, value=tag)
        for tag in tags
        if current.lower() in tag.lower()
    ][:25]

@bot.tree.command(
    name="nsfw",
    description="Gửi ảnh"
)
@app_commands.autocomplete(tag=tag_autocomplete)
@app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
async def nsfw_command(interaction: discord.Interaction, tag: str):
    await interaction.response.defer()

    await send_random_image(interaction, tag)


bot.run(TOKEN)