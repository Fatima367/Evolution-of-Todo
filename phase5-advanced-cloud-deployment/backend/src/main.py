"""FastAPI application entry point"""
import signal
import sys
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings, validate_environment
from src import database
from src.database import initialize_database
from src.api.auth_router import router as auth_router
from src.api.task_router import router as task_router
from src.api.chat_router import router as chat_router
from src.api.routers.recurring import router as recurring_router
from src.api.routers.reminders import router as reminders_router
from src.api.routers.audit import router as audit_router
from src.api.routers.notifications import router as notifications_router
from src.api.middleware.tracing import TracingMiddleware
from src.api.middleware.rate_limit import RateLimitMiddleware
from src.api.middleware.logging import LoggingMiddleware
from src.lib.logging import setup_logging, get_logger

# OpenTelemetry instrumentation
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
import os

# Initialize logging
setup_logging(level=os.getenv("LOG_LEVEL", "INFO"))
logger = get_logger(__name__)

# Graceful shutdown flag
shutdown_event = asyncio.Event()

# Configure OpenTelemetry
def configure_opentelemetry():
    """Configure OpenTelemetry tracing"""
    # Create resource with service information
    resource = Resource.create({
        "service.name": "todoboard-backend",
        "service.version": settings.app_version,
        "service.namespace": "todoboard",
        "deployment.environment": os.getenv("ENVIRONMENT", "production"),
    })

    # Create tracer provider
    tracer_provider = TracerProvider(resource=resource)

    # Configure OTLP exporter
    otlp_exporter = OTLPSpanExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317"),
        insecure=True
    )

    # Add batch span processor
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)

    # Set global tracer provider
    trace.set_tracer_provider(tracer_provider)

    return tracer_provider


def handle_shutdown_signal(signum, frame):
    """Handle shutdown signals (SIGTERM, SIGINT)"""
    logger.info(f"Received shutdown signal: {signum}")
    shutdown_event.set()


# Register signal handlers for graceful shutdown
signal.signal(signal.SIGTERM, handle_shutdown_signal)
signal.signal(signal.SIGINT, handle_shutdown_signal)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown

    Handles:
    - Environment validation
    - Database initialization
    - OpenTelemetry setup
    - Graceful shutdown
    """
    # Startup
    logger.info("Starting TodoBoard Backend API")

    # Validate environment variables
    try:
        validate_environment()
        logger.info("Environment validation passed")
    except ValueError as e:
        logger.error(f"Environment validation failed: {e}")
        sys.exit(1)

    # Initialize OpenTelemetry
    tracer_provider = configure_opentelemetry()
    logger.info("OpenTelemetry configured")

    # Initialize database
    try:
        initialize_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        sys.exit(1)

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Starting graceful shutdown")

    # Wait for shutdown signal or timeout
    try:
        await asyncio.wait_for(shutdown_event.wait(), timeout=30.0)
    except asyncio.TimeoutError:
        logger.warning("Shutdown timeout reached, forcing shutdown")

    # Close database connections
    try:
        if database.engine:
            database.engine.dispose()
            logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")

    # Shutdown OpenTelemetry
    try:
        tracer_provider.shutdown()
        logger.info("OpenTelemetry shutdown complete")
    except Exception as e:
        logger.error(f"Error shutting down OpenTelemetry: {e}")

    logger.info("Graceful shutdown complete")


# Create FastAPI application with lifespan
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API for Todo Full-Stack Web Application with AI chatbot, user authentication and task management",
    lifespan=lifespan
)

# Instrument FastAPI
FastAPIInstrumentor.instrument_app(app)

# Instrument SQLAlchemy (will be applied when engine is created)
SQLAlchemyInstrumentor().instrument()

# Instrument requests library
RequestsInstrumentor().instrument()

# Add middleware (order matters - first added is outermost)
# 1. Tracing middleware (adds request ID)
app.add_middleware(TracingMiddleware)

# 2. Logging middleware (logs requests/responses with request ID)
app.add_middleware(LoggingMiddleware, log_request_body=False, log_response_body=False)

# 3. Rate limiting middleware (prevents abuse)
app.add_middleware(RateLimitMiddleware, requests_per_minute=100, anonymous_requests_per_minute=20)

# 4. CORS middleware (must be last to apply to all routes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(task_router)
app.include_router(chat_router)
app.include_router(recurring_router)
app.include_router(reminders_router)
app.include_router(audit_router)
app.include_router(notifications_router)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Todo Web Application API",
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy"}


@app.get("/readiness")
async def readiness_check():
    """Readiness check for Kubernetes"""
    # Check if shutdown has been initiated
    if shutdown_event.is_set():
        return {"status": "shutting_down"}, 503

    # Check database connection
    try:
        from src.database import get_session
        with next(get_session()) as session:
            session.execute("SELECT 1")
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {"status": "not_ready", "error": str(e)}, 503
