---
description: "PHR for fixing MCP tools return type bug in todo_chatkit"
---

# PHR: Fix MCP Tools Return Type Bug

**ID**: 0008
**TITLE**: Fix MCP tools return type bug
**STAGE**: refactor
**DATE_ISO**: 2025-12-29
**SURFACE**: agent
**MODEL**: claude-opus-4-5-20251101
**FEATURE**: 003-todo-ai-chatbot
**BRANCH**: 003-todo-ai-chatbot
**USER**: N/A (bug fix)

**COMMAND**: /sp.implement @specs/003-todo-ai-chatbot/tasks.md + bug fix

**LABELS**: ["bugfix", "mcp-tools", "chatbot"]

**LINKS**: |
  - SPEC: `specs/003-todo-ai-chatbot/spec.md`
  - TASKS: `specs/003-todo-ai-chatbot/tasks.md`

**FILES_YAML**: |
  - phase3-todo-ai-chatbot/backend/src/todo_chatkit/tools.py

**TESTS_YAML**: |
  - phase3-todo-ai-chatbot/backend/tests/unit/test_mcp_tools.py (tests expect dict returns)

**PROMPT_TEXT**: |
  /sp.implement @specs/003-todo-ai-chatbot/tasks.md . ALso the chatbot says it has created the task but there is no task created, so it is unable to create and show tasks

**RESPONSE_TEXT**: |
  Fixed MCP tools to return dictionaries instead of plain strings. All 5 tools (add_task, list_tasks, complete_task, delete_task, update_task) now return structured dict responses with proper keys like task_id, status, title, priority. This enables correct tool call result parsing by the OpenAI Agents SDK and proper task persistence in the database.

**OUTCOME**: |
  - SUCCESS: All MCP tools now return dict[str, str] instead of str
  - add_task returns: {"task_id": "...", "status": "created", "title": "...", "priority": "..."}
  - list_tasks returns: {"tasks": [...], "count": N, "message": "..."}
  - complete_task returns: {"task_id": "...", "status": "completed", "title": "..."}
  - delete_task returns: {"task_id": "...", "status": "deleted", "title": "..."}
  - update_task returns: {"status": "updated", "title": "...", "priority": "...", "task_status": "...", "changes": "..."}

---
