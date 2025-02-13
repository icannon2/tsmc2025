from google import genai
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session
from google.cloud import aiplatform

from .config import Config

google_ai_inited = False


class State:
    """
    Global state
    """

    client: aiplatform
    engine: Engine
    session: Session
    genai: genai

    def __init__(self, config: Config):
        global google_ai_inited
        if not google_ai_inited:
            google_ai_inited = True
            aiplatform.init(
                project=config.google_project_id, location=config.google_location
            )

        self.client = genai.Client(config.google_api_key)
        self.engine = create_engine(config.database_path)
        self.session = Session(bind=self.engine)

        pass
