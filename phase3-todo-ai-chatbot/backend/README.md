# Todo Web Application - Backend

FastAPI backend for the Todo Full-Stack Web Application with user authentication and task management.

## Features

- RESTful API with FastAPI
- SQLModel ORM with Neon Serverless PostgreSQL
- JWT-based authentication
- User isolation and data security
- Automatic API documentation (Swagger/ReDoc)
- Database migrations with Alembic
- Package management with uv (recommended)

## Project Structure

```
backend/
├── src/
│   ├── models/          # SQLModel entities
│   ├── schemas/         # Pydantic validation schemas
│   ├── services/        # Business logic
│   ├── api/             # API endpoints
│   ├── auth/            # Authentication utilities
│   ├── config.py        # Configuration
│   ├── database.py      # Database connection
│   └── main.py          # FastAPI application
├── alembic/             # Database migrations
├── tests/               # Test suite
├── requirements.txt     # Python dependencies
└── .env.example         # Environment variables template
```

## Setup

### Prerequisites

- Python 3.13+
- Neon Serverless PostgreSQL account

### Installation

```bash
# Create virtual environment
# Using standard venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Alternative: Using uv venv (recommended)
# uv venv
# source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
# Alternative: pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your database credentials
```

### Database Migration

```bash
# Initialize Alembic (already done)
# alembic init alembic

# Create initial migration
# Run with uv (recommended)
uv run alembic revision --autogenerate -m "Initial migration"
# Alternative: alembic revision --autogenerate -m "Initial migration"

# Apply migrations
# Run with uv (recommended)
uv run alembic upgrade head
# Alternative: alembic upgrade head
```

### Running

```bash
# Development mode with auto-reload
# Run with uv (recommended)
uv run uvicorn src.main:app --reload --port 8000
# Alternative: uvicorn src.main:app --reload --port 8000

# Production mode
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000
# Alternative: uvicorn src.main:app --host 0.0.0.0 --port 8000
```

Note: Ensure all Python packages and tools (like uvicorn, pytest, etc.) are installed using uv for a consistent development experience.

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/me` - Get current user

### Tasks (Protected)
- `GET /tasks/` - Get user's tasks (with filtering)
- `POST /tasks/` - Create new task
- `GET /tasks/{id}` - Get specific task
- `PUT /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task

All task endpoints require JWT authentication.

### ChatKit AI (Protected)
- `POST /chatkit` - Chat Interface Endpoint (supports streaming)
- `GET /chatkit/health` - Health check for ChatKit server

The AI Assistant can manage your tasks through natural language, including creating, listing, updating, completing, and deleting tasks. It also supports bulk operations and referring to tasks by name.

## MCP Tools (AI Assistant)

The AI Assistant uses Model Context Protocol (MCP) tools to interact with the task database:

- `add_task(title, description, priority)`: Create a new task.
- `list_tasks(status)`: List tasks with optional status filter. Supports searching by title.
- `complete_task(task_id)`: Mark a task as completed (accepts UUIDs or Titles).
- `delete_task(task_id)`: Delete a task (accepts UUIDs or Titles).
- `update_task(task_id, ...)`: Update task properties (accepts UUIDs or Titles).
- `bulk_complete()`: Mark all tasks as completed.
- `bulk_delete()`: Delete all completed tasks.
- `clear_all()`: Delete all tasks (requires confirmation).

## Testing

```bash
# Run all tests
# Run with uv (recommended)
uv run pytest
# Alternative: pytest

# Run with coverage
# Run with uv (recommended)
uv run pytest --cov=src tests/
# Alternative: pytest --cov=src tests/

# Run specific test file
# Run with uv (recommended)
uv run pytest tests/unit/test_task_service.py -v
# Alternative: pytest tests/unit/test_task_service.py -v
```

## Code Quality

```bash
# Format code
# Run with uv (recommended)
uv run black src/ tests/
# Alternative: black src/ tests/

# Lint code
# Run with uv (recommended)
uv run ruff check src/ tests/ --fix
# Alternative: ruff check src/ tests/ --fix

# Type checking
# Run with uv (recommended)
uv run mypy src/
# Alternative: mypy src/
```

## Environment Variables

See `.env.example` for required environment variables:

- `DATABASE_URL` - Neon PostgreSQL connection string
- `JWT_SECRET_KEY` - Secret key for JWT token generation
- `JWT_ALGORITHM` - JWT algorithm (default: HS256)
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration time
- `CORS_ORIGINS` - Allowed CORS origins

## Security

- All passwords are hashed using bcrypt
- Password length limited to 72 bytes when UTF-8 encoded (due to bcrypt limitation)
- JWT tokens for authentication
- User isolation enforced at database query level
- Input validation with Pydantic models
- CORS configured for trusted origins only

## Development

```bash
# Start with auto-reload
uvicorn src.main:app --reload

# Run tests in watch mode
# Run with uv (recommended)
uv run pytest-watch
# Alternative: pytest-watch

# Format on save (configure your IDE)
```

## License

See repository root for license information.
