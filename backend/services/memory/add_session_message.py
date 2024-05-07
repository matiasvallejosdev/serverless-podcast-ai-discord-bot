import os
import json
import boto3
import datetime

from boto3.dynamodb.conditions import Key, Attr

from utils.lambda_utils import load_body_from_event, load_path_parameter_from_event


def lambda_handler(event, context):
    # Extract path parameters
    session_id = load_path_parameter_from_event(event, "session_id")
    if not session_id:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "session_id is required"}),
        }

    session_id = f"SESSION#{session_id}"
    body = load_body_from_event(event)

    # Check if the message fields are present in the request body
    message = body.get("message")
    user_id = body.get("user_id")
    if not message or not user_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "'message' and 'user_id' is required."}),
        }

    # Check the format of the message field
    if "role" not in message or "content" not in message:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {"message": "Both role and content are required in the message"}
            ),
        }

    # Prepare dynamodb resource and table
    dynamodb = boto3.resource("dynamodb")
    memory_table = dynamodb.Table(os.getenv("MEMORY_TABLE_NAME"))

    # Generate a unique message ID, e.g., based on the current timestamp
    message_id = f"MESSAGE_{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}"

    # Prepare the item to be inserted into the table
    item = {
        "pk": session_id,  # Use the session_id as the partition key "pk
        "sk": message_id,
        "message": {"role": message["role"], "content": message["content"]},
        "created_at": datetime.datetime.now().isoformat(),
    }

    try:
        # Check if the session exists if not create a new session
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

        # Insert the item into DynamoDB
        memory_table.put_item(Item=item)
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {"message": "Error querying session metadata", "error": str(e)}
            ),
        }

    # Return success response
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": "Message added successfully!", "item": item}),
    }
