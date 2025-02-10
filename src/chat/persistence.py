from sqlalchemy import Column, Integer, String


class Chatroom:
    __tabename__ = "chatroom"

    id = Column(Integer, primary_key=True)
    thread_id = Column(String(255), nullable=False)
    user_id = Column(String(255), nullable=False)

    def __init__(self, id: int, thread_id: str, user_id: str):
        self.id = id
        self.thread_id = thread_id
        self.user_id = user_id


class Message:
    __tablename__ = "message"

    id = Column(Integer, primary_key=True)
    chatroom_id = Column(Integer, nullable=False)
    user_id = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)
    content = Column(String(255), nullable=False)

    def __init__(
        self, id: int, chatroom_id: int, user_id: str, role: str, content: str
    ):
        self.id = id
        self.chatroom_id = chatroom_id
        self.user_id = user_id
        self.role = role
        self.content = content
