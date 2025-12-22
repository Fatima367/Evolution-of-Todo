# Todo Web Application - Backend

FastAPI backend for the Todo Full-Stack Web Application with user authentication and task management.

## Features

- RESTful API with FastAPI
- SQLModel ORM with Neon Serverless PostgreSQL
- JWT-based authentication
- User isolation and data security
- Automatic API documentation (Swagger/ReDoc)
- Database migrations with Alembic

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
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your database credentials
```

### Database Migration

```bash
# Initialize Alembic (already done)
# alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### Running

```bash
# Development mode with auto-reload
uvicorn src.main:app --reload --port 8000

# Production mode
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

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

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/unit/test_task_service.py -v
```

## Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/ --fix

# Type checking
mypy src/
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
- JWT tokens for authentication
- User isolation enforced at database query level
- Input validation with Pydantic models
- CORS configured for trusted origins only

## Development

```bash
# Start with auto-reload
uvicorn src.main:app --reload

# Run tests in watch mode
pytest-watch

# Format on save (configure your IDE)
```

## License

See repository root for license information.
