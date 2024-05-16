import os
import boto3

from boto3.dynamodb.conditions import Key, Attr
from common.utils.lambda_utils import load_body_from_event

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
    session_id = load_path_parameter_from_event(event, "session_id")
    if not session_id:
        raise ValueError("session_id is required")
    session_id = f"SESSION#{session_id}"

    body = load_body_from_event(event)
    if not body:
        raise ValueError("Body is required")
    return session_id, body


def lambda_handler(event, context):
    try:
        session_id, body = parse_and_validate(event)

        res_session = memory_table.query(
            KeyConditionExpression=Key("pk").eq(session_id),
            FilterExpression=Attr("is_deleted").eq(False),
        )
        session_item = res_session.get("Items", [])

        if not session_item:
            return not_found_error()

        metadata = session_item[0].get("metadata", {})
        metadata.update(body)

        res = memory_table.update_item(
            Key={"pk": session_id},
            UpdateExpression="SET metadata = :val",
            ExpressionAttributeValues={":val": metadata},
        )

        if res["ResponseMetadata"]["HTTPStatusCode"] != 200:
            raise boto3.exceptions.Boto3Error("Failed to update session metadata!")

        body = {"message": "Session metadata updated successfully"}
        return success_response(body)
    except ValueError as e:
        return error_response(str(e))
    except boto3.exceptions.Boto3Error as e:
        return error_response(str(e))
    except Exception as e:
        return internal_server_error()
