---
id: 0018
title: Rebrand TodoEvo to TodoBoard
stage: refactor
date: 2026-01-03
surface: agent
model: claude-sonnet-4-5-20250929
feature: 003-todo-ai-chatbot
branch: 003-todo-ai-chatbot
user: user
command: change all TodoEvo to TodoBoard
labels: [rebranding, refactor, frontend]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - phase3-todo-ai-chatbot/frontend/app/layout.tsx
  - phase3-todo-ai-chatbot/frontend/app/terms/page.tsx
  - phase3-todo-ai-chatbot/frontend/app/privacy/page.tsx
  - phase3-todo-ai-chatbot/frontend/app/page.tsx
  - phase3-todo-ai-chatbot/frontend/components/layout/Navbar.tsx
  - phase3-todo-ai-chatbot/frontend/components/layout/Footer.tsx
  - phase3-todo-ai-chatbot/frontend/components/layout/DashboardSidebar.tsx
  - phase3-todo-ai-chatbot/frontend/app/auth/layout.tsx
  - phase2-todo-web/frontend/app/layout.tsx
  - phase2-todo-web/frontend/components/layout/Navbar.tsx
  - phase2-todo-web/frontend/components/layout/Footer.tsx
  - phase2-todo-web/frontend/components/layout/DashboardSidebar.tsx
  - phase2-todo-web/frontend/app/auth/layout.tsx
  - phase2-todo-web/frontend/app/page.tsx
tests:
  - null
---

## Prompt

change all TodoEvo to TodoBoard

## Response snapshot

I have updated the codebase to replace "TodoEvo" with "TodoBoard" across multiple frontend files in both Phase 2 and Phase 3 directories. This included metadata titles, brand labels in layouts, and legal documents.

## Outcome

- ✅ Impact: Successfully rebranded the application to TodoBoard.
- 🧪 Tests: No functional tests run, verified content change via file reading.
- 📁 Files: Updated 14 files across phase 2 and phase 3 frontend directories.
- 🔁 Next prompts: none
- 🧠 Reflection: The replacement was straightforward as it primarily affected UI labels and metadata.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): null
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): null
