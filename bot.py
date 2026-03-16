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

    image = post.get("file_url")

    embed = discord.Embed(
        title=f"Image: {tag}",
        color=0x7289da
    )

    embed.set_image(url=image)

    view = ImageView(lambda i: send_random_image(i, tag))

    if interaction.response.is_done():
        await interaction.edit_original_response(embed=embed, view=view)
    else:
        await interaction.response.send_message(embed=embed, view=view)
    if not image:
        await interaction.followup.send("Ảnh không hợp lệ.")
    return

@bot.tree.command(
    name="nsfw",
    description="Gửi ảnh"
)
async def nsfw_command(interaction: discord.Interaction, tag: str):
    await interaction.response.defer()

    await send_random_image(interaction, tag)


bot.run(TOKEN)