from google import genai
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session
from google.cloud import aiplatform
from google import genai

from .config import Config

google_ai_inited = False


class GlobalState:
    """
    Global state
    """

    engine: Engine
    session: Session
    client: genai.Client

    def __init__(self, config: Config):
        self.client = genai.Client(api_key=config.gemini_api_key)
        self.engine = create_engine(config.database_path)
        self.session = Session(bind=self.engine)

        pass
