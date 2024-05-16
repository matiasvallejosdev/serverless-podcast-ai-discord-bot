import aiohttp
from typing import List, Dict
from abc import ABC, abstractmethod
from src.api.api_interface import APIInterface


class ServerlessInterface(ABC):
    @abstractmethod
    async def chat_completion(self, session_messages: List[Dict]) -> Dict:
        """Should be implemented to handle chat completion."""
        pass

    @abstractmethod
    async def save_session(
        self, session_id: str, session_messages: List[dict], session_metadata: dict
    ) -> Dict:
        """Should be implemented to save the session."""
        pass
    
    @abstractmethod
    async def get_all_session(self) -> List[dict]:
        """Should be implemented to get all sessions."""
        pass
    
    @abstractmethod
    async def get_session(self, session_id: str) -> List[dict]:
        """Should be implemented to get a specific session."""
        pass
    
    @abstractmethod
    async def delete_session(self, session_id: str) -> Dict:
        """Should be implemented to delete a specific session."""
        pass


class PodcastAgentBotAPI(APIInterface, ServerlessInterface):
    def __init__(
        self, api_base_url: str, api_key_value: str, api_key_header: str
    ) -> None:
        super().__init__(api_base_url, api_key_value, api_key_header)

    def _build_url(self, path: str) -> str:
        return f"{self.base_url}/{path}"

    async def chat_completion(self, session_messages: List[Dict]) -> Dict:
        path = "gpt/ask"
        url = self._build_url(path)
        body = {"messages": session_messages}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=body, headers=self.headers) as res:
                if res.status != 200:
                    return {"status": "error", "message": "Internal server error."}
                try:
                    response_json = await res.json()
                    return response_json
                except Exception as e:
                    return {"status": "error", "message": str(e)}

    async def save_session(self, session_id: str, session_messages: List[dict], session_metadata: dict) -> Dict:
        path = f"sessions/{session_id}"
        url = self._build_url(path)
        body = {"messages": session_messages, "metadata": session_metadata}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=body, headers=self.headers) as res:
                if res.status != 200:
                    return {"status": "error", "message": "Internal server error."}
                try:
                    response_json = await res.json()
                    return response_json
                except Exception as e:
                    return {"status": "error", "message": str(e)}

    async def get_all_session(self) -> List[dict]:
        path = f"sessions/"
        url = self._build_url(path)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as res:
                if res.status != 200:
                    return {"status": "error", "message": "Internal server error."}
                try:
                    response_json = await res.json()
                    return response_json
                except Exception as e:
                    return {"status": "error", "message": str(e)}
                
    async def get_session(self, session_id: str) -> List[dict]:
        path = f"sessions/{session_id}"
        url = self._build_url(path)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as res:
                if res.status != 200:
                    return {"status": "error", "message": "Internal server error."}
                try:
                    response_json = await res.json()
                    return response_json
                except Exception as e:
                    return {"status": "error", "message": str(e)}
                
    async def delete_session(self, session_id: str) -> Dict:
        path = f"sessions/{session_id}"
        url = self._build_url(path)
        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=self.headers) as res:
                if res.status != 200:
                    return {"status": "error", "message": "Internal server error."}
                try:
                    response_json = await res.json()
                    return response_json
                except Exception as e:
                    return {"status": "error", "message": str(e)}