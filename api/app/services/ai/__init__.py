from app.core.config import get_settings
from app.services.ai.provider import AIProvider


def get_ai_provider() -> AIProvider:
    s = get_settings()
    if s.ai_provider == "stub":
        from app.services.ai.stub_client import StubClient
        return StubClient()
    if s.ai_provider == "gemini":
        from app.services.ai.gemini_client import GeminiClient
        return GeminiClient()
    raise RuntimeError(f"unknown AI_PROVIDER={s.ai_provider}")
