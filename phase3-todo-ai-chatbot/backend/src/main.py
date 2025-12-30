"""FastAPI application entry point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.database import create_db_and_tables
from src.api.auth_router import router as auth_router
from src.api.task_router import router as task_router
from src.api.chat_router import router as chat_router


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API for Todo Full-Stack Web Application with user authentication and task management"
)

# Configure CORS
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


@app.on_event("startup")
def on_startup():
    """Initialize database tables on startup"""
    create_db_and_tables()


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
