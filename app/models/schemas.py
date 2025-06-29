from pydantic import BaseModel, Field
from typing import List


class QueryInput(BaseModel):
    """QueryInput 모델은 사용자의 질문과 세션 ID를 포함합니다.
    question: 사용자의 질문 내용
    session_id: 현재 대화 세션의 고유 식별자
    """
    question: str
    session_id: str


class AnswerAndFollowup(BaseModel):
    
    """AnswerAndFollowup 모델은 OpenAI Function Calling을 통해
    답변과 후속 질문을 구조화하여 반환하는 데 사용됩니다.
    answer: 답변 내용
    follow_up: 후속 질문 내용
    """ 
    answer: str = Field(
        ...,
        description="스마트스토어 고객 질문에 대한 정확하고 친절한 답변"
    )
    follow_up: list[str] = Field(
        default_factory=list,
        description="답변 이후, 사용자가 이어서 궁금해할 만한 한 문장짜리 후속 질문. 반드시 물음표로 끝나는 질문 형식이어야 하며, 2개 이상의 질문을 해야함."
    )