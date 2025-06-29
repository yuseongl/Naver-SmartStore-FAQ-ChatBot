import json


class ChatSessionService:
    """
    ChatSessionService is responsible for managing chat sessions.
    It saves and retrieves chat messages from Redis.
    """

    def __init__(self, redis_client, session_key_prefix, max_session_length):
        self.redis_client = redis_client
        self.session_key_prefix = session_key_prefix
        self.max_session_length = max_session_length

    async def _session(self, session_id: str) -> list:
        return f"{self.session_key_prefix}{session_id}"

    async def save_session(
        self,
        session_id: str,
        role: str,
        message: str,
    ):
        """
        Save the chat session to Redis.

        Args:
            session_id (str): Unique identifier for the session.
            question (str): User's question.
            context (str): Retrieved context.
            response (str): AI's response.
        """
        session_key = await self._session(session_id)
        messages = {"role": role, "content": message}
        self.redis_client.rpush(session_key, json.dumps(messages, ensure_ascii=False))
        self.redis_client.ltrim(
            session_key, 0, self.max_session_length - 1
        )  # Keep only the last MAX_SESSION_LENGTH items

    async def get_session_history(self, session_id: str) -> list[dict]:
        """
        Retrieve the chat session history from Redis.

        Args:
            session_id (str): Unique identifier for the session.

        Returns:
            list[dict]: List of messages in the session.
        """
        session_key = await self._session(session_id)
        messages = self.redis_client.lrange(session_key, 0, -1)
        return [json.loads(msg) for msg in messages] if messages else []
