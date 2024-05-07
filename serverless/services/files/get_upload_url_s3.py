import os
import json
import datetime
import boto3


def lambda_handler(event, context):
    if not event.get("queryStringParameters"):
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Query parameters are missing."}),
        }

    # Extract parameters from the query string
    query_params = event["queryStringParameters"]
    s3_key = query_params.get("key")
    s3_expiresin = query_params.get("expiresIn")

    # Check if required parameters are provided
    if not s3_key or not s3_expiresin:
        return {
            "statusCode": 400,
            "body": json.dumps(
                {
                    "message": "You must include 'key' and 'expiresIn' in your query request."
                }
            ),
        }

    try:
        # Ensure expiresIn is an integer
        s3_expiresin = int(s3_expiresin)
    except ValueError:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "expiresIn must be a valid integer."}),
        }

    # Get the S3 bucket name from environment variables
    s3_bucket_name = os.getenv("S3_BUCKET_NAME")

    # Generate the presigned URL
    s3_client = boto3.client("s3")
    url = s3_client.generate_presigned_post(
        Bucket=s3_bucket_name, Key=s3_key, ExpiresIn=s3_expiresin
    )

    body = {
        "url": url,
        "keyFile": s3_key,
        "expiresIn": s3_expiresin,
        "created_at": datetime.datetime.now().isoformat(),
    }

    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Content-Type": "application/json",
        },
        "body": json.dumps(body),
    }
    return response
