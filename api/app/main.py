from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from app.core.config import get_settings
from app.api.routes import auth as auth_routes
from app.api.routes import companies as companies_routes
from app.api.routes import notes as notes_routes
from app.api.routes import compare as compare_routes

settings = get_settings()
app = FastAPI(title="Company Intel API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth_routes.router)
app.include_router(companies_routes.router)
app.include_router(notes_routes.router)
app.include_router(compare_routes.router)

Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
