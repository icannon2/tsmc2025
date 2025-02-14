from src.chat.room_state import RoomState
from src.config import Config
from src.state import GlobalState
import asyncio


class FakeRole:
    def __init__(self, id):
        self.id = id


async def main():
    config = Config()
    global_state = GlobalState(config)
    room = RoomState(
        config, global_state, [FakeRole(1339499087489273868)], roomtype="summarize"
    )
    print("Room created")
    print("Hi! How can I help you today?")
    while True:
        message = input("User: ")
        response = await room.get_response(message)
        print("Bot: " + response)


if __name__ == "__main__":
    asyncio.run(main())
