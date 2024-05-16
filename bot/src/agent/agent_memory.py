from typing import Dict, List, Optional, Union
# uuid is used to generate a unique session id
import uuid


class MemoryInterface:
    def append(self, user_id: str, message: Dict) -> None:
        """Append a message to the session.

        Args:
            user_id (str): User ID to identify the user.
            message (Dict): Message and content to append.
        """
        raise NotImplementedError("This method should be overridden by subclasses")

    def get(self) -> Dict[str, Union[str, List[Dict]]]:
        """Get the session.

        Returns:
            dict: The in-memory session_id and messages.
        """
        raise NotImplementedError("This method should be overridden by subclasses")

    def remove(self) -> None:
        """Remove or clear the session."""
        raise NotImplementedError("This method should be overridden by subclasses")

    def restore(self, session_id: str, messages: List[dict]) -> None:
        """Restore the session.

        Args:
            session_id (str): Session ID to restore.
        """
        raise NotImplementedError("This method should be overridden by subclasses")


class InMemoryDB(MemoryInterface):
    def __init__(self, assistant_prompt: Optional[List[Dict]] = None):
        self.session_id = "default"
        self.storage: List[Dict] = []
        self.assistant_prompt = assistant_prompt or []
        self._generate_session()

    def __str__(self) -> str:
        return "Storage: InMemory. Be careful, it will be lost when the program ends."

    def _generate_session(self) -> None:
        id = uuid.uuid4()
        self.session_id = str(id)
        self._initialize()

    def _initialize(self) -> None:
        if self.assistant_prompt is not []:
            self.storage = self.assistant_prompt
        else:
            print("Warning: No assistant prompt provided. Session will be empty.")
            self.storage = []

    def _get_session(self) -> List[Dict]:
        return self.storage

    def append(self, user_id: str, message: Dict) -> None:
        if not isinstance(message, dict):
            raise ValueError("Message should be a dictionary.")

        message.update({"user_id": user_id})
        self._get_session().append(message)

    def get(self) -> Dict[str, Union[str, List[Dict]]]:
        session = {
            "session_id": self.session_id,
            "messages": self._get_session(),
        }
        return session

    def remove(self) -> None:
        self.storage.clear()
        self._generate_session()
        
    def restore(self, messages: List[dict]) -> None:
        self.remove()
        self.storage = messages
