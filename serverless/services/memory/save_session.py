import os
import boto3
import datetime

from boto3.dynamodb.conditions import Key, Attr

from common.utils.lambda_utils import (
    load_body_from_event,
    load_path_parameter_from_event,
)
from common.utils.error_handler import error_response, internal_server_error
from common.utils.response_utils import success_response

table_name = os.getenv("MEMORY_TABLE_NAME")
memory_table = boto3.resource("dynamodb").Table(table_name)


def parse_and_validate(event):
    session_id = load_path_parameter_from_event(event, "session_id")
    if not session_id:
        raise ValueError("session_id is required")
    session_id = f"SESSION#{session_id}"

    body = load_body_from_event(event)
    messages = body.get("messages")
    metadata = body.get("metadata", {})
    if not messages:
        raise ValueError("'messages' is required.")

    if not isinstance(messages, list):
        raise ValueError("messages should be a list of messages")

    for message in messages:
        if not isinstance(message, dict):
            raise ValueError("Each message should be a dictionary")

        if (
            "role" not in message
            or "content" not in message
        ):
            raise ValueError(
                "Each message should have 'role' and 'content' keys."
            )

    return session_id, messages, metadata


def lambda_handler(event, context):
    try:
        session_id, messages, metadata = parse_and_validate(event)

        session = memory_table.query(
            KeyConditionExpression=Key("pk").eq(session_id)
        )
        
        if session.get("Items"):
            return error_response("Session already exists. You can't save it again. You can only update metadata.")
        
        item = {
            "pk": session_id,
            "messages": messages,
            "metadata": metadata,
            "is_deleted": False,
            "created_at": datetime.datetime.now().isoformat(),
        }
        memory_table.put_item(Item=item)

        return success_response(item)
    except ValueError as e:
        return error_response(str(e))
    except Exception as e:
        return internal_server_error()
