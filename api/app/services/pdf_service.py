from weasyprint import HTML
from app.models.company import Company


def render_pdf(company: Company) -> bytes:
    html = _render_html(company)
    return HTML(string=html).write_pdf()


def _render_html(c: Company) -> str:
    competitors_html = "".join(
        f"<li><b>{x.name}</b> (strength {x.strength_score}/100)<ul>"
        + "".join(f"<li>{b}</li>" for b in (x.summary or []))
        + "</ul></li>"
        for x in c.competitors
    )

    def bullets(xs):
        return "".join(f"<li>{b}</li>" for b in (xs or []))

    return f"""
<html><head><meta charset="utf-8">
<style>
  body {{ font-family: -apple-system, Helvetica, Arial; margin: 32px; color:#1a1a1a; }}
  h1 {{ margin: 0; }}
  h2 {{ margin-top: 24px; border-bottom: 1px solid #ddd; padding-bottom: 4px; }}
  .meta {{ color: #555; font-size: 12px; margin-bottom: 16px; }}
  .score {{ font-size: 36px; font-weight: 700; }}
</style></head><body>
  <h1>{c.name}</h1>
  <div class="meta">{c.market_tag or ""} · HQ: {c.hq or "—"} · {c.website or ""}</div>
  <div class="score">Score: {c.score_total or 0}/100</div>
  <h2>Summary</h2><ul>{bullets(c.summary)}</ul>
  <h2>Investment Thesis</h2><ul>{bullets(c.investment_thesis)}</ul>
  <h2>Risks &amp; Red Flags</h2><ul>{bullets(c.risks)}</ul>
  <h2>Why This Company Matters</h2><ul>{bullets(c.why_matters)}</ul>
  <h2>Competitors</h2><ol>{competitors_html}</ol>
  <h2>Investment Memo</h2><div>{(c.memo_markdown or "").replace(chr(10), "<br/>")}</div>
</body></html>
"""
