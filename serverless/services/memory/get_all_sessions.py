import os
import boto3
from boto3.dynamodb.conditions import Attr, Key
from common.utils.lambda_utils import load_path_parameter_from_event
from common.utils.error_handler import (
    error_response,
    internal_server_error,
    not_found_error,
)
from common.utils.response_utils import success_response


table_name = os.getenv("MEMORY_TABLE_NAME")
memory_table = boto3.resource("dynamodb").Table(table_name)


def lambda_handler(event, context):
    try:
        # Get all sessions from the memory table with the is_deleted attribute set to False
        response = memory_table.scan(
            FilterExpression=Attr("is_deleted").eq(False)
        )
        sessions_items = response.get("Items", [])

        return success_response(sessions_items)
    except ValueError as e:
        return error_response(str(e))
    except boto3.exceptions.ResourceNotFoundException as e:
        return not_found_error()
    except Exception as e:
        return internal_server_error()
