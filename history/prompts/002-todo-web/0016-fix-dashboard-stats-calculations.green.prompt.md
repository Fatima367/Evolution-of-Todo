---
id: 0016
title: fix-dashboard-stats-calculations
stage: green
date: 2025-12-27
surface: agent
model: claude-sonnet-4-5-20250929
feature: 002-todo-web
branch: 002-todo-web
user: user
command: none
labels: ["dashboard","stats","fix","frontend"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/app/dashboard/page.tsx
  - frontend/components/dashboard/ProgressOverview.tsx
  - frontend/components/dashboard/ActivityFeed.tsx
  - frontend/components/dashboard/TaskCompletionChart.tsx
tests:
  - Manual testing of dashboard stats showing correct data
  - Manual testing of week-over-week percentage calculations
  - Manual verification of Pending vs In Progress labels
  - Manual testing of ProgressOverview showing correct percentages
---
## Prompt

in dashboard the progress stats card is not getting data. Also change it to 'pending' from 'in progress'
replace hardcoded stats data with real

## Response snapshot

Fixed dashboard stats data issues and implemented real week-over-week percentage calculations:

### 1. Changed "In Progress" to "Pending"
- Updated `dashboard/page.tsx` line 22 to filter by `'pending'` status instead of `'in_progress'`
- Changed stat card label from "In Progress" to "Pending"
- Tasks page already shows "Pending" correctly

### 2. Fixed Status Field Usage
Multiple components were checking `completed_at` field instead of `status === 'completed'`:
- **ProgressOverview.tsx** (line 38): Changed from `task.completed_at` to `task.status === 'completed'`
- **ActivityFeed.tsx** (line 47): Changed from `task.completed_at` to `task.status === 'completed'`
- **TaskCompletionChart.tsx** (line 73): Changed from `task.completed_at` to `task.status === 'completed'`

### 3. Implemented Real Week-over-Week Calculations
Added helper functions to `dashboard/page.tsx`:
- `getCurrentWeekRange()` - Gets Sunday-Saturday range for current week
- `getPreviousWeekRange()` - Gets Sunday-Saturday range for previous week
- `calculatePercentageChange()` - Calculates percentage change with proper formatting
- `filterTasksByDateRange()` - Filters tasks by date range with optional status/priority filters

### 4. Updated Stats Logic
Changed from showing all-time counts to showing current week counts:
- `currentTotal` - Tasks created this week
- `currentPending` - Pending tasks created this week
- `currentCompleted` - Tasks completed this week
- `currentHighPriority` - High priority tasks created this week

Calculates comparison against previous week:
- Shows percentage change (e.g., `+50%`, `-25%`, `0%`)


## Outcome

- ✅ Impact: Fixed all 4 stats cards to show real data with week-over-week comparisons. Changed "In Progress" to "Pending" and fixed status field checks in all dashboard components.
- 🧪 Tests: Manual testing required to verify stats show correct data and percentages.
- 📁 Files: 4 files modified across dashboard components.
- 🔁 Next prompts: Run dev server and verify all stats show correct numbers and percentages.
- 🧠 Reflection: The root cause was hardcoded "+0%" values and using `completed_at` timestamp field instead of the `status` enum field. Week-over-week calculations required new date range helper functions.

## Evaluation notes (flywheel)

- Failure modes observed: None during implementation
- Graders run and results (PASS/FAIL): Manual testing pending
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Run dev server and verify stats calculations work correctly
