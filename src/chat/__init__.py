from discord import ChannelType, Message, Interaction

from .room_state import RoomState
from ..state import GlobalState
from sqlalchemy.ext.declarative import declarative_base
from ..handler import CommandHandlerImpl, MessageHandlerImpl
from ..config import Config
from .persistence import Chatroom as ChatroomModel

engine = None
Base = declarative_base()


class ChatMessageHandler(MessageHandlerImpl):
    perroom_state_map: dict[str, RoomState]
    global_state: GlobalState

    def __init__(self, state: GlobalState, per_state_map: dict[str, RoomState]):
        self.global_state = state
        self.perroom_state_map = per_state_map
        super().__init__()

    async def handle_message(self, message: Message) -> bool:
        channel_id = message.channel.id

        if channel_id not in self.perroom_state_map:
            return False

        room_state = self.perroom_state_map[channel_id]

        response = await room_state.get_response(
            message.content,
        )
        visualizer = room_state.get_visualizer()
        await visualizer.process_message(response, message.channel)

        # await message.channel.send(response[:2000])

        return True


class ChatCommandHandler(CommandHandlerImpl):
    command_name = "talk"
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

    async def handle_command(self, interaction: Interaction) -> bool:
        if interaction.channel.id in self.allowed_channels:
            thread = await interaction.channel.create_thread(
                name="chat", type=ChannelType.private_thread
            )
            if thread:
                await thread.send(
                    f"Hi {interaction.user.mention}! How can I help you today?"
                )
            else:
                raise Exception("Failed to create a thread")

            room_state = RoomState(
                self.config, self.global_state, interaction.user.roles, roomtype="chat"
            )
            self.perroom_state_map[thread.id] = room_state

            # visualizer = room_state.get_visualizer()
            # await visualizer.process_message(
            #     """         aaa       <chart>{ "type": "line", "title": "TTIIITLE", "labels": [ "2022-Q1", "2022-Q2", "2022-Q3", "2022-Q4" ], "sql": "SELECT CompanyName as company, CONCAT(CalendarYear, '-', CalendarQuater) as time, Revenue as value, 'Revenue' as stat FROM FIN_Data_Derived WHERE CompanyName = 'Nvidia' AND CalendarYear = 2022 UNION ALL SELECT  CompanyName as company, CONCAT(CalendarYear, '-', CalendarQuater) as time, Gross_Profit as value, 'Gross_Profit' as stat FROM FIN_Data_Derived WHERE CompanyName = 'Nvidia' AND CalendarYear = 2022" }</chart>testtesttest

            #     here's graph2 yoyoyo
            #     <chart>  {"title": "FOUR companies", "type": "line", "x-axis-label": "company", "y-axis-label": "USD", "sql": "SELECT CompanyName AS company, CONCAT(CalendarYear, '-', CalendarQuater) AS time, Return_on_Assets AS value, 'Return_on_Assets' AS stat FROM FIN_Data_Derived WHERE CompanyName IN ('Microchip', 'Nvidia', 'Qorvo', 'TSMC')"
            #   }</chart> """,
            #     thread,
            # )

            model = ChatroomModel(thread_id=thread.id, user_id=interaction.user.id)
            self.global_state.session.add(model)
            self.global_state.session.commit()

            return True
        return False


class SummarizeCommandHandler(CommandHandlerImpl):
    command_name = "sum"
    description = "create a summarize"
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

    async def handle_command(self, interaction: Message, args) -> bool:
        if interaction.channel.id in self.allowed_channels:
            thread = await interaction.channel.create_thread(
                name="summarize", type=ChannelType.private_thread
            )
            if thread:
                await thread.send(
                    f"Hi {interaction.user.mention}! I am now generating the report..."
                )
            else:
                raise Exception("Failed to create a thread")

            room_state = RoomState(
                self.config,
                self.global_state,
                interaction.user.roles,
                roomtype="summarize",
            )

            self.perroom_state_map[thread.id] = room_state

            model = ChatroomModel(thread_id=thread.id, user_id=interaction.user.id)
            self.global_state.session.add(model)
            self.global_state.session.commit()

            response = await room_state.get_response(args)

            visualizer = room_state.get_visualizer()
            await visualizer.process_message(response, thread)


            return True
        return False
