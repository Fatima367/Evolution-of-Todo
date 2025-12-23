# Todo Full-Stack Web Application (Phase II)

A modern, full-stack todo application built with Next.js 16+, FastAPI, and PostgreSQL. Features user authentication, task management with priorities and tags, and responsive design.

## Features

- **User Authentication**: Secure registration and login with JWT tokens
- **Task Management**: Complete CRUD operations for tasks
- **Data Isolation**: Each user's tasks are private and isolated
- **Rich Task Features**: Priorities, tags, due dates, and status tracking
- **Responsive Design**: Mobile, tablet, and desktop support
- **Persistent Storage**: PostgreSQL database with proper migrations
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

## Tech Stack

- **Frontend**: Next.js 16+ with App Router, TypeScript, Tailwind CSS
- **Backend**: FastAPI with SQLModel ORM, Pydantic validation
- **Package Manager**: uv (recommended for backend dependency management)
- **Database**: Neon Serverless PostgreSQL (production), PostgreSQL (local dev)
- **Authentication**: Better Auth with JWT tokens
- **Testing**: pytest (backend), Jest + Playwright (frontend)

## Quick Start

See [specs/002-todo-web/quickstart.md](../specs/002-todo-web/quickstart.md) for detailed setup instructions.

### Prerequisites

- Python 3.13+
- Node.js 18+
- Docker (optional, for local PostgreSQL)

### Local Development

1. **Start PostgreSQL (optional)**:
   ```bash
   docker-compose up -d
   ```

2. **Backend Setup**:
   ```bash
   cd backend
   # Create virtual environment using standard venv
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Alternative: Using uv venv (recommended)
   # uv venv
   # source .venv/bin/activate

   # Install dependencies
   uv pip install -r requirements.txt
   # Alternative: pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your database credentials
   # Run with uv (recommended)
   uv run alembic upgrade head
   # Alternative: alembic upgrade head
   # Run with uv (recommended)
   uv run uvicorn src.main:app --reload
   # Alternative: uvicorn src.main:app --reload
   ```
   Note: Ensure all Python dependencies and tools are managed using uv for a consistent development experience.

3. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   cp .env.example .env.local
   # Edit .env.local with your backend API URL
   npm run dev
   ```

4. **Access**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Project Structure

```
phase2-todo-web/
├── backend/           # FastAPI backend
│   ├── src/
│   │   ├── models/    # SQLModel entities
│   │   ├── schemas/   # Pydantic schemas
│   │   ├── api/       # API routes
│   │   ├── services/  # Business logic
│   │   └── main.py    # App entry point
│   ├── tests/         # Backend tests
│   └── alembic/       # Database migrations
├── frontend/          # Next.js frontend
│   ├── src/
│   │   ├── app/       # App Router pages
│   │   ├── components/ # React components
│   │   ├── lib/       # Utilities & API
│   │   └── hooks/     # Custom React hooks
│   └── tests/         # Frontend tests
└── docker-compose.yml # Local PostgreSQL
```

## Documentation

- [Feature Specification](../specs/002-todo-web/spec.md)
- [Implementation Plan](../specs/002-todo-web/plan.md)
- [Data Model](../specs/002-todo-web/data-model.md)
- [API Contract](../specs/002-todo-web/contracts/todo-api-openapi.yaml)
- [Quickstart Guide](../specs/002-todo-web/quickstart.md)

## Testing

```bash
# Backend tests
# Run with uv (recommended)
cd backend && uv run pytest
# Alternative: cd backend && pytest

# Frontend tests
cd frontend && npm test

# E2E tests
cd frontend && npm run test:e2e
```

## License

See repository root for license information.
