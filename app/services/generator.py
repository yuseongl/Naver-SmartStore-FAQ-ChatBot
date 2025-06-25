async def generate_response(prompt: str) -> str:
    """
    Generate a response from OpenAI's GPT model based on the provided prompt.

    Args:
        prompt (str): The input prompt for the model.

    Returns:
        str: The generated response from the model.
    """
    from api.ask import client

    response = await client.chat.completions.create(
        model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], stream=True
    )

    async for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            yield content
