from os import environ
from dotenv import load_dotenv
  # Load environment variables from .env

class Config:
    database_path: str
    datasource_path: str
    discord_token: str
    google_api_key: str
    google_project_id: str
    google_location: str
    
    gemini_api_key: str
    """
    List of channels where the commands is allowed to work
    """
    allowed_channels: list[str] = [1339150923594727488]

    """
    Load the configuration from env
    """

    def __init__(self):
        load_dotenv()
        self.database_path = environ.get("DATABASE_PATH")
        self.discord_token = environ.get("DISCORD_TOKEN")
        self.google_api_key = environ.get("GOOGLE_API_KEY")
        self.gemini_api_key = environ.get("GEMINI_API_KEY")
