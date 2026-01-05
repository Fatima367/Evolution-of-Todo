---
id: "0023"
title: "implement-favorites-and-recurring-tasks"
stage: "green"
date: "2026-01-05"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "003-todo-ai-chatbot"
branch: "003-todo-ai-chatbot"
user: "shanzay"
command: "git add + commit"
labels: ["features","tasks","favorites","recurring","calendar"]
links:
  spec: "null"
  ticket: "null"
  adr: "null"
  pr: "null"
files:
  - "phase3-todo-ai-chatbot/backend/alembic/versions/002_add_is_favorite_and_recurring_type.py"
  - "phase3-todo-ai-chatbot/backend/src/api/task_router.py"
  - "phase3-todo-ai-chatbot/backend/src/models/task.py"
  - "phase3-todo-ai-chatbot/backend/src/schemas/task_schemas.py"
  - "phase3-todo-ai-chatbot/backend/src/services/task_service.py"
  - "phase3-todo-ai-chatbot/frontend/app/dashboard/calendar/page.tsx"
  - "phase3-todo-ai-chatbot/frontend/app/dashboard/favorites/page.tsx"
  - "phase3-todo-ai-chatbot/frontend/app/dashboard/tasks/page.tsx"
  - "phase3-todo-ai-chatbot/frontend/components/layout/DashboardSidebar.tsx"
  - "phase3-todo-ai-chatbot/frontend/components/tasks/CreateTaskModal.tsx"
  - "phase3-todo-ai-chatbot/frontend/components/tasks/EditTaskModal.tsx"
  - "phase3-todo-ai-chatbot/frontend/components/tasks/TaskForm.tsx"
  - "phase3-todo-ai-chatbot/frontend/components/tasks/TaskItem.tsx"
  - "phase3-todo-ai-chatbot/frontend/components/tasks/TaskList.tsx"
  - "phase3-todo-ai-chatbot/frontend/hooks/useTasks.ts"
  - "phase3-todo-ai-chatbot/frontend/lib/api.ts"
  - "phase3-todo-ai-chatbot/frontend/lib/types.ts"
  - "phase3-todo-ai-chatbot/frontend/components/auth/LoginModal.tsx"
  - "phase3-todo-ai-chatbot/frontend/components/auth/SignUpModal.tsx"
  - "phase2-todo-web/frontend/app/icon.svg"
tests:
  - "None"
---

## Prompt

Staged implementation of favorites and recurring tasks features:

**Backend Changes:**
- Added `is_favorite` (boolean) and `recurring_type` (enum: none, daily, weekly, monthly, yearly) columns to tasks table via Alembic migration 002
- New `PATCH /tasks/{task_id}/favorite` endpoint to toggle favorite status
- New `is_favorite` query parameter for filtering tasks
- Updated Task model, schemas, and service layer

**Frontend Changes:**
- New Calendar view page at `/dashboard/calendar` with monthly calendar grid showing tasks by due date
- New Favorites view page at `/dashboard/favorites` showing only favorited tasks
- Added favorite star toggle button to TaskItem with visual feedback
- Added recurring type selector to TaskForm (Create/Edit task modals)
- Updated DashboardSidebar with new Calendar and Favorites navigation items
- Updated API client with `toggleFavorite` method
- Updated TypeScript types and useTasks hook

## Response snapshot

Successfully implemented favorites and recurring tasks features across backend and frontend. Added database migration, API endpoints, calendar visualization, and favoriting UI with star toggle.

## Outcome

- ✅ Impact: Users can now mark tasks as favorites and view them in a dedicated page, set recurring task schedules, and view tasks in a calendar view organized by due date
- 🧪 Tests: None
- 📁 Files: 20 files modified/created (847 insertions, 76 deletions)
- 🔁 Next prompts: "Implement recurring task generation logic" for automatic task creation
- 🧠 Reflection: Feature completes core favorites and recurring functionality; calendar view enhances task visualization by due dates

## Evaluation notes (flywheel)

- Failure modes observed: "null"
- Graders run and results (PASS/FAIL): "null"
- Prompt variant (if applicable): "null"
- Next experiment (smallest change to try): "null"
