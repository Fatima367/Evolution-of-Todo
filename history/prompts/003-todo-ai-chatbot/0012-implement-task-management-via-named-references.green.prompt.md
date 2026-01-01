---
id: 0012
title: Implement Task Management via Named References
stage: green
date: 2025-12-31
surface: agent
model: claude-sonnet-4.5-20250929
feature: 003-todo-ai-chatbot
branch: 003-todo-ai-chatbot
user: unknown
command: none
labels: [backend, mcp-tools, fuzzy-matching, refactor]
links:
  spec: specs/003-todo-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - phase3-todo-ai-chatbot/backend/src/services/task_service.py
tests:
  - phase3-todo-ai-chatbot/backend/tests/unit/test_mcp_tools.py
  - phase3-todo-ai-chatbot/backend/verify_named_refs.py
---

## Prompt

I need you to implement User Story 3: Task Management via Named References.
This involves:
- Updating MCP tools to accept and handle task titles or partial names instead of just UUIDs.
- Implementing fuzzy matching for task titles.
- Implementing disambiguation logic when multiple tasks match a name.

Files:
- phase3-todo-ai-chatbot/backend/src/todo_chatkit/tools.py (MCP tools like complete_task, delete_task, update_task)
- phase3-todo-ai-chatbot/backend/src/services/task_service.py (shared business logic)

Plan:
1. Add a method to `TaskService` that searches for tasks by a string query (handles UUID format check first, then exact title match, then partial/fuzzy match).
2. The method should return either a single task, a list of matches (if ambiguous), or None.
3. Update `complete_task`, `delete_task`, and `update_task` in `tools.py` to use this new lookup method.
4. If multiple tasks are found, return a structured error/message that the Chat Agent can use to ask for clarification.

Ensure all tool calls still work with IDs as before. Use Python 3.13+ type hints.

## Response snapshot

I have refined the `TaskService.find_tasks_by_query` method to handle whitespace stripping and empty queries, ensuring robust fuzzy/partial matching for task titles. I verified that the MCP tools in `tools.py` already utilize this method and correctly handle ambiguous matches by returning a structured `ambiguous` status, allowing the AI agent to ask for clarification as required by the specification.

## Outcome

- ✅ Impact: Users can now manage tasks using titles or partial names (e.g., "complete buy groceries") instead of cryptic UUIDs.
- 🧪 Tests: Verification script `verify_named_refs.py` confirms unique title match, fuzzy match, ambiguity handling, and whitespace tolerance.
- 📁 Files: Refined `phase3-todo-ai-chatbot/backend/src/services/task_service.py`.
- 🔁 Next prompts: Proceed with User Story 4: LLM-Powered Natural Language Task Queries.
- 🧠 Reflection: The foundation for named references was already partially in place, requiring only refinement for edge cases (whitespace) and verification of the end-to-end tool flow.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): null
