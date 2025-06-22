import redis
import json
import os
from core import REDIS_HOST,REDIS_PORT, REDIS_DB, SESSION_KEY_PREFIX, MAX_SESSION_LENGTH

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

async def _session(session_id: str) -> list:
    return f"{SESSION_KEY_PREFIX}{session_id}"

async def save_session(session_id: str, role: str, message: str):
    """
    Save the chat session to Redis.
    
    Args:
        session_id (str): Unique identifier for the session.
        question (str): User's question.
        context (str): Retrieved context.
        response (str): AI's response.
    """
    session_key = await _session(session_id)
    messages = {"role": role, "message": message}
    redis_client.rpush(session_key, json.dumps(messages,ensure_ascii=False))
    redis_client.ltrim(session_key, 0, MAX_SESSION_LENGTH - 1)  # Keep only the last MAX_SESSION_LENGTH items

async def get_session_history(session_id: str) -> list[dict]:
    """
    Retrieve the chat session history from Redis.
    
    Args:
        session_id (str): Unique identifier for the session.
    
    Returns:
        list[dict]: List of messages in the session.
    """
    session_key = await _session(session_id)
    messages = redis_client.lrange(session_key, 0, -1)
    return [json.loads(msg) for msg in messages] if messages else []