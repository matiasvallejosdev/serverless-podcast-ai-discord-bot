from importlib import metadata
import os
from datetime import datetime
from typing import Dict

from src.agent.agent_memory import MemoryInterface
from src.api.serverless import ServerlessInterface
from src.whisper.audio import AudioInterface


class PodcastAgent:
    def __init__(
        self,
        serverless_api: ServerlessInterface,
        memory: MemoryInterface,
        audio: AudioInterface,
        base_path: str,
    ):
        self.serverless_api = serverless_api
        self.memory = memory
        self.audio = audio
        self.base_path = base_path

        self.audio_base_path = os.path.join(base_path, "audio")
        self.transcription_base_path = os.path.join(base_path, "transcriptions")

        os.makedirs(self.audio_base_path, exist_ok=True)
        os.makedirs(self.transcription_base_path, exist_ok=True)

    def __str__(self) -> str:
        message = [
            self.memory.__str__(),
            self.audio.__str__(),
        ]
        return "\n".join(message)

    async def get_response(self, user_id: str, text: str) -> str:
        # Appending the role and content to memory
        self.memory.append(user_id, {"role": "user", "content": text})

        # Generate AI Response
        session = self.memory.get()
        messages = session["messages"]
        response = await self.serverless_api.chat_completion(messages)

        last_message = response["last_message"]
        context = response["context"]
        memory = response["memory"]
        memory_count = response["memory_count"]

        self.memory.append(user_id, last_message)
        return last_message, context, memory, memory_count
    
    async def save_session(self) -> dict:
        # Save the session
        session = self.memory.get()
        messages = session["messages"]
        session_id = session["session_id"]
        metadata = {
            "title": "Podcast Agent GPT",
        }
        res = await self.serverless_api.save_session(session_id, messages, metadata)
        self.memory.remove()
        return res
    
    async def delete_session(self, session_id: str) -> dict:
        return await self.serverless_api.delete_session(session_id)
    
    async def get_all_sessions(self) -> list:
        return await self.serverless_api.get_all_session()
    
    async def restore_session(self, session_id: str):
        res = await self.serverless_api.get_session(session_id)
        messages = res.get("messages", [])
        self.memory.restore(session_id, messages)
        
    def clear_memory(self):
        self.memory.remove()

    # async def save_session(self, user_id: str) -> None:
    #     """Using the memory interface to save the session of a user.

    #     Args:
    #         user_id (str): User ID to save the session.
    #     """
    #     self.memory.save(user_id)

    # def clean_history(self, user_id: str) -> None:
    #     """Using the memory interface to clean the history of a user.

    #     Args:
    #         user_id (str): User ID to clean the history.
    #     """
    #     self.memory.remove(user_id)

    # async def get_transcriptions_async(
    #     self, file_name: str, language: str, fp16: bool
    # ) -> str:
    #     """Get transcriptions from an audio file asynchronously

    #     Args:
    #         file_name (str): File name of the audio file ending with .mp3, .wav, or .flac

    #     Returns:
    #         str: _description_
    #     """
    #     audio_path = os.path.join(self.audio_base_path, file_name)
    #     transcriptions = await self.audio.transcript_async(audio_path, language, fp16)
    #     return transcriptions

    # def save_transcription(self, transcriptions: str, name: str) -> str:
    #     """Save transcriptions to a file

    #     Args:
    #         transcriptions (str): Transcriptions string to save
    #         file_name (str): File name ending with .txt

    #     Raises:
    #         ValueError: File name cannot be empty
    #         ValueError: Transcriptions cannot be empty

    #     Returns:
    #         str: Returns the name of the file saved
    #     """
    #     if not name:
    #         raise ValueError("File name cannot be empty")
    #     if not transcriptions:
    #         raise ValueError("Transcriptions cannot be empty")

    #     file_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{name}.txt"
    #     transcriptions_path = os.path.join(self.transcription_base_path, file_name)

    #     with open(transcriptions_path, "w") as f:
    #         f.write(transcriptions)

    #     return file_name

    # def append(self, user_id: str, message: Dict, session_id: str) -> None:
    #     session_id = f"SESSION#{session_id}"
    #     path = f"{self.base_url}/sessions/{session_id}"
    #     body = {"user_id": user_id, "message": message}
    #     headers = {"x-api-key": self.api_key}
    #     response = requests.post(path, json=body, headers=headers)
    #     if response.status_code != 200:
    #         raise Exception("Failed to append the message.")
