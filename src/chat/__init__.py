from discord import ChannelType, Message
from .state import State as PerroomState
from ..state import State as GlobalState
from sqlalchemy.ext.declarative import declarative_base

from ..handler import CommandHandlerImpl, MessageHandlerImpl
from ..config import Config
from .persistence import Message as MessageModel, Chatroom as ChatroomModel

engine = None
Base = declarative_base()


class ChatMessageHandler(MessageHandlerImpl):
    # a mapping from thread_id to the state of the chatroom
    perroom_state: dict[PerroomState]
    global_state: GlobalState

    def __init__(self, state: GlobalState, per_state: dict[PerroomState]):
        self.global_state = state
        self.perroom_state = per_state
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

        chat_history = (
            self.state.session.query(MessageModel)
            .filter_by(chatroom_id=chatroom.id)
            .order_by(MessageModel.id.desc())
            .first()
        )
        if chat_history is None:
            chat_history = "[]"
        else:
            chat_history = chat_history.content

        response, new_chat_history = self.state.chat_instance.get_response(
            message.content, chat_history
        )

        model = MessageModel(
            chatroom_id=chatroom.id,
            user_id=message.author.id,
            role="user",
            content=new_chat_history,
        )
        self.state.session.add(model)
        self.state.session.commit()

        await message.channel.send(response)

        return False


class ChatCommandHandler(CommandHandlerImpl):
    command_name = "chat"
    description = "create a chat"

    allowed_channels: list[str]

    perroom_state: dict[PerroomState]

    def __init__(self, config: Config, perroom_state: dict[PerroomState]):
        self.perroom_state = perroom_state

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
