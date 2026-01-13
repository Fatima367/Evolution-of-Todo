# Implementation Plan: Advanced Cloud Deployment

**Branch**: `005-advanced-cloud-deployment` | **Date**: 2026-01-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-advanced-cloud-deployment/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement Phase V of the Evolution of Todo application with advanced task management features (recurring tasks, due dates, reminders, priorities, tags, search/filter/sort), event-driven architecture using Kafka for asynchronous processing, Dapr for distributed runtime abstraction, and production-grade Kubernetes deployment on cloud providers (Azure/GCP/Oracle). Includes local Minikube development environment, CI/CD pipeline with GitHub Actions, and comprehensive observability with monitoring, logging, and distributed tracing.

## Technical Context

**Language/Version**: Python 3.13+ (backend services), TypeScript 5+ (frontend), Bash (deployment scripts)
**Primary Dependencies**:
- Backend: FastAPI, SQLModel, Neon PostgreSQL driver, aiokafka/kafka-python, Dapr Python SDK, pydantic
- Frontend: Next.js 16+, React, Tailwind CSS, Better Auth (from Phase II)
- Infrastructure: Kubernetes, Helm, Dapr, Kafka/Redpanda, Docker
- Monitoring: Prometheus, Grafana, OpenTelemetry (or cloud provider equivalents)
- CI/CD: GitHub Actions

**Storage**: Neon Serverless PostgreSQL (existing from Phase II) with new tables for recurring patterns, reminders, audit logs; Kafka topics for event streaming

**Testing**: pytest (backend unit/integration), Playwright (frontend E2E), Kubernetes manifest validation, Helm chart testing

**Target Platform**:
- Local: Minikube on Windows/Mac/Linux
- Production: Azure Kubernetes Service (AKS), Google Kubernetes Engine (GKE), or Oracle Kubernetes Engine (OKE)
- Container Registry: Docker Hub, GitHub Container Registry, or cloud provider registries

**Project Type**: Distributed web application with microservices architecture (frontend SPA, backend API, notification service, recurring task service, audit service)

**Performance Goals**:
- API response time: <500ms p95 for user operations
- Event processing: 1,000+ events/minute sustained, 2,000 events/minute burst
- Real-time updates: <2 seconds latency for task changes across devices
- Search performance: <1 second for 10,000 tasks
- Deployment time: <15 minutes for production rollout

**Constraints**:
- Must use free tier/trial credits for all cloud services
- Must maintain backward compatibility with existing task schema from Phase II/III
- Must use existing Better Auth authentication (no new auth system)
- Must deploy via Helm charts (no manual kubectl commands)
- Must support at least 10,000 tasks per user without degradation
- Must follow Agentic Dev Stack workflow (no manual coding)

**Scale/Scope**:
- Users: 10,000 concurrent users target
- Data: 10,000 tasks per user, 1,000 events/minute baseline
- Services: 5-7 microservices (frontend, backend API, notification service, recurring task service, audit service, optional WebSocket service)
- Infrastructure: 3-5 Kubernetes nodes (local), 2-10 nodes (cloud with auto-scaling)
- Deployment environments: Local (Minikube), Staging (cloud), Production (cloud)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Spec-Driven Development (SDD)
- **Status**: PASS
- **Evidence**: Following Agentic Dev Stack workflow (spec.md created, now executing plan.md, tasks.md will follow)
- **Validation**: All implementation will reference task IDs and validate against spec requirements

### ✅ Phase-Gated Evolution
- **Status**: PASS
- **Evidence**: This is Phase V, building upon completed Phase II (auth + DB), Phase III (AI chatbot), and Phase IV (Helm charts)
- **Dependencies Verified**: Better Auth functional, task CRUD operational, containerization complete
- **Validation**: No phase skipping; each previous phase delivered working software

### ✅ Feature Completeness Mandate
- **Status**: PASS
- **Evidence**: Implementing all three feature tiers:
  - Basic: CRUD operations (inherited from Phase II)
  - Intermediate: Priorities, tags, search, filter, sort (FR-001 to FR-010)
  - Advanced: Recurring tasks, due dates, reminders (FR-005, FR-006, FR-004)
- **Validation**: All applicable features from spec requirements mapped to implementation

### ✅ Multi-User Authentication (Phase II+)
- **Status**: PASS
- **Evidence**: Using existing Better Auth with JWT tokens from Phase II
- **User Isolation**: All new tables (recurring_patterns, reminders, audit_logs) include user_id
- **API Security**: All endpoints validate JWT and filter by user_id
- **Validation**: No shared state; row-level security enforced

### ✅ AI-Native Design (Phase III+)
- **Status**: PASS
- **Evidence**: Maintaining OpenAI Agents SDK with MCP tools from Phase III
- **Stateless Server**: Conversation state persisted in DB (no in-memory sessions)
- **Tool-Based Actions**: All AI actions map to defined MCP tools
- **Validation**: Natural language interface preserved; no changes to AI architecture

### ✅ Cloud-Native Architecture (Phase IV+)
- **Status**: PASS
- **Evidence**: Core focus of Phase V implementation
- **Stateless Servers**: All services stateless; state in DB or Kafka
- **Explicit Data Ownership**: user_id on all entities; tenant isolation enforced
- **Clear Service Boundaries**:
  - Frontend SPA (Next.js)
  - Backend API (FastAPI)
  - Notification Service (Kafka consumer)
  - Recurring Task Service (Kafka consumer)
  - Audit Service (Kafka consumer)
- **Container-First**: Docker images, Kubernetes manifests, Helm charts
- **Validation**: Horizontal scaling enabled; resilience patterns implemented

### ✅ Reusable Intelligence via Claude Subagents
- **Status**: PASS
- **Evidence**: Using specialized subagents throughout development
- **Subagents Used**: Explore (codebase analysis), Plan (this phase), Backend Specialist, Kubernetes Deployment Agent
- **Reusable Artifacts**: Cloud-Native Blueprints for infrastructure-as-code
- **Validation**: Demonstrates AI-native development workflow

### ✅ Performance and Scalability
- **Status**: PASS
- **Evidence**: Performance goals defined and achievable
- **API Response Time**: <500ms p95 target (constitution requires <500ms)
- **Database Optimization**: Neon connection pooling, indexes on user_id and query fields
- **Validation**: Performance requirements align with constitution standards

### ✅ Security & Hardening
- **Status**: PASS
- **Evidence**: Comprehensive security measures
- **JWT Authentication**: Better Auth with token validation
- **User Isolation**: All queries filter by user_id from validated JWT
- **API Key Management**: Secrets in Kubernetes Secrets, no .env commits
- **Input Validation**: Pydantic models for all API inputs
- **CORS/CSRF**: Configured for trusted origins only
- **Validation**: Security principles enforced at all layers

### ⚠️ Complexity Considerations
- **New Services**: Adding 3-4 new microservices (notification, recurring task, audit, optional WebSocket)
- **Justification**: Event-driven architecture requires dedicated consumers; cannot be handled by main API without blocking
- **Mitigation**: Each service has single responsibility; clear boundaries; independently scalable
- **Alternative Rejected**: Monolithic approach would violate stateless server principle and create performance bottlenecks

### ✅ Quality Standards
- **Status**: PASS
- **Evidence**: All quality standards addressed
- **Deterministic Behavior**: Event ordering guaranteed; time-dependent logic uses explicit comparisons
- **Clear Error Handling**: Structured error responses with codes and messages
- **Clean Separation**: Services layer, repositories, UI components properly separated
- **Human-Readable Logs**: Structured JSON logs with context (user_id, request_id)
- **Validation**: Code quality standards enforced

### Constitution Check Summary
**Overall Status**: ✅ PASS - All gates satisfied, ready for Phase 0 research

**Violations Requiring Justification**: 1 (see Complexity Tracking section)

**Re-check Required After Phase 1**: Yes (validate design decisions against architecture principles)

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
# Distributed Web Application with Microservices

# Frontend (existing from Phase II/III)
todo-board-frontend/
├── src/
│   ├── app/                    # Next.js 16+ App Router
│   ├── components/             # React components
│   │   ├── tasks/              # Task management UI
│   │   ├── filters/            # Search/filter/sort UI (NEW)
│   │   └── notifications/      # Reminder notifications UI (NEW)
│   ├── lib/
│   │   ├── auth/               # Better Auth integration
│   │   └── api/                # API client
│   └── types/                  # TypeScript types
└── tests/
    └── e2e/                    # Playwright tests

# Backend API (existing from Phase II/III, extended)
todo-board-backend/
├── src/
│   ├── models/                 # SQLModel entities
│   │   ├── task.py             # Extended with priority, tags, due_date (NEW)
│   │   ├── recurring_pattern.py # NEW
│   │   ├── reminder.py         # NEW
│   │   └── audit_log.py        # NEW
│   ├── services/
│   │   ├── task_service.py     # Extended with search/filter/sort (NEW)
│   │   ├── event_publisher.py  # Kafka event publishing (NEW)
│   │   └── dapr_client.py      # Dapr SDK integration (NEW)
│   ├── api/
│   │   ├── routers/
│   │   │   ├── tasks.py        # Extended endpoints
│   │   │   ├── recurring.py    # NEW
│   │   │   └── reminders.py    # NEW
│   │   └── middleware/         # Auth, logging, tracing
│   └── mcp/                    # MCP tools (existing from Phase III)
└── tests/
    ├── unit/
    └── integration/

# Notification Service (NEW microservice)
services/notification-service/
├── src/
│   ├── consumer.py             # Kafka consumer for reminder events
│   ├── notifier.py             # Web push notification sender
│   └── config.py
├── Dockerfile
└── tests/

# Recurring Task Service (NEW microservice)
services/recurring-task-service/
├── src/
│   ├── consumer.py             # Kafka consumer for task completion events
│   ├── scheduler.py            # Creates next task occurrence
│   └── config.py
├── Dockerfile
└── tests/

# Audit Service (NEW microservice)
services/audit-service/
├── src/
│   ├── consumer.py             # Kafka consumer for all task events
│   ├── logger.py               # Writes to audit_logs table
│   └── config.py
├── Dockerfile
└── tests/

# Infrastructure (Kubernetes, Helm, Dapr)
infrastructure/
├── kubernetes/
│   ├── base/                   # Base manifests
│   │   ├── namespace.yaml
│   │   ├── configmaps/
│   │   └── secrets/
│   ├── local/                  # Minikube overlays
│   └── cloud/                  # Cloud provider overlays (AKS/GKE/OKE)
├── helm/
│   └── todo-app/               # Helm chart (extended from Phase IV)
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── values-local.yaml   # Minikube values
│       ├── values-cloud.yaml   # Cloud values
│       └── templates/
│           ├── frontend/
│           ├── backend/
│           ├── notification-service/  # NEW
│           ├── recurring-task-service/ # NEW
│           ├── audit-service/  # NEW
│           ├── kafka/          # NEW (or external)
│           └── dapr/           # NEW
└── dapr/
    └── components/             # Dapr component definitions
        ├── pubsub-kafka.yaml   # Kafka pub/sub
        ├── statestore-postgres.yaml # State management
        └── secrets-k8s.yaml    # Secrets store

# CI/CD
.github/
└── workflows/
    ├── build-and-test.yml      # Build, test, scan
    ├── deploy-staging.yml      # Auto-deploy to staging
    └── deploy-production.yml   # Manual approval for prod

# Deployment Scripts
scripts/
├── local/
│   ├── setup-minikube.sh       # Initialize Minikube
│   ├── install-dapr.sh         # Install Dapr on K8s
│   ├── deploy-local.sh         # Deploy to Minikube
│   └── teardown-local.sh
└── cloud/
    ├── setup-cluster.sh        # Create cloud K8s cluster
    ├── deploy-cloud.sh         # Deploy to cloud
    └── teardown-cloud.sh

# Monitoring & Observability
monitoring/
├── prometheus/
│   └── config.yaml             # Prometheus configuration
├── grafana/
│   └── dashboards/             # Pre-built dashboards
└── opentelemetry/
    └── collector-config.yaml   # Trace collection
```

**Structure Decision**: Distributed web application with microservices architecture. Selected this structure because:
1. **Existing Foundation**: Builds on Phase II/III frontend and backend
2. **Service Separation**: New microservices (notification, recurring task, audit) are independent services with dedicated Dockerfiles
3. **Infrastructure-as-Code**: Kubernetes manifests and Helm charts enable declarative deployment
4. **Dapr Integration**: Separate directory for Dapr components (pub/sub, state, secrets)
5. **CI/CD Automation**: GitHub Actions workflows for automated build/test/deploy
6. **Local/Cloud Parity**: Same Helm chart with different values files for Minikube vs cloud

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Adding 3-4 new microservices (notification, recurring task, audit, optional WebSocket) | Event-driven architecture requires dedicated Kafka consumers that run continuously and independently. Each service has a single, focused responsibility that cannot be combined without violating separation of concerns. | **Monolithic approach**: Handling all event processing in the main API would block user requests, violate stateless server principle, and create performance bottlenecks. **Background workers in main API**: Would still require separate processes/containers, so no complexity reduction. **Combining services**: Notification + recurring task + audit have different scaling needs, failure modes, and responsibilities - combining would create tight coupling and reduce resilience. |

**Justification Summary**: The microservices architecture is the simplest viable approach that satisfies the constitution's requirements for stateless servers, clear service boundaries, and horizontal scalability. Each service can fail, scale, and deploy independently, which is essential for production-grade cloud-native applications.

**Mitigation Strategies**:
1. **Shared Libraries**: Common code (Kafka client, DB models, logging) extracted to shared Python packages
2. **Standardized Structure**: All services follow identical project structure for maintainability
3. **Unified Deployment**: Single Helm chart deploys all services with consistent configuration
4. **Dapr Abstraction**: Dapr sidecars handle infrastructure complexity (pub/sub, state, secrets), keeping service code simple
5. **Clear Boundaries**: Each service has well-defined inputs (Kafka topics) and outputs (DB writes, notifications), no inter-service dependencies
