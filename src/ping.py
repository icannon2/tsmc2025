from discord import Message
from .bot import CommandHandlerImpl


class PingCommandHandler(CommandHandlerImpl):
    command_name = "ping"
    description = "Ping command"

    async def handle_command(self, message: Message) -> bool:
        await message.channel.send("Pong!")
        return True
