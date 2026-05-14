# TodoBoard Architecture - Phase V

## Overview

TodoBoard Phase V implements a cloud-native, event-driven microservices architecture deployed on Kubernetes. The system uses Kafka for asynchronous event processing, Dapr for distributed runtime abstraction, and supports both local development (Minikube) and production cloud deployment (Azure/GCP/Oracle).

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              User Devices                                    │
│                    (Web Browsers, Mobile Devices)                           │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 │ HTTPS
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Kubernetes Ingress                                   │
│                    (TLS Termination, Routing)                               │
└──────────────┬──────────────────────────────────────┬───────────────────────┘
               │                                       │
               │                                       │
               ▼                                       ▼
┌──────────────────────────┐              ┌──────────────────────────┐
│   Frontend Service       │              │   Backend API Service    │
│   (Next.js 16+)          │              │   (FastAPI + SQLModel)   │
│                          │              │                          │
│   - React UI             │              │   - REST API             │
│   - Better Auth Client   │◄─────────────┤   - JWT Auth             │
│   - WebSocket Client     │   HTTP/WS    │   - Task CRUD            │
│   - Real-time Updates    │              │   - User Management      │
└──────────────────────────┘              └────────────┬─────────────┘
                                                       │
                                                       │ Publishes Events
                                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Dapr Pub/Sub Component                              │
│                         (Kafka Message Broker)                               │
│                                                                              │
│   Topics:                                                                    │
│   • task-events        - All task CRUD operations (audit trail)            │
│   • task-updates       - Real-time updates (WebSocket broadcast)           │
│   • reminders          - Scheduled reminder notifications                   │
│   • dead-letter-queue  - Failed events for retry/investigation             │
└──────┬──────────────────────┬──────────────────────┬────────────────────────┘
       │                      │                      │
       │ Consumes             │ Consumes             │ Consumes
       ▼                      ▼                      ▼
┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│ Notification     │   │ Recurring Task   │   │ Audit Service    │
│ Service          │   │ Service          │   │                  │
│                  │   │                  │   │                  │
│ - Reminder       │   │ - Task           │   │ - Event Logging  │
│   Processing     │   │   Scheduling     │   │ - Audit Trail    │
│ - Web Push       │   │ - Pattern        │   │ - Compliance     │
│ - Email (future) │   │   Matching       │   │ - Analytics      │
└──────────────────┘   └────────┬─────────┘   └────────┬─────────┘
                                │                       │
                                │ Writes                │ Writes
                                ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Neon Serverless PostgreSQL                                │
│                                                                              │
│   Tables:                                                                    │
│   • users              - User accounts and authentication                   │
│   • tasks              - Task data with priorities, tags, due dates         │
│   • recurring_patterns - Recurring task definitions                         │
│   • reminders          - Reminder schedules                                 │
│   • audit_logs         - Complete audit trail of all operations             │
│   • conversations      - AI chatbot conversation history                    │
│   • messages           - AI chatbot messages                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         Dapr State Store Component                           │
│                      (PostgreSQL for distributed state)                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        Dapr Secrets Component                                │
│                    (Kubernetes Secrets Management)                           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         Observability Stack                                  │
│                                                                              │
│   • Prometheus      - Metrics collection and storage                        │
│   • Grafana         - Metrics visualization and dashboards                  │
│   • OpenTelemetry   - Distributed tracing                                   │
│   • Structured Logs - JSON logs with request IDs                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Service Components

### 1. Frontend Service (Next.js)

**Purpose**: User interface and client-side application logic

**Technology Stack**:
- Next.js 16+ with App Router
- React 18+ with Server Components
- TypeScript 5+
- Tailwind CSS for styling
- Better Auth for authentication
- WebSocket client for real-time updates

**Key Features**:
- Server-side rendering (SSR) for initial page loads
- Client-side routing for navigation
- Real-time task updates via WebSocket
- Responsive design for mobile and desktop
- Dark mode support

**Deployment**:
- Containerized with Docker
- Deployed as Kubernetes Deployment
- Horizontal scaling supported
- Health checks: `/api/health`

### 2. Backend API Service (FastAPI)

**Purpose**: Core business logic and REST API

**Technology Stack**:
- FastAPI (Python 3.13+)
- SQLModel for ORM
- Pydantic for validation
- Better Auth for JWT authentication
- Dapr SDK for event publishing

**Key Features**:
- RESTful API endpoints for task management
- JWT-based authentication and authorization
- User isolation (all queries filtered by user_id)
- Event publishing for all task operations
- Advanced search, filter, and sort capabilities
- Recurring task pattern management
- Reminder scheduling

**API Endpoints**:
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/tasks` - List tasks with filters
- `POST /api/tasks` - Create task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `PATCH /api/tasks/{id}/complete` - Toggle completion
- `POST /api/recurring` - Create recurring pattern
- `POST /api/reminders` - Create reminder

**Deployment**:
- Containerized with Docker
- Deployed as Kubernetes Deployment with Dapr sidecar
- Horizontal Pod Autoscaler (HPA) for auto-scaling
- Health checks: `/health`, `/health/ready`
- Metrics: `/metrics` (Prometheus format)

### 3. Notification Service

**Purpose**: Process reminder events and send notifications

**Technology Stack**:
- Python 3.13+
- Kafka consumer (aiokafka)
- Web Push API for browser notifications
- Prometheus metrics

**Key Features**:
- Consumes events from `reminders` topic
- Sends Web Push notifications to users
- Retry logic with exponential backoff
- Dead letter queue for failed notifications
- Metrics for monitoring delivery rates

**Event Processing**:
- Subscribes to: `reminders`
- Event type: `reminder.due`
- Processing: Sends notification to user's registered devices

**Deployment**:
- Containerized with Docker
- Deployed as Kubernetes Deployment with Dapr sidecar
- Horizontal Pod Autoscaler for high load
- Metrics: `/metrics`

### 4. Recurring Task Service

**Purpose**: Generate next instances of recurring tasks

**Technology Stack**:
- Python 3.13+
- Kafka consumer (aiokafka)
- SQLModel for database access
- Prometheus metrics

**Key Features**:
- Consumes task completion events
- Checks if task has recurring pattern
- Calculates next occurrence based on pattern
- Creates new task instance automatically
- Handles various recurrence patterns (daily, weekly, monthly, custom)

**Event Processing**:
- Subscribes to: `task-events`
- Event type: `task.completed`
- Processing: Creates next task instance if recurring pattern exists

**Deployment**:
- Containerized with Docker
- Deployed as Kubernetes Deployment with Dapr sidecar
- Horizontal Pod Autoscaler for scalability
- Metrics: `/metrics`

### 5. Audit Service

**Purpose**: Maintain complete audit trail of all operations

**Technology Stack**:
- Python 3.13+
- Kafka consumer (aiokafka)
- SQLModel for database access
- Prometheus metrics

**Key Features**:
- Consumes all task events
- Writes audit logs to database
- Provides compliance and analytics data
- Immutable audit trail
- Supports forensic analysis

**Event Processing**:
- Subscribes to: `task-events`
- Event types: `task.created`, `task.updated`, `task.completed`, `task.deleted`
- Processing: Writes structured audit log entry

**Deployment**:
- Containerized with Docker
- Deployed as Kubernetes Deployment with Dapr sidecar
- Metrics: `/metrics`

## Event Flow

### Task Creation Flow

```
1. User creates task in Frontend
   ↓
2. Frontend sends POST /api/tasks to Backend API
   ↓
3. Backend API validates and saves task to PostgreSQL
   ↓
4. Backend API publishes events:
   - task.created → task-events topic (for audit)
   - task.changed → task-updates topic (for real-time)
   ↓
5. Consumers process events:
   - Audit Service: Writes audit log
   - WebSocket Service: Broadcasts to connected clients
   ↓
6. Frontend receives WebSocket update
   ↓
7. UI updates in real-time across all devices
```

### Recurring Task Completion Flow

```
1. User marks recurring task as complete
   ↓
2. Backend API updates task status
   ↓
3. Backend API publishes task.completed event
   ↓
4. Recurring Task Service consumes event
   ↓
5. Service checks for recurring pattern
   ↓
6. Service calculates next occurrence
   ↓
7. Service creates new task instance
   ↓
8. New task appears in user's task list
```

### Reminder Notification Flow

```
1. User creates task with due date and reminder
   ↓
2. Backend API saves task and reminder
   ↓
3. Scheduled job checks for due reminders
   ↓
4. Backend API publishes reminder.due event
   ↓
5. Notification Service consumes event
   ↓
6. Service sends Web Push notification
   ↓
7. User receives notification on all devices
```

## Data Flow

### Authentication Flow

```
1. User submits credentials to Frontend
   ↓
2. Frontend sends POST /api/auth/login to Backend
   ↓
3. Backend validates credentials against PostgreSQL
   ↓
4. Backend generates JWT token with user_id
   ↓
5. Frontend stores token in localStorage
   ↓
6. All subsequent requests include JWT in Authorization header
   ↓
7. Backend validates JWT and extracts user_id
   ↓
8. All database queries filtered by user_id
```

### Real-Time Update Flow

```
1. User A creates/updates task on Device 1
   ↓
2. Backend publishes task.changed event to task-updates topic
   ↓
3. WebSocket Service consumes event
   ↓
4. WebSocket Service broadcasts to all connected clients for user_id
   ↓
5. User A's Device 2 receives WebSocket message
   ↓
6. Frontend updates UI without page refresh
   ↓
7. Change appears instantly on all devices
```

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 16+, React, TypeScript | User interface |
| **Backend API** | FastAPI, SQLModel, Python 3.13+ | Business logic |
| **Database** | Neon Serverless PostgreSQL | Data persistence |
| **Message Broker** | Kafka (via Dapr) | Event streaming |
| **Distributed Runtime** | Dapr | Service abstraction |
| **Container Runtime** | Docker | Application packaging |
| **Orchestration** | Kubernetes (Minikube/AKS/GKE/OKE) | Container management |
| **Package Management** | Helm | Kubernetes deployment |
| **Monitoring** | Prometheus, Grafana | Observability |
| **Tracing** | OpenTelemetry | Distributed tracing |
| **CI/CD** | GitHub Actions | Automation |

## Deployment Architecture

### Local Development (Minikube)

- Single-node Kubernetes cluster
- Kafka via Strimzi operator
- Dapr installed via Helm
- All services deployed with reduced resource limits
- Ingress for local access (localhost)
- Development-friendly configuration

### Production Cloud (AKS/GKE/OKE)

- Multi-node Kubernetes cluster (2-10 nodes)
- Managed Kafka service or Strimzi with replication
- Dapr installed via Helm
- Horizontal Pod Autoscaling enabled
- TLS/SSL certificates via cert-manager
- Network policies for security
- Pod Disruption Budgets for high availability
- Rolling updates with zero downtime
- Resource requests and limits optimized
- Monitoring and alerting configured

## Scalability

### Horizontal Scaling

All services support horizontal scaling:

- **Frontend**: Stateless, scales based on CPU/memory
- **Backend API**: Stateless, scales based on request rate
- **Notification Service**: Scales based on queue depth
- **Recurring Task Service**: Scales based on event rate
- **Audit Service**: Scales based on event rate

### Auto-Scaling Configuration

```yaml
# Example HPA for Backend API
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## High Availability

### Resilience Features

1. **Service Redundancy**: Multiple replicas of each service
2. **Health Checks**: Liveness and readiness probes
3. **Graceful Shutdown**: Services handle SIGTERM properly
4. **Circuit Breakers**: Prevent cascade failures
5. **Retry Logic**: Exponential backoff for transient failures
6. **Dead Letter Queue**: Failed events preserved for investigation
7. **Database Connection Pooling**: Efficient resource usage
8. **Event Ordering**: Guaranteed by Kafka partitioning on user_id

### Failure Recovery

- **Pod Failure**: Kubernetes automatically restarts failed pods
- **Node Failure**: Pods rescheduled to healthy nodes
- **Database Failure**: Connection retry with exponential backoff
- **Kafka Failure**: Event buffering and retry
- **Deployment Failure**: Automatic rollback on health check failure

## Security

### Authentication & Authorization

- JWT-based authentication with Better Auth
- Token validation on every request
- User isolation enforced at database level
- All queries filtered by authenticated user_id

### Network Security

- TLS/SSL for all external communication
- Network policies for service-to-service communication
- Secrets stored in Kubernetes Secrets
- No hardcoded credentials

### Data Security

- Passwords hashed with bcrypt
- Database credentials in Kubernetes Secrets
- API keys in environment variables
- Audit trail for compliance

## Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| API Response Time | <500ms p95 | Prometheus histogram |
| Event Processing | 1,000+ events/min sustained | Kafka consumer lag |
| Real-Time Latency | <2 seconds | WebSocket message timestamp |
| Search Performance | <1 second for 10,000 tasks | API response time |
| Deployment Time | <15 minutes | CI/CD pipeline duration |
| Availability | 99.9% uptime | Uptime monitoring |

## Monitoring & Observability

### Metrics (Prometheus)

- Request rate, latency, error rate per endpoint
- Event processing rate and lag per consumer
- Database connection pool usage
- Resource utilization (CPU, memory, disk)
- Custom business metrics (tasks created, completed, etc.)

### Logs (Structured JSON)

- Request/response logs with request_id
- Event processing logs with event_id
- Error logs with stack traces
- Audit logs for compliance

### Traces (OpenTelemetry)

- Distributed tracing across services
- Request flow visualization
- Performance bottleneck identification
- Error propagation tracking

### Dashboards (Grafana)

- Cluster overview (nodes, pods, resources)
- Application metrics (requests, latency, errors)
- Kafka metrics (topics, partitions, lag)
- Business metrics (active users, tasks, events)

## References

- [Event Schemas Documentation](./event-schemas.md)
- [Dapr Setup Guide](./dapr-setup.md)
- [Deployment Quickstart](../README.md#deployment)
- [Monitoring Setup](../monitoring/README.md)
