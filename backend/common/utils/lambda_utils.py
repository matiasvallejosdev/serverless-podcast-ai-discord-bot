import json

def load_body_from_event(event):
    # Attempt to load JSON from the request body
    body = event.get("body", "{}")  # Default to empty JSON string if body is None
    if isinstance(body, str):  # Check if body is a string and parse it
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            body = {}
            print("Failed to parse JSON from request body")
    return body

def load_path_parameter_from_event(event, param_name):
    # Extract a path parameter from the event
    return event.get("pathParameters", {}).get(param_name)