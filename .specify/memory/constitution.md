<!--
Sync Impact Report:
===================
Version Change: 0.0.0 → 1.0.0 (Initial constitution ratification)
Modified Principles: N/A (initial creation)
Added Sections:
  - Core Principles (7 principles defined)
  - Technical & Non-Functional Standards
  - Architecture Principles
  - Coding Standards
  - Security & Hardening
  - Quality Standards
  - Success Criteria
  - Constraints
  - Non-Negotiable Rules
  - AI Agent Rules
  - Evaluation Alignment
  - Governance

Templates Requiring Updates:
  ✅ .specify/templates/plan-template.md - Constitution Check section aligned
  ✅ .specify/templates/spec-template.md - Requirements sections aligned
  ✅ .specify/templates/tasks-template.md - Task organization aligned

Follow-up TODOs:
  - Define specific success criteria measurements once Phase I is complete
  - Review and update constitution after Phase II authentication implementation
  - Establish ADR review cadence once /sp.adr command is used

Rationale: MAJOR version (1.0.0) selected as this is the initial formal ratification
of the project constitution establishing all foundational principles.
-->

# Evolution of Todo Constitution

## Core Principles

### I. Spec-Driven Development (SDD)
All feature development MUST follow the Agentic Dev Stack workflow:
- **Spec → Plan → Tasks → Implement** - Each stage creates formal artifacts
- Specifications define WHAT (user scenarios, requirements, success criteria)
- Plans define HOW (architecture, decisions, technical approach)
- Tasks define STEPS (concrete implementation actions with dependencies)
- Implementation references Task IDs and validates against specs

**Rationale**: Ensures traceability, prevents scope creep, enables autonomous agents to work from written specifications rather than implicit assumptions.

### II. Phase-Gated Evolution
Development MUST progress through five distinct phases, each building upon the previous:
- **Phase I**: Python 3.13+ CLI with in-memory storage (Basic features only)
- **Phase II**: Full-stack web (Next.js + FastAPI + Neon DB) with authentication (Basic + Intermediate features)
- **Phase III**: AI chatbot integration (OpenAI Agents SDK + MCP tools) supporting natural language (All features including Advanced)
- **Phase IV**: Local Kubernetes deployment (Docker + Helm + Minikube) with AIOps
- **Phase V**: Cloud-native production (Kafka + Dapr + Cloud K8s) with all advanced features

**Rationale**: Iterative complexity ensures each phase delivers working software. No phase can be skipped; each validates architecture before adding complexity.

### III. Feature Completeness Mandate
Every phase MUST implement applicable features from three tiers:
- **Basic Features**: CRUD operations, task completion, data persistence (where applicable)
- **Intermediate Features**: Priorities, tags, search, filter, sort
- **Advanced Features**: Recurring tasks, due dates, reminders (Kafka events in Phase V)

**Rationale**: Demonstrates progressive enhancement. Phase I establishes core flows, Phase II adds persistence and multi-user, Phase III adds AI, Phases IV-V add cloud-native capabilities.

### IV. Multi-User Authentication (Phase II+)
From Phase II onward, all features MUST enforce:
- User isolation via Better Auth with JWT tokens
- Row-level security in database queries (user_id filtering)
- No shared state across user sessions
- API endpoints validate JWT and extract user context

**Rationale**: Security cannot be retrofitted. Authentication architecture established in Phase II carries through all subsequent phases.

### V. AI-Native Design (Phase III+)
AI chatbot integration (Phase III onward) MUST:
- Use OpenAI Agents SDK with explicit MCP tool definitions
- Support natural language for ALL features (e.g., "Reschedule morning meetings to 2 PM")
- Maintain stateless server design with DB-persisted conversation state
- Never rely on "magic prompts" - all AI actions must map to defined tools

**Rationale**: Tool-based AI architecture ensures deterministic, testable behavior. Natural language is a UX layer over formal tool calls.

### VI. Cloud-Native Architecture (Phase IV+)
Deployment architecture MUST be:
- **Stateless servers**: No in-memory session storage, all state in DB or message queues
- **Explicit data ownership**: Every entity has clear ownership (user_id, tenant_id)
- **Clear service boundaries**: Backend API, Frontend SPA, AI Service, Event Processors
- **Container-first**: Docker images, Kubernetes manifests, Helm charts

**Rationale**: Cloud-native patterns enable horizontal scaling, resilience, and portability across local (Minikube) and cloud (DOKS/GKE/AKS) environments.

### VII. Reusable Intelligence via Claude Subagents
Development workflow MUST leverage Claude Code subagents:
- Use specialized subagents (Explore, Plan, Implement, BetterAuth, FastAPI, etc.) for domain-specific tasks
- Capture reusable knowledge in agent skills for bonus points (+200 points)
- Create Cloud-Native Blueprints for infrastructure-as-code reuse

**Rationale**: Demonstrates AI-native development workflow, maximizes judging points, creates portable knowledge artifacts.

## Technical & Non-Functional Standards

### Performance and Scalability
- **CLI Response Time**: Phase I commands must complete in <1 second for typical operations
- **API Response Time**: Backend endpoints (Phase II+) must target <500ms for 95th percentile
- **Frontend Performance**: Time to Interactive (TTI) <3 seconds on mobile devices
- **Database Optimization**: Utilize Neon's connection pooling, indexing on user_id and commonly queried fields

### UI/UX & Accessibility Standards
- **Responsive Design**: Full mobile/tablet/desktop support using Tailwind CSS
- **Accessibility**: WCAG 2.1 AA compliance - keyboard navigation, ARIA labels, color contrast
- **Dark/Light Mode**: Theme support via CSS variables or Tailwind dark: classes
- **Professional UI**: Clean, intuitive design using shadcn/ui components where applicable
- **Chatbot UX**: Easily accessible, smooth interactions, clear feedback on AI actions

### Better User Experience
- **Interactivity**: Real-time feedback, optimistic UI updates, loading states
- **Scaffolding**: Clear onboarding, sample data for new users, contextual help
- **Visualizers**: Charts/graphs for productivity metrics, calendar views for due dates

### Chatbot Integrity Standards
- **Natural Language Processing**: OpenAI Agents SDK with structured tool definitions (MCP SDK)
- **Stateless Server**: No in-memory conversation state; all context persisted in DB
- **Tool-Based Actions**: Every AI action maps to explicit function calls (create_todo, update_priority, etc.)
- **Urdu Support** (Bonus +100): Detect language, translate prompts/responses bidirectionally

## Architecture Principles

### Stateless Servers
- No session state in application memory
- JWT tokens carry authentication context
- Conversation state (Phase III+) stored in database with session_id
- Enables horizontal scaling and zero-downtime deployments

### Explicit Data Ownership
- Every table includes `user_id` (Phase II+) or `tenant_id` (if multi-tenant expansion)
- All queries filter by owner to enforce isolation
- Cascading deletes on user removal
- Audit logs track data access patterns

### Clear Service Boundaries
- **Backend API** (FastAPI): Business logic, data access, authentication
- **Frontend SPA** (Next.js): UI rendering, client-side routing, API consumption
- **AI Service** (Phase III+): OpenAI Agents SDK, MCP tool execution
- **Event Processors** (Phase V): Kafka consumers for recurring tasks, reminders

### Tool-Based AI (No Magic Prompts)
- MCP tools define explicit input/output schemas (Pydantic models)
- AI responses map to function calls with validated parameters
- Errors surfaced via tool execution results, not prompt engineering
- Conversation logs capture tool invocations for debugging

## Coding Standards

### Clean Code
- **Python**: Follow PEP 8, use type hints (Python 3.13+ syntax)
- **TypeScript**: Strict mode enabled, explicit interfaces for all props
- **Error Handling**: Graceful degradation, user-friendly error messages, logging at ERROR level
- **Documentation**: Docstrings for all functions, README with setup/demo instructions
- **Testing**: Basic unit tests covering core flows (e.g., CRUD operations, auth middleware)

### Strict Typing
- **Backend**: Pydantic models for all API request/response bodies
- **Frontend**: TypeScript interfaces for React props, API responses
- **No `any` types**: Use `unknown` and type guards where dynamic types required

### Modularity
- **Backend**: Separate routers, services, models, schemas
- **Frontend**: Reusable components, custom hooks, service layers
- **Config**: Environment variables via `.env` (local) and secrets management (production)

### Production-Ready Code
- All code must be demo-ready in <90 seconds
- No hardcoded credentials or API keys in source
- Linting and formatting tools configured (ruff/black for Python, ESLint/Prettier for TS)
- Build passes without warnings

## Security & Hardening

### JWT for Authentication
- Better Auth library for session management (Phase II+)
- Tokens include `user_id`, expiration, refresh token flow
- HTTP-only cookies for web clients, Authorization header for API clients

### User Isolation
- All database queries filter by `user_id` from validated JWT
- No cross-user data leakage (test with multiple accounts)
- Admin endpoints (if any) require elevated privileges

### API Key Management
- **DO NOT** commit secrets to repository
- Use `.env` files for local development (excluded from git)
- Cloud deployments use secret management (Kubernetes Secrets, cloud provider vaults)

### Input Validation
- Pydantic models validate all API inputs
- Reject malformed requests with 400 Bad Request
- Sanitize inputs to prevent SQL injection, XSS (use ORM - SQLModel)

### CORS/CSRF
- Configure CORS to allow only trusted origins (frontend domain)
- CSRF tokens for state-changing operations (if using cookie-based auth)

### Dependency Scanning
- Regularly audit Python (pip/uv) and Node.js (npm) dependencies
- Update packages with known vulnerabilities
- Use tools like `safety` (Python) or `npm audit` (Node.js)

## Quality Standards

### Deterministic Behavior
- Same input must produce same output (no hidden randomness except AI responses, which are logged)
- Time-dependent logic (e.g., "due today") uses explicit date comparisons, not "now" assumptions

### Clear Error Handling
- Structured error responses with `error_code`, `message`, `details`
- HTTP status codes follow REST conventions (400 client error, 500 server error)
- Frontend displays user-friendly error messages, logs technical details to console

### Clean Separation of Concerns
- Business logic isolated from HTTP routing (services layer)
- Data access isolated from business logic (repositories/models)
- UI components don't contain business logic (use hooks/services)

### Human-Readable Logs and Responses
- Structured JSON logs with timestamp, level, user_id, request_id
- API responses include clear field names (snake_case for Python, camelCase for TS/JSON)
- Chatbot responses in natural language, tool calls logged separately

## Success Criteria

### Phase I (CLI) Success Criteria
- SC-001: User can create, read, update, delete todos via CLI commands
- SC-002: User can mark todos complete/incomplete
- SC-003: Data persists in memory during session (resets on restart)
- SC-004: CLI responds in <1 second for typical operations
- SC-005: Basic unit tests pass for CRUD operations

### Phase II (Web + DB) Success Criteria
- SC-006: User can register, login, logout via web UI
- SC-007: Todos persist in Neon PostgreSQL database
- SC-008: Multi-user isolation enforced (user A cannot see user B's todos)
- SC-009: Web UI fully responsive (mobile/tablet/desktop)
- SC-010: API response time <500ms for 95% of requests

### Phase III (AI Chatbot) Success Criteria
- SC-011: User can create/update todos via natural language (e.g., "Add dentist appointment tomorrow at 2pm")
- SC-012: Chatbot uses MCP tools for all data operations (no direct DB access)
- SC-013: Conversation state persists across sessions
- SC-014: Chatbot handles ambiguous input gracefully (asks clarifying questions)
- SC-015: (Bonus) Urdu language support works bidirectionally

### Phase IV (Local K8s) Success Criteria
- SC-016: Application runs on Minikube with Helm chart deployment
- SC-017: Backend and frontend deployed as separate services
- SC-018: Persistent volumes configured for database
- SC-019: Application recovers from pod restarts without data loss
- SC-020: AIOps dashboard (if implemented) visualizes metrics

### Phase V (Cloud K8s) Success Criteria
- SC-021: Application deployed to cloud Kubernetes (DOKS/GKE/AKS/OKE)
- SC-022: Kafka integration for recurring tasks and reminders
- SC-023: Dapr sidecars handle pub/sub and state management
- SC-024: Horizontal auto-scaling based on load
- SC-025: Advanced features (recurring, due dates, reminders) fully functional

### Bonus Features Success Criteria
- SC-026: (+200) Reusable Claude subagents/skills documented and functional
- SC-027: (+200) Cloud-Native Blueprints enable 1-click infra setup
- SC-028: (+100) Urdu language detection and translation in chatbot
- SC-029: (+200) Voice commands via Web Speech API for todo input

## Constraints

### Infrastructure
- **Free Tier Only**: Neon Serverless (PostgreSQL), OpenAI API free credits, cloud K8s free tiers
- **Usage Limits**: Stay within free tier limits (database size, API calls, compute hours)
- **Cost Awareness**: Monitor usage, implement rate limiting if approaching limits

### Deployment
- **Simple Setup**: README with clear prerequisites, step-by-step instructions
- **Replicable**: Local Minikube setup must work on Windows/Mac/Linux
- **Cloud Portability**: Helm charts work across DOKS/GKE/AKS with minimal changes
- **Spec-Driven Infra**: Use blueprints (Terraform/Pulumi/Helm) rather than manual cloud console clicks

## Non-Negotiable Rules

### Specification Primacy
- **All behavior must trace back to a written specification**
- If output is incorrect, update the spec first, THEN implement
- Never patch code manually without corresponding spec/plan update

### Implementation Traceability
- Every code change must reference a Task ID from `tasks.md`
- Task descriptions must be concrete (file paths, function names)
- No "miscellaneous" tasks - decompose into specific actions

### No Skipped Phases
- Phase I must be completed before Phase II begins
- Each phase validates architecture before adding next layer
- If phase fails validation, refactor before proceeding

## AI Agent Rules

### Agents Must Stop if Spec Missing
- If `/sp.specify` has not been run for a feature, refuse to implement
- If `spec.md` exists but lacks user scenarios, request clarification
- No implementation from verbal instructions alone - spec must exist

### Task ID References Required
- Every implementation must cite Task IDs (e.g., "Implements T012: Create Todo model")
- Task completion must verify acceptance criteria from `tasks.md`
- If task ambiguous, update `tasks.md` before implementing

### Human as Tool Strategy
- Invoke user for clarification when requirements ambiguous
- Present options for architectural decisions (don't assume)
- Surface unforeseen dependencies discovered during implementation
- Checkpoint after major milestones, confirm next steps

## Evaluation Alignment

### Visible Spec Evolution
- All specs stored in `specs/<feature>/` with timestamped updates
- Prompt History Records (PHR) in `history/prompts/` for every user interaction
- Architecture Decision Records (ADR) in `history/adr/` for significant decisions

### Clear Architectural Reasoning
- ADRs document options considered, tradeoffs, rationale
- Plan documents explain WHY (not just WHAT) for design choices
- Code comments explain complex logic, not obvious syntax

### Demonstrated AI-Native Workflow
- Use of Claude Code subagents documented in PHRs
- Reusable agent skills created for bonus points
- MCP tool definitions show tool-based AI architecture
- Conversation logs (Phase III+) demonstrate natural language understanding

## Governance

### Amendment Procedure
- Constitution changes require user approval (cannot be auto-updated by agents)
- Version bumps follow semantic versioning:
  - **MAJOR**: Backward-incompatible principle removals or redefinitions
  - **MINOR**: New principles added or material expansions
  - **PATCH**: Clarifications, wording fixes, non-semantic refinements
- Amendments trigger template sync (plan, spec, tasks templates updated)

### Versioning Policy
- Constitution version tracked in this file's footer
- ADR created for MAJOR/MINOR changes explaining rationale
- Dependent templates reference constitution version for compatibility

### Compliance Review Expectations
- Every `/sp.plan` execution includes "Constitution Check" gate
- Task generation validates against principles (e.g., no Phase II tasks before Phase I complete)
- Code reviews verify task traceability, spec alignment
- PHRs capture compliance violations for retrospective analysis

### Runtime Guidance
- CLAUDE.md contains prompts, iterations, agent-specific guidance
- README.md provides setup, demo, architecture overview
- This constitution is the authoritative source for all governance and principles

**Version**: 1.0.0 | **Ratified**: 2025-12-18 | **Last Amended**: 2025-12-18
