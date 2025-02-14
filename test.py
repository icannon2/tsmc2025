from src.chat.room_state import RoomState
from src.config import Config
from src.state import GlobalState
import asyncio


async def main():
    config = Config()
    global_state = GlobalState(config)
    room = RoomState(config, global_state, [])
    print("Room created")
    print("Hi! How can I help you today?")
    while True:
        message = input("User: ")
        response = await room.get_response(message)
        print("Bot:" + response)


if __name__ == "__main__":
    asyncio.run(main())
