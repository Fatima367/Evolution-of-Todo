# Backend Guidelines for `phase2-todo-web`

This document outlines the technical stack, architectural patterns, and API design for the FastAPI backend of the Evolution-of-Todo application.

## 1. Core Technology Stack

| Category | Technology | Purpose |
| :--- | :--- | :--- |
| **Framework** | FastAPI | High-performance Python web framework for building APIs. |
| **Language** | Python 3.11+ | Core programming language. |
| **ORM** | SQLModel | For database interaction, combining Pydantic and SQLAlchemy. |
| **Database** | Neon Serverless PostgreSQL | For persistent, scalable data storage. |
| **Authentication** | Better Auth / JWT | Token-based authentication to secure endpoints. |
| **Migrations** | Alembic | For managing database schema changes. |
| **Testing** | Pytest | For unit, integration, and contract testing. |

---

## 2. Project Structure & Patterns

### Project Structure
```
/backend
├── /alembic/             # Alembic migration scripts
├── /src/                 # Main source code
│   ├── /api/             # API endpoint routers (e.g., tasks, auth)
│   ├── /core/            # Core application settings, security
│   ├── /db/              # Database session management
│   ├── /models/          # SQLModel table definitions (e.g., task.py)
│   ├── /schemas/         # Pydantic validation schemas
│   ├── /services/        # Business logic for API routes
│   └── main.py           # FastAPI application entrypoint
├── /tests/               # Pytest tests
│   ├── /integration/
│   └── /unit/
├── alembic.ini           # Alembic configuration
├── pytest.ini            # Pytest configuration
└── requirements.txt      # Python dependencies
```

### Key Architectural Patterns
- **Layered Architecture**: The code is organized into distinct layers: `api` (HTTP handling), `services` (business logic), and `models` (data access), promoting separation of concerns.
- **Dependency Injection**: FastAPI's `Depends` system is used to inject dependencies like database sessions and authenticated user information into route handlers.
- **Repository Pattern (Simplified)**: The `services` layer acts as a repository, abstracting database queries from the API routes. All database logic should be contained within the `services`.
- **Schema-Driven Development**: Pydantic schemas in the `/schemas` directory are used for request/response validation, ensuring data integrity and providing automatic API documentation.

---

## 3. Authentication & Security

Authentication is handled via JWTs, coordinated with the frontend's "Better Auth" library.

- **JWT Verification**: A middleware in `src/core/security.py` must intercept every protected request. It validates the `Authorization: Bearer <token>` header and decodes the JWT to extract the `user_id`.
- **User Context**: The authenticated `user_id` is injected into the route handler, making it available for data filtering.
- **Data Isolation**: **All database queries for user-specific resources (like tasks) MUST be filtered by the authenticated `user_id`**. This is a critical security requirement to prevent users from accessing data that does not belong to them.

---

## 4. API Endpoints

The API follows RESTful principles. All endpoints (except auth) are protected and require a valid JWT.

### Auth Endpoints (`/api/auth`)
- **`POST /api/auth/register`**: Creates a new user.
- **`POST /api/auth/login`**: Issues a JWT for a registered user.

### Task Endpoints (`/api/tasks`)
- **`GET /api/tasks`**: List all tasks for the authenticated user. Supports filtering and sorting.
- **`POST /api/tasks`**: Create a new task.
- **`GET /api/tasks/{task_id}`**: Retrieve a single task.
- **`PUT /api/tasks/{task_id}`**: Update a task's details.
- **`DELETE /api/tasks/{task_id}`**: Delete a task.
- **`PATCH /api/tasks/{task_id}/complete`**: Toggle a task's completion status.

---

## 5. Database Schema

The schema is defined using SQLModel in `/src/models` and managed with Alembic migrations.

### `tasks` Table
| Column | Type | Constraints |
| :--- | :--- | :--- |
| `id` | `Integer` | Primary Key, Autoincrement |
| `user_id` | `String`/`UUID` | Foreign Key to `users.id`, Not Null |
| `title` | `String` | Not Null |
| `description` | `String` | Nullable |
| `completed` | `Boolean` | Not Null, Default: `False` |
| `priority` | `String` | Default: `'medium'` |
| `due_date` | `DateTime` | Nullable |

### Indexes
- An index must exist on `tasks.user_id` for fast querying of user-specific tasks.

---

## 6. Development Workflow

### Setup & Running
1.  Create and activate a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Set up your `.env` file with the `DATABASE_URL` and `BETTER_AUTH_SECRET`.
4.  Run database migrations:
    ```bash
    alembic upgrade head
    ```
5.  Start the development server:
    ```bash
    uvicorn src.main:app --reload
    ```
The API will be available at `http://127.0.0.1:8000`.
