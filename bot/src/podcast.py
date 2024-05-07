import os
from datetime import datetime

from ...backend.services.gpt.src.models import ModelInterface
from ...backend.services.memory.src.memory import MemoryInterface
from .audio import AudioInterface


class PodcastGpt:
    def __init__(
        self,
        model: ModelInterface,
        memory: MemoryInterface,
        audio: AudioInterface,
        base_path: str,
    ):
        self.model = model
        self.memory = memory
        self.audio = audio
        self.base_path = base_path

        self.audio_base_path = os.path.join(base_path, "audio")
        self.transcription_base_path = os.path.join(base_path, "transcriptions")

        os.makedirs(self.audio_base_path, exist_ok=True)
        os.makedirs(self.transcription_base_path, exist_ok=True)

    def __str__(self) -> str:
        message = [
            self.model.__str__(),
            self.memory.__str__(),
            self.audio.__str__(),
        ]
        return "\n".join(message)

    def get_response(self, user_id: str, text: str) -> str:
        # Appending the role and content to memory
        self.memory.append(user_id, {"role": "user", "content": text})

        # Generate AI Response
        response = self.model.chat_completion(self.memory.get(user_id))

        # Appending the role and content to memory
        self.memory.append(
            user_id, {"role": response["role"], "content": response["content"]}
        )
        return response

    def clean_history(self, user_id: str) -> None:
        """Using the memory interface to clean the history of a user.

        Args:
            user_id (str): User ID to clean the history.
        """
        self.memory.remove(user_id)

    async def get_transcriptions_async(
        self, file_name: str, language: str, fp16: bool
    ) -> str:
        """Get transcriptions from an audio file asynchronously

        Args:
            file_name (str): File name of the audio file ending with .mp3, .wav, or .flac

        Returns:
            str: _description_
        """
        audio_path = os.path.join(self.audio_base_path, file_name)
        transcriptions = await self.audio.transcript_async(audio_path, language, fp16)
        return transcriptions

    def save_transcription(self, transcriptions: str, name: str) -> str:
        """Save transcriptions to a file

        Args:
            transcriptions (str): Transcriptions string to save
            file_name (str): File name ending with .txt

        Raises:
            ValueError: File name cannot be empty
            ValueError: Transcriptions cannot be empty

        Returns:
            str: Returns the name of the file saved
        """
        if not name:
            raise ValueError("File name cannot be empty")
        if not transcriptions:
            raise ValueError("Transcriptions cannot be empty")

        file_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{name}.txt"
        transcriptions_path = os.path.join(self.transcription_base_path, file_name)

        with open(transcriptions_path, "w") as f:
            f.write(transcriptions)

        return file_name
