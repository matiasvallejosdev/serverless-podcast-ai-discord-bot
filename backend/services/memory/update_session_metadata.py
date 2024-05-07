import os
import json
import boto3

from boto3.dynamodb.conditions import Key
from utils.lambda_utils import load_body_from_event


def lambda_handler(event, context):
    # Extract session_id from the request and validate
    session_id = event.get("pathParameters", {}).get("session_id")
    if not session_id:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "session_id is required"}),
        }

    # Initialize the DynamoDB resource
    dynamodb = boto3.resource("dynamodb")
    memory_table = dynamodb.Table(os.getenv("MEMORY_TABLE_NAME"))

    # Load body from the event
    body = load_body_from_event(event)
    if not body:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Body is required"}),
        }

    session_id = f"SESSION#{session_id}"

    # Construct the update expression and attribute values
    update_expression = "SET "
    expression_attribute_values = {}
    for key, value in body.items():
        update_expression += f"{key} = :{key}, "
        expression_attribute_values[f":{key}"] = value
    update_expression = update_expression.rstrip(", ")

    try:
        response = memory_table.update_item(
            Key={"pk": session_id, "sk": "METADATA"},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="UPDATED_NEW",
        )
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {"message": "Error updating session metadata", "error": str(e)}
            ),
        }

    response = {"message": "Session metadata updated successfully"}
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(response),
    }
