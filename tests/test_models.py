import pytest
from src.models import OpenAIModel

from dotenv import load_dotenv, find_dotenv
import os


@pytest.fixture
def model():
    load_dotenv(find_dotenv())
    model = OpenAIModel(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_engine=os.getenv("OPENAI_GPTMODEL"),
        temperature=int(os.getenv("OPENAI_TEMPERATURE")),
        max_tokens=int(os.getenv("OPENAI_TOKENS")),
    )
    return model


def test_model_instance(model):
    assert isinstance(model, OpenAIModel)


def test_str_method(model):
    assert str(model) == f"OpenAIModel: {model.model_engine}"


def test_chat_completion(model):
    messages = [{"role": "user", "content": "Hello, how are you?"}]
    response = model.chat_completion(messages)
    print("response", response)
    assert response["status"] == "success"
    assert "How can I assist you today?" in response["content"]
    assert response["role"] == "assistant"


def test_chat_completion_invalid_messages(model):
    messages = "Hello, how are you?"
    response = model.chat_completion(messages)
    assert response["status"] == "error"
    assert response["role"] == "program"
    assert "Messages should not be empty" in response["content"]


def test_chat_completion_invalid_messages(model):
    messages = "Hello, how are you?"
    response = model.chat_completion(messages)
    assert response["status"] == "error"
    assert response["role"] == "program"
    assert "Messages should be a list" in response["content"]


def test_chat_completion_api_error(model):
    # remove the api key to raise an exception
    model.model_engine = ""
    messages = [{"role": "user", "content": "Hello, how are you?"}]
    response = model.chat_completion(messages)
    assert response["status"] == "error"
    assert response["role"] is "assistant"


def test_chat_completion_empty_content(model):
    messages = [{"role": "user", "content": ""}]
    response = model.chat_completion(messages)
    assert response["status"] == "error"
    assert "Content should not be empty" in response["content"]


def test_chat_completion_special_characters(model):
    messages = [{"role": "user", "content": "@#$%^&*()"}]
    response = model.chat_completion(messages)
    assert response["status"] == "success"
    assert response["content"]  # Check if there is a valid response


def test_chat_completion_different_temperature(model):
    original_temperature = model.temperature
    model.temperature = 1  # Setting a different temperature
    try:
        messages = [{"role": "user", "content": "Hello, how are you?"}]
        response = model.chat_completion(messages)
        assert response["status"] == "success"
        assert response["content"]  # Check if there is a valid response
    finally:
        model.temperature = original_temperature  # Reset temperature


def test_str_model(model):
    assert (
        str(model)
        == f"Model: OpenAI. Engine: {model.model_engine}. Temperature: {model.temperature}. Max Tokens: {model.max_tokens}."
    )
