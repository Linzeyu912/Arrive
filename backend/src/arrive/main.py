from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from .api import router
from .config import get_settings
from .database import create_schema
from .errors import ConflictError, InvariantError, NotFoundError


def create_app(*, initialize_database: bool = True) -> FastAPI:
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        if initialize_database:
            create_schema()
        yield

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description=(
            "Backend for faithful thought capture, source attribution, "
            "time-indexed viewpoint responses, and thought maps."
        ),
        lifespan=lifespan,
    )

    @app.exception_handler(NotFoundError)
    async def not_found_handler(
        _request: Request, exc: NotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @app.exception_handler(ConflictError)
    async def conflict_handler(
        _request: Request, exc: ConflictError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(exc)},
        )

    @app.exception_handler(InvariantError)
    async def invariant_handler(
        _request: Request, exc: InvariantError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": str(exc)},
        )

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "arrive-backend", "version": "0.1.0"}

    app.include_router(router, prefix=settings.api_prefix)
    return app


app = create_app()
