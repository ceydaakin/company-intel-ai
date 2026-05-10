from google import genai
from google.genai import types
from app.core.config import get_settings
from app.schemas.company import CompanyCreate
from app.schemas.report import CompanyReport

PROMPT = """You are an analyst at a top-tier venture capital firm.
Produce a structured intelligence report for the company below.

Company: {name}
HQ: {hq}
Website: {website}
Context from analyst: {context}

Constraints:
- Each bullet list (summary, investment_thesis, risks, why_matters) must contain 4 to 5 short bullets, each one sentence.
- Provide exactly 5 competitors with their own 4-5 bullet summaries and a strength_score 0-100.
- market_tag is a single short label like "Enterprise SaaS", "Fintech Infrastructure", "AI Tooling".
- score_breakdown is a 0-100 score for each of: market, team, moat, traction, fund_fit.
- memo_markdown is a one-page (~250-400 word) investment memo in Markdown with sections: Overview, Why Now, Thesis, Risks, Recommendation.
"""


class GeminiClient:
    def __init__(self) -> None:
        s = get_settings()
        if not s.ai_api_key:
            raise RuntimeError("AI_API_KEY is not set")
        self._client = genai.Client(api_key=s.ai_api_key)
        self._model = s.ai_model

    async def generate_report(self, payload: CompanyCreate) -> CompanyReport:
        prompt = PROMPT.format(
            name=payload.name,
            hq=payload.hq or "unknown",
            website=str(payload.website) if payload.website else "unknown",
            context=payload.context or "(none)",
        )
        result = await self._client.aio.models.generate_content(
            model=self._model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=CompanyReport,
                temperature=0.4,
            ),
        )
        # SDK returns a parsed pydantic instance when response_schema is a Pydantic model
        if isinstance(result.parsed, CompanyReport):
            return result.parsed
        # Fallback: validate raw JSON
        return CompanyReport.model_validate_json(result.text)
