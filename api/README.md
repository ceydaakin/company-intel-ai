# api

FastAPI backend for Company Intel AI.

## Local dev

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

Swagger: http://localhost:8000/docs · Metrics: http://localhost:8000/metrics
