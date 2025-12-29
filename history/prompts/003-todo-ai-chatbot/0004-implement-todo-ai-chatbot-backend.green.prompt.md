---
id: 0004
title: implement-todo-ai-chatbot-backend
stage: green
date: 2025-12-28
surface: agent
model: claude-sonnet-4.5
feature: 003-todo-ai-chatbot
branch: 003-todo-ai-chatbot
user: shanzay
command: /sp.implement
labels: ["chatkit", "openai-agents", "groq", "mcp-tools", "postgresql", "backend"]
links:
  spec: ../../specs/003-todo-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - phase3-todo-ai-chatbot/backend/pyproject.toml
  - phase3-todo-ai-chatbot/backend/.env.example
  - phase3-todo-ai-chatbot/backend/src/models/conversation.py
  - phase3-todo-ai-chatbot/backend/src/models/message.py
  - phase3-todo-ai-chatbot/backend/src/models/__init__.py
  - phase3-todo-ai-chatbot/backend/src/models/user.py
  - phase3-todo-ai-chatbot/backend/alembic/versions/003_add_conversations_and_messages.py
  - phase3-todo-ai-chatbot/backend/src/chatkit/__init__.py
  - phase3-todo-ai-chatbot/backend/src/chatkit/store.py
  - phase3-todo-ai-chatbot/backend/src/chatkit/tools.py
  - phase3-todo-ai-chatbot/backend/src/chatkit/server.py
  - phase3-todo-ai-chatbot/backend/src/api/chat_router.py
  - phase3-todo-ai-chatbot/backend/src/main.py
  - phase3-todo-ai-chatbot/README.md
  - phase3-todo-ai-chatbot/IMPLEMENTATION_COMPLETE.md
tests:
  - Migration successfully applied (conversations and messages tables created)
  - Dependencies installed (93 packages including chatkit and agents)
  - Database schema validated
---

## Prompt

User requested implementation of Todo AI Chatbot (Phase III).

Initial request: `@specs/003-todo-ai-chatbot/tasks.md`

User clarification:
- Working directory is `phase3-todo-ai-chatbot` (not `backend` directly)
- Use ChatKit expert agents available in `.claude/agents/chatkit-expert-agent/`

Task: Implement complete backend infrastructure for AI-powered chatbot using:
- OpenAI ChatKit Server (`openai-chatkit`)
- OpenAI Agents SDK (`openai-agents`)
- Groq LLM provider (via LiteLLM)
- MCP tools for task management
- PostgreSQL-backed conversation persistence
- Stateless architecture with full conversation history

## Response snapshot

Implemented complete Phase III backend with following components:

**1. Dependencies & Configuration:**
- Added ChatKit (`openai-chatkit<=1.4.0`) and OpenAI Agents SDK with LiteLLM (`openai-agents[litellm]>=0.6.2`)
- Added email-validator for Pydantic EmailStr support
- Updated `.env.example` with Groq configuration (GROQ_API_KEY, GROQ_MODEL)

**2. Database Models:**
- Created `Conversation` model with user_id, timestamps, and message relationships
- Created `Message` model with role enum (USER/ASSISTANT), content, and foreign keys
- Updated `User` model with conversations and messages relationships
- Created Alembic migration 003 for new tables with proper indexes

**3. PostgreSQL-Backed ChatKit Store:**
- Implemented all 14 required Store abstract methods
- User isolation enforced (all queries filter by user_id from JWT)
- Conversation and message persistence with pagination support
- ID generation using UUID for uniqueness

**4. MCP Tools (5 total):**
- `add_task` - Create new task with title, description, priority
- `list_tasks` - List tasks with optional status filter
- `complete_task` - Mark task as completed
- `delete_task` - Remove task permanently
- `update_task` - Modify task title, description, priority, status
- All tools enforce user isolation via user_id parameter

**5. ChatKit Server:**
- Groq LLM integration via LiteLLM (`groq/llama-3.3-70b-versatile`)
- **CRITICAL ID collision fix** for LiteLLM/non-OpenAI providers
- Full conversation history support using ThreadItemConverter
- Agent instructions with tool descriptions
- Streaming response support

**6. API Integration:**
- Created chat router with `/chatkit` endpoint
- JWT authentication via existing `get_current_user` dependency
- ChatContext with user_id and database session
- Streaming and non-streaming response handling
- Health check endpoint at `/chatkit/health`
- Registered router in main FastAPI app

**7. Documentation:**
- Comprehensive README with setup instructions
- Implementation summary document
- Environment configuration guide
- Troubleshooting section
- Example conversations

**Critical Technical Implementation - ID Collision Fix:**

Implemented fix in `src/chatkit/server.py` for LiteLLM/Groq ID collision issue where provider-generated message IDs could conflict:

```python
id_mapping: dict[str, str] = {}

async for event in stream_agent_response(agent_context, result):
    if event.type == "thread.item.added":
        if isinstance(event.item, AssistantMessageItem):
            old_id = event.item.id
            if old_id not in id_mapping:
                new_id = self.store.generate_item_id("message", thread, context)
                id_mapping[old_id] = new_id
            event.item.id = id_mapping[old_id]
```

**Installation & Migration:**
- Ran `uv sync` successfully (93 packages installed)
- Applied Alembic migration 003 successfully
- Database tables created: conversations, messages with proper indexes

## Outcome

- ✅ Impact: Complete backend implementation for Phase III Todo AI Chatbot. Ready for frontend integration.
- 🧪 Tests: Migration validated, dependencies installed, database schema created. Manual testing pending.
- 📁 Files: 15 files created/modified across models, services, API, migrations, and documentation
- 🔁 Next prompts: Implement frontend with ChatKit React, create unit/integration tests, deploy to production
- 🧠 Reflection: ChatKit expert knowledge was crucial for implementing ID collision fix and proper store methods. Stateless architecture ensures horizontal scalability.

## Evaluation notes (flywheel)

- Failure modes observed: Initial migration dependency issue (referenced non-existent revision 002, fixed by setting down_revision='001'), missing email-validator dependency for Pydantic EmailStr
- Graders run and results (PASS/FAIL): PASS - Dependencies installed, PASS - Migration applied, PASS - All required Store methods implemented, PASS - ID collision fix included
- Prompt variant (if applicable): Used ChatKit backend skill directly instead of generic backend specialist agent
- Next experiment (smallest change to try): Add unit tests for MCP tools, implement frontend ChatKit React integration, add conversation list endpoint for user dashboard
