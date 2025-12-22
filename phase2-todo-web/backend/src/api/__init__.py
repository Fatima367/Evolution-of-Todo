"""API routers"""
from src.api.auth_router import router as auth_router
from src.api.task_router import router as task_router

__all__ = ["auth_router", "task_router"]
