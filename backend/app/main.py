import os
import sys
from contextlib import asynccontextmanager

# Ensure repository root is on sys.path for scraper package
_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    yield
    # Shutdown actions


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="HackBubble - Hackathon discovery and intelligent team formation platform API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register standardized exceptions
    register_exception_handlers(app)

    # Register API routers
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_application()


@app.get("/", tags=["Root"])
async def root():
    return {
        "app": settings.APP_NAME,
        "version": "0.1.0",
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health",
    }
