import os
import json
import boto3
from boto3.dynamodb.conditions import Key


def lambda_handler(event, context):
    # Extract path parameters
    session_id = event.get("pathParameters", {}).get("session_id")
    if not session_id:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "session_id is required"}),
        }

    session_id = f"SESSION#{session_id}"
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(os.getenv("MEMORY_TABLE_NAME"))

    # Step 1: Query to find all messages for the session
    try:
        response = table.query(
            KeyConditionExpression=Key("pk").eq(session_id)
            & Key("sk").begins_with("MESSAGE_")
        )
        messages = response.get("Items", [])
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {"message": "Failed to query messages", "error": str(e)}
            ),
        }

    # Step 2: Delete each message item
    try:
        with table.batch_writer() as batch:
            for message in messages:
                batch.delete_item(Key={"pk": message["pk"], "sk": message["sk"]})
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {"message": "Failed to delete messages", "error": str(e)}
            ),
        }

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": "All messages deleted successfully"}),
    }
