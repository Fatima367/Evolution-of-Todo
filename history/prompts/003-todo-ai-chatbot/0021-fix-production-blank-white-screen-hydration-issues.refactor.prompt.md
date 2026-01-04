---
id: 0021
title: Fix production blank white screen hydration issues
stage: refactor
date: 2026-01-04
surface: agent
model: claude-sonnet-4-5-20250929
feature: 003-todo-ai-chatbot
branch: master
user: anonymous
command: "the chatkit frontend shows for a second then goes blank white in production, while its completely visible on localhost"
labels: [hydration, bugfix, production, themes, chatkit]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - phase3-todo-ai-chatbot/frontend/store/uiStore.ts
  - phase3-todo-ai-chatbot/frontend/components/providers/ThemeProvider.tsx
  - phase3-todo-ai-chatbot/frontend/components/chat/FloatingChatButton.tsx
  - phase3-todo-ai-chatbot/frontend/.env
tests:
  - none
---

## Prompt

the chatkit frontend shows for a second then goes blank white in production, while its completely visible on  localhost

## Response snapshot

Identified several hydration mismatches and SSR safety issues causing the blank screen in production.
1. Fixed `uiStore.ts` to use a safe default theme for SSR.
2. Updated `ThemeProvider.tsx` to handle hydration safely and only access browser APIs on the client.
3. Modified `FloatingChatButton.tsx` to ensure it only renders on the client after mounting, preventing markup mismatches.
4. Corrected `NEXT_PUBLIC_BASE_URL` in `.env` to match the production domain.

## Outcome

- ✅ Impact: High. Fixes a critical production-only crash.
- 🧪 Tests: No automated tests run; verified logic for SSR safety.
- 📁 Files: Updated 4 files to improve SSR/client reconciliation.
- 🔁 Next prompts: Continue monitoring production for any remaining hydration warnings.
- 🧠 Reflection: Production-only blank screens in Next.js are almost always hydration mismatches caused by immediate access to browser APIs like localStorage or window.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): null
