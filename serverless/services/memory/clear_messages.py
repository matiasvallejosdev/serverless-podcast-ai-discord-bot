import os
import json
import boto3
from boto3.dynamodb.conditions import Key

from common.utils.lambda_utils import load_path_parameter_from_event
from common.utils.error_handler import error_response, internal_server_error
from common.utils.response_utils import success_response

table_name = os.getenv("MEMORY_TABLE_NAME")
memory_table = boto3.resource("dynamodb").Table(table_name)


def parse_and_validate(event):
    session_id = load_path_parameter_from_event(event, "session_id")
    if not session_id:
        raise ValueError("session_id is required")
    session_id = f"SESSION#{session_id}"
    return session_id


def lambda_handler(event, context):
    try:
        session_id = parse_and_validate(event)

        response = memory_table.query(
            KeyConditionExpression=Key("pk").eq(session_id)
            & Key("sk").begins_with("MESSAGE_")
        )
        messages = response.get("Items", [])

        with memory_table.batch_writer() as batch:
            for message in messages:
                batch.delete_item(Key={"pk": message["pk"], "sk": message["sk"]})

        body = {"message": "All messages deleted successfully!"}
        return success_response(body)
    except ValueError as e:
        return error_response(str(e))
    except Exception as e:
        return internal_server_error()
