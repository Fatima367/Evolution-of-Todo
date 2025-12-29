# Quick Start Guide: Todo AI Chatbot

**Feature**: 003-todo-ai-chatbot
**Phase**: III - AI Chatbot Integration
**Prerequisites**: Phase II (Web + DB + Auth) must be complete

## Prerequisites

### Required Software

| Tool | Minimum Version | Installation |
|------|----------------|--------------|
| Python | 3.13+ | [python.org](https://python.org/) |
| Node.js | 20+ | [nodejs.org](https://nodejs.org/) |
| uv (Python package manager) | Latest | `pip install uv` |
| Docker | 24+ | [docker.com](https://docker.com/) (optional) |
| psql (PostgreSQL client) | 15+ | `apt install postgresql-client` |

### Required Accounts

| Service | Purpose | Free Tier? |
|---------|---------|-------------|
| Neon | Serverless PostgreSQL | Yes (500MB) |
| Groq | LLM API provider | Yes (monthly credits) |
| Better Auth (optional for Phase II) | Authentication | Self-hosted |

## Initial Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-repo/Evolution-of-Todo.git
cd Evolution-of-Todo
git checkout 003-todo-ai-chatbot
```

### 2. Set Up Python Backend

```bash
# Navigate to backend directory
cd backend

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install fastapi uvicorn[standard] sqlmodel psycopg2-binary alembic openai mcp
```

### 3. Set Up Neon Database

```bash
# 1. Create Neon project at https://neon.tech/console
# 2. Get connection string from Dashboard → Connection Details → Connection string

# 3. Set DATABASE_URL in .env
echo "DATABASE_URL=postgresql://user:pass@ep-xyz.region.aws.neon.tech/neondb" > .env
```

### 4. Get Groq API Key

```bash
# 1. Create account at https://console.groq.com/
# 2. Navigate to API Keys → Create API Key
# 3. Copy the key (starts with gsk_)

# 4. Set GROQ_API_KEY in .env
echo "GROQ_API_KEY=gsk_your_key_here" >> .env

# 5. Choose model (Llama 3.3 70B Versatile is recommended for free tier)
echo "GROQ_MODEL=llama-3.3-70b-versatile" >> .env
```

### 5. Run Database Migrations

```bash
# Run Phase III migrations (adds conversations and messages tables)
alembic upgrade head

# Verify tables created
psql $DATABASE_URL -c "\dt"
# Expected: users, tasks, conversations, messages, alembic_version
```

### 6. Start Backend Server

```bash
# Run FastAPI server with auto-reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Backend API will be available at: http://localhost:8000

### 7. Set Up Frontend (Optional - for chat UI)

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# Set API base URL
echo "VITE_API_BASE_URL=http://localhost:8000/api" > .env.local

# Start dev server
npm run dev
```

Frontend will be available at: http://localhost:5173

## Testing the Chatbot

### Using cURL

```bash
# 1. Create a new conversation and send a message
curl -X POST http://localhost:8000/api/test_user/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a task to buy groceries"
  }'

# Response:
# {
#   "conversation_id": 1,
#   "response": "I've added 'Buy groceries' to your task list.",
#   "tool_calls": [{
#     "tool": "add_task",
#     "parameters": {"user_id": "test_user", "title": "Buy groceries"},
#     "result": {"task_id": 1, "status": "created", "title": "Buy groceries"}
#   }]
# }

# 2. Continue the conversation
curl -X POST http://localhost:8000/api/test_user/chat \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": 1,
    "message": "Show me my tasks"
  }'

# Response:
# {
#   "conversation_id": 1,
#   "response": "Here are your tasks:\n\n1. Buy groceries",
#   "tool_calls": [{
#     "tool": "list_tasks",
#     "parameters": {"user_id": "test_user", "status": "all"},
#     "result": [{"id": 1, "title": "Buy groceries", "completed": false, ...}]
#   }]
# }

# 3. Complete a task
curl -X POST http://localhost:8000/api/test_user/chat \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": 1,
    "message": "Mark task 1 as complete"
  }'
```

### Using the Frontend Chat UI

1. Open http://localhost:5173/chat in your browser
2. Type "Add a task to buy groceries" and send
3. The AI will respond confirming the task was created
4. Type "Show me my tasks" to see the task list
5. Type "Mark task 1 as complete" to mark it done

## Example Conversations

### Create and Complete Tasks

```
You: Add a task to call mom tonight
AI: I've added 'Call mom tonight' to your task list.

You: Add another task to pay bills
AI: I've added 'Pay bills' to your task list.

You: What's pending?
AI: Here are your pending tasks:
1. Call mom tonight
2. Pay bills

You: Mark task 1 as complete
AI: I've marked 'Call mom tonight' as completed.
```

### Delete and Update Tasks

```
You: Show me all my tasks
AI: Here are your tasks:
1. Call mom tonight (completed)
2. Pay bills (pending)

You: Delete the bills task
AI: I've deleted 'Pay bills' from your task list.

You: Change task 1 to Call mom at 7pm
AI: I've updated 'Call mom tonight' to 'Call mom at 7pm'.
```

### Bulk Operations

```
You: Add task: Walk the dog
AI: I've added 'Walk the dog' to your task list.

You: Add task: Feed the cat
AI: I've added 'Feed the cat' to your task list.

You: Mark all tasks as complete
AI: I've marked all tasks as completed:
- Call mom at 7pm
- Walk the dog
- Feed the cat
```

## Troubleshooting

### Backend Won't Start

**Problem**: `ModuleNotFoundError: No module named 'fastapi'`
**Solution**: Activate virtual environment and install dependencies:
```bash
source .venv/bin/activate
uv pip install -r requirements.txt
```

**Problem**: `Connection refused to database`
**Solution**: Verify `DATABASE_URL` is correct and Neon project is active:
```bash
psql $DATABASE_URL -c "SELECT 1"
```

### AI Not Responding

**Problem**: `Error calling Groq API`
**Solution**: Verify `GROQ_API_KEY` is valid and has credits:
```bash
curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer $GROQ_API_KEY"
```

### CORS Errors in Frontend

**Problem**: `Access-Control-Allow-Origin` errors
**Solution**: Add frontend URL to CORS configuration in `backend/src/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Conversation Not Found

**Problem**: `404 Conversation not found`
**Solution**: Start a new conversation by omitting `conversation_id` from request

## Architecture Overview

```
┌─────────────┐     ┌──────────────────────────────────┐     ┌─────────────┐
│  Frontend   │────▶│    FastAPI Server           │     │  Neon DB    │
│  (Next.js)   │     │  POST /api/{user_id}/chat │────▶│ PostgreSQL   │
│             │◀────│  ┌────────────────────┐      │     │             │
└─────────────┘     │  │  OpenAI Agents    │      │     └─────────────┘
                      │  │  (Groq LLM)     │      │
                      │  └────────┬─────────┘      │
                      │           │                │
                      │           ▼                │
                      │  ┌────────────────────┐      │
                      │  │  MCP Tools        │      │
                      │  │  • add_task      │      │
                      │  │  • list_tasks     │      │
                      │  │  • complete_task  │◀─────┤
                      │  │  • delete_task    │      │
                      │  │  • update_task    │      │
                      │  └────────────────────┘      │
                      └──────────────────────────────────┘
```

## Next Steps

After verifying the chatbot works:

1. **Run tests**: `pytest backend/tests/ -v`
2. **Review implementation**: See `data-model.md` for schema details
3. **Extend functionality**: Add bulk operations, task search, etc.
4. **Deploy**: Configure production secrets and deploy to cloud

## Support

- **Documentation**: See `spec.md` for requirements
- **API Reference**: See `contracts/chat-api.yaml` for API details
- **MCP Tools**: See `contracts/mcp-tools.yaml` for tool definitions
- **Issues**: Create GitHub issue with error details and logs
