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
    message = body.get("message")
    user_id = body.get("user_id")
    if not message or not user_id:
        raise ValueError("'message' and 'user_id' is required.")

    if not message.get("role") or not message.get("content"):
        raise ValueError("Both 'role' and 'content' are required in the message")
    return session_id, message, user_id


def lambda_handler(event, context):
    try:
        session_id, message, user_id = parse_and_validate(event)
        message_id = f"MESSAGE_{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}"

        item = {
            "pk": session_id,
            "sk": message_id,
            "message": {"role": message["role"], "content": message["content"]},
            "created_at": datetime.datetime.now().isoformat(),
        }

        metadata_response = memory_table.query(
            KeyConditionExpression=Key("pk").eq(session_id) & Key("sk").eq("METADATA"),
            FilterExpression=Attr("is_deleted").eq(False) & Attr("is_deleted").exists(),
        )
        metadata_items = metadata_response.get("Items", [])
        if not metadata_items:
            metadata_item = {
                "pk": session_id,
                "sk": "METADATA",
                "is_deleted": False,
                "user_id": user_id,
                "created_at": datetime.datetime.now().isoformat(),
            }
            memory_table.put_item(Item=metadata_item)

        memory_table.put_item(Item=item)
        return success_response(item)
    except ValueError as e:
        return error_response(str(e))
    except Exception as e:
        return internal_server_error()
