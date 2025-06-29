from openai import pydantic_function_tool
from models.schemas import AnswerAndFollowup
import json


class OpenAIClient:
    def __init__(self, client: str):
        self.client = client


    async def stream_answer_and_followup(self, messages: list[dict]):
            """
            OpenAI Function Calling 기반으로 '답변+후속질문'을 스트리밍 구조화하여 반환.

            Args:
                messages (list[dict]): GPT 대화 히스토리

            Yields:
                dict: {"answer": ..., "follow_up": ...} or 부분 결과
            """
            # Function Tool 정의
            tool = pydantic_function_tool(AnswerAndFollowup, name="answer_and_followup")

            # Function Calling 스트리밍 호출
            async with self.client.beta.chat.completions.stream(
                model="gpt-4o-mini",
                messages=messages,
                response_format=AnswerAndFollowup,
            ) as stream:
                async for event in stream:
                    if event.type == "content.delta":
                        if event.parsed:
                            yield event.parsed
                            
                    elif event.type == "error":
                        raise RuntimeError(f"OpenAI Error: {event.error}")


    async def generate_response(self, messages: list[dict]) -> str:
        """
        Generate a response from OpenAI's GPT model based on the provided prompt.

        Args:
            prompt (str): The input prompt for the model.

        Returns:
            str: The generated response from the model.
        """

        response = await self.client.chat.completions.create(
            model="gpt-4o-mini", messages=messages, stream=True
        )

        async for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                yield content

