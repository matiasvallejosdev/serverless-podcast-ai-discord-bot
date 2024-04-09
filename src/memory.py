from typing import Dict, List
from collections import defaultdict


class MemoryInterface:
    def append(self, user_id: str, message: Dict) -> None:
        pass

    def get(self, user_id: str) -> str:
        return ""

    def remove(self, user_id: str) -> None:
        pass


class InMemory(MemoryInterface):
    def __init__(self, system_message: str = None):
        self.storage = defaultdict(list)
        self.system_message = system_message
        
    def __str__(self) -> str:
        return f"Storage: InMemory. Be careful, it will be lost when the program ends."

    def _initialize(self, user_id: str):
        if isinstance(self.system_message, Dict):
            self.storage[user_id] = [self.system_message]
        elif isinstance(self.system_message, List):
            self.storage[user_id] = self.system_message
        elif isinstance(self.system_message, str):
            self.storage[user_id] = [{"role": "system", "content": self.system_message}]
        else:
            self.storage[user_id] = [
                {"role": "system", "content": "You're a general assitant."}
            ]

    def append(self, user_id: str, message: Dict) -> None:
        """Appends a message to the user's message history.

        Args:
            user_id (str): user id to store the message.
            message (Dict): It contains the role and content of the messsage it is a dictionary expected in openai api.
        """
        if not isinstance(message, Dict):
            raise ValueError("Message should be a dictionary.")

        if self.storage[user_id] == []:
            # Initialize the user's message history
            # It will uses default message if system_message is not provided.
            self._initialize(user_id)
        self.storage[user_id].append(message)

    def get(self, user_id: str) -> str:
        """Gets the user's message history.

        Args:
            user_id (str): user id to get the message history.

        Returns:
            List: list of messages for the user.
        """
        # raise an exception if the user_id is not in the storage
        if user_id not in self.storage:
            raise KeyError(f"User {user_id} does not exist.")

        return self.storage[user_id]

    def remove(self, user_id: str) -> None:
        """Remove or clear the user's message history.

        Args:
            user_id (str): user id identify the user to remove the message history.
        """
        # raise an exception if the user_id is not in the storage
        if user_id not in self.storage:
            return f"User {user_id} does not exist."

        self.storage[user_id] = []
