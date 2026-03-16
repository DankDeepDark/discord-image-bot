import aiohttp
import random
from config import HEADERS

class ImageAPI:

    @staticmethod
    async def fetch_images(url):
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise Exception(f"API error {resp.status}")

                data = await resp.json()

                if isinstance(data, dict):
                    data = data.get("posts", [])

                return data

    @staticmethod
    def pick_random(posts):
        valid = [p for p in posts if isinstance(p, dict)]

        if not valid:
            return None

        return random.choice(valid)