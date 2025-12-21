# Quickstart Guide: Todo Full-Stack Web Application

## Prerequisites

- Python 3.13+ installed
- Node.js 18+ installed
- npm or yarn package manager
- Access to Neon Serverless PostgreSQL (free tier available)

## Local Development Setup

### 1. Clone and Navigate to Project

```bash
git clone <repository-url>
cd phase2-todo-web
```

### 2. Backend Setup (FastAPI)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database connection details and JWT secrets
```

### 3. Database Setup

```bash
# Using Alembic for database migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 4. Frontend Setup (Next.js)

```bash
# From project root, navigate to frontend
cd frontend

# Install dependencies
npm install
# or
yarn install

# Set up environment variables
cp .env.example .env.local
# Edit with your backend API URL
```

### 5. Running the Application

#### Backend (in one terminal):
```bash
cd backend
source venv/bin/activate  # Activate virtual environment
uvicorn src.main:app --reload --port 8000
```

#### Frontend (in another terminal):
```bash
cd frontend
npm run dev
# or
yarn dev
```

### 6. Access the Application

- Frontend: http://localhost:3000
- Backend API docs: http://localhost:8000/docs
- Backend API redoc: http://localhost:8000/redoc

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost:5432/todo_db
JWT_SECRET=your-super-secret-jwt-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BASE_URL=http://localhost:3000
```

## Initial Setup Steps

1. Register a new account at http://localhost:3000/auth/register
2. Login at http://localhost:3000/auth/login
3. Start creating tasks at http://localhost:3000/tasks

## Running Tests

### Backend Tests
```bash
cd backend
python -m pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm run test
# or
yarn test
```

## Docker Compose (Alternative Setup)

For a complete local environment including PostgreSQL:

```bash
# From project root
docker-compose up -d
```

This will start PostgreSQL, and you can then run the backend and frontend separately as described above.

## API Endpoints Overview

- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /tasks/` - Get user's tasks
- `POST /tasks/` - Create new task
- `GET /tasks/{id}` - Get specific task
- `PUT /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task

## Troubleshooting

### Common Issues

1. **Database Connection Errors**: Verify your Neon PostgreSQL connection string is correct in `.env`
2. **CORS Errors**: Ensure your frontend URL is added to the CORS allowed origins in backend settings
3. **Authentication Issues**: Check that JWT secrets match between backend and frontend configurations
4. **Port Conflicts**: Change ports in commands if 3000 or 8000 are already in use

### Development Commands

- **Backend formatting**: `black src/ tests/` and `ruff check src/ tests/ --fix`
- **Frontend formatting**: `npm run format` or `yarn format`
- **Database migration**: `alembic revision --autogenerate -m "migration message" && alembic upgrade head`