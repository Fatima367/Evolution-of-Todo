# Research Notes: Todo AI Chatbot

**Feature**: 003-todo-ai-chatbot
**Created**: 2025-12-28
**Purpose**: Document technology research and architectural decisions for Phase III

## Overview

Phase III adds an AI-powered chatbot interface to the existing Phase II web application. This document captures research on key technologies, architectural patterns, and integration approaches.

## Technology Decisions

### 1. OpenAI Agents SDK with Groq

**Decision**: Use OpenAI Agents SDK configured with Groq API as the LLM provider.

**Rationale**:
- OpenAI Agents SDK provides structured tool orchestration and conversation management
- Groq API offers fast inference with compatible OpenAI-style API
- SDK handles conversation state, tool selection, and response generation
- Explicit tool definitions align with MCP tool-based architecture principle

**Alternatives Considered**:

| Option | Pros | Cons | Rejection Reason |
|--------|-------|--------|-----------------|
| Direct Groq API calls | Simpler, lighter weight | Requires manual tool orchestration, conversation management, prompt engineering |
| LangChain | Rich ecosystem, flexible | More complex setup, overkill for this use case |
| Vercel AI SDK | Simple integration | Limited tool support, less control over agent behavior |

### 2. Model Context Protocol (MCP) Server

**Decision**: Implement MCP server using Official MCP SDK (Python) to expose task management operations.

**Rationale**:
- MCP provides standardized tool interface for AI agents
- Enables clean separation between AI logic and business operations
- Tools can be versioned and tested independently
- Aligns with "Tool-Based AI (No Magic Prompts)" principle

**MCP Tools to Implement**:

| Tool | Purpose | Input Schema | Output Schema |
|-------|---------|---------------|---------------|
| `add_task` | Create new task | user_id (str, required), title (str, required), description (str, optional) | task_id (int), status (str), title (str) |
| `list_tasks` | Retrieve tasks | user_id (str, required), status (str, optional: "all"/"pending"/"completed") | Array of task objects |
| `complete_task` | Mark task complete | user_id (str, required), task_id (int, required) | task_id (int), status (str), title (str) |
| `delete_task` | Remove task | user_id (str, required), task_id (int, required) | task_id (int), status (str), title (str) |
| `update_task` | Modify task | user_id (str, required), task_id (int, required), title (str, optional), description (str, optional) | task_id (int), status (str), title (str) |

**Alternatives Considered**:

| Option | Pros | Cons | Rejection Reason |
|--------|-------|--------|-----------------|
| Direct database access from agent | Simpler | Violates tool-based principle, harder to test, security risk |
| HTTP-based tool API | Language agnostic | Adds network overhead, more complex deployment |
| In-process function calls | Fastest | Couples AI to business logic, less modular |

### 3. Stateless Chat Endpoint Architecture

**Decision**: Each chat request is processed independently with conversation history fetched from database.

**Request Flow**:

```
1. POST /api/{user_id}/chat
   ├─ Request body: { conversation_id?, message }
   │
2. Fetch conversation history (if conversation_id provided)
   │  SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at
   │
3. Build message array for agent (history + new message)
   │  [{"role": "user", "content": "..."}, ...]
   │
4. Store user message in database
   │  INSERT INTO messages (user_id, conversation_id, role, content) ...
   │
5. Run AI agent with MCP tools
   │  OpenAI Agents SDK + MCP tool calls
   │
6. Store assistant response in database
   │  INSERT INTO messages (user_id, conversation_id, role, content) ...
   │
7. Return response
   │  { conversation_id, response, tool_calls }
```

**Rationale**:
- Stateless design enables horizontal scaling
- Server restarts don't lose conversation state
- Each request is independently testable
- Follows constitution's "Stateless Servers" principle

**Alternatives Considered**:

| Option | Pros | Cons | Rejection Reason |
|--------|-------|--------|-----------------|
| In-memory conversation cache | Faster | Violates stateless principle, data loss on restart |
| Redis for session state | Fast, distributed | Adds infrastructure complexity, not needed for this scale |

### 4. Database Schema Extensions

**Decision**: Add `conversations` and `messages` tables to existing PostgreSQL schema.

**Conversations Table**:

```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
```

**Messages Table**:

```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    conversation_id INTEGER NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
```

**Rationale**:
- Extends existing schema from Phase II
- Foreign keys ensure referential integrity
- Cascading deletes handle user/account deletion
- Indexes on frequently queried columns (user_id, conversation_id)

### 5. Frontend Chat UI

**Decision**: Implement custom chat component using Next.js App Router, shadcn/ui components, and Tailwind CSS.

**Component Structure**:

```
ChatInterface (page: /chat)
├── ChatContainer (scrollable message list)
│   ├── MessageBubble (user messages)
│   └── MessageBubble (assistant messages with tool call indicators)
└── ChatInput (fixed bottom bar)
    └── TextInput + Send Button
```

**Rationale**:
- Consistent with existing Phase II frontend stack
- shadcn/ui provides polished, accessible components
- Tailwind CSS enables responsive design
- Custom implementation allows full control over UX and theming

**Alternatives Considered**:

| Option | Pros | Cons | Rejection Reason |
|--------|-------|--------|-----------------|
| OpenAI ChatKit (hosted) | Quick setup, managed | Requires domain allowlist configuration, less control, external dependency |
| Stream Chat SDK | Real-time streaming | Overkill for MVP, adds complexity |
| Third-party chat component | Feature-rich | Less control over styling, potential bloat |

### 6. Agent Prompt Engineering

**Decision**: Use structured system prompt with explicit tool descriptions.

**System Prompt Template**:

```
You are a helpful todo assistant. Help users manage their tasks using the provided tools.

Available tools:
- add_task: Create a new task (requires title, optionally description)
- list_tasks: Show tasks with optional status filter
- complete_task: Mark a task as complete
- delete_task: Remove a task
- update_task: Change task title or description

Behavior guidelines:
- Always confirm actions with friendly response
- If task ID is provided, use it directly
- If task name is ambiguous, ask for clarification
- Handle errors gracefully
- Be concise and helpful
```

**Rationale**:
- Explicit tool definitions prevent hallucinations
- Clear guidelines ensure consistent behavior
- Tool-based approach aligns with constitution

### 7. Error Handling Strategy

**Decision**: Graceful degradation with user-friendly error messages.

**Error Scenarios**:

| Scenario | Error Response | User Message |
|-----------|----------------|--------------|
| Invalid task ID | 404 with error details | "Task not found. Would you like to see your task list?" |
| Empty task title | 400 validation error | "What task would you like to add?" |
| Ambiguous task reference | Successful list + clarification | "I found multiple tasks with 'meeting'. Which one do you mean?" |
| MCP tool failure | 500 with logged details | "Something went wrong. Please try again." |

**Rationale**:
- Graceful handling prevents user frustration
- Error codes enable frontend-specific responses
- Errors are logged for debugging

### 8. Testing Strategy

**Decision**: Multi-layer testing approach with focus on stateless behavior.

**Test Layers**:

1. **Unit Tests** (pytest):
   - MCP tool functions
   - Conversation service CRUD
   - Message service CRUD

2. **Integration Tests** (pytest + test database):
   - Chat endpoint full flow
   - Conversation resumption after restart
   - User isolation enforcement

3. **E2E Tests** (Playwright):
   - User creates task via chat
   - User lists tasks via chat
   - User completes task via chat
   - Conversation persists across page refresh

**Rationale**:
- Unit tests verify tool behavior
- Integration tests verify stateless architecture
- E2E tests verify user experience

### 9. Environment Configuration

**Decision**: Environment variables for all secrets and configuration.

**Required .env Variables**:

```bash
# Database (from Phase II)
DATABASE_URL=postgresql://user:pass@host/db

# Better Auth (from Phase II)
BETTER_AUTH_SECRET=your-secret
BETTER_AUTH_URL=https://your-domain.com

# AI Provider
GROQ_API_KEY=gsk_...  # AI agents MUST NOT read this
GROQ_MODEL=llama-3.3-70b-versatile

# Application
API_BASE_URL=http://localhost:8000
```

**Security Consideration**:
- AI agents only read `.env.example` for reference
- Actual `.env` is gitignored
- Production uses cloud secret management

## Integration with Phase II

### Reusing Existing Components

| Component | How Used |
|-----------|-----------|
| Task model/database | Extended with conversation/message tables |
| Better Auth | JWT validation on chat endpoint |
| User model | Foreign key for user isolation |
| API infrastructure | CORS, logging, error handling |

### New Components Required

| Component | Purpose |
|-----------|---------|
| Conversation model | Chat session tracking |
| Message model | Message history |
| MCP server | Tool definitions and execution |
| Chat endpoint | Main API entry point |
| Chat UI | Frontend interface |

## Open Questions (Resolved)

### Q1: ChatKit vs Custom Implementation
**Decision**: Custom implementation with Next.js + shadcn/ui
**Reason**: Full control, consistent with existing stack, avoids external domain configuration

### Q2: MCP Server Hosting
**Decision**: MCP server runs as part of backend service
**Reason**: Simpler deployment, no network overhead, shared database access

### Q3: Conversation Context Window
**Decision**: Full conversation history loaded from database
**Reason**: Simpler implementation, unlimited context (within practical limits), easier debugging

## Performance Considerations

### Database Indexing
- `conversations(user_id)`: Fast user conversation lookup
- `messages(conversation_id)`: Efficient message history retrieval
- `messages(user_id)`: User-wide message queries (if needed)

### Query Optimization
- Limit conversation history to last N messages for LLM context window
- Pagination for task lists with many items
- Connection pooling via SQLAlchemy

### Caching Strategy
- No in-memory caching (stateless requirement)
- Rely on database query optimization
- Consider read replicas if scaling needed

## Security Considerations

### User Isolation
- All queries filtered by `user_id` from JWT
- No cross-user data access paths
- Test with multiple user accounts

### Input Validation
- Pydantic models validate all API inputs
- Reject malformed requests with 400
- Sanitize to prevent SQL injection (ORM handles)

### API Key Management
- AI agents only read `.env.example`
- Production uses cloud secret management
- Never commit secrets to repository

## References

- [OpenAI Agents SDK Documentation](https://platform.openai.com/docs/agents)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Groq API Documentation](https://console.groq.com/docs)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
