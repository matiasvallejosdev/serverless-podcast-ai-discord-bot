class APIInterface:
    """APIInterface class to be inherited by API classes."""
    def __init__(
        self, api_base_url: str, api_key_value: str, api_key_header: str
    ) -> None:
        self.base_url = api_base_url
        self.headers = {
            api_key_header: api_key_value,
            "Content-Type": "application/json",
        }
