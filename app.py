from src.config import Config
import discord
from src.chat import ChatMessageHandler, ChatCommandHandler, SummarizeCommandHandler
from src.state import GlobalState
from src.account import AccountCommandHandler
from discord import app_commands


config = Config()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

perroom_state_map = {}
global_state = GlobalState(config)

message_handler = ChatMessageHandler(global_state, perroom_state_map)
chat_command_handler = ChatCommandHandler(config, global_state, perroom_state_map)
summarize_command_handler = SummarizeCommandHandler(
    config, global_state, perroom_state_map
)
account_command_handler = AccountCommandHandler()


@client.event
async def on_ready():
    await tree.sync()  # Sync the command tree with Discord
    print(f"目前登入身份 --> {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    await message_handler.handle_message(message)


@tree.command(name="talk", description="Have a chat with the bot")
async def talk(interaction: discord.Interaction):
    await chat_command_handler.handle_command(interaction)
    await interaction.response.send_message("Has opened a thread...")


@tree.command(name="summarize", description="Give a summarize")
@app_commands.describe(
    language="language",
    company="company",
    start_time="Ex: 2023/Q1",
    end_time="Ex. 2024/Q2",
)
async def summarize(
    interaction: discord.Interaction,
    language: str,
    company: str,
    start_time: str,
    end_time: str,
):
    await summarize_command_handler.handle_command(
        interaction, (language, company, start_time, end_time)
    )

@tree.command(name="register", description="For account operation")
async def register(interaction: discord.Interaction):
    await account_command_handler.handle_command(interaction)


client.run(config.discord_token)
