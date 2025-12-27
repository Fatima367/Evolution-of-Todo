# Implementation Plan: Task Sorting

**Branch**: `002-todo-web` | **Date**: 2025-12-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/002-todo-web/sorting-feature/spec.md`

**Note**: This is a sub-feature of 002-todo-web that adds sorting capabilities to the existing task management system.

## Summary

Implementation of task sorting functionality allowing users to reorder their task lists by due date, priority, or alphabetical order. The feature will add both backend support for sorting queries and frontend UI controls for selecting and applying sort options. This is an enhancement to the existing task management system that improves task organization and productivity by providing multiple sorting perspectives.

## Technical Context

**Language/Version**: Python 3.13+ (Backend), TypeScript/JavaScript (Frontend)
**Primary Dependencies**: Next.js 16+ (Frontend), FastAPI (Backend), SQLModel ORM, Neon Serverless PostgreSQL, Zustand (state), Framer Motion (animations)
**Storage**: Neon Serverless PostgreSQL - existing tasks table with indexed fields (due_date, priority, title)
**Testing**: pytest (Backend), Jest/React Testing Library (Frontend)
**Target Platform**: Web application with responsive design (mobile <768px, tablet 768-1024px, desktop >1024px using Tailwind breakpoints: sm/md/lg/xl)
**Project Type**: Full-stack web application enhancement (frontend + backend modifications)
**Performance Goals**: <500ms API response time (p95) with sorting queries, <1 second frontend sort UI response
**Constraints**: Must integrate with existing task filters, maintain user data isolation, WCAG 2.1 AA compliance
**Scale/Scope**: Enhancement for multi-user task management system, works with existing 100+ task datasets
**Operational Parameters**:
- Sort options: due_date, priority, title (alphabetical)
- Sort directions: ascending, descending
- Sort state persistence: local storage (Zustand store)
- Combined with existing filters: apply sort after filter operation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### SDD Compliance Check
- ✅ Spec exists at `specs/002-todo-web/sorting-feature/spec.md` with user scenarios and requirements
- ✅ Following Phase II (Full-stack web) enhancement to existing task system
- ✅ Feature completeness: Implements Intermediate feature (sort) as specified in constitution

### Architecture Compliance Check
- ✅ Multi-user authentication enforced via existing Better Auth with JWT tokens (no changes needed)
- ✅ User isolation via user_id filtering preserved in sorting logic
- ✅ Stateless server design maintained (sorting is request-side or client-side state)
- ✅ Explicit data ownership with user_id on all task entities (existing)
- ✅ Clear service boundaries: Backend API (FastAPI) sorting + Frontend SPA (Next.js) UI controls

### Technology Stack Alignment
- ✅ Next.js 16+ with App Router for frontend sort UI components
- ✅ FastAPI with SQLModel ORM for backend sort query support
- ✅ Neon Serverless PostgreSQL with indexed fields (due_date, priority, title)
- ✅ Zustand for client-side sort state management

### Security & Hardening Compliance
- ✅ JWT-based authentication preserved (no changes to auth flow)
- ✅ Input validation via Pydantic models maintained
- ✅ No hardcoded credentials/secrets
- ✅ User data isolation enforced - sorting only applies to user's own tasks

### Performance & Quality Standards
- ✅ Target <500ms API response time with sorting (indexed fields ensure fast queries)
- ✅ Responsive UI with mobile support for sort controls
- ✅ WCAG 2.1 AA compliance for sort accessibility (keyboard navigation, ARIA labels)
- ✅ Strict typing with TypeScript interfaces and Pydantic models

## Project Structure

### Documentation (this feature)

```text
specs/002-todo-web/sorting-feature/
├── spec.md              # Feature specification (already created)
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── task-sorting-api.yaml
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root - modifications to existing structure)

```text
phase2-todo-web/
├── backend/
│   ├── src/
│   │   ├── models/
│   │   │   └── task.py              # No changes - fields already indexed
│   │   ├── schemas/
│   │   │   └── task_schemas.py     # Add sort option schemas
│   │   ├── services/
│   │   │   └── task_service.py      # Add sorting logic to queries
│   │   └── api/
│   │       └── task_router.py        # Add sort parameters to GET /api/tasks
│   └── tests/
│       └── integration/
│           └── test_task_sorting.py  # New tests for sorting
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   └── tasks/
    │   │       ├── SortDropdown.tsx    # New sort control component
    │   │       └── TaskList.tsx       # Modify to use sort state
    │   ├── lib/
    │   │   └── hooks/
    │   │       └── useTaskSort.ts    # New hook for sort state management
    │   └── store/
    │       └── uiStore.ts             # Add sort state (or use local hook)
    └── tests/
        └── components/
            └── SortDropdown.test.tsx   # New component tests
```

**Structure Decision**: This is an enhancement feature that modifies existing files rather than creating new project structure. The sorting functionality integrates with the existing task management system, requiring:
- Backend: Add query parameters to existing task list endpoint
- Frontend: Add sort control UI and state management to tasks page
- No new tables or major architectural changes needed

## Complexity Tracking

> No constitution violations - all gates passed

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

---

## Phase 0: Research & Analysis

### Research Findings

**Backend Sorting Strategy**:
- SQLModel/SQLAlchemy supports dynamic ordering via `order_by()` with field names as strings
- Neon PostgreSQL has existing indexes on `due_date`, `priority`, and `title` fields
- Sorting should be done at database level for efficiency (not in-memory)
- Must handle NULL values (tasks without due dates) - PostgreSQL default behavior places NULL last in ascending order

**Frontend Sort State Management**:
- Options:
  1. Zustand store (global state across pages)
  2. Local hook with localStorage persistence
  3. URL query parameters (shareable sort state)
- **Decision**: Use custom hook with localStorage for simplicity and persistence, consider URL params later if shareability needed

**UI/UX Design Patterns**:
- Sort control should be a dropdown with:
  - Sort by field selector (Due Date, Priority, Title)
  - Direction toggle (Ascending/Descending) with visual indicator (arrow icon)
- Should integrate with existing FilterDropdown component patterns
- Animation: Use Framer Motion for dropdown transitions
- Accessibility: Keyboard navigation, ARIA labels, visible focus states

**Integration with Existing Filters**:
- Current filter implementation uses `useTaskFilters` hook
- Sort should apply AFTER filtering to maintain performance
- Filter and sort state should be independent but composable

---

## Phase 1: Design & Contracts

### Data Model Changes

**Backend (No schema changes needed)**:

The existing `Task` model already has all required fields with indexes:

```python
class Task(SQLModel, table=True):
    # ... existing fields ...
    title: str = Field(min_length=1, max_length=200, nullable=False)  # Already indexed for sort
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, nullable=False, index=True)  # Indexed
    due_date: Optional[datetime] = Field(default=None, index=True)  # Indexed
```

**Frontend Types**:

```typescript
// New sort-related types
type SortField = 'due_date' | 'priority' | 'title';
type SortDirection = 'asc' | 'desc';

interface SortOption {
  field: SortField;
  direction: SortDirection;
}

interface SortConfig {
  label: string;
  value: SortField;
  icon: LucideIcon;
  defaultDirection: SortDirection;
}
```

### API Contracts

#### Enhanced GET /api/tasks Endpoint

**Existing Request Parameters** (preserve):
- `status`: Filter by task status
- `priority`: Filter by priority level
- `tags`: Filter by tags
- `search`: Search query

**New Request Parameters**:
```yaml
sort_by:
  type: string
  enum: ["due_date", "priority", "title"]
  description: Field to sort tasks by
  default: "created_at"
  required: false

sort_order:
  type: string
  enum: ["asc", "desc"]
  description: Sort direction (ascending or descending)
  default: "desc"
  required: false
```

**Response Format** (unchanged):
```yaml
type: array
items:
  type: object
  properties:
    id: string
    title: string
    description: string
    status: string
    priority: string
    due_date: string (ISO 8601 or null)
    tags: array of strings
    created_at: string (ISO 8601)
    updated_at: string (ISO 8601)
    completed_at: string (ISO 8601 or null)
```

**OpenAPI Contract**: See `contracts/task-sorting-api.yaml`

### Frontend Components

**New Component: SortDropdown**
- Props: `onSortChange: (sort: SortOption) => void`, `currentSort: SortOption`
- UI: Dropdown with sort options, direction toggle arrow
- Animation: Framer Motion fade/slide
- Accessibility: Full keyboard support, ARIA labels

**Modified Component: TaskList**
- Props unchanged (receives sorted tasks from parent)
- No changes needed - renders tasks as-is

**Modified Component: tasks/page.tsx**
- Add SortDropdown next to FilterDropdowns
- Manage sort state with useTaskSort hook
- Pass sort parameters to API client

**New Hook: useTaskSort**
- State: `sort: SortOption` with localStorage persistence
- Methods: `setSort(field: SortField)`, `toggleDirection()`, `resetSort()`
- Computed: `sortLabel: string` for UI display

### Quick Start Guide

1. **Backend Integration**:
   - Modify `task_service.py` to accept `sort_by` and `sort_order` parameters
   - Update `GET /api/tasks` endpoint in `task_router.py` to pass sort parameters
   - Add integration tests for sorting edge cases

2. **Frontend Integration**:
   - Create `SortDropdown.tsx` component following FilterDropdown pattern
   - Create `useTaskSort.ts` hook with localStorage persistence
   - Update `tasks/page.tsx` to add SortDropdown and pass sort params to API
   - Add sort state to task list query (React Query)

3. **Testing**:
   - Test each sort option (due_date, priority, title)
   - Test direction toggle (asc/desc)
   - Test sorting with active filters
   - Test edge cases (empty list, tasks with null due dates, identical values)

---

## Constitution Check (Post-Design)

*Re-evaluating gates after Phase 1 design*

### SDD Compliance Check
- ✅ Design aligns with spec requirements
- ✅ No breaking changes to existing functionality
- ✅ Incremental enhancement approach

### Architecture Compliance Check
- ✅ Stateless server maintained (sorting is query-based)
- ✅ Clear separation: Backend handles query sorting, frontend manages UI state
- ✅ Existing user isolation preserved

### Performance & Quality Standards
- ✅ Database indexes ensure <500ms response time for sorting
- ✅ Responsive UI with mobile support
- ✅ WCAG 2.1 AA compliance planned (keyboard nav, ARIA)

**All gates passed - ready for task generation**
