from typing import List, Dict
import aiohttp
from abc import ABC, abstractmethod


class ServerlessInterface(ABC):
    @abstractmethod
    async def chat_completion(self, messages: List[Dict]) -> Dict:
        """Should be implemented to handle chat completion."""
        pass


class ServerlessAPI(ServerlessInterface):
    def __init__(self, api_base_url: str, api_key_value: str, api_key_header: str) -> None:
        self.base_url = api_base_url
        self.headers = {api_key_header: api_key_value, "Content-Type": "application/json"}

    def _build_url(self, path: str) -> str:
        return f"{self.base_url}/{path}"
    
    async def chat_completion(self, messages: List[Dict]) -> Dict:
        path = "gpt/ask"
        url = self._build_url(path)
        body = {"messages": messages}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=body, headers=self.headers) as res:
                if res.status != 200:
                    return {"status": "error", "message": "Internal server error."}
                try:
                    response_json = await res.json()
                    return response_json
                except Exception as e:
                    return {"status": "error", "message": str(e)}
