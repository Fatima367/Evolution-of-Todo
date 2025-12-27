---
id: 1
title: todo-web-specification
stage: spec
date: 2025-12-21
surface: agent
model: claude-sonnet-4-5-20250929
feature: todo-web
branch: 002-todo-web
user: claude
command: /sp.specify @specs.txt
labels: [specification, web-app, todo]
links:
  spec: specs/002-todo-web/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/002-todo-web/spec.md
 - specs/002-todo-web/checklists/requirements.md
tests:
 - null
---

## Prompt

# **Phase II: Todo Full-Stack Web Application**

## **1. Overview & Objectives**

**Objective:** Transform the console app into a modern, multi-user, full-stack web application with persistent storage, user authentication, and a responsive web interface.

**Development Approach:** This project will follow a spec-driven development workflow. Specifications are defined first, then a plan is generated, and tasks are implemented based on the plan.

### **User Stories**
- As a user, I can sign up for a new account.
- As a user, I can log in to my account.
- As a user, I can create, view, update, and delete my own tasks.
- As a user, I can mark a task as complete.
- As a user, my tasks are private and cannot be seen by other users.
- As a user, my tasks persist across sessions.

### **Acceptance Criteria**
- All API endpoints are secured and require authentication.
- Users can only perform operations on tasks they own.
- The web interface is responsive and works on modern browsers.
- Data persists after a page reload or new session.

---

## **2. Technology Stack**

| Layer | Technology |
| :---- | :---- |
| Frontend | Next.js 16+ (App Router) |
| Backend | Python FastAPI |
| ORM | SQLModel |
| Database | Neon Serverless PostgreSQL |
| Authentication | Better Auth |

---

## **3. Architecture & Monorepo Structure**

This project uses a monorepo that organizes code by phase.

### **Folder Structure**
```
Evolution-of-Todo/
├── .specify/           # Spec-Kit Plus configuration and templates
├── specs/
│   ├── 001-todo-cli/
│   └── 002-todo-web/   # Specifications for this phase
│       ├── architecture.md
│       ├── features.md
│       └── ...
├── phase1-todo-cli/    # Code from the previous phase
└── phase2-todo-web/    # Root for the current phase's code
    ├── frontend/           # Next.js application
    │   └── ...
    ├── backend/            # FastAPI application
    │   └── ...
    └── docker-compose.yml  # For local development environment
```

---

## **4. Database Schema**

The database will be managed using **SQLModel** as the ORM. Alembic should be used for migrations.

### **`users` Table (Managed by Better Auth)**
| Column | Type | Constraints | Notes |
| :--- | :--- | :--- | :--- |
| `id` | `string` / `UUID` | Primary Key | Provided by Better Auth |
| `email` | `string` | Unique, Not Null | |
| `name` | `string` | | |
| `created_at` | `timestamp` | | |

### **`tasks` Table**
| Column | Type | Constraints | Default |
| :--- | :--- | :--- | :--- |
| `id` | `integer` | Primary Key, Autoincrement | |
| `user_id` | `string` / `UUID` | Foreign Key -> `users.id`, Not Null | |
| `title` | `string` | Not Null, (1-200 chars) | |
| `description` | `text` | Nullable | |
| `completed` | `boolean` | Not Null | `false` |
| `priority` | `string` | Enum('low', 'medium', 'high') | `'medium'` |
| `tags` | `JSON` / `string[]` | Nullable | |
| `due_date` | `datetime` | Nullable | |
| `created_at` | `timestamp` | Not Null | `CURRENT_TIMESTAMP` |
| `updated_at` | `timestamp` | Not Null | `CURRENT_TIMESTAMP` |

**Indexes:**
- An index should be created on `tasks.user_id` for efficient filtering.
- An index should be created on `tasks.completed` for status filtering.

---

## **5. REST API Endpoints**

**Base URL:** `/api`
**Authentication:** All endpoints listed below are protected and require a valid JWT token in the `Authorization: Bearer <token>` header. The backend will decode the token to identify the user and enforce data isolation.

---

### **`GET /api/tasks`**
- **Description:** List all tasks for the authenticated user.
- **Query Parameters:**
    - `status` (string): Filter by `"all"`, `"pending"`, or `"completed"`.
    - `sort` (string): Sort by `"created"`, `"title"`, or `"due_date"`.
- **Response:**
    - `200 OK`: `{ "tasks": [Task, ...] }`

---

### **`POST /api/tasks`**
- **Description:** Create a new task for the authenticated user.
- **Request Body:**
    ```json
    {
      "title": "string (required)",
      "description": "string (optional)",
      "priority": "string ('low', 'medium', 'high', optional)",
      "tags": ["string", "array", "optional"],
      "due_date": "ISO8601 datetime (optional)"
    }
    ```
- **Response:**
    - `201 Created`: The created `Task` object.

---

### **`GET /api/tasks/{task_id}`**
- **Description:** Get a single task by its ID.
- **Response:**
    - `200 OK`: The requested `Task` object.
    - `404 Not Found`: If the task does not exist or does not belong to the user.

---

### **`PUT /api/tasks/{task_id}`**
- **Description:** Update a task's details.
- **Request Body:** Contains any subset of the fields from the `POST /api/tasks` body.
- **Response:**
    - `200 OK`: The updated `Task` object.
    - `404 Not Found`: If the task does not exist or does not belong to the user.

---

### **`DELETE /api/tasks/{task_id}`**
- **Description:** Delete a task.
- **Response:**
    - `204 No Content`
    - `404 Not Found`: If the task does not exist or does not belong to the user.

---

### **`PATCH /api/tasks/{task_id}/complete`**
- **Description:** Toggle a task's completion status.
- **Request Body (Optional):**
    ```json
    { "completed": true }
    ```
- **Response:**
    - `200 OK`: The updated `Task` object.
    - `404 Not Found`: If the task does not exist or does not belong to the user.

---

## **6. Authentication & Security**

Authentication is handled by integrating **Better Auth** on the frontend with a **JWT verification** middleware on the backend.

### **Authentication Flow**
1.  **Login:** User logs in on the Next.js frontend. Better Auth creates a session and issues a JWT token.
2.  **API Call:** The frontend includes the JWT in the `Authorization: Bearer <token>` header of every API request to the FastAPI backend.
3.  **Verification:** A FastAPI middleware intercepts the request, extracts the token, and verifies its signature using a shared secret key.
4.  **User Identification:** If the token is valid, the middleware decodes it to get the `user_id`.
5.  **Data Isolation:** All API route handlers use the authenticated `user_id` to filter database queries, ensuring a user can only access their own data.

### **Shared Secret**
Both the frontend (Better Auth) and backend (FastAPI) **must** use the same secret key for signing and verifying JWTs. This key will be provided via the `BETTER_AUTH_SECRET` environment variable in both services.

### **Error Handling**
- **401 Unauthorized:** Returned for requests with a missing, invalid, or expired JWT token.
- **403 Forbidden:** Returned if a user tries to access a resource that exists but does not belong to them (though this is often handled as a 404 to avoid leaking information).
- **404 Not Found:** Returned if a resource does not exist.

---

## **7. Frontend & UI Components**

The frontend will be a responsive single-page application built with **Next.js** and styled with **Tailwind CSS**.

### **Key Pages**
- `/auth`: A single page for both Signup and Signin forms.
- `/tasks`: The main dashboard to display and manage the user's tasks.

### **UI Components**
- **`AuthForm`**: A form with email and password inputs for signup/signin.
- **`TaskList`**: Displays tasks in a table or list format, showing title, description, priority, tags, status, and action buttons.
- **`TaskForm`**: A modal or inline form with inputs for creating or editing a task (title, description, priority, tags).
- **Action Buttons**: Buttons for edit, delete, and toggling completion status for each task.

---

## **8. Development Workflow & Guidelines**

### **Running the Application**
- **Frontend:** `cd phase2-todo-web/frontend && npm run dev`
- **Backend:** `cd phase2-todo-web/backend && uvicorn main:app --reload`
- **All Services:** `cd phase2-todo-web && docker-compose up`

### **Backend Guidelines (`/phase2-todo-web/backend/CLAUDE.md`)**
- **Stack:** FastAPI, SQLModel, Neon PostgreSQL.
- **Structure:** `main.py` (entry point), `models.py` (database models), `routes/` (API handlers), `db.py` (database connection).
- **Conventions:** Use Pydantic models for request/response validation and handle errors with `HTTPException`.

### **Frontend Guidelines (`/phase2-todo-web/frontend/CLAUDE.md`)**
- **Stack:** Next.js (App Router), TypeScript, Tailwind CSS.
- **Patterns:** Use server components by default. API calls should be centralized in a dedicated client module (e.g., `/lib/api.ts`).
- **Styling:** Use Tailwind CSS utility classes directly. Avoid inline styles.

## Response snapshot

Created comprehensive specification for the Phase II Todo Full-Stack Web Application. The specification includes:
- User scenarios for registration, authentication, task management, and data isolation
- Functional requirements covering user management, task operations, security, and persistence
- Success criteria with measurable outcomes for performance and usability
- Quality validation checklist confirming the specification meets standards

## Outcome

- ✅ Impact: Created complete feature specification ready for planning phase
- 🧪 Tests: null
- 📁 Files: Created spec.md and requirements checklist in specs/002-todo-web/
- 🔁 Next prompts: Ready for /sp.plan to create implementation plan
- 🧠 Reflection: Specification follows template structure and captures all essential requirements from the feature description

## Evaluation notes (flywheel)

- Failure modes observed: null
- Graders run and results (PASS/FAIL): null
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): null