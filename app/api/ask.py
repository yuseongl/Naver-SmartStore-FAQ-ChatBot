from openai import AsyncOpenAI
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models import QueryInput
from core import get_chroma_collections
from services import retrieve_context
from services import get_session_history
from services import rewrite_if_needed
from services.prompting import build_history_prompt, build_system_prompt
from services import save_session
from services import generate_response
from utils import is_reject_message

from core.config import OPEN_AI_API_KEY

router = APIRouter()
client = AsyncOpenAI(api_key=OPEN_AI_API_KEY)

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

    # history save reject filter
    if not is_reject_message(full_response):
        # save the message    
        await save_session(session_id, '사용자', message=query)
        await save_session(session_id, '상담원', message=full_response)

@router.post("/ask/stream")
async def ask_q(input: QueryInput):
    """
    Handle the user's question, retrieve context, generate a response, and log the interaction.
    
    Args:
        input (QueryInput): The user's question.
    
    Returns:
        dict: The AI's response and the retrieved context.
    """
    query = input.question
    session_id = input.session_id

    # rewrite the user's question
    rewrited_query = await rewrite_if_needed(query)
    print("rewrite:",rewrited_query)
    # Save the user's question in the session
    # Retrieve context from the Chroma collection
    history = await get_session_history(session_id)
    collections = await get_chroma_collections()
    context = await retrieve_context(query, collections)
    print('참고 문헌:\n\n',context)
    
    # Build the prompt for the response
    history_prompt = build_history_prompt(history)
    system_prompt = build_system_prompt(context, rewrited_query, history_prompt)
    print(system_prompt)
    return StreamingResponse(
        stream_response_with_saving(system_prompt, session_id, query), 
        media_type="text/plain"
        )
    

    