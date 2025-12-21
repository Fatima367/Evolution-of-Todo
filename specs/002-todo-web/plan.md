# Implementation Plan: Todo Full-Stack Web Application

**Branch**: `002-todo-web` | **Date**: 2025-12-21 | **Spec**: [spec.md](/specs/002-todo-web/spec.md)
**Input**: Feature specification from `/specs/002-todo-web/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implementation of a multi-user, full-stack web application with persistent storage, user authentication, and responsive UI. The solution follows the Phase II architecture as defined in the constitution, using Next.js 16+ with App Router for the frontend, FastAPI with SQLModel ORM for the backend, and Neon Serverless PostgreSQL for persistent storage. User authentication is implemented with Better Auth using JWT tokens to ensure secure session management and proper data isolation between users. The application will support all CRUD operations for tasks with additional features like priorities, tags, due dates, and responsive design to meet WCAG 2.1 AA compliance standards.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.13+ (Backend), TypeScript/JavaScript (Frontend)
**Primary Dependencies**: Next.js 16+ (Frontend), FastAPI (Backend), SQLModel ORM, Neon Serverless PostgreSQL, Better Auth
**Storage**: Neon Serverless PostgreSQL database with SQLModel ORM
**Testing**: pytest (Backend), Jest/React Testing Library (Frontend)
**Target Platform**: Web application (responsive, mobile/tablet/desktop compatible)
**Project Type**: Full-stack web application (frontend + backend)
**Performance Goals**: <500ms API response time (p95), <3 seconds Time to Interactive on mobile
**Constraints**: Free tier usage limits, JWT-based authentication, user data isolation, WCAG 2.1 AA compliance
**Scale/Scope**: Multi-user support, responsive UI, persistent storage

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### SDD Compliance Check
- ✅ Spec exists at `/specs/002-todo-web/spec.md` with user scenarios and requirements
- ✅ Following Phase II (Full-stack web) as required after Phase I completion
- ✅ Feature completeness: Basic (CRUD), Intermediate (priorities, tags, due dates), Advanced features planned

### Architecture Compliance Check
- ✅ Multi-user authentication enforced via Better Auth with JWT tokens (FR-010)
- ✅ User isolation via user_id filtering in database queries (FR-007, FR-009)
- ✅ Stateless server design with JWT for session management (Constitution VII.121-125)
- ✅ Explicit data ownership with user_id on all entities (Constitution VII.127-131)
- ✅ Clear service boundaries: Backend API (FastAPI) + Frontend SPA (Next.js) (Constitution VII.133-137)

### Technology Stack Alignment
- ✅ Next.js 16+ with App Router for frontend (meets responsive UI requirement FR-012)
- ✅ FastAPI with SQLModel ORM for backend (meets API and database requirements)
- ✅ Neon Serverless PostgreSQL for persistent storage (FR-008)
- ✅ Better Auth for user authentication (FR-001, FR-002, FR-010)

### Security & Hardening Compliance
- ✅ JWT-based authentication with user context extraction (FR-010)
- ✅ Input validation via Pydantic models (FR-011)
- ✅ No hardcoded credentials/secrets (Constitution VII.166)
- ✅ User data isolation enforced at database query level (FR-007)

### Performance & Quality Standards
- ✅ Target <500ms API response time (p95) (Constitution VII.97)
- ✅ Responsive UI with mobile support (FR-012, Constitution VII.102)
- ✅ WCAG 2.1 AA compliance (Constitution VII.103)
- ✅ Strict typing with TypeScript interfaces and Pydantic models (Constitution VII.154-156)

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
phase2-todo-web/
├── backend/
│   ├── src/
│   │   ├── models/
│   │   │   ├── user.py          # User entity with authentication fields
│   │   │   └── task.py          # Task entity with user relationship
│   │   ├── schemas/             # Pydantic models for API validation
│   │   │   ├── user_schemas.py
│   │   │   └── task_schemas.py
│   │   ├── api/
│   │   │   ├── auth_router.py   # Authentication endpoints
│   │   │   └── task_router.py   # Task management endpoints
│   │   ├── services/
│   │   │   ├── auth_service.py  # Authentication business logic
│   │   │   └── task_service.py  # Task business logic
│   │   └── main.py              # FastAPI application entry point
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── contract/
│   ├── requirements.txt
│   └── alembic/
│       └── versions/            # Database migration files
│
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js App Router structure
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx         # Home/Dashboard page
│   │   │   ├── auth/
│   │   │   │   ├── login/
│   │   │   │   │   └── page.tsx
│   │   │   │   └── register/
│   │   │   │       └── page.tsx
│   │   │   └── tasks/
│   │   │       ├── page.tsx     # Tasks list page
│   │   │       └── [id]/
│   │   │           └── page.tsx # Individual task page
│   │   ├── components/
│   │   │   ├── ui/              # Reusable UI components (shadcn/ui)
│   │   │   ├── auth/
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   └── RegisterForm.tsx
│   │   │   ├── tasks/
│   │   │   │   ├── TaskList.tsx
│   │   │   │   ├── TaskItem.tsx
│   │   │   │   └── TaskForm.tsx
│   │   │   └── layout/
│   │   │       ├── Header.tsx
│   │   │       └── Sidebar.tsx
│   │   ├── lib/
│   │   │   ├── api.ts           # API service functions
│   │   │   ├── auth.ts          # Authentication utilities
│   │   │   └── types.ts         # TypeScript interfaces
│   │   ├── hooks/
│   │   │   ├── useAuth.ts       # Authentication hook
│   │   │   └── useTasks.ts      # Task management hook
│   │   └── styles/
│   │       └── globals.css      # Tailwind CSS configuration
│   ├── tests/
│   │   ├── unit/
│   │   └── e2e/
│   ├── package.json
│   ├── next.config.js
│   └── tailwind.config.js
├── docker-compose.yml           # For local development with Postgres
└── .env.example               # Environment variables template
```

**Structure Decision**: Full-stack web application with separate frontend (Next.js) and backend (FastAPI) following the constitution's clear service boundaries principle. This structure enables independent scaling, separate deployment, and clear separation of concerns between UI rendering and business logic.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
