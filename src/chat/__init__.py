from discord import ChannelType, Message
from google import genai
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session
from ..bot import CommandHandlerImpl, MessageHandlerImpl
from config import Config

state = None


class State:
    client: genai.Client
    engine: Engine
    session: Session

    def __init__(self, config: Config):
        self.client = genai.Client(config.google_api_key)
        self.engine = create_engine(config.database_path)
        self.session = Session(bind=self.engine)

        pass


class ChatCommandHandler(CommandHandlerImpl):
    command_name = "chat"
    description = "create a chat"

    allowed_channels: list[str]

    def __init__(self, config: Config):
        global state
        if state is None:
            state = State(config)

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

            # presist the thread id in the database

            return True
        return False


class ChatMessageHandler(MessageHandlerImpl):
    def __init__(self, config: Config):
        global state
        if state is None:
            state = State(config)
        super().__init__()

    async def handle_message(self, message: Message) -> bool:
        channel_id = message.channel.id
        # attempt to get the thread id from the database
        return False


"""
An abstract class for function calling.

We actually create new instances of this class when a chatroom is created.
"""


class FunctionCalling:
    name: str
    description: str
    parameters: any

    def __init__(self, state: State):
        pass

    """
    Process the request and return the response.

    request is a string that conforms to the function's parameters.

    For example, if the function is to add two numbers, request can be "{\"a\": 1, \"b\": 2 }".(serialized json string)
    """

    def process(self, request: str):
        pass
