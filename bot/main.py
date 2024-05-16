from importlib import metadata
import os
from pyexpat.errors import messages
import discord

from dotenv import load_dotenv, find_dotenv
from common.utils.utils import read_json

from src.whisper.audio import WhisperModel
from src.discord.discord import DiscordClient, DiscordSender

from src.agent.agent_podcast import PodcastAgent
from src.agent.agent_memory import InMemoryDB

from data.discord import commands_info, usage_info, copyright_info
from data.prompts import summarize_prompt, pre_transcription_prompt

from src.api.serverless import ServerlessAPI

load_dotenv(find_dotenv())
API_BASE_URL = os.getenv("API_BASE_URL")
API_KEY_VALUE = os.getenv("API_KEY_VALUE")
API_KEY_HEADER = os.getenv("API_KEY_HEADER")

# Initialize models
audio = WhisperModel()
assistant = read_json("./config/prompt_assistant.json")
inmemory = InMemoryDB(assistant_prompt=assistant)
serverless = ServerlessAPI(
    api_base_url=API_BASE_URL,
    api_key_value=API_KEY_VALUE,
    api_key_header=API_KEY_HEADER,
)

base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files")
podcast_gpt = PodcastAgent(serverless, inmemory, audio, base_path)


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

        await interaction.response.defer()
        try:
            last_message, context, memory, memory_count = (
                await podcast_gpt.get_response(user_id, message)
            )
            await sender.send_message(
                interaction, user_id, message, last_message["content"]
            )
        except Exception as e:
            await sender.send_message(interaction, user_id, message, str(e))

    @client.tree.command(
        name="save_session_to_memory",
        description="Save the current conversation to the memory persistance.",
    )
    async def save(interaction: discord.Interaction):
        user_id = interaction.user.id

        if client.is_channel_allowed(str(interaction.channel_id)) is False:
            send = "You're not allowed to use this command in this channel."
            await sender.send_message(interaction, user_id, "/save", send)
            return

        await interaction.response.defer()
        try:
            res = await podcast_gpt.save_session()
            if res.get("status") == "error":
                raise Exception("Error saving the memory. Please try again.")

            messages = [
                "Memory saved successfully. We're ready for the next conversation. 🚀",
                "If you want to restore the conversation, use the /restore command.",
            ]
            await sender.send_message(
                interaction, user_id, "/save", "\n".join(messages)
            )
        except Exception as e:
            await sender.send_message(interaction, user_id, "/save", str(e))

    @client.tree.command(
        name="get_all_sessions",
        description="Restore a conversation using session_id.",
    )
    async def get_all_sessions(interaction: discord.Interaction):
        user_id = interaction.user.id

        if client.is_channel_allowed(str(interaction.channel_id)) is False:
            send = "You're not allowed to use this command in this channel."
            await sender.send_message(interaction, user_id, "/restore", send)
            return

        await interaction.response.defer()
        try:
            res = await podcast_gpt.get_all_sessions()
            body = [
                f"You saved {len(res)} sessions. Here are the details:",
                "--------------------------------------------------------",
            ]
            for session in res:
                metadata = session.get("metadata", {})
                messages = session.get("messages", [])
                
                pk = session.get("pk", "").replace("SESSION#", "")
                date = session.get("created_at", "No date")
                title = metadata.get("title", "No title")
                
                text = f"- {title} with session_id `{pk}`. It has {len(messages)} messages. ({date.split('T')[0].replace('-', '/')})"
                body.append(text)
            body.append("--------------------------------------------------------")
            body.append(
                "To restore a session, use the `/restore` command with the session_id."
            )
            await sender.send_message(interaction, user_id, "/restore", "\n".join(body))
        except Exception as e:
            await sender.send_message(interaction, user_id, "/restore", str(e))

    @client.tree.command(
        name="restore_session",
        description="Restore a conversation using session_id.",
    )
    async def restore_session(interaction: discord.Interaction, session_id: str):
        user_id = interaction.user.id

        if client.is_channel_allowed(str(interaction.channel_id)) is False:
            send = "You're not allowed to use this command in this channel."
            await sender.send_message(interaction, user_id, "/restore", send)
            return

        await interaction.response.defer()
        try:
            restored_messages = await podcast_gpt.restore_session(session_id)

            user_message = [
                "Memory restored successfully. We're ready to continue the conversation 😃",
                "If you want to save the conversation, use the `/save` command.",
            ]
            await sender.send_message(
                interaction, user_id, "/restore", "\n".join(user_message)
            )
            
            restored_messages.pop(0)
            for msg in restored_messages:
                if msg["role"] == "assistant":
                    await sender.send_message(
                        interaction, user_id, "/restore", msg["content"]
                    )
        except Exception as e:
            await sender.send_message(interaction, user_id, "/restore", str(e))

    @client.tree.command(
        name="clear_memory",
        description="Clear the memory of the current conversation.",
    )
    async def clear(interaction: discord.Interaction):
        user_id = interaction.user.id

        if client.is_channel_allowed(str(interaction.channel_id)) is False:
            send = "You're not allowed to use this command in this channel."
            await sender.send_message(interaction, user_id, "/clear", send)
            return

        await interaction.response.defer()
        try:
            podcast_gpt.clear_memory()
            messages = [
                "Memory cleared successfully. We're ready for the next conversation. 🚀",
                "If you want to restore the conversation, use the /restore command.",
            ]
            await sender.send_message(
                interaction, user_id, "/clear", "\n".join(messages)
            )
        except Exception as e:
            await sender.send_message(interaction, user_id, "/clear", str(e))

    @client.tree.command(
        name="delete_session",
        description="Delete a conversation using session_id.",
    )
    async def delete_session(interaction: discord.Interaction, session_id: str):
        user_id = interaction.user.id

        if client.is_channel_allowed(str(interaction.channel_id)) is False:
            send = "You're not allowed to use this command in this channel."
            await sender.send_message(interaction, user_id, "/delete", send)
            return

        await interaction.response.defer()
        try:
            res = await podcast_gpt.delete_session(session_id)
            if res.get("status") == "error":
                raise Exception("Session not found. Please check the session_id.")

            messages = [
                f"Session {session_id} deleted successfully. You can't restore this conversation anymore. 🗑️",
                "If you want to restore the conversation, use the `/restore` command.",
                "If you want to save the conversation, use the `/save` command.",
            ]
            await sender.send_message(
                interaction, user_id, "/delete", "\n".join(messages)
            )
        except Exception as e:
            await sender.send_message(interaction, user_id, "/delete", str(e))

    @client.tree.command(
        name="purge_channel",
        description="Purge the chat history of the user.",
    )
    async def purge_channel(interaction: discord.Interaction):
        user_id = interaction.user.id

        if client.is_channel_allowed(str(interaction.channel_id)) is False:
            send = "You're not allowed to use this command in this channel."
            await sender.send_message(interaction, user_id, "/clear", send)
            return

        await interaction.response.defer(ephemeral=True)
        channel = interaction.channel
        if channel is not None:
            deleted = await channel.purge(limit=None)
            send = f"Channel purged. Removed {len(deleted)} messages."
            await sender.send_message(interaction, user_id, "/purge", send)

    # Run your discord client
    client.run(token=os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    run()
