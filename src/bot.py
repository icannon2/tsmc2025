import discord
from discord.ext import commands

from .config import Config


class DiscordBot(commands.Bot):
    token: str

    def __init__(self, config: Config):
        self.token = config.discord_token

        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(intents=intents, command_prefix="/")

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content == "ping":
            await message.channel.send("pong")

    def init_command(self):
        @self.command()
        async def ping(ctx):
            await ctx.send("pong")

    def run(self):
        self.init_command()
        super().run(self.token)
