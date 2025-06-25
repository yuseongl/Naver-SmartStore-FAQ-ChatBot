import re
import os
from string import Template
from openai import AsyncOpenAI
from functools import lru_cache
from core.config import OPEN_AI_API_KEY

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "../", "utils", "templates", "rewrite_prompt.txt")

client = AsyncOpenAI(api_key=OPEN_AI_API_KEY)
KEYWORDS = [r"\b스마트\s?스토어\b", r"\b스토어센터\b", r"\b스토어\s?개설\b", r"\b네이버\s?쇼핑\b"]
_pat = re.compile("|".join(KEYWORDS), re.I)


def build_write_prompt(context: str) -> str:
    """네이버 스마트스토어 상담원용 시스템 프롬프트 생성"""
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = Template(f.read())   
    return template.safe_substitute(context=context)

async def _rewriter(query:str) -> str:
    resp = await client.chat.completions.create(
        model= "gpt-4o-mini",
        messages=[{"role": "user", "content": query}],
        max_tokens=200
    )
 
    return resp.choices[0].message.content.strip()

async def rewrite_if_needed(q:str) -> str:
    if _pat.search(q):
        return q
    
    return await _rewriter(build_write_prompt(q))
