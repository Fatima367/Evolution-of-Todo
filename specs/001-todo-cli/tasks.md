---
description: "Task list for Todo CLI Application implementation"
---

# Tasks: Todo CLI Application

**Input**: Design documents from `/specs/001-todo-cli/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan in src/
- [ ] T002 Initialize Python project with uv and dependencies in pyproject.toml
- [ ] T003 [P] Install SQLModel, rich, and inquirer-python dependencies
- [ ] T004 Create src/models/, src/services/, src/cli/, and src/lib/ directories

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Create Task model with SQLModel in src/models/task.py following data model specification
- [ ] T006 [P] Create PriorityEnum and StatusEnum in src/models/task.py
- [ ] T007 [P] Create database engine setup with SQLite in src/models/task.py (memory for Phase I)
- [ ] T008 Create TodoApp service class in src/services/todo_service.py with basic structure
- [ ] T009 [P] Create utility functions for input validation in src/lib/utils.py
- [ ] T010 [P] Create helper functions for formatting and display in src/lib/utils.py
- [ ] T011 Setup basic CLI structure with rich formatting in src/cli/main.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Initialize Todo CLI with Menu (Priority: P1) 🎯 MVP

**Goal**: A user opens the terminal and runs the todo CLI application. The app displays a colorful menu with options to view, add, update, mark, and delete tasks.

**Independent Test**: Can be fully tested by launching the CLI application and verifying the menu displays properly with available options.

### Implementation for User Story 1

- [ ] T012 [US1] Implement colorful menu display function in src/cli/main.py
- [ ] T013 [US1] Implement menu navigation and selection logic in src/cli/main.py
- [ ] T014 [US1] Create main application loop in src/cli/main.py
- [ ] T015 [US1] Add rich formatting and styling to menu interface in src/cli/main.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Add and View Tasks (Priority: P1)

**Goal**: A user adds a new task with a title, optional description, and priority level. The user can then view all tasks in a color-coded table format.

**Independent Test**: Can be fully tested by adding a task and then viewing it in the task list.

### Implementation for User Story 2

- [ ] T016 [P] [US2] Implement add_task method in src/services/todo_service.py
- [ ] T017 [P] [US2] Implement validation for task title (1-200 chars) in src/lib/utils.py
- [ ] T018 [P] [US2] Implement validation for task description (max 500 chars) in src/lib/utils.py
- [ ] T019 [P] [US2] Implement validation for priority (Low/Medium/High) in src/lib/utils.py
- [ ] T020 [US2] Implement view_tasks method in src/services/todo_service.py
- [ ] T021 [US2] Create formatted table display for tasks in src/lib/utils.py
- [ ] T022 [US2] Integrate add_task functionality with CLI menu in src/cli/main.py
- [ ] T023 [US2] Integrate view_tasks functionality with CLI menu in src/cli/main.py
- [ ] T024 [US2] Add success/error messages for add/view operations in src/cli/main.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Update and Mark Tasks (Priority: P2)

**Goal**: A user updates an existing task by providing its ID and new title/description. A user can also mark tasks with different statuses.

**Independent Test**: Can be fully tested by updating a task and verifying the changes are reflected, or changing task status and seeing the update.

### Implementation for User Story 3

- [ ] T025 [P] [US3] Implement update_task method in src/services/todo_service.py
- [ ] T026 [P] [US3] Implement mark_task method in src/services/todo_service.py
- [ ] T027 [P] [US3] Implement validation for task ID existence in src/lib/utils.py
- [ ] T028 [US3] Implement validation for status (Pending/In-Progress/Completed) in src/lib/utils.py
- [ ] T029 [US3] Integrate update_task functionality with CLI menu in src/cli/main.py
- [ ] T030 [US3] Integrate mark_task functionality with CLI menu in src/cli/main.py
- [ ] T031 [US3] Add error handling for invalid task IDs in src/services/todo_service.py

**Checkpoint**: At this point, User Stories 1, 2 AND 3 should all work independently

---

## Phase 6: User Story 4 - Delete Tasks (Priority: P2)

**Goal**: A user removes unwanted tasks by providing the task ID. The system confirms deletion and removes the task permanently.

**Independent Test**: Can be fully tested by deleting a task and verifying it no longer appears in the task list.

### Implementation for User Story 4

- [ ] T032 [US4] Implement delete_task method in src/services/todo_service.py
- [ ] T033 [US4] Integrate delete_task functionality with CLI menu in src/cli/main.py
- [ ] T034 [US4] Add confirmation prompts for task deletion in src/cli/main.py
- [ ] T035 [US4] Add success/error messages for delete operations in src/cli/main.py

**Checkpoint**: At this point, User Stories 1, 2, 3 AND 4 should all work independently

---

## Phase 7: User Story 5 - Persistence with SQLModel (Priority: P3)

**Goal**: Tasks are saved locally using SQLModel and persist between application sessions. The data survives app restarts.

**Independent Test**: Can be tested by adding tasks, closing the app, restarting it, and verifying tasks are still available.

### Implementation for User Story 5

- [ ] T036 [US5] Modify database connection to use file-based SQLite (sqlite:///todo.db) in src/models/task.py
- [ ] T037 [US5] Update all CRUD operations in src/services/todo_service.py to use persistent storage
- [ ] T038 [US5] Implement first-run logic to create default task "[User's Name]'s first todo" in src/services/todo_service.py
- [ ] T039 [US5] Test persistence by restarting application and verifying tasks remain in src/cli/main.py

**Checkpoint**: All user stories should now be independently functional with persistent storage

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T040 [P] Add comprehensive error handling and exit codes (2 for validation errors) in src/cli/main.py
- [ ] T041 [P] Implement edge case handling (empty task list, invalid inputs) in src/services/todo_service.py
- [ ] T042 [P] Add input sanitization and security validation in src/lib/utils.py
- [ ] T043 [P] Improve UI/UX with better color schemes and formatting in src/cli/main.py
- [ ] T044 [P] Add graceful shutdown handling in src/cli/main.py
- [ ] T045 [P] Add logging functionality for debugging in src/lib/utils.py
- [ ] T046 Run quickstart.md validation to ensure all functionality works as expected

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 5 (P3)**: Can start after Foundational (Phase 2) - Depends on previous stories for testing

### Within Each User Story

- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 2

```bash
# Launch all validation functions for User Story 2 together:
Task: "Implement validation for task title (1-200 chars) in src/lib/utils.py"
Task: "Implement validation for task description (max 500 chars) in src/lib/utils.py"
Task: "Implement validation for priority (Low/Medium/High) in src/lib/utils.py"

# Launch all service methods for User Story 2 together:
Task: "Implement add_task method in src/services/todo_service.py"
Task: "Implement view_tasks method in src/services/todo_service.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. Complete Phase 4: User Story 2
5. **STOP and VALIDATE**: Test User Stories 1 & 2 independently
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
   - Developer D: User Story 4
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence