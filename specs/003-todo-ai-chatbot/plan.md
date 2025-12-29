# Implementation Plan: Todo AI Chatbot

**Branch**: `003-todo-ai-chatbot` | **Date**: 2025-12-28 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-todo-ai-chatbot/spec.md`

**Note**: This template is filled in by `/sp.plan` command. See `.specify/templates/commands/plan.md` for execution workflow.

## Summary

Phase III introduces an AI-powered chatbot interface for managing todos through natural language. This phase builds upon the Phase II web application by adding an OpenAI Agents SDK integration with MCP (Model Context Protocol) tools that expose task operations. The system maintains a stateless server architecture where all conversation context is persisted to the database, enabling horizontal scaling and resilience.

**Primary Technical Approach**:
- OpenAI Agents SDK orchestrates conversation flow and tool selection
- MCP server exposes task management operations as structured tools
- Stateless FastAPI endpoint processes each request independently
- Database-backed conversation history enables session resumption
- User-scoped isolation via JWT-based authentication (from Phase II)

## Technical Context

**Language/Version**: Python 3.13+ for backend, TypeScript 5+ for frontend
**Primary Dependencies**: FastAPI, OpenAI Agents SDK, Official MCP SDK, SQLModel, Neon Serverless PostgreSQL, Better Auth (from Phase II), Groq API (LLM provider)
**Storage**: Neon Serverless PostgreSQL (tasks, conversations, messages)
**Testing**: pytest for backend, Playwright for frontend E2E testing
**Target Platform**: Linux server (backend), Browser (frontend chat interface)
**Project Type**: web application (extends existing Phase II backend/frontend structure)
**Performance Goals**: <3 second response time for typical chat exchanges, <500ms for database queries, support 100 concurrent users
**Constraints**: Stateless server (no in-memory session state), all AI actions via explicit MCP tools (no "magic prompts"), user isolation enforced at DB level
**Scale/Scope**: Single database with user-isolated data, designed for horizontal scaling via load balancers

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase1 design.*

| Constitution Principle | Status | Notes |
|---------------------|--------|--------|
| **Spec-Driven Development (SDD)** | ✅ PASS | Spec exists with user stories, requirements, and success criteria |
| **Phase-Gated Evolution** | ✅ PASS | Phase III builds on completed Phase II (web + DB + auth) |
| **Feature Completeness Mandate** | ✅ PASS | All Basic features from spec covered via MCP tools |
| **Multi-User Authentication** | ✅ PASS | Better Auth from Phase II reused with JWT validation |
| **AI-Native Design (Phase III+)** | ✅ PASS | OpenAI Agents SDK + MCP tools, no magic prompts |
| **Cloud-Native Architecture** | ✅ PASS | Stateless server, DB-persisted state, container-ready |
| **Stateless Servers** | ✅ PASS | No in-memory session state, all conversation state in DB |
| **Explicit Data Ownership** | ✅ PASS | user_id on all entities, filtered queries |
| **Clear Service Boundaries** | ✅ PASS | API endpoints, MCP tools, frontend separate concerns |
| **Tool-Based AI (No Magic Prompts)** | ✅ PASS | All task operations via explicit MCP tool calls |
| **Performance and Scalability** | ✅ PASS | <3s response target, <500ms API p95, indexed queries |
| **Clean Code** | ✅ PASS | Python 3.13+ type hints, Pydantic models, docstrings |
| **Strict Typing** | ✅ PASS | Pydantic models for API, TypeScript for frontend |
| **Modularity** | ✅ PASS | Separated routers, services, models, MCP tools |
| **Security & Hardening** | ✅ PASS | JWT auth, user isolation, input validation, no secrets in code |
| **API Key Management** | ✅ PASS | .env for local, cloud secrets for production; AI agents only read .env.example |
| **No Skipped Phases** | ✅ PASS | Phase II complete before Phase III begins |

**All gates pass**. Proceeding to Phase 0 research.

## Project Structure

### Documentation (this feature)

```text
specs/003-todo-ai-chatbot/
├── spec.md              # Feature specification (/sp.specify command)
├── plan.md              # This file (/sp.plan command)
├── research.md          # Phase 0 output - technology research and decisions
├── data-model.md        # Phase 1 output - database schema
├── quickstart.md        # Phase 1 output - setup and run instructions
├── contracts/           # Phase 1 output - API and MCP tool schemas
│   ├── chat-api.yaml    # OpenAPI spec for chat endpoint
│   └── mcp-tools.yaml   # MCP tool schemas
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

This feature extends the existing Phase II web application structure:

```text
# Backend (extends existing phase2-todo-web/backend/)
backend/
├── src/
│   ├── models/
│   │   ├── task.py              # Task model (extends Phase II)
│   │   ├── conversation.py       # NEW: Conversation model
│   │   └── message.py          # NEW: Message model
│   ├── services/
│   │   ├── todo_service.py       # Task CRUD operations
│   │   ├── conversation_service.py  # NEW: Conversation management
│   │   └── chat_service.py      # NEW: Chat orchestration + AI agent
│   ├── mcp/
│   │   ├── server.py             # NEW: MCP server entry point
│   │   └── tools.py              # NEW: MCP tool definitions
│   ├── api/
│   │   ├── todos.py             # Existing todo endpoints
│   │   └── chat.py              # NEW: POST /api/{user_id}/chat endpoint
│   └── main.py                 # FastAPI application
└── tests/
    ├── test_todo_service.py
    ├── test_conversation_service.py
    ├── test_mcp_tools.py
    └── test_chat_endpoint.py

# Frontend (extends existing phase2-todo-web/frontend/)
frontend/
├── src/
│   ├── components/
│   │   ├── ChatInterface.tsx   # NEW: Chat UI component
│   │   └── MessageBubble.tsx    # NEW: Message display
│   ├── services/
│   │   └── chatService.ts        # NEW: API client for chat
│   └── pages/
│       └── chat.tsx             # NEW: Chat page route
└── tests/
    └── chat.spec.ts
```

**Structure Decision**: This feature extends the existing Phase II web application structure (backend/frontend pattern). The ChatKit UI mentioned in the spec will be implemented as a custom frontend component using Next.js and shadcn/ui for consistency with the existing codebase. The MCP server runs as part of the backend service, exposing tools to the AI agent via internal communication.

## Complexity Tracking

No constitution violations require justification. The design follows established patterns from Phase II and adheres to AI-Native Design principles.
