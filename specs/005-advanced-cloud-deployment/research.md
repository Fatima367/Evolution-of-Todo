# Research: Advanced Cloud Deployment

**Feature**: 005-advanced-cloud-deployment
**Date**: 2026-01-12
**Phase**: Phase 0 - Research and Technology Decisions

## Overview

This document captures research findings, technology decisions, and architectural rationale for implementing Phase V of the Evolution of Todo application. All decisions prioritize free tier compatibility, cloud-native patterns, and alignment with the project constitution.

---

## Decision 1: Event Streaming Platform

### Decision
Use **Kafka-compatible event streaming** with flexible implementation:
- **Local (Minikube)**: Strimzi Kafka Operator (self-hosted in Kubernetes)
- **Cloud**: Redpanda Cloud Serverless (free tier) OR Strimzi self-hosted

### Rationale
1. **Kafka-Compatible API**: Industry standard with mature ecosystem (aiokafka, kafka-python)
2. **Dapr Abstraction**: Dapr pub/sub component supports Kafka, making implementation swappable
3. **Free Tier Availability**: Redpanda Cloud offers serverless free tier; Strimzi is free (compute cost only)
4. **Event Ordering**: Kafka guarantees ordering within partitions (required by FR-013)
5. **At-Least-Once Delivery**: Native support for delivery guarantees (required by FR-014)
6. **Multiple Consumers**: Topic-based pub/sub supports independent consumers (required by FR-015)

### Alternatives Considered
| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| **RabbitMQ** | Simpler setup, good for message queuing | Weaker event ordering guarantees, less suited for event streaming | Event ordering critical for task operations; Kafka better for event-driven architecture |
| **Redis Streams** | Very fast, simple | Not designed for durable event storage, limited retention | Need audit trail with 90-day retention; Redis Streams not ideal for long-term storage |
| **Cloud Pub/Sub (GCP)** | Fully managed, auto-scaling | Vendor lock-in, no free tier, not Kafka-compatible | Must support multiple cloud providers; Kafka compatibility enables portability |
| **AWS Kinesis** | Fully managed, AWS native | Vendor lock-in, no free tier, different API | Same issues as Cloud Pub/Sub; Kafka API more portable |

### Implementation Notes
- Use Dapr pub/sub component for abstraction (swap Kafka for RabbitMQ with config change)
- Kafka topics: `task-events`, `reminders`, `task-updates`
- Partition by `user_id` for ordering guarantees per user
- Retention: 7 days for events (sufficient for replay), 90 days for audit logs (stored in DB)

---

## Decision 2: Distributed Application Runtime

### Decision
Use **Dapr (Distributed Application Runtime)** with sidecars for all services

### Rationale
1. **Infrastructure Abstraction**: Dapr components abstract Kafka, PostgreSQL, Kubernetes Secrets
2. **Simplified Service Code**: Services call Dapr HTTP API instead of managing Kafka clients directly
3. **Portability**: Swap infrastructure (Kafka → RabbitMQ) with YAML config change, no code changes
4. **Built-in Patterns**: Retries, circuit breakers, service invocation with discovery
5. **Kubernetes Native**: Dapr designed for Kubernetes, integrates with K8s primitives
6. **Free and Open Source**: No licensing costs, active CNCF project

### Alternatives Considered
| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| **Direct Kafka Clients** | Full control, no abstraction overhead | Tight coupling to Kafka, harder to swap, more boilerplate | Violates constitution's preference for loose coupling; harder to test locally |
| **Service Mesh (Istio)** | Comprehensive traffic management, security | Heavy resource usage, complex setup, overkill for this scale | Too complex for free tier constraints; Dapr lighter weight |
| **Spring Cloud** | Mature Java ecosystem | Requires Java/JVM, not Python-native | Backend is Python 3.13+; Spring Cloud not applicable |
| **No Abstraction Layer** | Simplest approach | Every service reimplements Kafka, DB, secrets logic | Code duplication, harder to maintain, violates DRY principle |

### Implementation Notes
- Dapr components: `pubsub-kafka.yaml`, `statestore-postgres.yaml`, `secrets-k8s.yaml`
- Services call `http://localhost:3500/v1.0/publish/...` for event publishing
- Dapr sidecars injected via Kubernetes annotations
- Dapr CLI for local development (dapr run)

---

## Decision 3: Local Development Environment

### Decision
Use **Minikube** with Helm charts for local Kubernetes deployment

### Rationale
1. **Kubernetes Parity**: Same Kubernetes API as cloud, ensures local/cloud consistency
2. **Cross-Platform**: Works on Windows, Mac, Linux (required by constitution)
3. **Resource Efficient**: Runs on developer laptops with 8GB+ RAM
4. **Helm Support**: Native support for Helm charts (same charts for local and cloud)
5. **Free**: No cost for local development

### Alternatives Considered
| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| **Docker Compose** | Simpler, faster startup | Not Kubernetes, no parity with production | Must validate K8s manifests locally; Docker Compose doesn't test K8s-specific features |
| **Kind (Kubernetes in Docker)** | Lightweight, fast | Less mature tooling than Minikube | Minikube more widely adopted, better documentation |
| **k3s** | Very lightweight, production-grade | Requires Linux or WSL on Windows | Cross-platform requirement; Minikube easier on Windows |
| **Cloud Dev Environment** | No local setup needed | Costs money, requires internet, slower iteration | Free tier constraint; local development faster |

### Implementation Notes
- Minikube with Docker driver (most compatible)
- Enable addons: `ingress`, `metrics-server`, `dashboard`
- Helm chart with `values-local.yaml` for Minikube-specific config
- Scripts: `setup-minikube.sh`, `deploy-local.sh`, `teardown-local.sh`

---

## Decision 4: Cloud Kubernetes Provider

### Decision
Support **multiple cloud providers** with preference order:
1. **Oracle Cloud (OKE)** - Always Free tier (4 OCPUs, 24GB RAM, no time limit)
2. **Google Cloud (GKE)** - $300 credit, 90 days
3. **Azure (AKS)** - $200 credit, 30 days

### Rationale
1. **Free Tier Priority**: Oracle Cloud offers always-free K8s, best for learning without time pressure
2. **Multi-Cloud Support**: Helm charts work across all three with minimal changes
3. **No Vendor Lock-In**: Kubernetes API is portable, Dapr abstracts cloud-specific services
4. **Cost Optimization**: Oracle free tier eliminates compute costs for hackathon

### Alternatives Considered
| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| **Single Cloud (GKE only)** | Simpler, one set of docs | Vendor lock-in, credit expires | Constitution requires portability; Oracle free tier better for long-term |
| **DigitalOcean (DOKS)** | Simple, good docs | No free tier, $12/month minimum | Cost constraint; Oracle/GCP/Azure have free tiers |
| **AWS (EKS)** | Most popular, mature | Complex setup, no generous free tier | Setup complexity high; GKE/AKS simpler for K8s |

### Implementation Notes
- Helm chart with cloud-specific values files: `values-oke.yaml`, `values-gke.yaml`, `values-aks.yaml`
- Cloud provider differences handled via Helm templating
- Scripts: `setup-cluster.sh` with `--provider` flag
- Documentation includes setup for all three providers

---

## Decision 5: Monitoring and Observability Stack

### Decision
Use **Kubernetes-native monitoring** with flexibility:
- **Metrics**: Prometheus (self-hosted) or cloud provider metrics (GCP Cloud Monitoring, Azure Monitor)
- **Visualization**: Grafana (self-hosted) or cloud provider dashboards
- **Logging**: Kubernetes logs with `kubectl logs` or cloud provider logging
- **Tracing**: OpenTelemetry collector (optional, for distributed tracing)

### Rationale
1. **Free Tier Compatible**: Prometheus/Grafana are free; cloud provider free tiers include basic monitoring
2. **Kubernetes Native**: Prometheus designed for K8s, scrapes metrics from pods automatically
3. **Flexible**: Can use self-hosted (Minikube, Oracle Cloud) or cloud-native (GCP, Azure)
4. **Standard Metrics**: Prometheus format is industry standard, exporters available for all services
5. **Grafana Dashboards**: Pre-built dashboards for Kubernetes, FastAPI, Kafka

### Alternatives Considered
| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| **Datadog** | Comprehensive, great UX | Expensive, no free tier for production | Cost constraint; free tier only for 5 hosts |
| **New Relic** | Full-stack observability | Limited free tier, vendor lock-in | Free tier insufficient for multiple services |
| **ELK Stack (Elasticsearch, Logstash, Kibana)** | Powerful logging and search | Heavy resource usage, complex setup | Resource constraint; Prometheus/Grafana lighter |
| **Cloud-Only (no self-hosted)** | Fully managed, no setup | Vendor lock-in, costs on Oracle Cloud | Must support Oracle Cloud free tier which doesn't include managed monitoring |

### Implementation Notes
- Prometheus deployed via Helm chart (kube-prometheus-stack)
- Grafana dashboards for: Kubernetes cluster, FastAPI metrics, Kafka lag, service health
- OpenTelemetry optional (enable for distributed tracing if needed)
- Alerts configured for: error rate >5%, latency p95 >2s, pod restarts

---

## Decision 6: CI/CD Pipeline

### Decision
Use **GitHub Actions** for automated build, test, and deployment

### Rationale
1. **Free for Public Repos**: Unlimited minutes for public repositories
2. **Native GitHub Integration**: Triggers on push, PR, manual approval
3. **Kubernetes Support**: Actions available for kubectl, Helm, cloud provider CLIs
4. **Secrets Management**: GitHub Secrets for storing cloud credentials, API keys
5. **Matrix Builds**: Test across multiple environments (local, staging, production)

### Alternatives Considered
| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| **GitLab CI** | Powerful, integrated with GitLab | Requires GitLab (project uses GitHub) | Project already on GitHub; no migration needed |
| **Jenkins** | Highly customizable, self-hosted | Requires server, complex setup, maintenance overhead | Free tier constraint; GitHub Actions simpler |
| **CircleCI** | Fast, good UX | Limited free tier (2,500 credits/month) | GitHub Actions more generous for public repos |
| **Manual Deployment** | No CI/CD setup needed | Error-prone, slow, not repeatable | Constitution requires automated deployment; manual violates best practices |

### Implementation Notes
- Workflows: `build-and-test.yml`, `deploy-staging.yml`, `deploy-production.yml`
- Build: Docker images pushed to GitHub Container Registry (ghcr.io)
- Test: pytest (backend), Playwright (frontend), Helm lint (manifests)
- Deploy: Helm upgrade with rollback on failure
- Security: Dependency scanning with `npm audit`, `safety` (Python), Trivy (container images)

---

## Decision 7: Database Schema Extensions

### Decision
Extend existing **Neon Serverless PostgreSQL** schema with new tables:
- `recurring_patterns` (task recurrence configuration)
- `reminders` (scheduled reminder events)
- `audit_logs` (complete task operation history)
- Extend `tasks` table with: `priority`, `tags`, `due_date`, `reminder_offset`

### Rationale
1. **Backward Compatibility**: Existing `tasks` table structure preserved, new columns added
2. **Normalized Design**: Recurring patterns separate table (1:1 with tasks), avoids JSON columns
3. **Query Performance**: Indexes on `user_id`, `due_date`, `priority`, `tags` for fast search/filter
4. **Audit Trail**: Separate `audit_logs` table for compliance (90-day retention)
5. **Neon Compatibility**: Uses standard PostgreSQL features, no Neon-specific extensions

### Alternatives Considered
| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| **JSON Columns for Metadata** | Flexible schema, fewer tables | Harder to query, no indexes on JSON fields | Search/filter performance critical; JSON queries slow |
| **Separate Database for Events** | Event store isolation | Additional database cost, complexity | Free tier constraint; Neon Serverless sufficient |
| **NoSQL (MongoDB)** | Flexible schema, good for events | Different tech stack, no free tier equivalent to Neon | Must use existing Neon DB; no additional databases allowed |
| **Event Sourcing (full)** | Complete audit trail, time travel | Complex, requires event replay logic | Overkill for requirements; audit logs sufficient |

### Implementation Notes
- SQLModel models for all new tables
- Alembic migrations for schema changes
- Indexes: `CREATE INDEX idx_tasks_user_due ON tasks(user_id, due_date)`
- Foreign keys: `recurring_patterns.task_id → tasks.id`, `reminders.task_id → tasks.id`

---

## Decision 8: Real-Time Updates Mechanism

### Decision
Use **WebSocket connections** for real-time task updates across devices

### Rationale
1. **Bi-Directional**: WebSocket supports server-push and client-send (required for <2s latency)
2. **Efficient**: Single persistent connection, no polling overhead
3. **Dapr Support**: Dapr can proxy WebSocket connections for service discovery
4. **Browser Support**: Native WebSocket API in all modern browsers
5. **Scalability**: WebSocket connections can be load-balanced across multiple backend instances

### Alternatives Considered
| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| **Server-Sent Events (SSE)** | Simpler than WebSocket, HTTP-based | One-way only (server to client), no client-send | Need bi-directional for future features (typing indicators, presence) |
| **Polling (short/long)** | Simplest, no persistent connections | High latency, inefficient, server load | Cannot meet <2s latency requirement reliably |
| **Kafka Direct (client-side)** | Real-time event stream | Exposes Kafka to clients, security risk, complex | Kafka should be internal only; WebSocket is client-facing abstraction |

### Implementation Notes
- WebSocket endpoint: `wss://api.example.com/ws/tasks`
- Authentication: JWT token in WebSocket handshake
- Message format: JSON with `event_type`, `task_id`, `task_data`
- Backend publishes to Kafka `task-updates` topic, WebSocket service consumes and broadcasts
- Optional: Separate WebSocket service (microservice) or embed in main API

---

## Decision 9: Notification Delivery Mechanism

### Decision
Use **Web Push API** for browser notifications (no email/SMS)

### Rationale
1. **Browser Native**: Web Push API supported in Chrome, Firefox, Edge, Safari
2. **No External Service**: No cost for push notifications (unlike email/SMS)
3. **User Consent**: Browser prompts for permission, GDPR-compliant
4. **Background Delivery**: Notifications delivered even when tab closed (service worker)
5. **Free Tier Compatible**: No third-party service costs

### Alternatives Considered
| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| **Email Notifications** | Universal, no browser required | Requires email service (SendGrid, Mailgun), costs money | Free tier constraint; Web Push is free |
| **SMS Notifications** | High open rate, mobile-friendly | Expensive ($0.01-0.05 per SMS), requires Twilio/similar | Cost prohibitive for free tier |
| **In-App Only** | Simplest, no external dependencies | User must have app open, misses reminders | Defeats purpose of reminders; need background delivery |
| **Firebase Cloud Messaging (FCM)** | Free, reliable, mobile support | Requires Firebase account, vendor lock-in | Web Push API is standard, no vendor lock-in |

### Implementation Notes
- Frontend: Service worker registers for push notifications
- Backend: Stores push subscription (endpoint, keys) in `user_preferences` table
- Notification service: Uses `pywebpush` library to send notifications
- Payload: JSON with task title, due time, action buttons (snooze, complete)

---

## Decision 10: Helm Chart Strategy

### Decision
Use **single Helm chart** with multiple values files for different environments

### Rationale
1. **DRY Principle**: Single source of truth for Kubernetes manifests
2. **Environment Parity**: Same chart ensures local/staging/production consistency
3. **Parameterization**: Values files customize for environment (replicas, resources, ingress)
4. **Version Control**: Chart version tracks application version
5. **Rollback Support**: Helm rollback command for failed deployments

### Alternatives Considered
| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| **Separate Charts per Environment** | Full flexibility per environment | Duplication, drift between environments | Violates DRY; hard to maintain consistency |
| **Kustomize** | Kubernetes-native, no templating | Less powerful than Helm, no rollback | Helm more mature, better rollback support |
| **Raw Manifests** | Simplest, no abstraction | No parameterization, manual updates | Cannot customize for local vs cloud without duplication |

### Implementation Notes
- Chart structure: `helm/todo-app/`
- Values files: `values.yaml` (defaults), `values-local.yaml`, `values-oke.yaml`, `values-gke.yaml`, `values-aks.yaml`
- Helm hooks: `pre-install` for database migrations, `post-install` for smoke tests
- Chart dependencies: Kafka (Strimzi), Dapr (dapr/dapr)

---

## Research Summary

### Key Technology Decisions
1. **Event Streaming**: Kafka-compatible (Strimzi or Redpanda Cloud)
2. **Distributed Runtime**: Dapr for infrastructure abstraction
3. **Local Development**: Minikube with Helm charts
4. **Cloud Providers**: Oracle Cloud (preferred), GCP, Azure
5. **Monitoring**: Prometheus + Grafana (self-hosted or cloud-native)
6. **CI/CD**: GitHub Actions
7. **Database**: Extend Neon PostgreSQL schema
8. **Real-Time Updates**: WebSocket connections
9. **Notifications**: Web Push API
10. **Deployment**: Single Helm chart with environment-specific values

### Alignment with Constitution
- ✅ **Cloud-Native Architecture**: Stateless services, Kubernetes-native, horizontal scaling
- ✅ **Free Tier Compatible**: All technologies have free tier or open-source options
- ✅ **Portability**: Multi-cloud support, no vendor lock-in
- ✅ **Spec-Driven**: All decisions traced to functional requirements
- ✅ **Production-Ready**: Monitoring, CI/CD, rollback support

### Next Steps
Proceed to **Phase 1: Design & Contracts** to create:
1. `data-model.md` - Database schema and entity relationships
2. `contracts/` - API contracts (OpenAPI specs)
3. `quickstart.md` - Local development setup guide
4. Update agent context with new technologies
