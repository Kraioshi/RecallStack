from fastapi import FastAPI

from app.api.exception_handlers import register_exception_handlers
from app.api.router import api_router


def create_app() -> FastAPI:
    """
    Build and configure the RecallStack FastAPI application.

    This is the main composition point for the web application. Routers,
    exception handlers, middleware, and other API-level configuration
    should be connected here rather than being scattered across feature
    modules.

    Keeping application construction in one place also makes the app easier
    to configure or replace in tests later.
    """
    app = FastAPI(
        title="RecallStack",
        version="0.1.0",
    )

    app.include_router(
        api_router,
        prefix="/api",
    )

    register_exception_handlers(app)

    return app


app = create_app()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
