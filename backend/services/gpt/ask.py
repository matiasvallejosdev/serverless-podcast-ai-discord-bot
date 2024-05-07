import os
import json
import openai

from typing import List
from .src.models import OpenAIModel
from utils.lambda_utils import load_body_from_event


def lambda_handler(event, context):
    if not event.get("body"):
        return {
            "statusCode": 400,
            "body": json.dumps(
                {"message": "Body parameters are missing. You must include 'messages'."}
            ),
        }

    body = load_body_from_event(event)
    messages = body.get("messages")

    if len(messages) == 0:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Body 'messages' must not be empty."}),
        }

    if isinstance(messages, List) is False:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Body 'messages' must be a list."}),
        }

    for msg in messages:
        if not msg.get("content") or not msg.get("role"):
            return {
                "statusCode": 400,
                "body": json.dumps(
                    {
                        "message": "Messages should not be empty. It should have 'role' and 'content' keys."
                    }
                ),
            }

    try:
        model = OpenAIModel(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_engine=os.getenv("OPENAI_GPTMODEL"),
            temperature=int(os.getenv("OPENAI_TEMPERATURE")),
            max_tokens=int(os.getenv("OPENAI_TOKENS")),
        )

        res = model.chat_completion(messages)
        if res.get("status") != "success":
            return {
                "statusCode": 400,
                "body": json.dumps({"role": res["role"], "content": res["content"]}),
            }
        else:
            messages.append({"role": res["role"], "content": res["content"]})
            return {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "context": model.__str__(),
                        "last_message": {
                            "role": res["role"],
                            "content": res["content"],
                        },
                        "memory": messages,
                        "memory_count": len(messages),
                    }
                ),
            }

        res = {"messages": messages}
        return {"statusCode": 200, "body": json.dumps(res)}
    except ValueError as ve:
        return {
            "statusCode": 400,
            "body": json.dumps({"role": res["role"], "content": res["content"]}),
        }
    except openai.OpenAIError as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"role": res["role"], "content": res["content"]}),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Internal Server Error."}),
        }
