import discord
from discord.ext import commands
from discord import Message

from .handler import CommandHandlerImpl, MessageHandlerImpl

from .state import GlobalState

from .config import Config

from .chat import ChatMessageHandler, ChatCommandHandler, SummarizeCommandHandler
from .ping import PingCommandHandler


class DiscordBot(commands.Bot, MessageHandlerImpl):
    token: str
    message_handlers: list[MessageHandlerImpl]
    command_handlers: list[CommandHandlerImpl]

    def __init__(self, config: Config):
        self.token = config.discord_token

        perroom_state_map = {}
        global_state = GlobalState(config)

        self.message_handlers = [ChatMessageHandler(global_state, perroom_state_map)]
        self.command_handlers = [
            ChatCommandHandler(config, global_state, perroom_state_map),
            SummarizeCommandHandler(config, global_state, perroom_state_map),
            PingCommandHandler(),
        ]

        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(intents=intents, command_prefix="/")

    async def handle_message(self, message: Message) -> bool:
        if message.content.startswith("/"):
            for handler in self.command_handlers:
                if await handler.handle_command(message):
                    return True

        for handler in self.message_handlers:
            if await handler.handle_message(message):
                return True

        return False

    async def on_ready(self):
        slash = await self.tree.sync()
        print(f"Logged in as {self.user}")
        print(f"Slash commands: {slash}")

    async def on_message(self, message: Message):
        if message.author != self.user:
            await self.handle_message(message)

    def init_command(self):
        for handler in self.command_handlers:

            @self.tree.command(
                name=handler.command_name, description=handler.description
            )
            async def command(interaction: discord.Interaction):
                await handler.handle_command(interaction.message, interaction)

    def run(self):
        self.init_command()
        super().run(self.token)
