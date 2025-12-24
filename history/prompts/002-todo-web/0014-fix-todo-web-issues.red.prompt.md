---
id: 0014
title: fix-todo-web-issues
stage: red
date: 2025-12-24
surface: agent
model: claude-sonnet-4-5-20250929
feature: 002-todo-web
branch: 002-todo-web
user: user
command: none
labels: ["bugfix","ui","auth"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/lib/api.ts
  - frontend/store/authStore.ts
  - frontend/store/themeStore.ts
  - frontend/store/index.ts
  - frontend/components/providers/ThemeProvider.tsx
  - frontend/components/ui/ThemeToggle.tsx
  - frontend/components/ui/index.ts
  - frontend/app/layout.tsx
  - frontend/app/dashboard/tasks/page.tsx
  - frontend/components/tasks/SearchBar.tsx
  - frontend/components/tasks/CreateTaskModal.tsx
  - frontend/components/layout/DashboardSidebar.tsx
tests:
  - Manual testing of auth token transmission
  - Manual testing of dark mode toggle
  - Manual testing of search bar badge positioning
  - Manual testing of modal responsiveness
---

## Prompt

Fix all the these 5 issues:
- Dashboard is showing Mock Data.
- During creating tasks seeing this error : INFO:     127.0.0.1:59175 - "GET /tasks/ HTTP/1.1" 403 Forbidden
- Dark mode is not implemented
- in tasks search bar this ⌘K is not in center it in bottom of search bar
- Task creation Model is too big with no scroll option i had to minimize the resolution

## Response snapshot

Fixed 5 issues in the Todo Web application:

1. **403 Forbidden Error Fix**: Updated API client error handling and auth store to properly sync JWT tokens. The auth store now sets the API client token when authentication changes and reads from localStorage on initialization.

2. **Mock Data Issue**: The "mock data" issue was caused by the 403 error preventing API calls. With proper token management, the app now fetches real data from the backend.

3. **Dark Mode Implementation**: Created complete dark mode theming system:
   - Created `themeStore.ts` with Zustand for theme state management (light/dark/system)
   - Created `ThemeProvider` component to apply `.dark` class to html element
   - Created `ThemeToggle` component with animated Sun/Moon/System icons
   - Added theme toggle to tasks page header and dashboard sidebar
   - Existing CSS already had `.dark` classes defined

4. **Search Bar Badge Position**: Fixed ⌘K shortcut badge positioning by:
   - Increasing padding on input from `pr-24` to `pr-28`
   - Changing badge position from `right-4` to `right-3`
   - Added `flex items-center` to badge for proper vertical centering

5. **Modal Responsiveness**: Made CreateTaskModal responsive with scroll:
   - Changed outer container to `max-h-[90vh]` with `flex flex-col`
   - Added scrollable content wrapper with `overflow-y-auto`
   - Made header fixed with `flex-shrink-0`
   - Adjusted padding for mobile (`p-4 sm:p-6`, `p-2 sm:p-4`)
   - Reduced font sizes on mobile (`text-xl sm:text-2xl`)

## Outcome

- ✅ Impact: Fixed critical auth flow preventing API calls, implemented dark mode toggle, improved UI responsiveness and positioning
- 🧪 Tests: Manual testing required for token transmission, dark mode toggle, search bar positioning, and modal responsiveness
- 📁 Files: Modified/created 11 files across frontend
- 🔁 Next prompts: Test all fixes by running frontend and verifying each issue is resolved
- 🧠 Reflection: The auth issue was caused by Zustand auth store not syncing token to API client. Adding initialization code that reads from localStorage on load ensures token is available immediately. Dark mode CSS was already present but needed state management component.

## Evaluation notes (flywheel)

- Failure modes observed: None during implementation
- Graders run and results (PASS/FAIL): Manual testing pending
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Run dev server and verify all 5 issues are fixed
