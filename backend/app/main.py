"""FastAPI composition root — assembles middleware, routers, and handlers."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router, include_agent_routers, include_agents_catalog
from app.core.config import settings
from app.core.logging import get_logger
from app.middleware.error_handler import register_error_handlers
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.request_id import RequestIDMiddleware

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("OneForAll  started", extra={"env": settings.app_env})
    yield
    logger.info("OneForAll  stopped")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url=None,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(RateLimitMiddleware)

    register_error_handlers(app)

    app.include_router(api_router, prefix=settings.api_v1_prefix)
    include_agent_routers(app, prefix=settings.api_v1_prefix)
    include_agents_catalog(app, prefix=settings.api_v1_prefix)

    return app


app = create_app()
