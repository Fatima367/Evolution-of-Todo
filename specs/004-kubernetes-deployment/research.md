# Research: Local Kubernetes Deployment

**Feature**: 004-kubernetes-deployment
**Date**: 2026-01-11
**Purpose**: Research containerization, Kubernetes deployment patterns, and Helm chart best practices for deploying the Phase III Todo application to a local Minikube cluster.

## Research Areas

### 1. Container Image Strategy

**Decision**: Multi-stage Docker builds with production-optimized images

**Rationale**:
- **Backend (FastAPI)**: Use Python 3.13-slim base image with multi-stage build to minimize image size. Install only production dependencies in final stage. Use non-root user for security.
- **Frontend (Next.js)**: Use Node.js 20-alpine base image with multi-stage build. Build static assets in build stage, serve with standalone output in production stage. Reduces image size from ~1GB to ~150MB.
- **Database (PostgreSQL)**: Use official postgres:16-alpine image. Lightweight and well-maintained by PostgreSQL team.

**Alternatives Considered**:
- **Single-stage builds**: Rejected - includes build tools and dev dependencies in production image, increasing size and attack surface
- **Distroless images**: Rejected for Phase IV - adds complexity for debugging in local development. Consider for Phase V production deployment.
- **Custom base images**: Rejected - unnecessary maintenance overhead for local deployment

**Best Practices Applied**:
- Layer caching optimization (COPY package files before source code)
- .dockerignore files to exclude unnecessary files (node_modules, .git, tests)
- Health check endpoints in application code (FastAPI /health, Next.js /api/health)
- Environment variable injection for configuration (DATABASE_URL, API_URL, etc.)

---

### 2. Kubernetes Resource Configuration

**Decision**: Separate Deployment resources for each service with appropriate resource limits

**Rationale**:
- **Deployments**: One Deployment per service (frontend, backend, database) for independent scaling and lifecycle management
- **Services**: ClusterIP for backend and database (internal only), NodePort or LoadBalancer for frontend (external access)
- **Resource Limits**: Set memory limits (backend: 512Mi, frontend: 256Mi, database: 512Mi) to prevent resource exhaustion on developer laptops
- **Replicas**: Single replica for database (StatefulSet not needed for local dev), 1-2 replicas for frontend/backend

**Alternatives Considered**:
- **Single Deployment with multiple containers**: Rejected - violates separation of concerns, makes scaling and updates difficult
- **StatefulSet for database**: Rejected for Phase IV - unnecessary complexity for single-node local deployment. Consider for Phase V with clustering.
- **DaemonSet**: Not applicable - no need to run pods on every node in single-node Minikube

**Best Practices Applied**:
- Liveness and readiness probes for all services (HTTP health checks)
- Rolling update strategy with maxSurge: 1, maxUnavailable: 0 for zero-downtime updates
- Pod anti-affinity rules (not needed for single-node, but documented for Phase V)
- Resource requests and limits to ensure QoS (Guaranteed class for database, Burstable for frontend/backend)

---

### 3. Configuration Management

**Decision**: ConfigMaps for non-sensitive configuration, Secrets for sensitive data, Helm values for environment-specific overrides

**Rationale**:
- **ConfigMap**: Store application configuration (API endpoints, feature flags, log levels). Mounted as environment variables or volume files.
- **Secrets**: Store sensitive data (database passwords, API keys, JWT secrets). Base64-encoded, mounted as environment variables. Never commit to git.
- **Helm Values**: Provide default values in values.yaml, environment-specific overrides in values-minikube.yaml. Enables reproducible deployments across environments.

**Alternatives Considered**:
- **Hardcoded configuration in Dockerfiles**: Rejected - requires rebuilding images for configuration changes
- **External secret management (Vault, AWS Secrets Manager)**: Rejected for Phase IV - adds complexity and external dependencies. Consider for Phase V cloud deployment.
- **Single values.yaml file**: Rejected - mixing local and production config increases risk of misconfiguration

**Best Practices Applied**:
- Separate values files per environment (values-minikube.yaml, values-production.yaml for Phase V)
- .env.example files in repository, actual .env files in .gitignore
- Secret rotation strategy documented (manual for Phase IV, automated for Phase V)
- Principle of least privilege (each service gets only the secrets it needs)

---

### 4. Data Persistence Strategy

**Decision**: PersistentVolumeClaim (PVC) with local storage for database, no persistence for frontend/backend

**Rationale**:
- **Database**: Requires persistent storage to survive pod restarts. Use PVC with 5Gi capacity, ReadWriteOnce access mode. Minikube provides default StorageClass (hostPath) for local development.
- **Frontend/Backend**: Stateless services, no persistent storage needed. All state in database or JWT tokens.
- **Backup Strategy**: Manual database dumps for Phase IV (pg_dump). Automated backups for Phase V.

**Alternatives Considered**:
- **EmptyDir volumes**: Rejected - data lost on pod restart, violates FR-004 (data persistence requirement)
- **HostPath volumes**: Rejected - ties deployment to specific node, not portable across environments
- **Cloud storage (EBS, GCE PD)**: Not applicable for Phase IV local deployment. Required for Phase V.

**Best Practices Applied**:
- PVC separate from Deployment (allows data to survive Deployment deletion)
- Storage class selection via Helm values (minikube: standard, cloud: gp3/pd-ssd)
- Volume mount paths follow Linux FHS conventions (/var/lib/postgresql/data)
- Backup and restore procedures documented in quickstart.md

---

### 5. Networking and Service Discovery

**Decision**: ClusterIP for internal services, NodePort for external access in Minikube, Ingress for Phase V

**Rationale**:
- **Backend Service**: ClusterIP type, port 8000. Accessible only within cluster. Frontend communicates via service DNS (todoboard-backend.default.svc.cluster.local).
- **Database Service**: ClusterIP type, port 5432. Accessible only by backend. Service name: todoboard-postgres.
- **Frontend Service**: NodePort type, port 3000 → 30000. Accessible from host machine via minikube ip:30000. LoadBalancer type for Phase V cloud deployment.
- **Ingress**: Optional for Phase IV (adds complexity). Required for Phase V with custom domains and TLS.

**Alternatives Considered**:
- **LoadBalancer for Minikube**: Requires minikube tunnel, adds setup complexity. NodePort simpler for local dev.
- **Ingress for Phase IV**: Rejected - requires Ingress controller installation (nginx, traefik), adds complexity without benefit for single-user local deployment
- **HostNetwork**: Rejected - bypasses Kubernetes networking, defeats purpose of learning K8s

**Best Practices Applied**:
- Service naming convention: {chart-name}-{component} (todoboard-backend, todoboard-frontend)
- DNS-based service discovery (no hardcoded IPs)
- Network policies to restrict traffic (frontend → backend only, backend → database only)
- Health check endpoints for service readiness

---

### 6. Helm Chart Structure

**Decision**: Single Helm chart with subcharts for each service, templated resources with values-driven configuration

**Rationale**:
- **Chart Organization**: One chart (todoboard) with templates for all resources. Simpler than multiple charts for small application.
- **Templating**: Use Helm template functions ({{ .Values.backend.image }}, {{ .Release.Name }}) for flexibility. Enables deploying multiple instances with different names.
- **Values Hierarchy**: Default values in values.yaml, environment overrides in values-{env}.yaml, user overrides via --set flags.
- **Hooks**: Pre-install hook for database migrations (alembic upgrade head). Ensures schema up-to-date before application starts.

**Alternatives Considered**:
- **Separate charts per service**: Rejected - increases complexity, requires managing chart dependencies. Better for microservices with independent release cycles.
- **Kustomize instead of Helm**: Rejected - Helm provides better templating, package management, and rollback capabilities. Kustomize better for simple overlays.
- **Plain YAML manifests**: Rejected - no templating or configuration management, requires manual editing for different environments

**Best Practices Applied**:
- Chart.yaml with semantic versioning (0.1.0 for Phase IV)
- values.yaml with comprehensive comments explaining each field
- NOTES.txt template with post-install instructions (how to access application)
- _helpers.tpl for reusable template snippets (labels, selectors)
- helm lint and helm test for validation

---

### 7. Database Migration Strategy

**Decision**: Alembic migrations run as Helm pre-install/pre-upgrade hook

**Rationale**:
- **Timing**: Migrations must run before application pods start to ensure schema compatibility
- **Implementation**: Kubernetes Job resource with hook annotation (helm.sh/hook: pre-install,pre-upgrade). Runs alembic upgrade head in backend container.
- **Failure Handling**: Hook failure prevents deployment, ensuring database schema is valid before application starts
- **Rollback**: Manual rollback via alembic downgrade for Phase IV. Automated rollback strategy for Phase V.

**Alternatives Considered**:
- **Migrations in application startup**: Rejected - race conditions with multiple replicas, no failure isolation
- **Manual migrations**: Rejected - error-prone, not reproducible, violates automation principle
- **Init containers**: Considered but rejected - hooks provide better lifecycle management and failure handling

**Best Practices Applied**:
- Idempotent migrations (safe to run multiple times)
- Migration testing in CI/CD pipeline (Phase V)
- Database backup before migrations (documented in quickstart.md)
- Hook weight ordering (migrations before application deployment)

---

### 8. Health Checks and Observability

**Decision**: HTTP-based liveness and readiness probes, structured logging to stdout

**Rationale**:
- **Liveness Probes**: Detect crashed/deadlocked containers. HTTP GET to /health endpoint. Failure triggers container restart.
- **Readiness Probes**: Detect when container is ready to serve traffic. HTTP GET to /health endpoint with database connectivity check. Failure removes pod from service endpoints.
- **Startup Probes**: Allow slow-starting containers (database) extra time before liveness checks begin. Prevents premature restarts.
- **Logging**: JSON-structured logs to stdout/stderr. Kubernetes captures and makes available via kubectl logs. Centralized logging (ELK, Loki) for Phase V.

**Alternatives Considered**:
- **TCP probes**: Rejected - less informative than HTTP, can't check application health
- **Exec probes**: Rejected - requires shell in container, increases image size
- **No probes**: Rejected - violates production-readiness, can't detect failures

**Best Practices Applied**:
- Initial delay periods to allow application startup (backend: 10s, frontend: 5s, database: 30s)
- Failure thresholds (3 consecutive failures before action)
- Timeout values (5s for HTTP requests)
- Separate /health (liveness) and /ready (readiness) endpoints for fine-grained control

---

### 9. Security Considerations

**Decision**: Non-root containers, read-only root filesystem where possible, network policies, secret management

**Rationale**:
- **User Context**: Run containers as non-root user (UID 1000). Reduces impact of container escape vulnerabilities.
- **Filesystem**: Read-only root filesystem for frontend/backend. Writable volumes only where needed (/tmp, /var/log).
- **Network Policies**: Restrict traffic to minimum required (frontend → backend, backend → database). Deny all other traffic.
- **Secrets**: Kubernetes Secrets for sensitive data. Mounted as environment variables, not files (reduces exposure). Encrypted at rest in etcd (Phase V).

**Alternatives Considered**:
- **Root containers**: Rejected - security risk, violates least privilege principle
- **No network policies**: Rejected - allows unrestricted pod-to-pod communication, increases attack surface
- **Secrets in ConfigMaps**: Rejected - ConfigMaps not encrypted, visible in kubectl describe

**Best Practices Applied**:
- Security contexts in pod specs (runAsNonRoot: true, allowPrivilegeEscalation: false)
- Image scanning for vulnerabilities (manual for Phase IV, automated in CI/CD for Phase V)
- Regular dependency updates (npm audit, pip-audit)
- Principle of least privilege (minimal RBAC permissions)

---

### 10. Development Workflow and Tooling

**Decision**: Minikube for local cluster, kubectl for cluster interaction, Helm for deployment, optional AI tools (kubectl-ai, kagent, Gordon)

**Rationale**:
- **Minikube**: Lightweight, cross-platform, well-documented. Alternatives (kind, k3d) offer similar functionality but Minikube has better Windows support.
- **kubectl**: Standard Kubernetes CLI. Essential for debugging and manual operations.
- **Helm**: Package manager for Kubernetes. Simplifies deployment, configuration management, and rollback.
- **AI Tools**: Optional enhancements for developer experience. kubectl-ai for natural language queries, kagent for cluster analysis, Gordon for Docker operations.

**Alternatives Considered**:
- **Docker Compose**: Rejected - doesn't teach Kubernetes concepts, not portable to cloud
- **kind (Kubernetes in Docker)**: Rejected - better for CI/CD, Minikube better for local development
- **k3s/k3d**: Rejected - lightweight but less feature-complete than Minikube for learning

**Best Practices Applied**:
- Minikube addons (metrics-server, dashboard) for observability
- kubectl aliases and shell completion for productivity
- Helm chart testing (helm lint, helm template, helm test)
- Documentation with step-by-step instructions for setup

---

## Technology Decisions Summary

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Container Runtime | Docker Desktop | Cross-platform, well-documented, includes Kubernetes |
| Base Images | python:3.13-slim, node:20-alpine, postgres:16-alpine | Official images, security updates, minimal size |
| Orchestration | Kubernetes (Minikube) | Industry standard, portable to cloud, learning objective |
| Package Manager | Helm 3+ | Templating, configuration management, rollback support |
| Storage | PersistentVolumeClaim (hostPath) | Data persistence, survives pod restarts |
| Networking | ClusterIP + NodePort | Internal service discovery, external access for frontend |
| Configuration | ConfigMaps + Secrets | Separation of config and code, security for sensitive data |
| Health Checks | HTTP probes | Application-level health verification |
| Migrations | Helm hooks + Alembic | Automated, failure-safe database schema updates |
| Logging | Structured JSON to stdout | Kubernetes-native, ready for centralized logging |

---

## Implementation Priorities

### Phase IV (Local Kubernetes) - Current Focus

1. **P1 - Core Deployment**: Dockerfiles, basic Helm chart, single-replica deployments
2. **P2 - Configuration Management**: ConfigMaps, Secrets, values files
3. **P2 - Data Persistence**: PVC for database, migration hooks
4. **P3 - Observability**: Health probes, structured logging
5. **P3 - Security**: Non-root containers, network policies
6. **P3 - Documentation**: Quickstart guide, troubleshooting

### Phase V (Cloud Kubernetes) - Future Work

1. **Production Readiness**: Multi-replica deployments, HPA, resource quotas
2. **Advanced Networking**: Ingress with TLS, service mesh (Istio/Linkerd)
3. **Observability**: Prometheus metrics, Grafana dashboards, distributed tracing
4. **Security Hardening**: Pod security policies, OPA/Gatekeeper, secret encryption
5. **CI/CD Integration**: GitOps (ArgoCD/Flux), automated testing, canary deployments
6. **Cloud-Specific**: Cloud storage (EBS/GCE PD), cloud load balancers, managed databases

---

## Open Questions and Risks

### Resolved Questions
- ✅ Database persistence strategy: PVC with hostPath StorageClass
- ✅ External access method: NodePort for Minikube (LoadBalancer for Phase V)
- ✅ Migration timing: Helm pre-install/pre-upgrade hooks
- ✅ Configuration management: Helm values with environment-specific overrides

### Remaining Risks

1. **Resource Constraints**: Developer laptops may struggle with 3 services + Minikube overhead
   - **Mitigation**: Set conservative resource limits, document minimum requirements (4GB RAM, 2 CPU)

2. **Windows Compatibility**: Minikube on Windows can have networking issues
   - **Mitigation**: Test on Windows, provide troubleshooting guide, recommend WSL2

3. **Image Build Time**: Multi-stage builds can be slow on first run
   - **Mitigation**: Document layer caching, provide pre-built images for testing

4. **Database Connection Pooling**: Neon Serverless may not work in containerized environment
   - **Mitigation**: Use standard PostgreSQL container for Phase IV, reconnect to Neon for Phase V cloud deployment

5. **AI Tool Availability**: kubectl-ai, kagent, Gordon may not be available in all regions
   - **Mitigation**: Mark as optional, provide standard kubectl alternatives

---

## References

- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Helm Chart Best Practices](https://helm.sh/docs/chart_best_practices/)
- [Docker Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Next.js Docker Deployment](https://nextjs.org/docs/deployment#docker-image)
- [FastAPI Docker Deployment](https://fastapi.tiangolo.com/deployment/docker/)
- [PostgreSQL on Kubernetes](https://www.postgresql.org/docs/current/high-availability.html)
- [Kubernetes Security Best Practices](https://kubernetes.io/docs/concepts/security/overview/)
