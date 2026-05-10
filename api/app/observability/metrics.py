from prometheus_client import Counter, Histogram

ai_generation_total = Counter(
    "ai_generation_total", "AI report generations", ["result", "kind"]
)
ai_generation_duration = Histogram(
    "ai_generation_duration_seconds", "AI generation latency"
)
companies_created_total = Counter("companies_created_total", "Total companies created")
report_regenerations_total = Counter("report_regenerations_total", "Total report regenerations")
pdf_exports_total = Counter("pdf_exports_total", "Total PDF exports")
errors_total = Counter("errors_total", "Backend errors", ["kind"])
