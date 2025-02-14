from discord import ChannelType, Message
from .room_state import RoomState
from ..state import GlobalState
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum
from ..handler import CommandHandlerImpl, MessageHandlerImpl
from ..config import Config
from .persistence import Message as MessageModel, Chatroom as ChatroomModel

engine = None
Base = declarative_base()


class ChatMessageHandler(MessageHandlerImpl):
    # a mapping from thread_id to the state of the chatroom
    perroom_state_map: dict[str, RoomState]
    global_state: GlobalState

    def __init__(self, state: GlobalState, per_state_map: dict[str, RoomState]):
        self.global_state = state
        self.perroom_state_map = per_state_map
        super().__init__()

    async def handle_message(self, message: Message) -> bool:
        channel_id = message.channel.id
        if channel_id in self.perroom_state_map:
            room_state = self.perroom_state_map[channel_id]
        else:
            return False
        """
        chatroom = (
            self.global_state.session.query(ChatroomModel)
            .filter_by(thread_id=channel_id)
            .first()
        )

        if chatroom is None:
            return False
        

        raw_chat_history = (
            self.global_state.session.query(MessageModel)
            .filter_by(chatroom_id=channel_id)
            .order_by(MessageModel.id.desc())
            .all()
        )
        """

        # chat_history = [history.content for history in raw_chat_history]

        response = room_state.get_response(
            message.content,
        )

        """
        message_user = MessageModel(
            chatroom_id=channel_id,
            user_id=message.author.id,
            role="user",
            content=new_chat_history[1],
        )

        message_model = MessageModel(
            chatroom_id=channel_id,
            user_id=message.author.id,
            role="model",
            content=new_chat_history[0],
        )

        self.global_state.session.add(message_user)
        self.global_state.session.add(message_model)

        self.global_state.session.commit()
        """

        await message.channel.send(response)

        return True


class ChatCommandHandler(CommandHandlerImpl):
    command_name = "chat"
    description = "create a chat"
    global_state: GlobalState
    allowed_channels: list[str]
    config: Config
    perroom_state_map: dict[str, RoomState]

    def __init__(
        self,
        config: Config,
        state: GlobalState,
        perroom_state_map: dict[str, RoomState],
    ):
        self.perroom_state_map = perroom_state_map
        self.global_state = state
        self.allowed_channels = config.allowed_channels
        self.config = config
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

            room_state = RoomState(self.config, self.global_state, message.author.roles)
            self.perroom_state_map[thread.id] = room_state

            model = ChatroomModel(thread_id=thread.id, user_id=message.author.id)
            self.global_state.session.add(model)
            self.global_state.session.commit()

            return True
        return False
