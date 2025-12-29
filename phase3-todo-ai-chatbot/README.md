# Phase III: Todo AI Chatbot

AI-powered chatbot interface for natural language task management using OpenAI ChatKit, Agents SDK, and Groq LLM.

## Features

- 🤖 **Natural Language Task Management**: Create, list, update, complete, and delete tasks using conversational AI
- 💬 **ChatKit UI**: Beautiful chat interface with OpenAI's ChatKit React components
- 🔄 **Conversation Persistence**: Full conversation history stored in PostgreSQL
- 🛠️ **MCP Tools**: Structured tool-based AI (no magic prompts)
- ⚡ **Groq LLM**: Fast inference with Groq's llama-3.3-70b-versatile model
- 🔒 **User Isolation**: JWT-based authentication with multi-tenant data isolation
- 📊 **Stateless Architecture**: Horizontally scalable design

## Tech Stack

### Backend
- **Framework**: FastAPI
- **AI**: OpenAI Agents SDK + ChatKit Server
- **LLM Provider**: Groq (via LiteLLM)
- **Database**: Neon Serverless PostgreSQL
- **ORM**: SQLModel
- **Auth**: JWT (from Phase II)

### Frontend
- **Framework**: Next.js 16+ with App Router
- **UI**: ChatKit React + shadcn/ui + Tailwind CSS
- **Language**: TypeScript 5+

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL (Neon Serverless recommended)
- Groq API Key ([Get one free](https://console.groq.com/keys))

### Backend Setup

```bash
cd phase3-todo-ai-chatbot/backend

# Install dependencies with uv
uv sync

# Copy and configure environment
cp .env.example .env
# Edit .env and add:
# - DATABASE_URL (your Neon PostgreSQL URL)
# - GROQ_API_KEY (your Groq API key)
# - JWT_SECRET_KEY (from Phase II)

# Run database migrations
uv run alembic upgrade head

# Start backend server
uv run uvicorn src.main:app --reload
```

Backend will be available at: http://localhost:8000

### Frontend Setup

```bash
cd phase3-todo-ai-chatbot/frontend

# Install dependencies
npm install

# Copy and configure environment
cp .env.example .env.local
# Edit .env.local and add:
# - NEXT_PUBLIC_API_URL=http://localhost:8000

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:3000

**ChatKit AI Assistant**:
- A floating chat button will appear in the bottom-right corner for authenticated users
- Click the button to open the AI assistant popup
- The assistant can help you manage tasks through natural language
- Conversation history is automatically saved and persists across sessions

## API Endpoints

### Chat

- `POST /chatkit` - ChatKit protocol endpoint (requires JWT)
  - Handles chat messages and streams AI responses
  - Automatically manages conversation history
  - Executes MCP tools for task operations

### Tasks (from Phase II)

- `GET /api/tasks` - List tasks
- `POST /api/tasks` - Create task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task

### Auth (from Phase II)

- `POST /api/auth/register` - Register user
- `POST /api/auth/login` - Login and get JWT token

## MCP Tools

The AI agent has access to these tools for task management:

1. **add_task** - Create new task with title, description, and priority
2. **list_tasks** - List tasks with optional status filter
3. **complete_task** - Mark task as completed
4. **delete_task** - Remove task permanently
5. **update_task** - Modify task details

## Example Conversations

```
User: "Add a task to buy groceries"
Assistant: "I've created a new task: 'buy groceries' with medium priority."

User: "Show me all my pending tasks"
Assistant: "Here are your pending tasks:
1. Buy groceries (medium priority)
2. Finish project report (high priority)
..."

User: "Mark the groceries task as done"
Assistant: "Great! I've marked 'buy groceries' as completed."
```

## Architecture Highlights

### Stateless Server Design

- No in-memory session state
- All conversation history in PostgreSQL
- Server restarts don't lose conversations
- Horizontally scalable

### ID Collision Fix

Implements critical fix for LiteLLM/Groq ID collision issue where provider-generated message IDs could conflict, causing messages to overwrite each other. The fix maps provider IDs to unique database-generated IDs.

### User Isolation

- All queries filtered by `user_id` from JWT
- No cross-user data access
- Enforced at service layer and database level

## Database Schema

### New Tables (Phase III)

**conversations**
- `id` (PK, integer)
- `user_id` (FK to users, UUID)
- `created_at`, `updated_at` (timestamps)

**messages**
- `id` (PK, integer)
- `user_id` (FK to users, UUID)
- `conversation_id` (FK to conversations)
- `role` ('user' or 'assistant')
- `content` (text)
- `created_at` (timestamp)

## Development

### Run Tests

```bash
cd backend
uv run pytest
```

### Check Conversation Storage

GET http://localhost:8000/debug/threads (development only)

### Linting & Formatting

```bash
cd backend
uv run ruff check src/
uv run ruff format src/
```

## Troubleshooting

### Backend won't start

1. Check `.env` has valid `DATABASE_URL` and `GROQ_API_KEY`
2. Run `uv sync` to ensure all dependencies are installed
3. Run `uv run alembic upgrade head` to apply migrations

### Chat not working

1. Verify Groq API key is valid
2. Check browser console for errors
3. Verify JWT token is being sent in Authorization header
4. Check backend logs for error messages

### Messages overwriting each other

This should be fixed with the ID collision fix in `src/chatkit/server.py`. If you still see this issue:
1. Check that `id_mapping` dictionary is being used correctly
2. Verify `generate_item_id()` is creating unique IDs
3. Check `/debug/threads` endpoint to inspect stored message IDs

## Related Documentation

- [Specification](../../specs/003-todo-ai-chatbot/spec.md)
- [Implementation Plan](../../specs/003-todo-ai-chatbot/plan.md)
- [Data Model](../../specs/003-todo-ai-chatbot/data-model.md)
- [Tasks Breakdown](../../specs/003-todo-ai-chatbot/tasks.md)

## License

MIT
