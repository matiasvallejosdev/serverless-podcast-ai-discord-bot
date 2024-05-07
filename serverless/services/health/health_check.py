import json


def lambda_handler(event, context):
    """Health check function to test if the Lambda function is running.

    Args:
        event (obj): Event data passed to the function.
        context (obj): Runtime information provided by AWS Lambda.

    Returns:
        json: A JSON object containing the health check message.
    """
    body = {
        "message": "Health check successful",
        "region": context.invoked_function_arn.split(":")[3],
        "function_name": context.function_name,
    }

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps(body),
    }
