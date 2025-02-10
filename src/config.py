from os import environ


class Config:
    database_path: str
    discord_token: str
    google_api_key: str
    google_project_id: str
    google_location: str
    """
    List of channels where the commands is allowed to work
    """
    allowed_channels: list[str] = []

    """
    Load the configuration from env
    """

    def __init__(self):
        self.database_path = environ.get("DATABASE_PATH")
        self.discord_token = environ.get("DISCORD_TOKEN")
        self.google_api_key = environ.get("GOOGLE_API_KEY")
