import os
import boto3

from boto3.dynamodb.conditions import Attr, Key

from common.utils.lambda_utils import load_path_parameter_from_event
from common.utils.error_handler import (
    error_response,
    internal_server_error,
    not_found_error,
)
from common.utils.response_utils import success_response

table_name = os.getenv("MEMORY_TABLE_NAME")
memory_table = boto3.resource("dynamodb").Table(table_name)


def parse_and_validate(event):
    user_id = int(event.get("pathParameters", {}).get("user_id"))
    if not user_id:
        raise ValueError("user_id is required")
    user_id = int(user_id)
    return user_id


def clean_messages_items(message_items):
    messages = [msg["message"] for msg in message_items if "message" in msg]
    return messages


def lambda_handler(event, context):
    try:
        user_id = parse_and_validate(event)

        response = memory_table.scan(
            FilterExpression=Attr("is_deleted").eq(False)
            & Attr("sk").eq("METADATA")
            & Attr("user_id").eq(user_id)
        )
        sessions_items = response.get("Items", [])

        if not sessions_items or len(sessions_items) == 0:
            return not_found_error()

        for session in sessions_items:
            session_id = session["pk"]
            session.pop("user_id", None)
            messages_response = memory_table.query(
                KeyConditionExpression=Key("pk").eq(session_id)
                & Key("sk").begins_with("MESSAGE_")
            )
            messages_items = messages_response.get("Items", [])
            messages = clean_messages_items(messages_items)
            session["messages"] = messages

        data = (
            {
                key: val
                for key, val in sessions_items[0].items()
                if key != "sk" and key != "created_at" and key != "is_deleted"
            }
            if sessions_items
            else {}
        )
        body = {"user_id": user_id, "sessions": data}
        return success_response(body)
    except ValueError as e:
        return error_response(str(e))
    except Exception as e:
        return internal_server_error()
