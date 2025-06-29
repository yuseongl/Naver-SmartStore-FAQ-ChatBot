import os
from functools import lru_cache
from string import Template

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "../../utils/templates/system_prompt.txt")


class prompt_builder:
    """네이버 스마트스토어 상담원용 시스템 프롬프트 빌더"""

    @lru_cache(maxsize=2000)
    def load_template(self) -> Template:
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
            return Template(f.read())

    def build_system_prompt(self, context: str) -> dict:
        """
        네이버 스마트스토어 상담원용 시스템 메시지를 반환합니다.
        messages 배열에 바로 쓸 수 있도록 role/content 구조를 반환합니다.
        """
        template = self.load_template()
        system_content = template.safe_substitute(context=context)
        return {
            "role": "system",
            "content": system_content,
        }

    def build_history_prompt(self, history: list[dict]) -> str:
        """내부 히스토리(history)를 OpenAI messages로 변환"""
        messages = []
        recent_history = history[-5:]
        for msg in recent_history:
            messages.append({"role": msg.get("role", "user"), "content": msg.get("message", msg.get("content", ""))})
        return messages

    def build_user_prompt(self, query: str) -> str:
        """
        사용자 질문을 OpenAI messages로 변환합니다.
        query: 사용자의 질문
        """
        return {
            "role": "user",
            "content": query,
        }


# app/api/ask.py 내 사용 예시:
# from utils.prompt_builder import build_system_prompt, build_history_prompt
# context_lines = build_history_prompt(history)
# final_prompt = f"{context_lines}\n\n{build_system_prompt(context, query, rewrited_query)}"
