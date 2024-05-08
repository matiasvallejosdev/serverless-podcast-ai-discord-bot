# response_utils.py
import json
from common.utils.encoders import DecimalEncoder


def success_response(data, status_code=200):
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Content-Type": "application/json",
        },
        "body": json.dumps(data, cls=DecimalEncoder),
    }
