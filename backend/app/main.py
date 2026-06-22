from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import public, owner, ops, auth, verified, reports
from app.config import get_settings

settings = get_settings()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="MYEVIEW — Cameroon external digital-trust scoring platform",
    )

    cors_origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(public.router, prefix="/api/public", tags=["public"])
    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(owner.router, prefix="/api/owner", tags=["owner"])
    app.include_router(ops.router, prefix="/api/ops", tags=["ops"])
    app.include_router(verified.router, prefix="/api/verified", tags=["verified"])
    app.include_router(reports.router, prefix="/api/reports", tags=["reports"])

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
