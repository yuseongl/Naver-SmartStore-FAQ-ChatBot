import os
import re
from string import Template

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "../", "utils", "templates", "rewrite_prompt.txt")

KEYWORDS = [
    r"\b스마트\s?스토어\b",
    r"\b스토어센터\b",
    r"\b스토어\s?개설\b",
    r"\b네이버\s?쇼핑\b",
]
_pat = re.compile("|".join(KEYWORDS), re.I)


class RewriterService:
    """
    Service for rewriting user queries to match the context of Naver Smart Store.
    It uses OpenAI's API to generate a more suitable query if the original does not match predefined keywords.
    """

    def __init__(self, client):
        self.client = client
        if not client:
            raise ValueError("OpenAI client is required for RewriterService.")

    def build_write_prompt(self, context: str) -> str:
        """네이버 스마트스토어 상담원용 시스템 프롬프트 생성"""
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
            template = Template(f.read())
        return template.safe_substitute(context=context)

    async def _rewriter(self, query: str) -> str:
        resp = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": query}],
            max_tokens=200,
        )

        return resp.choices[0].message.content.strip()

    async def rewrite_if_needed(self, q: str) -> str:
        if _pat.search(q):
            return q

        return await self._rewriter(self.build_write_prompt(context=q))
