# Implementation Plan: Local Kubernetes Deployment

**Branch**: `004-kubernetes-deployment` | **Date**: 2026-01-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-kubernetes-deployment/spec.md`

## Summary

Deploy the Todo Chatbot application stack to local Kubernetes using Minikube. The implementation will containerize Phase III frontend and backend applications, create Helm charts for repeatable deployments, and integrate AI-assisted DevOps tools (kubectl-ai, Kagent, Gordon). All services will run on a single-node Minikube cluster for local development and testing without cloud costs.

## Technical Context

**Language/Version**: N/A (Infrastructure - Docker, Helm, Kubernetes manifests)
**Primary Dependencies**: Docker Desktop 4.53+, Minikube, Helm 3.x, kubectl, kubectl-ai, Kagent, Gordon (Docker AI)
**Storage**: ConfigMaps for config, Secrets for sensitive data, PersistentVolumeClaim for PostgreSQL data
**Testing**: `helm test`, `kubectl` validation commands, curl health checks
**Target Platform**: Minikube single-node Kubernetes cluster (Linux/Darwin/Windows)
**Project Type**: Infrastructure deployment (not application development)
**Performance Goals**: Pod startup <60s, pod-to-pod communication <500ms, rollback <30s
**Constraints**: Local development only, no cloud resources, resource-efficient (4GB RAM max)
**Scale/Scope**: Single user development environment, 2-3 replicas for stateless services

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Phase-Gated Evolution (II) | ✅ PASS | Phase III source code exists and is functional |
| Cloud-Native Architecture (VI) | ✅ PASS | Stateless servers, container-first design, Helm charts |
| Stateless Servers (Arch) | ✅ PASS | Backend is stateless, frontend is SPA, session in DB |
| Explicit Data Ownership (Arch) | ✅ PASS | Existing Phase III has user_id on all entities |
| Clear Service Boundaries (Arch) | ✅ PASS | Backend API, Frontend SPA, AI Service clearly separated |
| Container-First (VI) | ✅ PASS | Docker images required, Helm charts for deployment |
| No .env in Source (Security) | ✅ PASS | Using ConfigMaps/Secrets for K8s deployment |

## Project Structure

### Documentation (this feature)

```text
specs/004-kubernetes-deployment/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (this section)
├── data-model.md        # Phase 1 output (Kubernetes resources)
├── quickstart.md        # Phase 1 output (deployment guide)
├── contracts/           # Phase 1 output (Helm values schema)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Kubernetes deployment artifacts
k8s/
├── charts/
│   └── todoboard/
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── values-minikube.yaml
│       └── templates/
│           ├── _helpers.tpl
│           ├── deployment-frontend.yaml
│           ├── deployment-backend.yaml
│           ├── deployment-postgres.yaml
│           ├── service-frontend.yaml
│           ├── service-backend.yaml
│           ├── service-postgres.yaml
│           ├── configmap.yaml
│           ├── secret.yaml
│           └── pvc.yaml

# Docker build context
phase3-todo-ai-chatbot/
├── frontend/Dockerfile      # Already exists in phase3
├── backend/Dockerfile       # Already exists in phase3
└── ...
```

**Structure Decision**: Kubernetes artifacts placed in `k8s/` directory at repository root. Helm chart `todoboard` follows standard chart structure. PostgreSQL deployed as StatefulSet with PVC for data persistence. Frontend and backend as Deployments with Services.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

---

# Phase 0: Research

## Technical Decisions Requiring Research

### Decision 1: PostgreSQL Deployment Strategy

**Question**: Should PostgreSQL run inside Minikube (container) or connect to external Neon?

**Options**:
- **Option A**: Deploy PostgreSQL container inside Minikube
  - Pros: Fully self-contained, no external dependencies, matches production-like setup
  - Cons: Resource consumption, data persistence complexity
- **Option B**: Connect to existing Neon database (external)
  - Pros: Lower resource usage, uses production database
  - Cons: Requires network connectivity, may have latency

**Recommendation**: Option A (PostgreSQL in Minikube) for true local development experience.

### Decision 2: Service Exposure Method

**Question**: How should frontend/backend be exposed outside Minikube?

**Options**:
- **Option A**: NodePort Service
  - Pros: Simple, works out of box
  - Cons: Fixed port range (30000-32767)
- **Option B**: Ingress with ingress-nginx
  - Pros: Standard routing, host-based paths
  - Cons: Requires ingress controller addon
- **Option C**: Minikube tunnel
  - Pros: LoadBalancer type works
  - Cons: Requires running tunnel command

**Recommendation**: Option C (Minikube tunnel with LoadBalancer) for simplicity on local cluster.

### Decision 3: Resource Limits

**Question**: What resource limits (CPU/memory) should be set for containers?

**Options**:
- **Option A**: No limits (Guaranteed QoS)
  - Pros: No OOM kills
  - Cons: May consume excessive resources
- **Option B**: Conservative limits (512MB RAM, 0.5 CPU)
  - Pros: Resource efficient
  - Cons: May be too restrictive
- **Option C**: Moderate limits (1GB RAM, 1 CPU)
  - Pros: Balanced approach
  - Cons: Higher resource usage

**Recommendation**: Option C with configurable values.yaml for tuning.

### Decision 4: AI Tools Integration

**Question**: How to integrate kubectl-ai and Kagent for operations?

**Options**:
- **Option A**: Document commands only
  - Pros: Simple, no integration code
  - Cons: Manual operations
- **Option B**: Shell scripts wrapping commands
  - Pros: Automated, repeatable
  - Cons: Additional scripts to maintain
- **Option C**: Claude Code agent skills
  - Pros: Reusable, documented, bonus points
  - Cons: More upfront work

**Recommendation**: Option C (Claude Code agent skills) per constitution principle VII.

---

## Phase 0 Output: research.md

```markdown
# Research: Local Kubernetes Deployment

## PostgreSQL Deployment

**Decision**: Deploy PostgreSQL container inside Minikube

**Rationale**:
- Self-contained development environment
- No external dependencies or network issues
- Demonstrates StatefulSet + PVC patterns
- Matches architecture patterns for Phase V cloud deployment

**Implementation**:
- PostgreSQL 16 as Deployment with 1 replica
- PersistentVolumeClaim for data directory
- ConfigMap for postgresql.conf
- Secret for postgres password

**Alternatives Considered**:
- Neon external connection: Rejected because local dev should be offline-capable
- No database: Rejected because functionality testing requires data persistence

---

## Service Exposure

**Decision**: Use Minikube tunnel with LoadBalancer type Services

**Rationale**:
- Minikube tunnel creates virtual IPs for LoadBalancer services
- Simpler than Ingress (no controller installation needed)
- Works consistently across OS platforms
- Standard LoadBalancer pattern transfers to cloud K8s

**Implementation**:
- frontend Service type: LoadBalancer
- backend Service type: ClusterIP (internal only)
- postgres Service type: ClusterIP (internal only)
- Command: `minikube tunnel` in separate terminal

**Alternatives Considered**:
- NodePort: Rejected due to non-standard ports in URL
- Ingress: Rejected requires nginx-ingress addon installation

---

## Resource Limits

**Decision**: Moderate, configurable limits with burst capability

**Rationale**:
- Provides headroom for development workloads
- Prevents single pod from consuming all cluster resources
- Configurable via values.yaml for different machine capacities

**Implementation** (in values.yaml):
```yaml
frontend:
  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "500m"

backend:
  resources:
    requests:
      memory: "512Mi"
      cpu: "200m"
    limits:
      memory: "1Gi"
      cpu: "1000m"

postgres:
  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "500m"
```

**Alternatives Considered**:
- No limits: Rejected - allows unbounded resource consumption
- Conservative limits: Rejected - insufficient for AI chatbot operations

---

## AI Tools Integration

**Decision**: Create Claude Code agent skills for kubectl-ai and Kagent

**Rationale**:
- Per constitution principle VII: "Reusable Intelligence via Claude Subagents"
- Captures reusable knowledge for bonus points
- Documents best practices for AI-assisted operations

**Skills to Create**:
1. `.claude/skills/kubectl-ai-ops/` - Common kubectl-ai commands
2. `.claude/skills/kagent-health/` - Kagent cluster health commands

**Implementation**:
- Skills follow Claude Code skill format
- Include examples, best practices, common patterns

---

## Docker Image Strategy

**Decision**: Multi-stage builds with kaniko for local registry

**Rationale**:
- Phase III already has Dockerfiles
- Need to push to Minikube's Docker daemon or local registry
- Minikube's `eval $(minikube docker-env)` uses host Docker

**Implementation**:
```bash
# Build with Minikube Docker
eval $(minikube docker-env)
docker build -t todoboard-frontend:latest phase3-todo-ai-chatbot/frontend/
docker build -t todoboard-backend:latest phase3-todo-ai-chatbot/backend/

# Or use local registry
kubectl apply -f https://raw.githubusercontent.com/kubernetes/minikube/master/deploy/addons/registry-aliases/registry-aliases.yaml
```

---

## Helm Chart Structure

**Decision**: Single umbrella chart with subcharts for each service

**Rationale**:
- Simpler deployment (one helm install)
- Shared values across services
- Clear dependency management

**Chart.yaml dependencies**:
```yaml
dependencies:
  - name: common
    version: "0.0.1"
    repository: "file://../common"
```

**Alternative Considered**: Separate charts per service - Rejected for deployment complexity
```

---

# Phase 1: Design & Contracts

## Data Model: Kubernetes Resources

### Entities

#### Docker Image
- **Purpose**: Containerized application artifact
- **Fields**:
  - `name`: string (e.g., todoboard-frontend)
  - `tag`: string (e.g., latest, dev)
  - `pullPolicy`: "Always" | "IfNotPresent" | "Never"

#### ConfigMap
- **Purpose**: Non-sensitive configuration storage
- **Fields**:
  - `name`: string
  - `data`: map[string]string (key-value pairs)
  - `namespace`: string (default: default)

#### Secret
- **Purpose**: Sensitive data storage (base64 encoded)
- **Fields**:
  - `name`: string
  - `type`: "Opaque" | "kubernetes.io/basic-auth"
  - `data`: map[string]string (base64 encoded)

#### PersistentVolumeClaim
- **Purpose**: Storage request for persistent data
- **Fields**:
  - `name`: string
  - `storageClassName`: string
  - `accessModes`: ["ReadWriteOnce"]
  - `resources.requests.storage`: string (e.g., "1Gi")

#### Deployment
- **Purpose**: Manages pod replicas
- **Fields**:
  - `name`: string
  - `replicas`: integer
  - `selector.matchLabels`: map[string]string
  - `template.spec.containers`: []Container
  - `strategy.type`: "RollingUpdate" | "Recreate"

#### Service
- **Purpose**: Network endpoint for pods
- **Fields**:
  - `name`: string
  - `type`: "ClusterIP" | "NodePort" | "LoadBalancer"
  - `selector`: map[string]string (pods to target)
  - `ports`: []ServicePort

#### Pod (managed by Deployment)
- **Purpose**: Running container instance
- **Fields**:
  - `spec.containers`: []Container
  - `spec.volumes`: []Volume
  - `spec.resources`: ResourceRequirements

### Validation Rules

- All resource names must be lowercase, alphanumeric, max 63 chars
- ConfigMaps/Secrets must be in same namespace as consuming pods
- PVC storage request must be <= available PV capacity
- Container ports must be unique per pod
- Service selector must match pod labels

### State Transitions

```
Deployment: Pending → Creating → Running → Updating → Running (RollingUpdate)
Pod: Pending → ContainerCreating → Running → Succeeded/Failed
PVC: Pending → Bound → Released (on delete)
```

---

## API Contracts: Helm Values Schema

### values.yaml Structure

```yaml
# Global settings
global:
  imagePullPolicy: "IfNotPresent"
  imageRegistry: ""
  namespace: "todoboard"

# Frontend configuration
frontend:
  enabled: true
  replicaCount: 2
  image:
    repository: "todoboard-frontend"
    tag: "latest"
    pullPolicy: "IfNotPresent"
  service:
    type: "LoadBalancer"
    port: 3000
  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "500m"
  env:
    - name: "NEXT_PUBLIC_API_URL"
      value: "http://backend:8000"

# Backend configuration
backend:
  enabled: true
  replicaCount: 2
  image:
    repository: "todoboard-backend"
    tag: "latest"
    pullPolicy: "IfNotPresent"
  service:
    type: "ClusterIP"
    port: 8000
  resources:
    requests:
      memory: "512Mi"
      cpu: "200m"
    limits:
      memory: "1Gi"
      cpu: "1000m"
  env:
    - name: "DATABASE_URL"
      value: "postgresql://user:pass@postgres:5432/todoboard"
    - name: "OPENAI_API_KEY"
      valueFrom:
        secretKeyRef:
          name: todoboard-secrets
          key: openai-api-key

# PostgreSQL configuration
postgres:
  enabled: true
  replicaCount: 1
  image:
    repository: "postgres"
    tag: "16"
    pullPolicy: "IfNotPresent"
  service:
    type: "ClusterIP"
    port: 5432
  persistence:
    enabled: true
    storageClass: "standard"
    size: "1Gi"
  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "500m"
  env:
    - name: "POSTGRES_USER"
      value: "todoboard"
    - name: "POSTGRES_PASSWORD"
      valueFrom:
        secretKeyRef:
          name: todoboard-secrets
          key: postgres-password
    - name: "POSTGRES_DB"
      value: "todoboard"

# Ingress configuration (optional)
ingress:
  enabled: false
  className: ""
  hosts:
    - host: "todoboard.local"
      paths:
        - path: "/"
          pathType: "Prefix"
```

### values-minikube.yaml (Minikube-specific overrides)

```yaml
# Use LoadBalancer with Minikube tunnel
frontend:
  service:
    type: "LoadBalancer"

# PostgreSQL with hostPath for simplicity
postgres:
  persistence:
    storageClass: "standard"
  # Note: hostPath persistence is not recommended for production
```

---

## Quickstart Guide

```markdown
# Quickstart: Local Kubernetes Deployment

## Prerequisites

```bash
# Check installed versions
docker --version      # Requires 4.53+ for Gordon
minikube version      # Latest stable
helm version          # 3.x
kubectl version --client
kubectl-ai version    # Optional but recommended
```

## Setup

### 1. Start Minikube

```bash
# Start with adequate resources
minikube start --cpus=2 --memory=4096 --driver=docker

# Enable registry addon (optional, for local images)
minikube addons enable registry
```

### 2. Build Docker Images

```bash
# Point Docker to Minikube
eval $(minikube docker-env)

# Build images
docker build -t todoboard-frontend:latest phase3-todo-ai-chatbot/frontend/
docker build -t todoboard-backend:latest phase3-todo-ai-chatbot/backend/
```

### 3. Deploy with Helm

```bash
# Create namespace
kubectl create namespace todoboard

# Create secrets
kubectl create secret generic todoboard-secrets \
  --from-literal=postgres-password=your-secure-password \
  --from-literal=openai-api-key=your-api-key \
  --namespace=todoboard

# Install chart
helm install todoboard ./k8s/charts/todoboard \
  --namespace=todoboard \
  --values ./k8s/charts/todoboard/values-minikube.yaml

# Wait for pods
kubectl wait --for=condition=ready pod -l app=todoboard-frontend --timeout=300s
kubectl wait --for=condition=ready pod -l app=todoboard-backend --timeout=300s
kubectl wait --for=condition=ready pod -l app=todoboard-postgres --timeout=300s
```

### 4. Access Application

```bash
# Start tunnel in separate terminal
minikube tunnel

# Get frontend URL
echo "Frontend: http://$(kubectl get svc todoboard-frontend -n todoboard -o jsonpath='{.status.loadBalancer.ingress[0].ip}'):3000"
echo "Backend API: http://$(kubectl get svc todoboard-backend -n todoboard -o jsonpath='{.spec.clusterIP}'):8000"
```

## Verify Deployment

```bash
# Check pod status
kubectl get pods -n todoboard

# Check logs
kubectl logs -n todoboard -l app=todoboard-backend --tail=100

# Test health endpoint
curl http://localhost:3000/api/health

# Test API
curl http://localhost:8000/health
```

## Common Operations

### Scale services

```bash
kubectl scale deployment todoboard-frontend -n todoboard --replicas=3
```

### View logs

```bash
kubectl logs -n todoboard -l app=todoboard-backend -f
```

### Rollback

```bash
helm rollback todoboard 1 -n todoboard
```

### Uninstall

```bash
helm uninstall todoboard -n todoboard
kubectl delete namespace todoboard
```

## AI-Assisted Operations

### Using kubectl-ai

```bash
# Natural language kubectl commands
kubectl-ai "scale the frontend to 3 replicas"
kubectl-ai "check why pods are not starting"
kubectl-ai "show me recent errors in backend logs"
```

### Using Kagent

```bash
# Cluster health analysis
kagent "analyze cluster health"
kagent "optimize resource allocation"
kagent "what's my current capacity"
```

## Troubleshooting

### Pods not starting

```bash
# Check events
kubectl describe pod <pod-name> -n todoboard

# Check images exist
docker images | grep todoboard
```

### Connection refused

```bash
# Verify tunnel is running
minikube tunnel --cleanup

# Check services
kubectl get svc -n todoboard
```
```

---

## Agent Context Update

To be updated after plan completion via `.specify/scripts/bash/update-agent-context.sh`

### New Technologies Added

- Minikube: Local Kubernetes cluster management
- Helm 3: Kubernetes package manager
- kubectl-ai: Natural language kubectl commands
- Kagent: AI-assisted Kubernetes cluster management
- Gordon: Docker AI Agent for containerization

### Existing Technologies Used

- Docker: Container runtime (from Phase III)
- PostgreSQL: Database (from Phase III)
- FastAPI: Backend API (from Phase III)
- Next.js: Frontend (from Phase III)
