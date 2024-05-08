import os
import openai

from typing import List, Dict, Any
from .src.models import OpenAIModel

from common.utils.lambda_utils import load_body_from_event
from common.utils.error_handler import error_response, internal_server_error
from common.utils.response_utils import success_response


API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_ENGINE = os.getenv("OPENAI_GPTMODEL")
TEMPERATURE = int(os.getenv("OPENAI_TEMPERATURE", 0))
MAX_TOKENS = int(os.getenv("OPENAI_TOKENS", 0))


def parse_and_validate(event: Dict[str, Any]) -> List[Dict[str, str]]:
    messages = load_body_from_event(event).get("messages")

    if not messages or len(messages) == 0:
        raise ValueError("Body 'messages' must not be empty.")

    if not isinstance(messages, list):
        raise ValueError("Body 'messages' must be a list.")

    for msg in messages:
        if not msg.get("content") or not msg.get("role"):
            raise ValueError(
                "Messages should not be empty. It should have 'role' and 'content' keys."
            )
    return messages


def lambda_handler(event, context):
    try:
        messages = parse_and_validate(event)
        model = OpenAIModel(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_engine=os.getenv("OPENAI_GPTMODEL"),
            temperature=int(os.getenv("OPENAI_TEMPERATURE")),
            max_tokens=int(os.getenv("OPENAI_TOKENS")),
        )

        res = model.chat_completion(messages)
        if res.get("status") != "success":
            error_content = res["content"]
            return error_response(error_content)
        else:
            messages.append({"role": res["role"], "content": res["content"]})
            body = {
                "context": str(model),
                "last_message": {
                    "role": res["role"],
                    "content": res["content"],
                },
                "memory": messages,
                "memory_count": len(messages),
            }
            return success_response(body)
    except ValueError as e:
        return error_response(str(e))
    except openai.OpenAIError as e:
        return error_response(str(e))
    except Exception as e:
        return internal_server_error()
