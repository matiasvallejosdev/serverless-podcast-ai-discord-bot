import os
import json
import boto3

from boto3.dynamodb.conditions import Attr, Key
from utils.encoders import DecimalEncoder


def lambda_handler(event, context):
    user_id = int(event.get("pathParameters", {}).get("user_id"))
    if not user_id:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "session_id is required"}),
        }

    table_name = os.getenv("MEMORY_TABLE_NAME")
    memory_table = boto3.resource("dynamodb").Table(table_name)

    try:
        # Scan the table for all sessions where is_deleted is false
        response = memory_table.scan(
            FilterExpression=Attr("is_deleted").eq(False)
            & Attr("sk").eq("METADATA")
            & Attr("user_id").eq(user_id)
        )
        sessions_items = response.get("Items", [])

        # If no sessions are found, return a 404
        if not sessions_items or len(sessions_items) == 0:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": "No sessions found for this user"}),
            }

        # Optionally append messages for each session if needed
        for session in sessions_items:
            session_id = session["pk"]
            session.pop("user_id", None)
            messages_response = memory_table.query(
                KeyConditionExpression=Key("pk").eq(session_id)
                & Key("sk").begins_with("MESSAGE_")
            )
            messages_items = messages_response.get("Items", [])
            messages = [
                {
                    key: val
                    for key, val in msg.items()
                    if key == "message" or key == "sk"
                }
                for msg in messages_items
            ]
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
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Error fetching sessions: " + str(e)}),
        }

    # Format the response body with the sessions data
    response_body = json.dumps(
        {"user_id": user_id, "sessions": data, "session_count": len(data)},
        cls=DecimalEncoder,
    )

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": response_body,
    }
