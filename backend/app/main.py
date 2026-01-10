import asyncio
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


async def sync_motherduck_background() -> None:
    """Run MotherDuck sync in the background."""
    try:
        from app.database.sync_motherduck import sync_from_motherduck

        motherduck_db = os.getenv("MOTHERDUCK_DB")
        motherduck_token = os.getenv("MOTHERDUCK_TOKEN")

        if not motherduck_db or not motherduck_token:
            logger.info("MotherDuck credentials not configured, skipping sync")
            return

        local_db_path = settings.duckdb_path
        source_schema = os.getenv("MOTHERDUCK_SCHEMA", "dmt")

        logger.info("Starting MotherDuck sync in background...")
        await asyncio.to_thread(
            sync_from_motherduck,
            motherduck_db=motherduck_db,
            motherduck_token=motherduck_token,
            local_db_path=local_db_path,
            source_schema=source_schema,
        )
        logger.info("MotherDuck sync completed successfully")
    except Exception as e:
        logger.error(f"MotherDuck sync failed: {e}", exc_info=True)


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

    # Configure Langfuse
    if settings.langfuse_public_key and settings.langfuse_secret_key:
        os.environ["LANGFUSE_PUBLIC_KEY"] = settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = settings.langfuse_secret_key
        os.environ["LANGFUSE_HOST"] = settings.langfuse_host

        # Enable PydanticAI instrumentation
        try:
            from pydantic_ai import Agent
            Agent.instrument_all()
            logger.info(f"Langfuse instrumentation enabled at {settings.langfuse_host}")
        except ImportError:
            logger.warning("Could not import PydanticAI for instrumentation")
    else:
        logger.warning("Langfuse credentials not found - observability disabled")

    # Run MotherDuck sync during startup (blocking to prevent connection conflicts)
    await sync_motherduck_background()

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
