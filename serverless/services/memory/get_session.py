from importlib import metadata
import os
import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            if obj % 1 > 0:
                return float(obj)
            else:
                return int(obj)
        return super(DecimalEncoder, self).default(obj)


def lambda_handler(event, context):
    # Extracting user_id from pathParameters safely
    session_id = event.get("pathParameters", {}).get("session_id")
    if not session_id:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "session_id is required"}),
        }
    session_id = f"SESSION#{session_id}"

    # Initialize DynamoDB resource
    dynamodb = boto3.resource("dynamodb")
    memory_table = dynamodb.Table(os.getenv("MEMORY_TABLE_NAME"))

    try:
        # Query DynamoDB for metadata
        metadata_response = memory_table.query(
            KeyConditionExpression=Key("pk").eq(session_id) & Key("sk").eq("METADATA"),
            FilterExpression=Attr("is_deleted").eq(False) & Attr("is_deleted").exists(),
        )
        metadata_items = metadata_response.get("Items", [])

        if not metadata_items:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": "Session not found"}),
            }

        # Query DynamoDB for messages
        message_response = memory_table.query(
            KeyConditionExpression=Key("pk").eq(session_id)
            & Key("sk").begins_with("MESSAGE_")
        )
        message_items = message_response.get("Items", [])

        # perform metadata cleanup
        metadata = (
            {key: val for key, val in metadata_items[0].items() if key != "pk"}
            if metadata_items
            else {}
        )
        messages = [
            {key: val for key, val in msg.items() if key == "message" or key == "sk"}
            for msg in message_items
        ]
    except Exception as e:
        # Handle possible exceptions during the query operation
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": str(e)}),
        }

    # Return the query results as JSON
    response_body = {
        "session_id": session_id,
        "metadata": metadata,
        "messages": messages,
    }
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(response_body, cls=DecimalEncoder),
    }
