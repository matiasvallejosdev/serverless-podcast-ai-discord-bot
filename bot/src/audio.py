import os
import whisper
import asyncio


class AudioInterface:
    def transcript_async(self, path: str, language="es", fp16=False) -> str:
        """Transcribe an audio file asynchronously using the Whisper model using asyncio and transcribe method.

        Args:
            path (str): Path to the audio file.
            language (str, optional): Language model selected to transcribe. Defaults to "es".
            fp16 (bool, optional): Fp16 is the accuracy. Defaults to False.

        Returns:
            str: Transcription text of the audio file.
        """
        pass

    def transcript(self, path: str, language="es", fp16=False):
        """Transcribe an audio file using the Whisper model.

        Args:
            path (str): Path to the audio file.
            language (str, optional): Language model selected to transcribe. Defaults to "es".
            fp16 (bool, optional): Fp16 is the accuracy. Defaults to False.

        Raises:
            FileNotFoundError: There is no audio file in the path.
            ValueError: Audio file format not supported.
            ValueError: Audio file is empty.

        Returns:
            str: Transcription text of the audio file.
        """
        pass


class WhisperModel(AudioInterface):
    """
    A class representing a Whisper model for audio transcription.
    """

    def __init__(self) -> None:
        """
        Initializes the WhisperModel object and loads the Whisper model.
        """
        self.model = whisper.load_model("base")

    def __str__(self) -> str:
        return "Audio: Whisper Model powered by OpenAI."

    async def transcript_async(self, path: str, language="es", fp16=False):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.transcript, path, language, fp16)

    def transcript(self, path: str, language="es", fp16=False) -> str:
        # Check if the file exists and is not empty
        if not os.path.exists(path):
            raise FileNotFoundError(f"Audio file not found: {path}")

        # Check if the file format is supported
        if path.split(".")[-1] not in ["mp3", "wav", "flac"]:
            raise ValueError("Audio file format not supported")

        # Check if the file is empty
        if os.path.getsize(path) == 0:
            raise ValueError("Audio file is empty")

        # Attempt to load a portion of the audio to check its validity
        try:
            # Load the entire audio for transcription
            audio = whisper.load_audio(path)
        except Exception as e:
            print(f"Failed to load audio file: {e}")
            return None

        # Perform transcription
        result = self.model.transcribe(audio, language=language, fp16=fp16)
        transcription_text = result["text"]

        return transcription_text
