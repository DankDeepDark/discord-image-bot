import discord

class ImageView(discord.ui.View):

    def __init__(self, callback):
        super().__init__(timeout=120)
        self.callback = callback

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.callback(interaction)