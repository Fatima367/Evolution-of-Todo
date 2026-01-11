# Data Model: Kubernetes Deployment Configuration

**Feature**: 004-kubernetes-deployment
**Date**: 2026-01-11
**Purpose**: Define the deployment configuration entities and their relationships for the Kubernetes deployment of the Todo application.

## Overview

This data model describes the deployment configuration entities, not application data entities. The application data model (Tasks, Users, Conversations, Messages) remains unchanged from Phase III. This document focuses on the Kubernetes resources and deployment artifacts that enable the application to run in a containerized, orchestrated environment.

## Core Entities

### 1. Container Image

**Description**: Packaged application code with all dependencies, versioned and tagged for reproducibility.

**Attributes**:
- `name`: Image name (e.g., "todoboard-backend", "todoboard-frontend")
- `registry`: Container registry URL (e.g., "docker.io", "ghcr.io", or local for Minikube)
- `tag`: Version identifier (e.g., "0.1.0", "latest", git commit SHA)
- `digest`: SHA256 hash for immutable image reference
- `size`: Image size in bytes
- `layers`: List of filesystem layers
- `platform`: Target architecture (e.g., "linux/amd64", "linux/arm64")
- `buildContext`: Source directory for Docker build
- `dockerfile`: Path to Dockerfile

**Relationships**:
- One Container Image is referenced by one or more Deployment Configurations
- Container Images are stored in a Container Registry

**Validation Rules**:
- Tag must follow semantic versioning or be "latest"
- Image must be buildable from Phase III source code
- Image must include health check endpoint
- Image must run as non-root user (UID 1000)

**State Transitions**:
- Built → Pushed → Pulled → Running
- Can be rebuilt with same tag (overwrites) or new tag (versioned)

---

### 2. Deployment Configuration

**Description**: Declarative description of how the application should run, including resource requirements, replicas, and environment settings.

**Attributes**:
- `name`: Deployment name (e.g., "todoboard-backend")
- `namespace`: Kubernetes namespace (default: "default")
- `replicas`: Number of pod instances (1-3 for Phase IV)
- `image`: Reference to Container Image entity
- `resources`: CPU and memory requests/limits
  - `requests.cpu`: Minimum CPU (e.g., "100m")
  - `requests.memory`: Minimum memory (e.g., "128Mi")
  - `limits.cpu`: Maximum CPU (e.g., "500m")
  - `limits.memory`: Maximum memory (e.g., "512Mi")
- `env`: Environment variables (from ConfigMap or Secret)
- `ports`: Container ports to expose
- `volumeMounts`: Persistent storage mount points
- `livenessProbe`: Health check for container restart
- `readinessProbe`: Health check for traffic routing
- `strategy`: Update strategy (RollingUpdate, Recreate)

**Relationships**:
- One Deployment Configuration manages multiple Pod instances
- References one Container Image
- References zero or more Configuration Data entities (ConfigMaps)
- References zero or more Secret entities
- References zero or more Persistent Storage entities (PVCs)
- Exposes one or more Service Endpoints

**Validation Rules**:
- Replicas must be >= 1 for frontend/backend, = 1 for database
- Resource limits must be >= resource requests
- Total resource usage must not exceed 4GB RAM (Phase IV constraint)
- Liveness and readiness probes must be defined
- Image pull policy must be "IfNotPresent" for local development

**State Transitions**:
- Created → Progressing → Available → Updating → Available
- Can be scaled (change replicas), updated (change image), or deleted

---

### 3. Persistent Storage

**Description**: Data storage that survives pod lifecycle events, containing task data and conversation history.

**Attributes**:
- `name`: PVC name (e.g., "todoboard-postgres-data")
- `storageClass`: Storage provisioner (e.g., "standard" for Minikube)
- `accessMode`: Access pattern (ReadWriteOnce, ReadWriteMany, ReadOnlyMany)
- `capacity`: Storage size (e.g., "5Gi")
- `volumeMode`: Filesystem or Block
- `mountPath`: Path in container (e.g., "/var/lib/postgresql/data")
- `reclaimPolicy`: What happens when PVC deleted (Retain, Delete)

**Relationships**:
- One Persistent Storage is claimed by one PersistentVolumeClaim
- One PVC is mounted by one or more Pods (depending on accessMode)
- Bound to one PersistentVolume (provisioned by StorageClass)

**Validation Rules**:
- Capacity must be >= 5Gi for database
- AccessMode must be ReadWriteOnce for database (single writer)
- StorageClass must exist in cluster
- MountPath must not conflict with container filesystem

**State Transitions**:
- Pending → Bound → Released
- Data persists across pod restarts and redeployments
- Manual deletion required to reclaim storage

---

### 4. Service Endpoint

**Description**: Network access point that allows communication between application components and external access.

**Attributes**:
- `name`: Service name (e.g., "todoboard-backend")
- `type`: Service type (ClusterIP, NodePort, LoadBalancer)
- `clusterIP`: Internal cluster IP (auto-assigned)
- `ports`: Port mappings
  - `port`: Service port (e.g., 8000)
  - `targetPort`: Container port (e.g., 8000)
  - `nodePort`: External port for NodePort type (e.g., 30000)
  - `protocol`: TCP or UDP
- `selector`: Labels to match pods
- `sessionAffinity`: Client IP or None

**Relationships**:
- One Service Endpoint routes traffic to multiple Pod instances
- Selected by label selectors matching Deployment Configuration
- Referenced by other services via DNS (service-name.namespace.svc.cluster.local)

**Validation Rules**:
- Type must be ClusterIP for backend/database, NodePort for frontend (Phase IV)
- Port must match container port in Deployment Configuration
- NodePort must be in range 30000-32767
- Selector labels must match Deployment Configuration labels

**State Transitions**:
- Created → Active → Deleted
- Endpoints updated automatically as pods are added/removed

---

### 5. Configuration Data

**Description**: Application settings including database connections, API keys, feature flags, and resource limits.

**Attributes**:
- `name`: ConfigMap or Secret name
- `type`: ConfigMap (non-sensitive) or Secret (sensitive)
- `data`: Key-value pairs
  - ConfigMap: Plain text values
  - Secret: Base64-encoded values
- `immutable`: Whether data can be updated (false for Phase IV)

**Common Configuration Keys**:

**Backend ConfigMap**:
- `DATABASE_URL`: PostgreSQL connection string (references Secret for password)
- `CORS_ORIGINS`: Allowed frontend origins
- `LOG_LEVEL`: Logging verbosity (INFO, DEBUG, ERROR)
- `API_PREFIX`: API route prefix (e.g., "/api/v1")

**Frontend ConfigMap**:
- `NEXT_PUBLIC_API_URL`: Backend API URL
- `NEXT_PUBLIC_APP_NAME`: Application name
- `NODE_ENV`: Environment (development, production)

**Secrets**:
- `POSTGRES_PASSWORD`: Database password
- `JWT_SECRET`: JWT signing key
- `OPENAI_API_KEY`: OpenAI API key for chatbot
- `GROQ_API_KEY`: Groq API key for LLM

**Relationships**:
- One Configuration Data entity is referenced by one or more Deployment Configurations
- Mounted as environment variables or volume files in pods

**Validation Rules**:
- Secret values must not be committed to git
- ConfigMap values must not contain sensitive data
- Keys must follow UPPER_SNAKE_CASE convention
- Values must be valid for their data type (URLs, integers, booleans)

**State Transitions**:
- Created → Active → Updated → Active → Deleted
- Updates trigger pod restarts if mounted as environment variables

---

### 6. Deployment Artifact (Helm Chart)

**Description**: Packaged deployment configuration that can be versioned and distributed.

**Attributes**:
- `name`: Chart name (e.g., "todoboard")
- `version`: Chart version (e.g., "0.1.0")
- `appVersion`: Application version (e.g., "1.0.0")
- `description`: Chart description
- `templates`: Kubernetes resource templates
- `values`: Default configuration values
- `dependencies`: Chart dependencies (none for Phase IV)

**Chart Structure**:
```
todoboard/
├── Chart.yaml           # Chart metadata
├── values.yaml          # Default values
├── values-minikube.yaml # Environment-specific overrides
├── templates/           # Resource templates
│   ├── _helpers.tpl     # Template helpers
│   ├── NOTES.txt        # Post-install instructions
│   ├── deployment-*.yaml
│   ├── service-*.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── pvc.yaml
│   ├── ingress.yaml
│   ├── networkpolicy.yaml
│   └── hooks-db-migration.yaml
└── .helmignore          # Files to exclude from chart
```

**Relationships**:
- One Deployment Artifact contains multiple Kubernetes resource templates
- References all other entities (Deployments, Services, ConfigMaps, Secrets, PVCs)
- Can be installed multiple times with different release names

**Validation Rules**:
- Chart version must follow semantic versioning
- All templates must pass `helm lint`
- Values must have default values for all required fields
- NOTES.txt must provide clear post-install instructions

**State Transitions**:
- Packaged → Installed → Upgraded → Rolled Back → Uninstalled
- Each installation creates a Helm Release with revision history

---

## Entity Relationships Diagram

```
┌─────────────────────┐
│ Deployment Artifact │ (Helm Chart)
│   (todoboard)       │
└──────────┬──────────┘
           │ contains
           ▼
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  ┌──────────────┐      ┌──────────────┐               │
│  │ Container    │◄─────│ Deployment   │               │
│  │ Image        │      │ Configuration│               │
│  └──────────────┘      └──────┬───────┘               │
│                               │                        │
│                               │ exposes                │
│                               ▼                        │
│                        ┌──────────────┐               │
│                        │ Service      │               │
│                        │ Endpoint     │               │
│                        └──────────────┘               │
│                                                         │
│  ┌──────────────┐      ┌──────────────┐               │
│  │ Configuration│◄─────│ Deployment   │               │
│  │ Data         │      │ Configuration│               │
│  └──────────────┘      └──────┬───────┘               │
│                               │                        │
│                               │ mounts                 │
│                               ▼                        │
│                        ┌──────────────┐               │
│                        │ Persistent   │               │
│                        │ Storage      │               │
│                        └──────────────┘               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Deployment Configuration Instances

### Backend Deployment

- **Name**: todoboard-backend
- **Image**: todoboard-backend:0.1.0
- **Replicas**: 1
- **Resources**: 100m CPU / 512Mi memory
- **Ports**: 8000 (HTTP)
- **ConfigMap**: backend-config (DATABASE_URL, CORS_ORIGINS, LOG_LEVEL)
- **Secrets**: app-secrets (POSTGRES_PASSWORD, JWT_SECRET, OPENAI_API_KEY)
- **Service**: ClusterIP on port 8000

### Frontend Deployment

- **Name**: todoboard-frontend
- **Image**: todoboard-frontend:0.1.0
- **Replicas**: 1
- **Resources**: 50m CPU / 256Mi memory
- **Ports**: 3000 (HTTP)
- **ConfigMap**: frontend-config (NEXT_PUBLIC_API_URL)
- **Service**: NodePort on port 3000 → 30000

### Database Deployment

- **Name**: todoboard-postgres
- **Image**: postgres:16-alpine
- **Replicas**: 1 (StatefulSet not needed for Phase IV)
- **Resources**: 100m CPU / 512Mi memory
- **Ports**: 5432 (PostgreSQL)
- **Secrets**: postgres-secret (POSTGRES_PASSWORD, POSTGRES_USER, POSTGRES_DB)
- **PVC**: postgres-data (5Gi, ReadWriteOnce)
- **Service**: ClusterIP on port 5432

## Configuration Management Strategy

### Environment-Specific Values

**values.yaml** (defaults):
- Generic configuration suitable for any environment
- Conservative resource limits
- Placeholder values for secrets (overridden at install time)

**values-minikube.yaml** (local development):
- NodePort service type for frontend
- Local storage class (standard)
- Reduced resource limits for laptop constraints
- Single replicas for all services

**values-production.yaml** (Phase V, cloud deployment):
- LoadBalancer service type for frontend
- Cloud storage class (gp3, pd-ssd)
- Higher resource limits for production workloads
- Multiple replicas with HPA

### Secret Management

**Phase IV (Local Development)**:
- Secrets created manually via `kubectl create secret`
- Values stored in .env file (gitignored)
- Documented in quickstart.md

**Phase V (Cloud Production)**:
- Secrets managed via cloud provider (AWS Secrets Manager, GCP Secret Manager)
- Integrated with Kubernetes via External Secrets Operator
- Automated rotation and auditing

## Data Persistence Guarantees

### Database (PostgreSQL)

- **Persistence**: PVC with hostPath StorageClass (Minikube)
- **Backup**: Manual pg_dump (Phase IV), automated backups (Phase V)
- **Recovery**: Restore from dump file
- **Data Loss Scenarios**:
  - ✅ Pod restart: No data loss (PVC persists)
  - ✅ Deployment update: No data loss (PVC persists)
  - ✅ Helm upgrade: No data loss (PVC persists)
  - ⚠️ PVC deletion: Data loss (manual backup required)
  - ⚠️ Minikube deletion: Data loss (PVC on host filesystem)

### Application State (Frontend/Backend)

- **Persistence**: None (stateless services)
- **Session State**: JWT tokens (client-side)
- **Conversation State**: Database (persisted via PostgreSQL PVC)
- **Cache**: None (Phase IV), Redis (Phase V)

## Validation and Testing

### Deployment Validation

1. **Pre-deployment**: `helm lint`, `helm template` (syntax validation)
2. **Post-deployment**: `kubectl get pods`, `kubectl get services` (resource creation)
3. **Health checks**: HTTP requests to /health endpoints (application health)
4. **Data persistence**: Create task, restart pod, verify task exists (data integrity)
5. **Network connectivity**: Frontend → Backend → Database (service discovery)

### Configuration Validation

1. **ConfigMap**: `kubectl describe configmap` (values correct)
2. **Secret**: `kubectl get secret -o yaml` (base64 encoded, not plaintext)
3. **Environment variables**: `kubectl exec pod -- env` (injected correctly)
4. **Volume mounts**: `kubectl exec pod -- ls /path` (files mounted)

## Migration from Phase III

### Application Code Changes

**Minimal changes required**:
- ✅ Health check endpoints already exist (FastAPI /health, Next.js /api/health)
- ✅ Environment variable configuration already implemented
- ✅ Database connection via DATABASE_URL already supported
- ⚠️ Frontend API URL: Update to use Kubernetes service DNS or environment variable
- ⚠️ CORS configuration: Add Kubernetes service names to allowed origins

### Database Migration

**Phase III → Phase IV**:
1. Export Phase III database: `pg_dump neon_db > backup.sql`
2. Deploy Phase IV with empty database
3. Run migrations: Helm hook executes `alembic upgrade head`
4. Import data: `kubectl exec postgres-pod -- psql < backup.sql`
5. Verify: Check task count, user count, conversation count

**Rollback Plan**:
- Keep Phase III deployment running during Phase IV testing
- Export Phase IV data before rollback
- Restore Phase III database from backup

## Summary

This data model defines the deployment configuration entities for Kubernetes. Unlike traditional application data models, these entities describe infrastructure and deployment concerns rather than business domain entities. The model ensures:

- **Reproducibility**: Same configuration produces identical deployments
- **Portability**: Helm charts work across Minikube and cloud Kubernetes
- **Security**: Secrets separated from configuration, non-root containers
- **Reliability**: Health checks, resource limits, persistent storage
- **Maintainability**: Clear entity relationships, validation rules, state transitions

All entities are managed declaratively via Kubernetes manifests and Helm charts, enabling GitOps workflows and automated deployments.
