from src.config import Config
from src.bot import DiscordBot

if __name__ == "__main__":
    config = Config()
    bot = DiscordBot(config)
    bot.run()
