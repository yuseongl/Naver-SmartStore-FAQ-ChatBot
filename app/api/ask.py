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
    system_prompt = prompt_builder.build_system_prompt(context, rewrited_query, history_prompt)
    print(system_prompt)
    return StreamingResponse(
        stream_response_with_saving(
            final_prompt=system_prompt,
            session_id=session_id,
            query=query,
            generate_response=OpenAIClient.generate_response,
            save_session=session_service.save_session,
            is_reject_message=RejectFilter.is_reject_message,
        ),
        media_type="text/plain",
    )
