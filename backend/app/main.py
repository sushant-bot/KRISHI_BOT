from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import app.models  # noqa: F401
from app.config import get_settings
from app.database import Base, engine
from app.routes import (
    ai,
    alerts,
    decisions,
    digital_twin,
    farms,
    health,
    images,
    irrigation,
    sensors,
    translation,
    zones,
)
from app.services.farm import ConflictError, NotFoundError


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    try:
        from app.database import SessionLocal
        from app.models.farm import Farm
        from seed_demo_data import seed

        db = SessionLocal()
        try:
            if db.query(Farm).count() == 0:
                seed()
        finally:
            db.close()
    except Exception:
        pass
    yield


settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?|https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=404, content={"error": {"code": "NOT_FOUND", "message": str(exc)}}
    )


@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(
        status_code=409, content={"error": {"code": "CONFLICT", "message": str(exc)}}
    )


app.include_router(health.router, prefix="/api")
app.include_router(farms.router, prefix="/api")
app.include_router(zones.router, prefix="/api")
app.include_router(sensors.router, prefix="/api")
app.include_router(irrigation.router, prefix="/api")
app.include_router(images.router, prefix="/api")
app.include_router(images.zone_router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(ai.zone_router, prefix="/api")
app.include_router(decisions.router, prefix="/api")
app.include_router(decisions.zone_router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(digital_twin.router, prefix="/api")
app.include_router(translation.router, prefix="/api")
