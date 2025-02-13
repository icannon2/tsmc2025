import discord
from discord.ext import commands
from discord import Message

from .handler import CommandHandlerImpl, MessageHandlerImpl

from .chat import State as ChatState

from .config import Config

from .chat import ChatMessageHandler, ChatCommandHandler
from .ping import PingCommandHandler


class DiscordBot(commands.Bot, MessageHandlerImpl):
    token: str
    message_handlers: list[MessageHandlerImpl]
    command_handlers: list[CommandHandlerImpl]

    def __init__(self, config: Config):
        self.token = config.discord_token

        chat_state = ChatState(config)

        self.message_handlers = [ChatMessageHandler(config, chat_state)]
        self.command_handlers = [
            ChatCommandHandler(config, chat_state),
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

    async def on_message(self, message: Message):
        if message.author != self.user:
            await self.handle_message(message)

    def init_command(self):
        for handler in self.command_handlers:

            @self.command(name=handler.command_name, description=handler.description)
            async def command(ctx):
                await handler.handle_command(ctx)

    def run(self):
        self.init_command()
        super().run(self.token)
