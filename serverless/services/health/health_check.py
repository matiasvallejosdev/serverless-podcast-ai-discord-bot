from common.utils.response_utils import success_response


def lambda_handler(event, context):
    body = {
        "message": "Health check successful",
        "region": context.invoked_function_arn.split(":")[3],
        "function_name": context.function_name,
    }

    return success_response(body)