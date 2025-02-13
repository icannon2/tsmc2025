from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Chatroom(Base):
    __tablename__ = "chatroom"

    id = Column(Integer, primary_key=True)
    thread_id = Column(String(255), nullable=False)
    user_id = Column(String(255), nullable=False)


class Message(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True)
    chatroom_id = Column(Integer, nullable=False)
    user_id = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)
    content = Column(String(255), nullable=False)
