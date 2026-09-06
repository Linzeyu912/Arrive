from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from . import __version__
from .api import router
from .config import get_settings
from .database import run_migrations
from .errors import ConflictError, InvariantError, NotFoundError

logger = logging.getLogger("arrive")


def create_app(*, initialize_database: bool = True) -> FastAPI:
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        if initialize_database:
            run_migrations()
        yield

    app = FastAPI(
        title=settings.app_name,
        version=__version__,
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
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": str(exc)},
        )

    @app.exception_handler(IntegrityError)
    async def integrity_handler(request: Request, _exc: IntegrityError) -> JSONResponse:
        # Log only the failing route: driver messages may embed row values,
        # and stored content must stay out of logs.
        logger.warning(
            "database integrity violation on %s %s",
            request.method,
            request.url.path,
        )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "the request conflicts with stored records"},
        )

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "arrive-backend", "version": __version__}

    app.include_router(router, prefix=settings.api_prefix)
    return app


app = create_app()
