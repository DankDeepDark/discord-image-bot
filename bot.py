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
        url = f"https://danbooru.donmai.us/posts.json?tags={tag} order:random&limit=100"

        posts = await ImageAPI.fetch_images(url)

        posts = [
            p for p in posts
            if p.get("file_url") or p.get("large_file_url")
        ]

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
    
    post_url = f"https://danbooru.donmai.us/posts/{post['id']}"

    artist = post.get("tag_string_artist", "unknown")
    score = post.get("score", 0)
    rating = post.get("rating", "?")

    color_map = {
    "s": 0x3498db,
    "q": 0xf1c40f,
    "e": 0xe74c3c
}
    color = color_map.get(rating, 0x2b2d31)
    
    embed = discord.Embed(
        url=post_url,
        color=color
    )

    embed.set_image(url=image)
    embed.set_author(
    name=f"Tag: {tag.replace('_', ' ')}",
    icon_url="https://danbooru.donmai.us/favicon.ico"
)
    embed.add_field(name="Artist", value=artist, inline=True)
    embed.add_field(name="Score", value=score, inline=True)
    embed.add_field(name="Rating", value=rating, inline=True)
    embed.set_footer(
    text=f"Post ID: {post['id']} • Danbooru",
    icon_url="https://danbooru.donmai.us/favicon.ico"
)
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
    "1girl",
    "2girls",
    "waifu",
    "neko",
    "milf",
    "cosplay",
    "maid",
    "bikini",
    "thighhighs",
    "school_uniform",
    "marin_kitagawa",
    "raiden_shogun",
    "hatsune_miku",
    "rem_(re_zero)",
    "zero_two",
    "yor_forger",
    "makima_(chainsaw_man)",
]

    return [
        app_commands.Choice(name=tag, value=tag)
        for tag in tags
        if current.lower() in tag.lower()
    ][:25]

def is_nsfw():
    async def predicate(interaction: discord.Interaction):
        if interaction.channel and interaction.channel.is_nsfw():
            return True

        await interaction.response.send_message(
            "❌ Lệnh này chỉ dùng trong NSFW channel.",
            ephemeral=True
        )
        return False

    return app_commands.check(predicate)

@bot.tree.command(
    name="nsfw",
    description="Gửi ảnh"
)
@is_nsfw()
@app_commands.autocomplete(tag=tag_autocomplete)
@app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
async def nsfw_command(interaction: discord.Interaction, tag: str):
    await interaction.response.defer()

    await send_random_image(interaction, tag)


bot.run(TOKEN)