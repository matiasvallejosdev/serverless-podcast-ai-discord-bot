import os
import discord
from discord.ext.commands import CommandInvokeError

from datetime import datetime

from dotenv import load_dotenv, find_dotenv
from src.utils import read_json

from src.audio import WhisperModel
from src.models import OpenAIModel
from src.memory import InMemory
from src.discord import DiscordClient, DiscordSender

from src.podcast import PodcastGpt

from data.discord import commands_info, usage_info, copyright_info
from data.prompts import summarize_prompt

load_dotenv(find_dotenv())

# Initialize models
model = OpenAIModel(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_engine=os.getenv("OPENAI_GPTMODEL"),
    temperature=int(os.getenv("OPENAI_TEMPERATURE")),
    max_tokens=int(os.getenv("OPENAI_TOKENS")),
)
audio = WhisperModel()
system = read_json("system.json")
inmemory = InMemory(system_message=system)

base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files")
podcast_gpt = PodcastGpt(model, inmemory, audio, base_path)


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
        response = podcast_gpt.get_response(user_id, message)
        await sender.send_message(interaction, user_id, message, response["content"])

    @client.tree.command(
        name="purge",
        description="Purge the chat history of the user.",
    )
    async def purge(interaction: discord.Interaction):
        user_id = interaction.user.id
        channel_id = interaction.channel_id
        channel = client.get_channel(channel_id)

        if client.is_channel_allowed(str(channel_id)) is False:
            send = "You're not allowed to use this command in this channel."
            await sender.send_message(interaction, user_id, "/purge", send)
            return

        await interaction.response.defer(ephemeral=True)
        if channel is not None:
            deleted = await channel.purge(limit=None)
            send = f"Channel purged. Deleted {len(deleted)} messages."
            await sender.send_message(interaction, user_id, "/purge", send)

    @client.tree.command(
        name="clear",
        description="Clears your chat history, removing all previous interactions and responses.",
    )
    async def clear(interaction: discord.Interaction):
        user_id = interaction.user.id
        channel_id = interaction.channel_id
        channel = client.get_channel(channel_id)

        if client.is_channel_allowed(str(channel_id)) is False:
            send = "You're not allowed to use this command in this channel."
            await sender.send_message(interaction, user_id, "/clear", send)
            return

        if channel is not None:
            podcast_gpt.clean_history(user_id)
            send = [
                f"Messages history for {user_id} was cleared.",
                "You can now start a new conversation.",
            ]
            send_out = "\n".join(send)
            await sender.send_message(interaction, user_id, "/clear", send_out)

    # Upload audio file command
    @client.tree.command(
        name="upload_audio",
        description="Upload an audio file. The bot will transcribe it based on the selected language.",
    )
    async def upload_audio(
        interaction: discord.Interaction, attachment: discord.Attachment, language: str
    ):
        user_id = interaction.user.id
        channel_id = interaction.channel_id

        if client.is_channel_allowed(str(channel_id)) is False:
            send = "You're not allowed to use this command in this channel."
            await sender.send_message(interaction, user_id, "/upload_audio", send)
            return

        if not attachment.filename.lower().endswith((".mp3", ".wav", ".ogg")):
            await sender.send_message(
                interaction,
                user_id,
                "/upload_audio",
                "Please upload a valid audio file in mp3, wav, or ogg format.",
            )
            return

        language = language.lower()
        if language not in ["en", "es"]:
            await sender.send_message(
                interaction,
                user_id,
                "/upload_audio",
                "Please select a valid language: `en` for English or `es` for Spanish.",
            )
            return

        await interaction.response.defer()
        send = [
            f"Received audio file: {attachment.filename}",
            "Processing. Please wait...",
        ]
        send_out = "\n".join(send)
        await sender.send_message(interaction, user_id, "/upload_audio", send_out)

        attachment.filename = (
            f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{attachment.filename}"
        )
        audio_path = os.path.join(podcast_gpt.audio_base_path, attachment.filename)

        try:
            await attachment.save(audio_path)
        except IOError as e:
            await sender.send_message(
                interaction,
                user_id,
                "/upload_audio",
                f"Failed to save the audio file: {e}",
            )
            return

        try:
            audio_text = await podcast_gpt.audio.transcript_async(
                audio_path, language, False
            )
        except Exception as e:
            await sender.send_message(
                interaction,
                user_id,
                "/upload_audio",
                f"Failed to transcribe the audio file: {e}",
            )
            return

        name = os.path.splitext(attachment.filename)[0]
        transcript_filename = podcast_gpt.save_transcription(audio_text, name)
        transcript_path = os.path.join(
            # get file name without extension
            podcast_gpt.transcription_base_path,
            transcript_filename,
        )
        send = [
            "Audio transcription completed. I will send you the transcription file.",
        ]
        send_out = "\n".join(send)
        await sender.send_message(interaction, user_id, "/upload_audio", send_out)

        try:
            # Send the text file
            file = discord.File(transcript_path, filename=transcript_filename)
            await interaction.followup.send(file=file)
        except CommandInvokeError as e:
            await sender.send_message(
                interaction,
                user_id,
                "/upload_audio",
                f"Failed to send the transcription file: {e}",
            )
        try:
            last_message = []
            response = podcast_gpt.get_response(user_id, summarize_prompt)

            if response["status"] == "success":
                last_message.append(response["content"])
            else:
                error = response["content"]
                raise Exception(error)

            response = podcast_gpt.get_response(user_id, audio_text)
            if response["status"] == "success":
                last_message.append(response["content"])
            else:
                error = response["content"]
                raise Exception(error)

            send_out = "\n".join(last_message)
            await sender.send_message(interaction, user_id, "/upload_audio", send_out)
        except Exception as e:
            await sender.send_message(
                interaction,
                user_id,
                "/upload_audio",
                f"Failed to process the audio file: {e}",
            )
            await sender.send_message(
                interaction,
                user_id,
                "/upload_audio",
                "Please try again checking the audio file format and language.",
            )
            return

        send = [
            "Use the `/ask [question]` command to interact with me.",
            "If you need a summary of the audio content, use the `/summarize` command."
            "The `/clear` command will remove the chat history.",
        ]
        send_out = "\n".join(send)
        await sender.send_message(interaction, user_id, "/upload_audio", send_out)

        send = "I'm here to help you understand the content better."
        await sender.send_message(interaction, user_id, "/upload_audio", send)

    # Summarize
    @client.tree.command(
        name="summarize",
        description="Summarize the text from the audio transcription.",
    )
    async def summarize(interaction: discord.Interaction):
        user_id = interaction.user.id
        channel_id = interaction.channel_id

        if client.is_channel_allowed(str(channel_id)) is False:
            send = "You're not allowed to use this command in this channel."
            await sender.send_message(interaction, user_id, "/upload_audio", send)
            return

        await interaction.response.defer()

        try:
            prompt = "Based on the audio transcription provided, distill the key points and summarize the main message."
            response = podcast_gpt.get_response(user_id, prompt)
            if response["status"] == "success":
                await sender.send_message(
                    interaction, user_id, "/summarize", response["content"]
                )
            else:
                error = response["content"]
                raise Exception(error)
        except Exception as e:
            await sender.send_message(
                interaction,
                user_id,
                "/summarize" f"Falied to summarize the audio transcription: {e}",
            )
            return

    # Run your discord client
    client.run(token=os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    run()
