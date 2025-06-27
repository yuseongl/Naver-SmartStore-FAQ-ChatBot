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

    def build_system_prompt(self, context: str, question: str, history_prompt: str) -> str:
        """네이버 스마트스토어 상담원용 시스템 프롬프트 생성"""
        template = template = self.load_template()
        return template.safe_substitute(context=context, question=question, history_prompt=history_prompt)

    def build_history_prompt(self, history: list[dict]) -> str:
        """Redis에서 불러온 대화 기록을 프롬프트 문자열로 정리"""
        context_lines = ""
        for msg in history:
            role = msg.get("role", "user").capitalize()
            message = msg.get("message", "")
            context_lines += f"{role}: {message}\n"
            break
        return context_lines.strip()


# app/api/ask.py 내 사용 예시:
# from utils.prompt_builder import build_system_prompt, build_history_prompt
# context_lines = build_history_prompt(history)
# final_prompt = f"{context_lines}\n\n{build_system_prompt(context, query, rewrited_query)}"
