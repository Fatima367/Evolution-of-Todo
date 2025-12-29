---
description: "PHR for implementing remaining tasks from tasks.md"
---

# PHR: Implement Remaining Chatbot Tasks

**ID**: 0009
**TITLE**: Implement remaining chatbot tasks US3-US4
**STAGE**: green
**DATE_ISO**: 2025-12-29
**SURFACE**: agent
**MODEL**: claude-opus-4-5-20251101
**FEATURE**: 003-todo-ai-chatbot
**BRANCH**: 003-todo-ai-chatbot
**USER**: N/A (implementation)

**COMMAND**: /sp.implement @specs/003-todo-ai-chatbot/tasks.md

**LABELS**: ["implementation", "mcp-tools", "user-stories", "fuzzy-matching", "bulk-operations"]

**LINKS**: |
  - SPEC: `specs/003-todo-ai-chatbot/spec.md`
  - TASKS: `specs/003-todo-ai-chatbot/tasks.md`

**FILES_YAML**: |
  - phase3-todo-ai-chatbot/backend/src/todo_chatkit/tools.py
  - phase3-todo-ai-chatbot/backend/src/todo_chatkit/server.py

**TESTS_YAML**: |
  - phase3-todo-ai-chatbot/backend/tests/unit/test_mcp_tools.py (existing tests)
  - phase3-todo-ai-chatbot/backend/tests/unit/test_chatkit_store.py (existing tests)
  - phase3-todo-ai-chatbot/backend/tests/integration/test_chat_endpoint.py (existing tests)

**PROMPT_TEXT**: |
  /sp.implement @specs/003-todo-ai-chatbot/tasks.md . Use specialized subagents and skills

**RESPONSE_TEXT**: |
  Implemented User Story 3 (Task Management via Named References) and User Story 4 (Bulk Task Operations):

  **User Story 3 - Fuzzy Task Matching (T071-T078)**:
  - Added `_fuzzy_match()` function with character bigram similarity scoring (threshold 0.6)
  - Added `_extract_task_name_pattern()` to extract task names from natural language patterns like "the X task"
  - Added `find_task_by_name` MCP tool that returns: found (single match), ambiguous (multiple matches), not_found, or partial_match status with disambiguation guidance

  **User Story 4 - Bulk Operations (T079-T086)**:
  - Added `bulk_complete_tasks` MCP tool to complete all tasks with a specific status (default: pending)
  - Added `bulk_delete_completed` MCP tool to delete all completed tasks
  - Added `clear_all_tasks` MCP tool with explicit confirmation requirement ("confirm" or "yes")

  **Updated agent instructions** in server.py to include new tools and disambiguation behavior.

  All 9 MCP tools now return structured dict responses for proper parsing by the AI agent.

**OUTCOME**: |
  - SUCCESS: All new tools implemented with dict return types
  - find_task_by_name: Supports fuzzy matching with disambiguation for ambiguous references
  - bulk_complete_tasks: Completes all tasks matching a status filter
  - bulk_delete_completed: Removes all completed tasks in one call
  - clear_all_tasks: Requires explicit confirmation before destructive action
  - Syntax validation passed for all modified files

---
