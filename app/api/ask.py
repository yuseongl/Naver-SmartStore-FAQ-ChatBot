import json

from containers import Container
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from models import QueryInput

router = APIRouter()


async def stream_response_with_saving(
    final_prompt, session_id, query, generate_response, save_session, is_reject_message
):
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
    if not is_reject_message(text=full_response):
        # save the message
        await save_session(session_id, "사용자", message=query)
        await save_session(session_id, "상담원", message=full_response)


async def event_stream(
    prompt: str, rewrited_query: str, generate_response: str, save_session, session_id: int, is_reject_message
):
    # Function Calling 기반 구조체 스트리밍(답변+유도질문)
    full_response = ""
    async for partial in generate_response(prompt):
        if "answer" in partial:
            full_response = partial["answer"]
        # partial: {"answer": ...} 또는 {"follow_up": ...} (또는 둘 다)
        yield f"data: {json.dumps(partial, ensure_ascii=False)}\n\n"

    # history save reject filter
    if not is_reject_message(text=full_response):
        # save the message
        await save_session(session_id, "user", message=rewrited_query)
        await save_session(session_id, "assistant", message=full_response)


@router.post("/ask/stream")
@inject
async def ask_q(
    input: QueryInput,
    retriever=Depends(Provide[Container.retriever]),
    embedding_service=Depends(Provide[Container.embedding_service]),
    session_service=Depends(Provide[Container.chat_session_service]),
    OpenAIClient=Depends(Provide[Container.OpenAIClient]),
    rewriter=Depends(Provide[Container.rewriter]),
    prompt_builder=Depends(Provide[Container.prompt_builder]),
    chroma_client=Depends(Provide[Container.chroma_client]),
    RejectFilter=Depends(Provide[Container.RejectFilter]),
):
    """
    Handle the user's question, retrieve context, generate a response,
    and log the interaction.

    Args:
        input (QueryInput): The user's question.

    Returns:
        dict: The AI's response and the retrieved context.
    """
    query = input.question
    session_id = input.session_id

    # rewrite the user's question
    rewrited_query = await rewriter.rewrite_if_needed(query)
    # Save the user's question in the session
    # Retrieve context from the Chroma collection
    history = await session_service.get_session_history(session_id)
    collections = await chroma_client.get_chroma_collections(embedding_service.get_all_embeddings_async)
    context = await retriever.retrieve_context(
        query=query,
        collections=collections,
        get_all_embeddings_async=embedding_service.get_all_embeddings_async,
    )

    # Build the prompt for the response
    history_prompt = prompt_builder.build_history_prompt(history)
    system_prompt = prompt_builder.build_system_prompt(context)
    user_prompt = prompt_builder.build_user_prompt(rewrited_query)
    final_prompt = [system_prompt] + history_prompt + [user_prompt]
    print(f"Final Prompt: {final_prompt}")
    return StreamingResponse(
        event_stream(
            final_prompt,
            rewrited_query,
            OpenAIClient.stream_answer_and_followup,
            session_service.save_session,
            session_id,
            RejectFilter.is_reject_message,
        ),
        media_type="text/plain",
    )
