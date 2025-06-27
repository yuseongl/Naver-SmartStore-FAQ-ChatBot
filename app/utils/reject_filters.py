import os
from functools import lru_cache

FILE_PATH = os.path.join(os.path.dirname(__file__), "reject_phrases.txt")


class RejectFilter(Exception):
    """Reject 필터 관련 처리 클래스."""

    @lru_cache(maxsize=2000)
    def _load_reject_phrases(self) -> list[str]:
        """파일을 읽어 캐싱"""
        with open(FILE_PATH, encoding="utf-8") as f:
            # 공백 줄·주석(#) 무시
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]

    def is_reject_message(self, text: str) -> bool:
        """응답이 reject 목록에 해당하면 True."""
        for phrase in self._load_reject_phrases():
            if text.strip().startswith(phrase):
                return True
        return False
