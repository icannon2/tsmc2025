from openai import AsyncOpenAI
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from .config import Config

google_ai_inited = False


class GlobalState:
    """
    Global state
    """

    engine: Engine
    session: Session
    client: AsyncOpenAI

    def __init__(self, config: Config):
        self.client = AsyncOpenAI()

        self.engine = create_engine(config.database_path)
        self.session = Session(bind=self.engine)

        pass
