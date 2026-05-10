# api

FastAPI backend for Company Intel AI.

## Local dev

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

Swagger: http://localhost:8000/docs · Metrics: http://localhost:8000/metrics

## macOS PDF export note

WeasyPrint depends on system libraries (`pango`, `cairo`, `gdk-pixbuf`). Install with Homebrew:

```bash
brew install pango cairo gdk-pixbuf libffi
```

The dynamic linker may not pick them up automatically. Export the fallback path before running the server or tests:

```bash
export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib
```

The Docker image installs these libs directly, so `docker compose up --build` works without this step.

## Tests

```bash
DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib pytest -v
```
