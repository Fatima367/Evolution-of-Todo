# Data Model: Kubernetes Resources

This document defines the Kubernetes resource entities used for the local Kubernetes deployment.

## Entities

### Docker Image

**Purpose**: Containerized application artifact

**Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Image name (e.g., todoboard-frontend) |
| `tag` | string | Image tag (e.g., latest, dev) |
| `pullPolicy` | enum | When to pull image: "Always", "IfNotPresent", "Never" |

---

### ConfigMap

**Purpose**: Non-sensitive configuration storage

**Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `name` | string | ConfigMap name (max 63 chars, lowercase alphanumeric, hyphens) |
| `data` | map[string]string | Key-value pairs of configuration |
| `namespace` | string | Namespace (default: default) |

**Relationships**: Consumed by Pods via `envFrom.configMapRef` or `volumes`

---

### Secret

**Purpose**: Sensitive data storage (base64 encoded in K8s)

**Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Secret name |
| `type` | enum | "Opaque" (generic), "kubernetes.io/basic-auth" |
| `data` | map[string]string | Base64-encoded values |

**Relationships**: Consumed by Pods via `envFrom.secretRef` or `secretKeyRef`

---

### PersistentVolumeClaim

**Purpose**: Storage request for persistent data

**Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `name` | string | PVC name |
| `storageClassName` | string | Storage class (e.g., standard, hostpath) |
| `accessModes` | array | ["ReadWriteOnce"] for single node |
| `resources.requests.storage` | string | Requested size (e.g., "1Gi") |

**Relationships**: Referenced by Pod volumes

---

### Deployment

**Purpose**: Manages pod replicas with declarative updates

**Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Deployment name |
| `replicas` | integer | Number of pod replicas |
| `selector.matchLabels` | map[string]string | Pod selector |
| `template.metadata.labels` | map[string]string | Pod template labels |
| `template.spec.containers` | array | Container specifications |
| `strategy.type` | enum | "RollingUpdate" or "Recreate" |
| `strategy.rollingUpdate.maxSurge` | integer/string | Extra pods during update |
| `strategy.rollingUpdate.maxUnavailable` | integer/string | Unavailable pods during update |

---

### Service

**Purpose**: Network endpoint for pods with stable IP

**Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Service name |
| `type` | enum | "ClusterIP", "NodePort", "LoadBalancer" |
| `selector` | map[string]string | Pods to target |
| `ports[].port` | integer | Service port |
| `ports[].targetPort` | integer | Container port |
| `ports[].protocol` | enum | "TCP" (default) |

---

### Pod (managed by Deployment)

**Purpose**: Running container instance

**Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `spec.containers` | array | Container specs (name, image, ports, env) |
| `spec.volumes` | array | Volume mounts (ConfigMap, PVC) |
| `spec.resources` | object | Resource requests/limits |
| `spec.restartPolicy` | enum | "Always", "OnFailure", "Never" |

---

## Validation Rules

1. **Naming**: Resource names must be lowercase, alphanumeric, max 63 characters, hyphens allowed
2. **Namespace**: ConfigMaps/Secrets must be in same namespace as consuming pods
3. **Storage**: PVC storage request must be <= available PV capacity
4. **Ports**: Container ports must be unique per pod
5. **Selector**: Service selector must match pod labels exactly

---

## State Transitions

### Deployment State Machine

```
Creating → Available → Updating → Available (RollingUpdate)
           ↓
        Scaling → Available
```

### Pod State Machine

```
Pending → ContainerCreating → Running → Succeeded/Failed
          ↓                              ↓
       Waiting (Error)              Terminated
```

### PVC State Machine

```
Pending → Bound → Released → Pending (on delete)
          ↓
       Lost (if PV deleted)
```

---

## Example YAML Definitions

### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todoboard-backend
  labels:
    app: todoboard-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: todoboard-backend
  template:
    metadata:
      labels:
        app: todoboard-backend
    spec:
      containers:
        - name: backend
          image: todoboard-backend:latest
          ports:
            - containerPort: 8000
          envFrom:
            - configMapRef:
                name: todoboard-config
            - secretRef:
                name: todoboard-secrets
          resources:
            requests:
              memory: "512Mi"
              cpu: "200m"
            limits:
              memory: "1Gi"
              cpu: "1000m"
```

### Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: todoboard-backend
spec:
  type: ClusterIP
  selector:
    app: todoboard-backend
  ports:
    - port: 8000
      targetPort: 8000
```

### PVC

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: todoboard-postgres-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```
