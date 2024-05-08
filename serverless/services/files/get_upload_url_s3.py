import os
import datetime
import boto3

from common.utils.error_handler import error_response, internal_server_error
from common.utils.response_utils import success_response

s3_client = boto3.client("s3")
s3_bucket_name = os.getenv("S3_BUCKET_NAME")


def parse_and_validate(event):
    query_params = event.get("queryStringParameters", {})
    s3_key = query_params.get("key")
    s3_expiresin = query_params.get("expiresIn")

    if not s3_key or s3_expiresin is None:
        raise ValueError(
            "Both 'key' and 'expiresIn' parameters are required in the query."
        )

    try:
        s3_expiresin = int(s3_expiresin)
    except ValueError:
        raise ValueError("'expiresIn' must be a valid integer.")

    if (
        s3_expiresin <= 0 or s3_expiresin > 86400
    ):  # Example: limits expiresIn to 24 hours
        raise ValueError("'expiresIn' must be between 1 and 86400 seconds.")

    return s3_key, s3_expiresin


def lambda_handler(event, context):
    try:
        s3_key, s3_expiresin = parse_and_validate(event)
    except ValueError as e:
        return error_response(str(e))

    try:
        # Generate the presigned URL
        url = s3_client.generate_presigned_post(
            Bucket=s3_bucket_name, Key=s3_key, ExpiresIn=s3_expiresin
        )
    except Exception as e:
        return internal_server_error()

    body = {
        "url": url,
        "keyFile": s3_key,
        "expiresIn": s3_expiresin,
        "created_at": datetime.datetime.now().isoformat(),
    }

    return success_response(body)
