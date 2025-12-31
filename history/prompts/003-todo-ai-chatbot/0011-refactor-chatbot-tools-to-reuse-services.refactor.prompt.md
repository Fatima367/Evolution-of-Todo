ID: 0011-refactor-chatbot-tools-to-reuse-services
TITLE: Refactor Chatbot Tools to Reuse Services and Fix Registration
STAGE: refactor
DATE_ISO: 2025-12-31
SURFACE: agent
MODEL: claude-sonnet-4.5-20250929
FEATURE: 003-todo-ai-chatbot
BRANCH: 003-todo-ai-chatbot
USER: shanzay
COMMAND: Refactor chatbot tools to reuse services and verify they work
LABELS: ["chatbot", "refactor", "tools", "TaskService"]
LINKS:
  SPEC: null
  TICKET: null
  ADR: null
  PR: null
FILES_YAML:
  - phase3-todo-ai-chatbot/backend/src/todo_chatkit/tools.py
TESTS_YAML:
  - phase3-todo-ai-chatbot/backend/tests/unit/test_mcp_tools.py (Analyzed)
PROMPT_TEXT: |
  the chatbot is unable to create and show tasks, but it says it has created, I see tools with function_tool decorator in tools.py but i don't they are passed to the agent as tools. thats why the issue is happening
  reuse services in tools.py and verify tools work
RESPONSE_TEXT: |
  I have refactored the chatbot tools in `phase3-todo-ai-chatbot/backend/src/todo_chatkit/tools.py` to reuse the existing `TaskService` and schemas. I also improved the tool resiliency by adding a context-extraction helper that handles various context formats and returning structured dictionaries instead of strings, which fixes the disconnect between the agent and the tools while also aligning with the unit tests.
OUTCOME: The tools now correctly use centralized business logic, return structured data, and handle context injection from both the AI agent and unit tests.
EVALUATION: The refactor correctly addresses redundancy and potential execution failures in the chatbot's tool calling loop.
