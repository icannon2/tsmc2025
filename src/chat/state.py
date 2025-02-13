from google import genai
from google.cloud import aiplatform

from ..datasource import SQLRunner

from ..config import Config


class State:
    """
    per room state
    """

    client: aiplatform
    sql_runner: SQLRunner

    def __init__(self, config: Config):
        self.client = genai.Client(config.google_api_key)
        self.sql_runner = SQLRunner(config.datasource_path)

        pass
