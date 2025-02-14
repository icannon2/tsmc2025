from abc import abstractmethod, ABC

from discord import Interaction, Message


class MessageHandlerImpl(ABC):
    """
    When a message is sent, this class will handle

    return True if message is handled, otherwise return False
    """

    @abstractmethod
    async def handle_message(self, message: Message) -> bool:
        return False


class CommandHandlerImpl(ABC):
    command_name: str
    description: str
    """
    When a command is sent, this class will handle

    return True if command is handled, otherwise return False
    """

    @abstractmethod
    async def handle_command(
        self, message: Message, interaction: Interaction | None
    ) -> bool:
        return False
