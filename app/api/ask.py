from openai import AsyncOpenAI
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models.schemas import QueryInput
from core.chroma_client import get_chroma_collections
from services.retrieval import retrieve_context
from services.session import get_session_history
from services.rewriter_ import rewrite_if_needed
from utils.prompt_builder import build_history_prompt, build_system_prompt
from utils.token_streamer import stream_response_with_saving


from core.config import OPEN_AI_API_KEY

router = APIRouter()
client = AsyncOpenAI(api_key=OPEN_AI_API_KEY)

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
    

    