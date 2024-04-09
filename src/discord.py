import discord
from discord.ext import commands
from discord import Interaction, Intents, Message


class DiscordSender:
    async def send_message(
        self, interaction: Interaction, user_id: str, receive: str, message: str
    ):
        """
        Send a message using the Discord API to a Discord channel, either publicly or privately.

        Args:
            interaction (Interaction): The Discord interaction object.
            user_id (str): ID of the user who initiated the interaction.
            sent (str): The message received from the user.
            message (str): The response message to be sent.
        """
        try:
            print(f"{user_id} request: {receive}, response: {message}")

            # Check if interaction has been responded to
            if interaction.response.is_done():
                # Use follow-up for already acknowledged interactions
                await interaction.followup.send(message)
            else:
                # Acknowledge the interaction if not already done
                await interaction.response.send_message(message)
        except Exception as e:
            print(f"Error sending message: {e}")


class DiscordClient(commands.Bot):
    def __init__(
        self,
        intents: Intents,
        guild_id: int,
        guild_channel: str,
        commands_list: list,
        name: str,
        context: str,
        usage: list,
        copyright: list,
        command_prefix="!",
    ) -> None:
        super().__init__(intents=intents, command_prefix=command_prefix)
        self.guild_id = guild_id
        self.guild_channel = guild_channel
        self.commands_list = commands_list
        self.context = context
        self.name = name
        self.usage = usage
        self.copyright = copyright
        self.activity = discord.Activity(type=discord.ActivityType.watching, name=self.name)

    def __str__(self):
        return f"Discord Client ({self.name}): {self.guild_id}, {self.guild_channel}"

    def get_default_message(self):
        default_message = [
            f"# Welcome to {self.name}!",
            "This is a Discord bot that uses OpenAI's GPT and Whisper to analyze and summarize podcast episodes.",
            "## Context:",
            self.context,
            "## Commands:",
            *self.commands_list,
            "## Usage:",
            *self.usage,
            "## Legal:",
            *self.copyright,
        ]
        return default_message

    async def on_ready(self):
        for guild in self.guilds:
            if guild.id == self.guild_id:
                synced = await self.tree.sync()
                print(
                    self.__str__(),
                    f"{guild.name} (id: {guild.id})\n"
                    f"Discord Version: {discord.__version__}\n"
                    f"Commands: {str(len(synced))}\n"
                )
                break
            else:
                print("Bot is not in the specified guild.")

    async def on_message(self, message: Message):
        if message.author == self.user:
            return

        if self.is_channel_allowed(str(message.channel.id)) is False:
            return await message.channel.send(
                "You're not allowed to use this command in this channel."
            )

        for msg in self.get_default_message():
            await message.channel.send(msg)

    def is_channel_allowed(self, channel: str) -> bool:
        return channel == self.guild_channel
