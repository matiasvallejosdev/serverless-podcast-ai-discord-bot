import os
import pytest

from dotenv import load_dotenv, find_dotenv

from backend.services.gpt.src.models import OpenAIModel
from src.audio import WhisperModel
from backend.services.memory.src.memory import InMemory
from common.utils.utils import read_json

from src.podcast import PodcastGpt


@pytest.fixture
def base_path():
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, "temp")


@pytest.fixture
def podcast_gpt(base_path):
    load_dotenv(find_dotenv())

    model = OpenAIModel(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_engine=os.getenv("OPENAI_GPTMODEL"),
        temperature=int(os.getenv("OPENAI_TEMPERATURE")),
        max_tokens=int(os.getenv("OPENAI_TOKENS")),
    )
    audio = WhisperModel()
    system = read_json("system.json")
    inmemory = InMemory(system_message=system)

    podcast_gpt = PodcastGpt(model, inmemory, audio, base_path)
    return podcast_gpt


def test_podcast_gpt_initialization(podcast_gpt):
    assert podcast_gpt.model is not None
    assert podcast_gpt.memory is not None
    assert podcast_gpt.audio is not None
    assert os.path.isdir(podcast_gpt.audio_base_path)
    assert os.path.isdir(podcast_gpt.transcription_base_path)


def test_save_transcription_valid(podcast_gpt):
    transcriptions = "This is a test transcription."
    file_name = podcast_gpt.save_transcription(transcriptions, "test")

    assert os.path.exists(
        os.path.join(podcast_gpt.base_path, "transcriptions", file_name)
    )

    os.remove(os.path.join(podcast_gpt.base_path, "transcriptions", file_name))


def test_save_transcription_invalid_name(podcast_gpt):
    transcriptions = "This is a test transcription."

    with pytest.raises(ValueError) as e:
        podcast_gpt.save_transcription(transcriptions, "")

    assert str(e.value) == "File name cannot be empty"


def test_save_empty_transcription(podcast_gpt):
    transcriptions = ""

    with pytest.raises(ValueError) as e:
        podcast_gpt.save_transcription(transcriptions, "test.txt")

    assert str(e.value) == "Transcriptions cannot be empty"


@pytest.mark.asyncio
async def test_get_transcriptions_async_invalid_path(podcast_gpt):
    file_name = "test.mp3"
    with pytest.raises(FileNotFoundError) as e:
        await podcast_gpt.get_transcriptions_async(file_name, "es", False)
    assert (
        str(e.value)
        == f"Audio file not found: {os.path.join(podcast_gpt.audio_base_path, 'test.mp3')}"
    )


@pytest.mark.asyncio
async def test_get_transcriptions_async_valid(podcast_gpt):
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_name = os.path.join(base_path, "files", "test.mp3")
    transcriptions = await podcast_gpt.get_transcriptions_async(file_name, "es", False)
    assert transcriptions is not None
    assert "10 minutos para cambiar el mundo" in transcriptions


def test_clean_history(podcast_gpt):
    user_id = "test_user"
    podcast_gpt.memory.append(user_id, {"role": "user", "content": "Test message"})
    podcast_gpt.clean_history(user_id)
    assert podcast_gpt.memory.get(user_id) == []


def test_get_response(podcast_gpt):
    user_id = 1448
    input_text = "Hello!"
    response = podcast_gpt.get_response(user_id, input_text)

    assert response is not None
    assert response["role"] == "assistant"
    assert "Hello" in response["content"]
    assert response["status"] == "success"
