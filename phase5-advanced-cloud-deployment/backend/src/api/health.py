"""Health check endpoints for Kubernetes probes"""
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from src.database import get_session

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """
    Liveness probe endpoint

    Returns 200 if the service is alive and can handle requests.
    This endpoint should be lightweight and not depend on external services.
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "healthy",
            "service": "todoboard-backend"
        }
    )


@router.get("/health/ready")
async def readiness_check():
    """
    Readiness probe endpoint

    Returns 200 if the service is ready to accept traffic.
    Checks database connectivity and other critical dependencies.
    """
    try:
        # Check database connectivity
        async with get_session() as session:
            result = await session.execute(text("SELECT 1"))
            result.scalar()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "ready",
                "service": "todoboard-backend",
                "checks": {
                    "database": "connected"
                }
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "service": "todoboard-backend",
                "error": str(e)
            }
        )


@router.get("/health/startup")
async def startup_check():
    """
    Startup probe endpoint

    Returns 200 when the service has completed initialization.
    Used to delay liveness/readiness checks until startup is complete.
    """
    try:
        # Check if database migrations are complete
        async with get_session() as session:
            result = await session.execute(
                text("SELECT version_num FROM alembic_version LIMIT 1")
            )
            version = result.scalar()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "started",
                "service": "todoboard-backend",
                "database_version": version
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "starting",
                "service": "todoboard-backend",
                "error": str(e)
            }
        )
