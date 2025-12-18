---
name: FastAPI SQLModel Neon Skill
description: Expert skill for building RESTful APIs with FastAPI, SQLModel ORM, and Neon Serverless PostgreSQL. Handles database schemas, migrations, CRUD operations, and authentication integration.
tags: [fastapi, sqlmodel, postgresql, neon, orm, rest-api, backend]
---

# FastAPI + SQLModel + Neon Skill

## Overview

This skill provides expertise in building scalable, production-ready backend APIs using:
- **FastAPI** - Modern Python web framework with automatic OpenAPI docs
- **SQLModel** - SQL databases in Python, designed for simplicity and compatibility
- **Neon Serverless PostgreSQL** - Serverless Postgres with autoscaling and branching

## Core Capabilities

### 1. Project Structure

```
backend/
├── main.py                 # FastAPI app entry point
├── models.py               # SQLModel database models
├── routes/
│   ├── __init__.py
│   ├── tasks.py           # Task CRUD endpoints
│   ├── auth.py            # Authentication endpoints
│   └── chat.py            # Chatbot endpoints (Phase III)
├── db.py                  # Database connection and session
├── config.py              # Environment configuration
├── schemas.py             # Pydantic request/response models
├── dependencies.py        # Dependency injection (auth, etc.)
└── middleware.py          # JWT verification, CORS, etc.
```

### 2. Database Models with SQLModel

**Task Model Example:**
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, foreign_key="users.id")
    title: str = Field(max_length=200, index=True)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, index=True)
    priority: Optional[str] = Field(default="medium")  # high, medium, low
    due_date: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship (if User model exists)
    # user: Optional["User"] = Relationship(back_populates="tasks")
```

**Conversation Model (Phase III):**
```python
class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Message Model (Phase III):**
```python
class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    user_id: str = Field(index=True)
    role: str = Field(max_length=20)  # "user" or "assistant"
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### 3. Database Connection (Neon)

**db.py:**
```python
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import NullPool
import os

# Neon connection string from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# For Neon serverless, use NullPool to avoid connection pooling issues
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    poolclass=NullPool,  # Required for serverless
    connect_args={"sslmode": "require"}  # Neon requires SSL
)

def create_db_and_tables():
    """Create all tables on startup"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency for getting database sessions"""
    with Session(engine) as session:
        yield session
```

**Environment Setup (.env):**
```env
DATABASE_URL=postgresql://user:password@ep-name.region.aws.neon.tech/dbname?sslmode=require
```

### 4. FastAPI Application Setup

**main.py:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from db import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables
    create_db_and_tables()
    yield
    # Shutdown: cleanup (if needed)

app = FastAPI(
    title="Todo API",
    description="Evolution of Todo - Hackathon II",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from routes import tasks, auth, chat

app.include_router(tasks.router, prefix="/api", tags=["tasks"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(chat.router, prefix="/api", tags=["chat"])

@app.get("/")
async def root():
    return {"message": "Todo API - Hackathon II"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

### 5. CRUD Endpoints

**routes/tasks.py:**
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from models import Task
from db import get_session
from dependencies import get_current_user

router = APIRouter()

@router.get("/{user_id}/tasks", response_model=List[Task])
async def list_tasks(
    user_id: str,
    status_filter: str = "all",
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """List all tasks for a user"""
    # Verify user_id matches authenticated user
    if current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    query = select(Task).where(Task.user_id == user_id)

    if status_filter == "pending":
        query = query.where(Task.completed == False)
    elif status_filter == "completed":
        query = query.where(Task.completed == True)

    tasks = session.exec(query).all()
    return tasks

@router.post("/{user_id}/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str,
    task: Task,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Create a new task"""
    if current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    task.user_id = user_id  # Ensure user_id matches
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.get("/{user_id}/tasks/{task_id}", response_model=Task)
async def get_task(
    user_id: str,
    task_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific task"""
    if current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{user_id}/tasks/{task_id}", response_model=Task)
async def update_task(
    user_id: str,
    task_id: int,
    task_update: Task,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Update a task"""
    if current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update fields
    task.title = task_update.title
    task.description = task_update.description
    task.completed = task_update.completed
    task.priority = task_update.priority
    task.due_date = task_update.due_date
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.delete("/{user_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: str,
    task_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Delete a task"""
    if current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(task)
    session.commit()
    return None

@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=Task)
async def toggle_complete(
    user_id: str,
    task_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Toggle task completion status"""
    if current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    task.completed = not task.completed
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```

### 6. JWT Authentication Integration

**dependencies.py:**
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os

security = HTTPBearer()

SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
ALGORITHM = "HS256"

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Verify JWT token from Better Auth and extract user info"""
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        email = payload.get("email")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

        return {"id": user_id, "email": email}

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
```

### 7. Pydantic Schemas for Request/Response

**schemas.py:**
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[str] = Field("medium", pattern="^(high|medium|low)$")
    due_date: Optional[datetime] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[str] = Field(None, pattern="^(high|medium|low)$")
    due_date: Optional[datetime] = None
    completed: Optional[bool] = None

class TaskResponse(BaseModel):
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    priority: Optional[str]
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

### 8. Chat Endpoint (Phase III)

**routes/chat.py:**
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Optional, List
from models import Conversation, Message
from db import get_session
from dependencies import get_current_user

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None

class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: List[dict] = []

@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Handle chat messages with AI agent"""
    if current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Get or create conversation
    if request.conversation_id:
        conversation = session.get(Conversation, request.conversation_id)
        if not conversation or conversation.user_id != user_id:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

    # Store user message
    user_message = Message(
        conversation_id=conversation.id,
        user_id=user_id,
        role="user",
        content=request.message
    )
    session.add(user_message)
    session.commit()

    # Load conversation history
    messages_query = select(Message).where(
        Message.conversation_id == conversation.id
    ).order_by(Message.created_at)
    history = session.exec(messages_query).all()

    # TODO: Integrate OpenAI Agents SDK + MCP here
    # For now, return a placeholder
    assistant_response = "AI response placeholder"
    tool_calls = []

    # Store assistant message
    assistant_message = Message(
        conversation_id=conversation.id,
        user_id=user_id,
        role="assistant",
        content=assistant_response
    )
    session.add(assistant_message)
    session.commit()

    return ChatResponse(
        conversation_id=conversation.id,
        response=assistant_response,
        tool_calls=tool_calls
    )
```

### 9. Database Migrations

**Alembic Setup (Optional but Recommended):**
```bash
# Install alembic
pip install alembic

# Initialize alembic
alembic init alembic

# Edit alembic.ini - set sqlalchemy.url to your DATABASE_URL

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

**Simple Migration (Without Alembic):**
```python
# In db.py
def create_db_and_tables():
    """Create all tables - safe to run multiple times"""
    SQLModel.metadata.create_all(engine)
```

### 10. Error Handling

**Custom Exception Handlers:**
```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

## Best Practices

### 1. Security
- ✅ Always verify JWT tokens
- ✅ Filter queries by user_id to prevent data leaks
- ✅ Use parameterized queries (SQLModel handles this)
- ✅ Validate all input with Pydantic models
- ✅ Use HTTPS in production (Neon requires SSL)

### 2. Performance
- ✅ Use indexes on frequently queried columns
- ✅ Avoid N+1 queries (use eager loading if needed)
- ✅ Use connection pooling (except with Neon serverless)
- ✅ Add pagination for large result sets
- ✅ Cache frequently accessed data (Redis, if needed)

### 3. Code Organization
- ✅ Separate models, schemas, and business logic
- ✅ Use dependency injection for database sessions
- ✅ Keep routes focused and RESTful
- ✅ Write comprehensive docstrings
- ✅ Use type hints everywhere

### 4. Testing
```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_task():
    response = client.post(
        "/api/user123/tasks",
        json={"title": "Test task", "description": "Test"},
        headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test task"
```

## Common Patterns

### Pagination
```python
from typing import Optional

@router.get("/{user_id}/tasks")
async def list_tasks(
    user_id: str,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    query = select(Task).where(Task.user_id == user_id).offset(skip).limit(limit)
    tasks = session.exec(query).all()
    return tasks
```

### Filtering and Sorting
```python
@router.get("/{user_id}/tasks")
async def list_tasks(
    user_id: str,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    sort_by: str = "created_at",
    order: str = "desc",
    session: Session = Depends(get_session)
):
    query = select(Task).where(Task.user_id == user_id)

    if status == "completed":
        query = query.where(Task.completed == True)
    elif status == "pending":
        query = query.where(Task.completed == False)

    if priority:
        query = query.where(Task.priority == priority)

    # Sorting
    if order == "desc":
        query = query.order_by(getattr(Task, sort_by).desc())
    else:
        query = query.order_by(getattr(Task, sort_by))

    tasks = session.exec(query).all()
    return tasks
```

### Search
```python
@router.get("/{user_id}/tasks/search")
async def search_tasks(
    user_id: str,
    q: str,
    session: Session = Depends(get_session)
):
    """Full-text search in title and description"""
    query = select(Task).where(
        Task.user_id == user_id,
        (Task.title.contains(q)) | (Task.description.contains(q))
    )
    tasks = session.exec(query).all()
    return tasks
```

## Neon-Specific Considerations

### 1. Connection Pooling
```python
# Don't use connection pooling with Neon serverless
engine = create_engine(DATABASE_URL, poolclass=NullPool)
```

### 2. Branching for Development
Neon supports database branching like Git branches:
```bash
# Use Neon CLI or dashboard to create branches
neon branches create --name dev
neon branches create --name staging

# Use different connection strings per environment
DATABASE_URL_DEV=postgresql://...@dev-branch.neon.tech/...
DATABASE_URL_PROD=postgresql://...@main.neon.tech/...
```

### 3. Autoscaling
Neon automatically scales compute based on load. No configuration needed.

### 4. Cold Starts
Neon may have cold starts after inactivity. First query may be slower.

## Integration with Hackathon Phases

### Phase II: Full-Stack Web App
- Implement all Basic Level CRUD operations
- Add Better Auth JWT verification
- Create comprehensive API endpoints

### Phase III: AI Chatbot
- Add conversation and message models
- Create chat endpoint
- Integrate with OpenAI Agents SDK and MCP

### Phase V: Advanced Features
- Add recurring tasks support
- Implement due dates and reminders
- Add priorities, tags, search, filtering

## Dependencies

```toml
# pyproject.toml
[project]
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "sqlmodel>=0.0.22",
    "psycopg2-binary>=2.9.9",
    "python-jose[cryptography]>=3.3.0",
    "python-dotenv>=1.0.0",
    "pydantic>=2.0.0",
]
```

## Running the Application

```bash
# Install dependencies
uv sync

# Run development server
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run with custom environment
uv run --env-file .env.local uvicorn main:app --reload
```

## API Documentation

FastAPI automatically generates interactive API docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Summary

This skill provides complete backend API implementation using modern Python tools optimized for serverless deployment. Follow SDD principles: specify requirements, plan architecture, break into tasks, then implement with this skill.
