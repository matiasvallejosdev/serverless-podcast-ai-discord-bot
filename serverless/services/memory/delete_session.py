import os
import json
import boto3

from boto3.dynamodb.conditions import Key, Attr


def lambda_handler(event, context):
    session_id = event.get("pathParameters", {}).get("session_id")
    if not session_id:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "session_id is required"}),
        }

    # Initialize variables
    session_id = f"SESSION#{session_id}"
    table_name = os.getenv("MEMORY_TABLE_NAME")
    memory_table = boto3.resource("dynamodb").Table(table_name)

    # Delete it updating the is_deleted attribute
    try:
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

        res = memory_table.update_item(
            Key={"pk": session_id, "sk": "METADATA"},
            UpdateExpression="SET is_deleted = :val",
            ExpressionAttributeValues={":val": True},
        )
        if res["ResponseMetadata"]["HTTPStatusCode"] != 200:
            raise Exception("Error deleting session!")
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {"message": "Failed to delete session", "error": str(e)}
            ),
        }
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": "Session deleted successfully"}),
    }
