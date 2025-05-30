from services.session import save_session
from services.generator import generate_response

async def stream_response_with_saving(final_prompt, session_id, query):
    """
    Generate a response token by token and save the session.
    Args:
        final_prompt (str): The final prompt to send to the model.
        session_id (str): Unique identifier for the session.
        query (str): The user's question.
    Yields:
        str: The generated response token by token.
    """
    full_response = ""
    async for token in generate_response(final_prompt):
        full_response += token  # 토큰을 누적
        yield token

    # save the message    
    await save_session(session_id, '사용자', message=query)
    await save_session(session_id, '상담원', message=full_response)