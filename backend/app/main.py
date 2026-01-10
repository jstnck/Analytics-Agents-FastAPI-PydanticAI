import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import settings

# Configure logging
# Use uvicorn's default format for consistency
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(levelname)s:\t%(name)s - %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info(f"Starting {settings.app_name}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Using LLM model: {settings.default_llm_model}")

    # Configure API keys for PydanticAI agents
    if settings.anthropic_api_key:
        os.environ["ANTHROPIC_API_KEY"] = settings.anthropic_api_key
        logger.info("Anthropic API key configured")
    else:
        logger.warning("No Anthropic API key found")

    if settings.openai_api_key:
        os.environ["OPENAI_API_KEY"] = settings.openai_api_key
        logger.info("OpenAI API key configured")

    yield
    # Shutdown
    logger.info("Shutting down")


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root() -> dict[str, Any]:
    """Root endpoint."""
    return {"message": f"Welcome to {settings.app_name}"}
