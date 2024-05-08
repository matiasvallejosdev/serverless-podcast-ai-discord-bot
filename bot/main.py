import os
import discord

from dotenv import load_dotenv, find_dotenv
from common.utils.utils import read_json

from src.audio.audio import WhisperModel
from src.discord.discord import DiscordClient, DiscordSender

from src.app.podcast import PodcastGpt

from data.discord import commands_info, usage_info, copyright_info
from data.prompts import summarize_prompt, pre_transcription_prompt

from src.persitance.memory import InMemory
from src.api.serverless import ServerlessAPI

load_dotenv(find_dotenv())
API_BASE_URL = os.getenv("API_BASE_URL")
API_KEY_VALUE = os.getenv("API_KEY_VALUE")
API_KEY_HEADER = os.getenv("API_KEY_HEADER")

# Initialize models
audio = WhisperModel()
system = read_json("./config/system.json")
inmemory = InMemory(system_message="system")
serverless = ServerlessAPI(api_base_url=API_BASE_URL, api_key_value=API_KEY_VALUE, api_key_header=API_KEY_HEADER)

base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files")
podcast_gpt = PodcastGpt(serverless, inmemory, audio, base_path)


def run():
    """Run discord bot using discord client and sender."""
    intents = discord.Intents.all()

    client = DiscordClient(
        intents=intents,
        guild_id=int(os.getenv("DISCORD_GUILD_ID")),
        guild_channel=os.getenv("DISCORD_GUILD_CHANNEL"),
        name="Podcast Agent GPT",
        commands_list=commands_info,
        context=str(podcast_gpt),
        usage=usage_info,
        copyright=copyright_info,
    )
    sender = DiscordSender()

    @client.tree.command(
        name="help",
        description="Displays this list of commands, helping you understand how to interact with the agent.",
    )
    async def help(interaction: discord.Interaction):
        user_id = interaction.user.id

        if client.is_channel_allowed(str(interaction.channel_id)) is False:
            send = "You're not allowed to use this command in this channel."
            await sender.send_message(interaction, user_id, "/help", send)
            return

        send = "\n".join(usage_info)
        await sender.send_message(interaction, user_id, "/help", send)

    @client.tree.command(
        name="ask",
        description="Ask any question, and ChatGPT will respond with an insightful answer.",
    )
    async def ask(interaction: discord.Interaction, message: str):
        user_id = interaction.user.id

        if client.is_channel_allowed(str(interaction.channel_id)) is False:
            send = "You're not allowed to use this command in this channel."
            await sender.send_message(interaction, user_id, message, send)
            return

        if interaction.user == client.user:
            return

        await interaction.response.defer()
        try:
            response = await podcast_gpt.get_response(user_id, message)
            await sender.send_message(interaction, user_id, message, response["content"])
        except Exception as e:
            await sender.send_message(interaction, user_id, message, str(e))

    # Run your discord client
    client.run(token=os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    run()
