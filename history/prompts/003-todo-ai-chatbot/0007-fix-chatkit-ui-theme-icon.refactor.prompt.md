---
id: 0007
title: Fix chatkit UI theme and icon
stage: refactor
date: 2025-12-29
surface: agent
model: claude-sonnet-4-5-20250929
feature: 003-todo-ai-chatbot
branch: 003-todo-ai-chatbot
user: User
command: fix chatkit UI - theme not working, use paper plane icon
labels: ["frontend", "chatkit", "theme", "ui-fix"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - phase3-todo-ai-chatbot/frontend/components/chat/FloatingChatButton.tsx
tests: []
---

## Prompt

the chatkit UI is not as dashboard page and tasks page, also dark and light mode not working on it, use mcp server to see chatkit docs.

## Response snapshot

Fixed the ChatKit UI by:
1. Added theme integration using `useUIStore` to track light/dark mode
2. Made chat popup colors theme-aware with conditional styling for light mode (white bg) and dark mode (dark blue bg)
3. Updated themeConfig to dynamically switch between light and dark color schemes based on app theme
4. Replaced the up arrow icon with a proper paper plane SVG icon inline
5. Simplified the icon replacement logic and cleaned up CSS

## Outcome

- ✅ Impact: ChatKit UI now properly responds to dark/light mode changes
- 🧪 Tests: No tests added
- 📁 Files: Modified 1 file (FloatingChatButton.tsx)
- 🔁 Next prompts: None
- 🧠 Reflection: The chat component was already integrated globally in layout.tsx, so it appears on both dashboard and tasks pages. The issue was that it wasn't theme-aware and the icon replacement was using a workaround with emoji instead of proper SVG.
