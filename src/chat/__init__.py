from discord import ChannelType, Message

from .state import State

from ..handler import CommandHandlerImpl, MessageHandlerImpl
from ..config import Config
from .persistence import Message as MessageModel, Chatroom as ChatroomModel


class ChatMessageHandler(MessageHandlerImpl):
    state: State

    def __init__(self, state: State):
        self.state = state
        super().__init__()

    async def handle_message(self, message: Message) -> bool:
        channel_id = message.channel.id

        chatroom = (
            self.state.session.query(ChatroomModel)
            .filter_by(thread_id=channel_id)
            .first()
        )
        if chatroom is None:
            return False

        model = MessageModel(
            chatroom_id=chatroom.id,
            user_id=message.author.id,
            role="user",
            content=message.content,
        )
        self.state.session.add(model)
        self.state.session.commit()

        message.channel.send("I'm sorry, I'm not sure how to respond to that.")

        return False


class ChatCommandHandler(CommandHandlerImpl):
    command_name = "chat"
    description = "create a chat"

    allowed_channels: list[str]

    state: State

    def __init__(self, config: Config, state: State):
        self.state = state

        self.allowed_channels = config.allowed_channels
        super().__init__()

    async def handle_command(self, message: Message) -> bool:
        if (
            message.content.startswith("/chat")
            and message.channel.id in self.allowed_channels
        ):
            thread = await message.channel.create_thread(
                name="chat", type=ChannelType.private_thread
            )
            if thread:
                await thread.send(
                    f"Hi {message.author.mention}! How can I help you today?"
                )
            else:
                raise Exception("Failed to create a thread")

            model = ChatroomModel(thread_id=thread.id, user_id=message.author.id)
            self.state.session.add(model)
            self.state.session.commit()

            return True
        return False
