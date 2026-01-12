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


async def cleanup_memory_task() -> None:
    """Background task to periodically clean up in-memory caches."""
    from app.api.routes import cleanup_stale_conversations
    from app.auth import cleanup_stale_ip_usage

    # Run cleanup every hour
    CLEANUP_INTERVAL_SECONDS = 3600

    while True:
        try:
            await asyncio.sleep(CLEANUP_INTERVAL_SECONDS)
            logger.info("Running periodic memory cleanup...")

            # Clean up stale conversations and IP usage
            conv_cleaned = cleanup_stale_conversations()
            ip_cleaned = cleanup_stale_ip_usage()

            logger.info(
                f"Memory cleanup complete: {conv_cleaned} conversations, {ip_cleaned} IP records removed"
            )
        except Exception as e:
            logger.error(f"Memory cleanup task failed: {e}", exc_info=True)


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

    # Configure Langfuse with OpenTelemetry
    if settings.langfuse_public_key and settings.langfuse_secret_key:
        import base64

        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        # Set environment variables for Langfuse
        os.environ["LANGFUSE_PUBLIC_KEY"] = settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = settings.langfuse_secret_key
        os.environ["LANGFUSE_BASE_URL"] = settings.langfuse_host

        # Configure OpenTelemetry to export to Langfuse
        langfuse_auth = base64.b64encode(
            f"{settings.langfuse_public_key}:{settings.langfuse_secret_key}".encode()
        ).decode()

        os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = f"{settings.langfuse_host}/api/public/otel"
        os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {langfuse_auth}"

        # Initialize OpenTelemetry TracerProvider
        trace_provider = TracerProvider()
        trace_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
        trace.set_tracer_provider(trace_provider)

        # Enable PydanticAI instrumentation
        try:
            from pydantic_ai import Agent

            Agent.instrument_all()
            logger.info(
                f"Langfuse observability enabled: {settings.langfuse_host}/api/public/otel"
            )
        except ImportError:
            logger.warning("Could not import PydanticAI for instrumentation")
    else:
        logger.warning("Langfuse credentials not found - observability disabled")

    # Run MotherDuck sync during startup (blocking to prevent connection conflicts)
    await sync_motherduck_background()

    # Start background memory cleanup task
    cleanup_task = asyncio.create_task(cleanup_memory_task())
    logger.info("Started background memory cleanup task (runs every hour)")

    yield

    # Shutdown
    logger.info("Shutting down...")
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        logger.info("Memory cleanup task cancelled")
    logger.info("Shutdown complete")


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
