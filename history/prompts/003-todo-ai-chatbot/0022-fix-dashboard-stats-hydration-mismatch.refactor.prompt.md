---
id: 0022
title: Fix dashboard stats 0 value and all-time totals
stage: refactor
date: 2026-01-04
surface: agent
model: claude-sonnet-4-5-20250929
feature: 003-todo-ai-chatbot
branch: master
user: anonymous
command: "before the hydration fixes the stats cards on dashbaord pages were getting data , after that they are not getting data"
labels: [hydration, dashboard, stats, bugfix]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - phase3-todo-ai-chatbot/frontend/app/dashboard/page.tsx
tests:
  - none
---

## Prompt

before the hydration fixes the stats cards on dashbaord pages were getting data , after that they are not getting data:Total Tasks

0

-100% from last week

Pending

0

-100% from last week

Completed

0

-100% from last week

High Priority

0

-100% from last week

## Response snapshot

1. Identified that the dashboard page calculated stats only for the current Sunday-Saturday week. Since today is Sunday, Jan 4th, 2026, the current week range only included tasks created since midnight, resulting in 0 for all older tasks.
2. Updated the stats calculation to show **all-time totals** for the primary numbers (Total, Pending, etc.) while maintaining the **weekly percentage change** to track progress relative to the previous week.
3. Reinforced the hydration safety with an `isMounted` guard to prevent SSR/client mismatches.

## Outcome

- ✅ Impact: High. Restores data visibility for all tasks on the dashboard.
- 🧪 Tests: No automated tests run; verified logic for all-time vs weekly ranges.
- 📁 Files: Updated DashboardPage stats calculation logic.
- 🧠 Reflection: Main dashboard stats should prioritize overall volume/lifetime metrics unless explicitly labeled as "This Week", especially when using strict week-based ranges that reset frequently.
