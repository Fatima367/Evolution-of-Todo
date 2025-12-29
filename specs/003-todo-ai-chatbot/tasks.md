---

description: "Task list for 003-todo-ai-chatbot implementation"
---

# Tasks: Todo AI Chatbot

**Input**: Design documents from `/specs/003-todo-ai-chatbot/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Test tasks are included for validation of stateless architecture and MCP tool functionality.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `frontend/src/`, `frontend/tests/`
- **MCP**: `backend/src/mcp/`
- Extends existing Phase II structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for chatbot features

- [X] T001 Create backend/src/chatkit directory structure (implemented as src/chatkit/ instead of src/mcp/)
- [X] T002 Add OpenAI Agents SDK and MCP SDK dependencies to backend/pyproject.toml
- [X] T003 [P] Add frontend/src/components/chat directory structure in frontend/components/chat/ (README.md created, index.ts verified)
- [X] T004 [P] Create backend/tests/chat_tests directory in backend/tests/ (contract/, integration/, unit/ directories exist)
- [X] T005 Verify Groq API key available in .env (GROQ_API_KEY, GROQ_MODEL) - added to .env.example

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️  CRITICAL**: No user story work can begin until this phase is complete

### Database Layer

- [X] T006 Create Alembic migration for conversations table (combined with T007 in 003_add_conversations_and_messages.py)
- [X] T007 [P] Create Alembic migration for messages table (combined with T006 in single migration file)
- [X] T008 [P] Run database migrations with `alembic upgrade head`
- [X] T009 Verify conversations and messages tables exist in database

### Data Models

- [X] T010 Create Conversation SQLModel in backend/src/models/conversation.py (id, user_id, created_at, updated_at)
- [X] T011 [P] Create Message SQLModel in backend/src/models/message.py (id, user_id, conversation_id, role, content, created_at)
- [X] T012 Add MessageRole enum in backend/src/models/message.py (USER="user", ASSISTANT="assistant")
- [X] T013 [P] Update backend/src/models/__init__.py to export Conversation and Message

### MCP Server Foundation

- [X] T014 Create ChatKit server in backend/src/chatkit/server.py (using ChatKit Server instead of standalone MCP)
- [X] T015 [P] Implement add_task MCP tool in backend/src/chatkit/tools.py (user_id, title, description → task_id, status, title)
- [X] T016 [P] Implement list_tasks MCP tool in backend/src/chatkit/tools.py (user_id, status → task array)
- [X] T017 [P] Implement complete_task MCP tool in backend/src/chatkit/tools.py (user_id, task_id → task_id, status, title)
- [X] T018 [P] Implement delete_task MCP tool in backend/src/chatkit/tools.py (user_id, task_id → task_id, status, title)
- [X] T019 [P] Implement update_task MCP tool in backend/src/chatkit/tools.py (user_id, task_id, title, description → task_id, status, title)
- [X] T020 Register all MCP tools with proper schemas in backend/src/chatkit/server.py (via OpenAI Agents SDK Tool objects)

### Chat Service Layer

- [X] T021 PostgreSQL Store implementation in backend/src/chatkit/store.py (implements all 14 Store methods)
- [X] T022 [P] Message persistence via Store methods (add_thread_item, load_thread_items)
- [X] T023 Create ChatKit Server with OpenAI Agents SDK in backend/src/chatkit/server.py (orchestrates agent, tool calls)

### API Endpoint

- [X] T024 Create chat endpoint in backend/src/api/chat_router.py (POST /chatkit - using ChatKit protocol)
- [X] T025 Request validation handled by ChatKit protocol (ThreadItem format)
- [X] T026 Response streaming handled by ChatKit Server (StreamingResult)
- [X] T027 Register chat router in backend/src/main.py
- [X] T028 Configure CORS for frontend origin in backend/src/main.py (already configured from Phase II)

### Frontend Foundation

- [X] T029 Integrated ChatKit React component (uses ChatKit protocol, not custom chatService)
- [X] T030 Created FloatingChatButton component in frontend/components/chat/FloatingChatButton.tsx (popup with ChatKit)
- [X] T031 [P] ChatKit handles message rendering (user/assistant bubbles built-in)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Natural Language Task Management (Priority: P1) 🎯 MVP

**Goal**: Users can manage todos through natural language via AI chatbot

**Independent Test**: Send natural language messages to chat endpoint and verify correct MCP tools are invoked with task operations in database

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T032 [P] Test MCP add_task tool returns task_id and "created" status in backend/tests/unit/test_mcp_tools.py (41 test cases)
- [X] T033 [P] Test MCP list_tasks tool filters by status in backend/tests/unit/test_mcp_tools.py
- [X] T034 [P] Test MCP complete_task tool updates task status in backend/tests/unit/test_mcp_tools.py
- [X] T035 [P] Test MCP delete_task tool removes task in backend/tests/unit/test_mcp_tools.py
- [X] T036 [P] Test MCP update_task tool modifies task in backend/tests/unit/test_mcp_tools.py
- [X] T037 Test chat endpoint creates new conversation when conversation_id not provided in backend/tests/integration/test_chat_endpoint.py (16 test cases)
- [X] T038 Test chat endpoint returns conversation_id, response, and tool_calls in backend/tests/integration/test_chat_endpoint.py
- [X] T039 Test chat endpoint resumes existing conversation when conversation_id provided in backend/tests/integration/test_chat_endpoint.py
- [X] T040 Test user and assistant messages are persisted in database in backend/tests/integration/test_chat_endpoint.py
- [X] T041 Test chat endpoint is stateless (works after server restart) in backend/tests/integration/test_chat_endpoint.py

### Implementation for User Story 1

- [X] T042 [US1] Implement OpenAI Agents SDK integration (implemented in backend/src/todo_chatkit/server.py with Groq via LiteLLM)
- [X] T043 [US1] Wire MCP tools to OpenAI Agents SDK (implemented in server.py create_agent method)
- [X] T044 [US1] Implement conversation history loading (implemented in server.py respond method + store.py load_thread_items)
- [X] T045 [US1] Implement agent system prompt (implemented in server.py create_agent with tool descriptions)
- [X] T046 [US1] Implement user message storage (implemented in store.py add_thread_item)
- [X] T047 [US1] Implement assistant response storage (implemented in store.py add_thread_item)
- [X] T048 [US1] Implement tool_calls tracking (handled by ChatKit streaming events)
- [X] T049 [US1] Add error handling for Groq API failures (implemented in server.py with try/catch)
- [X] T050 [US1] Chat interface integrated (FloatingChatButton.tsx uses ChatKit React component)
- [X] T051 [US1] ChatKit component integrated (FloatingChatButton.tsx with useChatKit hook)
- [X] T052 [US1] Chat message sending (handled by ChatKit React component)
- [X] T053 [US1] Display conversation messages (handled by ChatKit React component)
- [X] T054 [US1] Display tool_calls indicators (handled by ChatKit React component)
- [X] T055 [US1] Auto-scroll to latest message (handled by ChatKit React component)
- [X] T056 [US1] Loading states for chat requests (handled by ChatKit React component)
- [X] T057 [US1] Conversation_id persistence (implemented in FloatingChatButton.tsx localStorage per-user)
- [X] T058 [US1] Style MessageBubble (handled by ChatKit React component with dark theme)
- [X] T059 [US1] Responsive styling (FloatingChatButton.tsx with responsive popup 420x600px)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Users can create, list, complete, update, and delete tasks via natural language.

---

## Phase 4: User Story 2 - Conversation Context Persistence (Priority: P1)

**Goal**: Conversation history persists across sessions and server restarts

**Independent Test**: Send messages in conversation, restart server, resume conversation by providing conversation_id and verify full history is available

### Tests for User Story 2 ⚠️

- [ ] T060 [P] Test conversation persists across multiple message exchanges in backend/tests/chat_tests/test_conversation_service.py
- [ ] T061 [P] Test conversation updated_at timestamp updates on each message in backend/tests/chat_tests/test_conversation_service.py
- [ ] T062 Test conversation can be resumed after server restart in backend/tests/chat_tests/test_chat_endpoint.py
- [ ] T063 Test messages are ordered by created_at ascending in backend/tests/chat_tests/test_message_service.py
- [ ] T064 Test frontend resends conversation_id on page refresh in frontend/tests/chat/chat.spec.ts

### Implementation for User Story 2

- [X] T065 [US2] Conversation retrieval (implemented in store.py load_thread + load_thread_items methods)
- [X] T066 [US2] Update conversation timestamp (implemented in store.py save_thread + add_thread_item methods)
- [X] T067 [US2] Return conversation_id (handled by ChatKit protocol in chat_router.py)
- [X] T068 [US2] Conversation_id in response (handled by ChatKit protocol responses)
- [X] T069 [US2] Store conversation_id in browser (implemented in FloatingChatButton.tsx with localStorage)
- [X] T070 [US2] Include conversation_id in requests (handled by ChatKit React component via initialThread prop)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Users can have conversations that persist across sessions.

---

## Phase 5: User Story 3 - Task Management via Named References (Priority: P2)

**Goal**: Users can refer to tasks by name instead of ID, with disambiguation for ambiguous references

**Independent Test**: Send "delete the meeting task" when multiple tasks contain "meeting" and verify assistant asks for clarification

### Tests for User Story 3 ⚠️

- [ ] T071 [P] Test agent asks for clarification on ambiguous task reference in backend/tests/chat_tests/test_chat_service.py
- [ ] T072 [P] Test agent handles unique task name correctly in backend/tests/chat_tests/test_chat_service.py
- [ ] T073 [P] Test fuzzy matching works for partial names in backend/tests/chat_tests/test_mcp_tools.py

### Implementation for User Story 3

- [ ] T074 [US3] Implement fuzzy task matching in list_tasks MCP tool (partial name search in backend/src/mcp/tools.py)
- [ ] T075 [US3] Add disambiguation logic for multiple matches in backend/src/mcp/tools.py (return options for user)
- [ ] T076 [US3] Update agent system prompt to handle disambiguation requests in backend/src/services/chat_service.py
- [ ] T077 [US3] Implement task name extraction from user message in backend/src/services/chat_service.py (identify "the X task" pattern)
- [ ] T078 [US3] Add clarification UI for disambiguation in frontend/src/components/chat/ChatInterface.tsx (show matching options)

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently. Users can reference tasks naturally.

---

## Phase 6: User Story 4 - Bulk Task Operations (Priority: P3)

**Goal**: Users can perform operations on multiple tasks at once through natural language

**Independent Test**: Send "mark all tasks as complete" and verify all pending tasks are marked complete

### Tests for User Story 4 ⚠️

- [ ] T079 [P] Test bulk complete all tasks operation in backend/tests/chat_tests/test_mcp_tools.py
- [ ] T080 [P] Test bulk delete completed tasks operation in backend/tests/chat_tests/test_mcp_tools.py
- [ ] T081 [P] Test "clear my list" deletes all tasks in backend/tests/chat_tests/test_mcp_tools.py

### Implementation for User Story 4

- [ ] T082 [US4] Add bulk_complete MCP tool in backend/src/mcp/tools.py (marks all user tasks as complete)
- [ ] T083 [US4] Add bulk_delete MCP tool for completed tasks in backend/src/mcp/tools.py (deletes all completed tasks)
- [ ] T084 [US4] Add clear_all MCP tool in backend/src/mcp/tools.py (deletes all tasks with confirmation)
- [ ] T085 [US4] Update agent system prompt for bulk operations in backend/src/services/chat_service.py
- [ ] T086 [US4] Add bulk operation confirmation UI in frontend/src/components/chat/ChatInterface.tsx (confirm destructive bulk actions)

**Checkpoint**: All user stories should now be independently functional. Users can perform bulk operations.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Testing & Validation

- [ ] T087 Run all backend tests with `pytest backend/tests/ -v`
- [ ] T088 Run all frontend tests with `npm test` (if configured)
- [ ] T089 Perform end-to-end manual testing: create task via chat, list tasks, complete task, delete task, resume conversation
- [ ] T090 Verify stateless behavior: restart backend, resume conversation, verify data intact

### Documentation

- [ ] T091 Update README.md with chatbot setup instructions
- [ ] T092 Add .env.example with GROQ_API_KEY placeholder in backend/.env.example
- [ ] T093 Document MCP tools usage in backend/README.md
- [ ] T094 Add conversation examples to quickstart.md

### Performance & Quality

- [ ] T095 Add response time logging to chat endpoint in backend/src/api/chat.py
- [ ] T096 Verify <3 second response time for typical chat exchanges
- [ ] T097 Run code linting: `ruff check backend/src/` and `npm run lint` (if configured)
- [ ] T098 Run code formatting: `ruff format backend/src/` and `npm run format` (if configured)

### Security Validation

- [ ] T099 Verify all queries filter by user_id in backend/src/services/
- [ ] T100 Verify no API keys committed to repository (check git history)
- [ ] T101 Verify CORS only allows frontend origin in backend/src/main.py

### Quickstart Validation

- [ ] T102 Follow quickstart.md setup instructions from scratch
- [ ] T103 Verify each quickstart example command works as documented
- [ ] T104 Verify troubleshooting section covers common issues

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Extends US1 but independently testable
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Extends US1 MCP tools
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Adds new MCP tools

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- MCP tools before ChatService integration
- Data models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- All tests for a user story marked [P] can run in parallel
- Backend tasks and frontend tasks for same story can run in parallel
- Data models (T010, T011) can run in parallel
- MCP tools (T015-T020) can run in parallel after T014
- Conversation and Message services (T021, T022) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "T032 Test MCP add_task tool"
Task: "T033 Test MCP list_tasks tool"
Task: "T034 Test MCP complete_task tool"
Task: "T035 Test MCP delete_task tool"
Task: "T036 Test MCP update_task tool"
Task: "T037 Test chat endpoint creates new conversation"
Task: "T038 Test chat endpoint returns response and tool_calls"
Task: "T039 Test chat endpoint resumes existing conversation"
Task: "T040 Test chat endpoint is stateless"

# Launch backend models together:
Task: "T010 Create Conversation SQLModel"
Task: "T011 Create Message SQLModel"

# Launch frontend components together:
Task: "T030 Create ChatInterface component"
Task: "T031 Create MessageBubble component"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only) 🎯

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T028) - CRITICAL
3. Complete Phase 3: User Story 1 (T032-T059)
4. **STOP and VALIDATE**: Test User Story 1 independently (all acceptance scenarios from spec.md)
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Complete Polish → Final production-ready system

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (backend + tests)
   - Developer B: User Story 1 (frontend + tests)
3. User Story 1 complete and validated
4. Developers proceed to User Stories 2, 3, 4 independently or in priority order

---

## Summary

| Metric | Count |
|---------|-------|
| **Total Tasks** | 104 |
| **Phase 1: Setup** | 5 tasks |
| **Phase 2: Foundational** | 28 tasks |
| **Phase 3: US1 (MVP)** | 28 tasks (11 tests + 17 implementation) |
| **Phase 4: US2** | 10 tasks (5 tests + 5 implementation) |
| **Phase 5: US3** | 8 tasks (3 tests + 5 implementation) |
| **Phase 6: US4** | 8 tasks (3 tests + 5 implementation) |
| **Phase 7: Polish** | 18 tasks |
| **Parallelizable Tasks** | ~35 tasks |
| **Test Tasks** | 21 tasks |

### MVP Scope (US1 Only)

For minimum viable product focusing on just User Story 1:
- Phase 1: 5 tasks
- Phase 2: 28 tasks
- Phase 3: 28 tasks
- Phase 7: Critical polish tasks (T087-T090)
- **Total MVP tasks**: ~70 tasks

### Validation: Format Checklist

- ✅ All tasks follow format: `- [ ] [ID] [P?] [Story] Description`
- ✅ All tasks have exact file paths
- ✅ Test tasks are marked [P] for parallel execution
- ✅ Implementation tasks have [Story] labels for traceability
- ✅ User stories organized by priority (P1 → P2 → P3)
- ✅ Foundational phase clearly separates blocking tasks
- ✅ Each user story has independent test criteria
- ✅ Parallel opportunities identified
