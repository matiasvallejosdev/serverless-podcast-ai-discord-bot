from typing import List
import openai
import json


class ModelInterface:
    def chat_completion(self, messages: List) -> str:
        """Chat completion to gpt using openai api with a model.
        Args:
            messages (list): List of messages with openai formatting.

        Returns:
            Dict: Response contains status, role, and content.
        """
        pass


class OpenAIModel(ModelInterface):
    def __init__(
        self, api_key: str, model_engine: str, temperature: str, max_tokens: int
    ):
        super().__init__()
        openai.api_key = api_key
        self.model_engine = model_engine or "gpt-3.5-turbo-1106"
        self.temperature = temperature
        self.max_tokens = max_tokens

    def __str__(self) -> str:
        return f"Model: OpenAI. Engine: {self.model_engine}. Temperature: {self.temperature}. Max Tokens: {self.max_tokens}."

    def chat_completion(self, messages: List):
        try:
            if not messages:
                raise ValueError("Messages should not be empty.")

            if not isinstance(messages, List):
                raise ValueError("Messages should be a list.")

            if not messages[0].get("content"):
                raise ValueError("Content should not be empty.")

            chat = openai.ChatCompletion.create(
                model=self.model_engine,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            # check if there is a choices in chat
            if chat.choices:
                role = chat.choices[0].message.role
                content = chat.choices[0].message.content
                response = {
                    "status": "success",
                    "role": role,
                    "content": content,
                }
                return response
            else:
                return {
                    "status": "error",
                    "role": "program",
                    "content": "No response from model. Please try again.",
                }
        except openai.OpenAIError as e:
            # Convert the exception to a string to get the error message
            error_message_str = str(e)
            # If the error message is JSON-like, you can parse it to extract detailed information
            try:
                error_details = json.loads(error_message_str.split(" - ", 1)[1])
                error_message = error_details.get("error", {}).get("message", "")
            except (IndexError, ValueError, KeyError):
                # Fallback to the entire error string if parsing fails
                error_message = error_message_str

            return {
                "status": "error",
                "role": "assistant",
                "content": error_message,
            }
        except ValueError as ve:
            return {
                "status": "error",
                "role": "program",
                "content": f"Client-side error: {str(ve)}",
            }
