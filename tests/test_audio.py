import pytest
import asyncio

from src.audio import WhisperModel


@pytest.fixture
def whisper_model():
    return WhisperModel()


@pytest.fixture
def base_path():
    base_path = "tests/files"
    return base_path


def test_whisper_model(whisper_model):
    assert whisper_model is not None
    assert whisper_model.model is not None


def test_valid_audio(base_path, whisper_model):
    path = f"{base_path}/test.mp3"
    text = whisper_model.transcript(path)
    assert text is not None
    assert "10 minutos para cambiar el mundo" in text


def test_invalid_path_audio(base_path, whisper_model):
    path = f"{base_path}/test.wav"

    with pytest.raises(FileNotFoundError) as e:
        whisper_model.transcript(path)

    assert str(e.value) == f"Audio file not found: {path}"


@pytest.mark.parametrize(
    "file_notsupported",
    [
        "notsupported.txt",
        "notsupported.jpg",
        "notsupported.png",
        "notsupported.mp4",
    ],
)
def test_invalid_format_audio(base_path, whisper_model, file_notsupported):
    path = f"{base_path}/{file_notsupported}"

    with pytest.raises(ValueError) as e:
        whisper_model.transcript(path)

    assert str(e.value) == "Audio file format not supported"


def test_empty_audio(base_path, whisper_model):
    path = f"{base_path}/empty.mp3"

    with pytest.raises(ValueError) as e:
        whisper_model.transcript(path)

    assert str(e.value) == "Audio file is empty"


@pytest.mark.asyncio
async def test_transcript_async(base_path, whisper_model):
    path = f"{base_path}/test.mp3"
    # Use await to call the asynchronous method
    text = await whisper_model.transcript_async(path)
    assert text is not None
    assert "10 minutos para cambiar el mundo" in text


def test_transcription_in_english(base_path, whisper_model):
    path = f"{base_path}/test_english.mp3"
    text = whisper_model.transcript(path, language="en")
    assert text is not None
    assert "What can I do for you?" in text


@pytest.mark.asyncio
async def test_concurrent_transcriptions(base_path):
    async def transcribe(path):
        # Instantiate a new model for each transcription task
        whisper_model = WhisperModel()
        return await whisper_model.transcript_async(path)

    path = f"{base_path}/test.mp3"
    tasks = [transcribe(path) for _ in range(5)]  # Create multiple tasks
    results = await asyncio.gather(*tasks)

    assert all(result is not None for result in results)
    assert all("10 minutos para cambiar el mundo" in result for result in results)


def test_large_audio_file(base_path, whisper_model):
    path = f"{base_path}/large_audio.mp3"
    text = whisper_model.transcript(path)
    assert text is not None
    assert len(text) > 1000


def test_whisper_str(whisper_model):
    assert str(whisper_model) == "Audio: Whisper Model powered by OpenAI."
