import os
import boto3

from boto3.dynamodb.conditions import Key
from common.utils.lambda_utils import load_body_from_event

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

    body = load_body_from_event(event)
    if not body:
        raise ValueError("Body is required")
    return session_id, body


def build_update_expression(body):
    update_expression = "SET "
    expression_attribute_values = {}
    for key, value in body.items():
        update_expression += f"{key} = :{key}, "
        expression_attribute_values[f":{key}"] = value
    update_expression = update_expression.rstrip(", ")
    return update_expression, expression_attribute_values


def lambda_handler(event, context):
    try:
        session_id, body = parse_and_validate(event)
        update_expression, expression_attribute_values = build_update_expression(body)

        res = memory_table.update_item(
            Key={"pk": session_id, "sk": "METADATA"},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="UPDATED_NEW",
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
