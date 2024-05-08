# error_handlers.py
import json


def error_response(message, status_code=400):
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Content-Type": "application/json",
        },
        "body": json.dumps({"message": message}),
    }


def not_found_error():
    return error_response("The specified resource was not found.", 404)


def internal_server_error():
    return error_response("Internal server error.", 500)
