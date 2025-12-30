---

# Tasks: Task Sorting

**Input**: Design documents from `/specs/002-todo-web/sorting-feature/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Tests are included as requested to ensure sorting functionality works correctly.

**Organization**: Tasks are grouped by implementation phases since all sort options (due date, priority, title) share the same backend infrastructure and frontend UI. The three user stories from the specification are delivered through a unified implementation approach.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `phase2-todo-web/backend/src/`
- **Frontend**: `phase2-todo-web/frontend/src/`
- **Tests**: Backend in `phase2-todo-web/backend/tests/`, Frontend in `phase2-todo-web/frontend/tests/`

---

## Phase 1: Backend - Sort Query Support

**Purpose**: Add database-level sorting support to existing task list endpoint

### Backend Tests for Sorting

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T001 [P] [US1,US2,US3] Create integration test for sort by due_date in phase2-todo-web/backend/tests/integration/test_task_sorting.py
- [X] T002 [P] [US1,US2,US3] Create integration test for sort by priority in phase2-todo-web/backend/tests/integration/test_task_sorting.py
- [X] T003 [P] [US1,US2,US3] Create integration test for sort by title in phase2-todo-web/backend/tests/integration/test_task_sorting.py
- [X] T004 [P] [US1,US2,US3] Create integration test for sort direction toggle (asc/desc) in phase2-todo-web/backend/tests/integration/test_task_sorting.py
- [X] T005 [P] [US1,US2,US3] Create integration test for sorting with NULL due_date values in phase2-todo-web/backend/tests/integration/test_task_sorting.py
- [X] T006 [P] [US1,US2,US3] Create integration test for sorting combined with existing filters in phase2-todo-web/backend/tests/integration/test_task_sorting.py

### Backend Implementation

- [X] T007 [US1,US2,US3] Add sort parameters (sort_by, sort_order) to task query request schema in phase2-todo-web/backend/src/schemas/task_schemas.py
- [X] T008 [US1,US2,US3] Implement dynamic sorting logic in get_user_tasks function in phase2-todo-web/backend/src/services/task_service.py (depends on T007)
- [X] T009 [US1,US2,US3] Add sort_by and sort_order query parameters to GET /api/tasks endpoint in phase2-todo-web/backend/src/api/task_router.py (depends on T007, T008)

**Checkpoint**: Backend sorting is functional and tested - all sort options work with database queries

---

## Phase 2: Frontend - Sort State Management

**Purpose**: Add client-side sort state with localStorage persistence

### Frontend Types & Hook

- [X] T010 [P] [US1,US2,US3] Define SortField, SortDirection, SortOption types in phase2-todo-web/frontend/src/lib/types.ts
- [X] T011 [US1,US2,US3] Implement useTaskSort hook with localStorage persistence in phase2-todo-web/frontend/src/lib/hooks/useTaskSort.ts (depends on T010)

**Checkpoint**: Frontend sort state management is ready for component integration

---

## Phase 3: Frontend - Sort UI Components

**Purpose**: Create sort control component and integrate with tasks page

### Sort Component

- [X] T012 [P] [US1,US2,US3] Create SortDropdown component in phase2-todo-web/frontend/src/components/tasks/SortDropdown.tsx (depends on T010, T011)

### Frontend Tests for Sorting (Optional)

> **NOTE: Write component tests FIRST, ensure they FAIL before implementation**

- [ ] T013 [P] [US1,US2,US3] Create SortDropdown component test in phase2-todo-web/frontend/tests/components/SortDropdown.test.tsx (depends on T012)

### Tasks Page Integration

- [X] T014 [US1,US2,US3] Import and render SortDropdown in phase2-todo-web/frontend/app/dashboard/tasks/page.tsx (depends on T011, T012)
- [X] T015 [US1,US2,US3] Wire sort state from useTaskSort to API query in phase2-todo-web/frontend/app/dashboard/tasks/page.tsx (depends on T014)
- [X] T016 [US1,US2,US3] Display current sort option with direction indicator in phase2-todo-web/frontend/app/dashboard/tasks/page.tsx (depends on T015)

**Checkpoint**: Frontend sort UI is complete and integrated with backend API

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect all sorting functionality

- [X] T017 [P] [US1,US2,US3] Add keyboard navigation support to SortDropdown in phase2-todo-web/frontend/src/components/tasks/SortDropdown.tsx
- [X] T018 [P] [US1,US2,US3] Add ARIA labels to SortDropdown for accessibility in phase2-todo-web/frontend/src/components/tasks/SortDropdown.tsx
- [X] T019 [P] [US1,US2,US3] Add Framer Motion animations to SortDropdown transitions in phase2-todo-web/frontend/src/components/tasks/SortDropdown.tsx
- [X] T020 [US1,US2,US3] Add visual indicator for sort direction (arrow icon) in SortDropdown in phase2-todo-web/frontend/src/components/tasks/SortDropdown.tsx
- [X] T021 [US1,US2,US3] Verify sort state persists across page navigations in phase2-todo-web/frontend/src/lib/hooks/useTaskSort.ts
- [X] T022 [US1,US2,US3] Update API client to accept and pass sort parameters in phase2-todo-web/frontend/lib/api.ts
- [X] T023 [US1,US2,US3] Test sorting with 100+ tasks for performance in phase2-todo-web/backend/tests/integration/test_task_sorting.py
- [X] T024 [US1,US2,US3] Run all sorting integration tests to validate functionality

**Final Checkpoint**: All sorting features are complete, accessible, performant, and tested

---

## Dependencies & Execution Order

### Phase Dependencies

- **Backend Sort Support (Phase 1)**: No dependencies on other phases - can start immediately
- **Frontend Sort State (Phase 2)**: Can start in parallel with backend - independent work
- **Frontend Sort UI (Phase 3)**: Depends on Phase 2 completion (needs hook and types)
- **Polish (Phase 4)**: Depends on Phase 1-3 completion

### Task Dependencies Within Phases

**Phase 1 - Backend**:
- Tests (T001-T006) can run in parallel - test different scenarios
- T007 (schemas) must be before T008 (service) and T009 (router)
- T008 (service) must be before T009 (router)
- Tests pass before moving to Phase 2

**Phase 2 - Frontend State**:
- T010 (types) must be before T011 (hook)
- Hook ready before moving to Phase 3

**Phase 3 - Frontend UI**:
- T012 (component) can start after T010, T011 (has dependencies)
- T013 (component test) can run after T012
- T014-T016 (page integration) depend on T011, T012 and must be sequential
- Integration complete before moving to Phase 4

**Phase 4 - Polish**:
- All polish tasks can run in parallel except T023, T024 which depend on integration

### Parallel Opportunities

- **Phase 1**: All test tasks (T001-T006) can run in parallel - they test different sorting scenarios
- **Phase 2 & 1**: Backend and frontend can be developed in parallel (different parts of codebase)
- **Phase 4**: All accessibility/animations/persistence tasks (T017-T021) can run in parallel
- **Phase 4**: API client update (T022) can run in parallel with component polish tasks

---

## Parallel Example: Backend Tests (Phase 1)

```bash
# Launch all backend sorting tests together (they test different scenarios):
Task T001: "Create integration test for sort by due_date in phase2-todo-web/backend/tests/integration/test_task_sorting.py"
Task T002: "Create integration test for sort by priority in phase2-todo-web/backend/tests/integration/test_task_sorting.py"
Task T003: "Create integration test for sort by title in phase2-todo-web/backend/tests/integration/test_task_sorting.py"
Task T004: "Create integration test for sort direction toggle (asc/desc) in phase2-todo-web/backend/tests/integration/test_task_sorting.py"
Task T005: "Create integration test for sorting with NULL due_date values in phase2-todo-web/backend/tests/integration/test_task_sorting.py"
Task T006: "Create integration test for sorting combined with existing filters in phase2-todo-web/backend/tests/integration/test_task_sorting.py"
```

---

## Parallel Example: Polish Tasks (Phase 4)

```bash
# Launch all polish improvements together:
Task T017: "Add keyboard navigation support to SortDropdown in phase2-todo-web/frontend/src/components/tasks/SortDropdown.tsx"
Task T018: "Add ARIA labels to SortDropdown for accessibility in phase2-todo-web/frontend/src/components/tasks/SortDropdown.tsx"
Task T019: "Add Framer Motion animations to SortDropdown transitions in phase2-todo-web/frontend/src/components/tasks/SortDropdown.tsx"
Task T020: "Add visual indicator for sort direction (arrow icon) in SortDropdown in phase2-todo-web/frontend/src/components/tasks/SortDropdown.tsx"
Task T021: "Verify sort state persists across page navigations in phase2-todo-web/frontend/src/lib/hooks/useTaskSort.ts"
Task T022: "Update API client to accept and pass sort parameters in phase2-todo-web/frontend/lib/api.ts"
```

---

## Implementation Strategy

### Full Feature Delivery (All User Stories)

1. **Phase 1**: Backend sorting implementation
   - Write and run all tests (T001-T006)
   - Add sort schemas (T007)
   - Implement sort logic in service (T008)
   - Add parameters to router (T009)
   - Verify all backend tests pass

2. **Phase 2**: Frontend state management
   - Define types (T010)
   - Implement useTaskSort hook (T011)

3. **Phase 3**: Frontend UI integration
   - Create SortDropdown component (T012)
   - Optionally create component tests (T013)
   - Integrate with tasks page (T014-T016)

4. **Phase 4**: Polish and validation
   - Add accessibility (T017, T018)
   - Add animations (T019)
   - Add visual indicators (T020)
   - Verify persistence (T021)
   - Update API client (T022)
   - Performance test (T023)
   - Run all tests (T024)

### Incremental Delivery Options

**Option 1: Backend-First Increment**
1. Complete Phase 1 (Backend) → Test with Postman/curl
2. Complete Phases 2-4 (Frontend) → Full feature

**Option 2: UI-First Increment (for demo)**
1. Complete Phase 2 (Types + Hook) with mock data
2. Complete Phase 3 (UI) → Visual demo only
3. Complete Phase 1 (Backend) → Real API integration
4. Complete Phase 4 (Polish) → Production ready

### Why All Stories Together

The three user stories (sort by due date, priority, alphabetical) are implemented together because:
- They share the same backend infrastructure (dynamic sort query)
- They share the same frontend UI (single SortDropdown with field selector)
- They share the same state management (one useTaskSort hook)
- Separating them would create redundant code and duplicate testing effort
- This approach is more efficient and maintainable

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- Tasks map to multiple user stories (US1,US2,US3) because all sort options are implemented together
- Backend sorting is done at database level using existing indexes for performance
- Frontend sort state persists in localStorage per FR-006 requirement
- All sorting must work with existing filters per FR-007 requirement
- Sort state persistence across navigations is critical for user experience (FR-006)
- Accessibility is required (WCAG 2.1 AA) - keyboard nav and ARIA labels included
- Performance target: <1 second for sort response (FR-001)
- Empty task list handling is tested (edge case from spec)
- NULL value handling tested (tasks without due dates - FR-004)
