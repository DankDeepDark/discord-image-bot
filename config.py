import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")

GUILD_ID = 1481299434301161614

HEADERS = {
    "User-Agent": "DiscordImageBot/1.0"
}