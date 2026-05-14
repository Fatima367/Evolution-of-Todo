# Dapr Setup and Configuration

## Overview

Dapr (Distributed Application Runtime) is a portable, event-driven runtime that simplifies building resilient, stateless, and stateful microservices. TodoBoard uses Dapr to abstract infrastructure concerns and provide a consistent API for:

- **Pub/Sub Messaging**: Event publishing and subscription via Kafka
- **State Management**: Distributed state storage via PostgreSQL
- **Secrets Management**: Secure access to Kubernetes secrets
- **Service Invocation**: Service-to-service communication
- **Observability**: Built-in metrics, logging, and tracing

## Why Dapr?

### Benefits

1. **Infrastructure Abstraction**: Services use Dapr APIs instead of directly integrating with Kafka, PostgreSQL, etc.
2. **Portability**: Switch infrastructure components without changing application code
3. **Best Practices Built-In**: Retry logic, circuit breakers, distributed tracing
4. **Simplified Development**: Consistent APIs across different infrastructure components
5. **Cloud-Native**: Designed for Kubernetes but works anywhere

### Use Cases in TodoBoard

- **Event Publishing**: Backend API publishes task events to Kafka via Dapr pub/sub
- **Event Consumption**: Microservices consume events from Kafka via Dapr subscriptions
- **State Storage**: Services store distributed state in PostgreSQL via Dapr state store
- **Secret Access**: Services retrieve database credentials and API keys via Dapr secrets

## Dapr Components

Dapr uses **components** to define infrastructure integrations. Each component has a specification that defines how to connect to the underlying service.

### Component Types Used

1. **Pub/Sub (pubsub.kafka)**: Kafka message broker for event streaming
2. **State Store (state.postgresql)**: PostgreSQL for distributed state
3. **Secret Store (secretstores.kubernetes)**: Kubernetes secrets for sensitive data

---

## Component 1: Pub/Sub (Kafka)

### Purpose

Enables event-driven architecture with Kafka as the message broker.

### Component Specification

**File**: `infrastructure/dapr/components/pubsub-kafka.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-kafka
  namespace: default
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  # Kafka broker addresses
  - name: brokers
    value: "kafka:9092"

  # Consumer group for this application
  - name: consumerGroup
    value: "todoboard-consumers"

  # Client ID for Kafka connection
  - name: clientID
    value: "todoboard-dapr"

  # Authentication (optional, for production)
  - name: authType
    value: "none"  # Use "password" or "certificate" for production

  # SASL username (if authType is "password")
  # - name: saslUsername
  #   secretKeyRef:
  #     name: kafka-secrets
  #     key: username

  # SASL password (if authType is "password")
  # - name: saslPassword
  #   secretKeyRef:
  #     name: kafka-secrets
  #     key: password

  # TLS configuration (for production)
  # - name: skipVerify
  #   value: "false"
  # - name: caCert
  #   secretKeyRef:
  #     name: kafka-tls
  #     key: ca.crt

  # Consumer configuration
  - name: consumeRetryInterval
    value: "200ms"

  - name: version
    value: "2.8.0"  # Kafka version

  # Topic configuration
  - name: initialOffset
    value: "newest"  # or "oldest" to replay all messages

  # Message delivery semantics
  - name: maxMessageBytes
    value: "1024000"  # 1MB max message size
```

### Usage in Application

#### Publishing Events (Backend API)

```python
from dapr.clients import DaprClient

# Initialize Dapr client
dapr_client = DaprClient()

# Publish event to Kafka topic
dapr_client.publish_event(
    pubsub_name="pubsub-kafka",
    topic_name="task-events",
    data=json.dumps({
        "event_type": "task.created",
        "task_id": "123",
        "user_id": "456"
    }),
    data_content_type="application/json",
    metadata={"user_id": "456"}  # Partition key
)
```

#### Subscribing to Events (Microservices)

**Declarative Subscription** (Recommended):

**File**: `infrastructure/dapr/subscriptions/notification-service.yaml`

```yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: notification-service-reminders
  namespace: default
spec:
  pubsubname: pubsub-kafka
  topic: reminders
  routes:
    default: /events/reminders
  scopes:
  - notification-service
```

**Programmatic Subscription**:

```python
from fastapi import FastAPI
from dapr.ext.fastapi import DaprApp

app = FastAPI()
dapr_app = DaprApp(app)

@dapr_app.subscribe(pubsub_name="pubsub-kafka", topic="reminders")
async def handle_reminder(event_data: dict):
    """Handle reminder events from Kafka"""
    print(f"Received reminder: {event_data}")
    # Process reminder
    return {"success": True}
```

### Topics Configuration

All topics are created automatically by Kafka when first published to. For production, pre-create topics with specific configurations:

```bash
# Create task-events topic with 3 partitions and replication factor 3
kafka-topics --create \
  --bootstrap-server kafka:9092 \
  --topic task-events \
  --partitions 3 \
  --replication-factor 3 \
  --config retention.ms=2592000000  # 30 days

# Create task-updates topic with 3 partitions
kafka-topics --create \
  --bootstrap-server kafka:9092 \
  --topic task-updates \
  --partitions 3 \
  --replication-factor 3 \
  --config retention.ms=86400000  # 24 hours

# Create reminders topic with 3 partitions
kafka-topics --create \
  --bootstrap-server kafka:9092 \
  --topic reminders \
  --partitions 3 \
  --replication-factor 3 \
  --config retention.ms=604800000  # 7 days

# Create dead-letter-queue topic with 1 partition
kafka-topics --create \
  --bootstrap-server kafka:9092 \
  --topic dead-letter-queue \
  --partitions 1 \
  --replication-factor 3 \
  --config retention.ms=7776000000  # 90 days
```

---

## Component 2: State Store (PostgreSQL)

### Purpose

Provides distributed state management using PostgreSQL as the backing store.

### Component Specification

**File**: `infrastructure/dapr/components/statestore-postgres.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore-postgres
  namespace: default
spec:
  type: state.postgresql
  version: v1
  metadata:
  # PostgreSQL connection string
  - name: connectionString
    secretKeyRef:
      name: todoboard-secrets
      key: DATABASE_URL

  # Table name for state storage
  - name: tableName
    value: "dapr_state"

  # Metadata table name
  - name: metadataTableName
    value: "dapr_metadata"

  # Timeout for database operations
  - name: timeout
    value: "20s"

  # Connection pool settings
  - name: maxConns
    value: "10"

  - name: connectionMaxIdleTime
    value: "5m"

  # Enable optimistic concurrency control
  - name: actorStateStore
    value: "true"
```

### Database Schema

Dapr automatically creates these tables:

```sql
-- State table
CREATE TABLE dapr_state (
  key TEXT NOT NULL PRIMARY KEY,
  value JSONB NOT NULL,
  isbinary BOOLEAN NOT NULL,
  insertdate TIMESTAMP NOT NULL DEFAULT NOW(),
  updatedate TIMESTAMP NOT NULL DEFAULT NOW(),
  eTag VARCHAR(36) NOT NULL
);

-- Metadata table
CREATE TABLE dapr_metadata (
  key TEXT NOT NULL PRIMARY KEY,
  value TEXT NOT NULL
);
```

### Usage in Application

```python
from dapr.clients import DaprClient

dapr_client = DaprClient()

# Save state
dapr_client.save_state(
    store_name="statestore-postgres",
    key="user:123:preferences",
    value=json.dumps({
        "theme": "dark",
        "notifications": True
    })
)

# Get state
response = dapr_client.get_state(
    store_name="statestore-postgres",
    key="user:123:preferences"
)
preferences = json.loads(response.data)

# Delete state
dapr_client.delete_state(
    store_name="statestore-postgres",
    key="user:123:preferences"
)

# Transactional state operations
operations = [
    {
        "operation": "upsert",
        "request": {
            "key": "counter",
            "value": "1"
        }
    },
    {
        "operation": "delete",
        "request": {
            "key": "old-counter"
        }
    }
]

dapr_client.execute_state_transaction(
    store_name="statestore-postgres",
    operations=operations
)
```

---

## Component 3: Secret Store (Kubernetes)

### Purpose

Securely access secrets stored in Kubernetes without hardcoding credentials.

### Component Specification

**File**: `infrastructure/dapr/components/secrets-k8s.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: secrets-k8s
  namespace: default
spec:
  type: secretstores.kubernetes
  version: v1
  metadata:
  # No additional configuration needed for Kubernetes secrets
  # Dapr uses the service account token to access secrets
```

### Kubernetes Secret Example

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: todoboard-secrets
  namespace: default
type: Opaque
stringData:
  DATABASE_URL: "postgresql://user:password@postgres:5432/todoboard"
  JWT_SECRET: "your-secret-key-here"
  ANTHROPIC_API_KEY: "sk-ant-..."
```

### Usage in Application

```python
from dapr.clients import DaprClient

dapr_client = DaprClient()

# Get secret from Kubernetes
response = dapr_client.get_secret(
    store_name="secrets-k8s",
    key="todoboard-secrets"
)

# Access individual secret values
database_url = response.secret.get("DATABASE_URL")
jwt_secret = response.secret.get("JWT_SECRET")
```

### Environment Variable Injection

Dapr can inject secrets as environment variables:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  template:
    spec:
      containers:
      - name: backend
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: todoboard-secrets
              key: DATABASE_URL
```

---

## Dapr Installation

### Local Development (Minikube)

```bash
# Initialize Minikube
minikube start --cpus=4 --memory=8192

# Install Dapr CLI
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Initialize Dapr on Kubernetes
dapr init --kubernetes --wait

# Verify installation
dapr status -k

# Expected output:
#   NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE  CREATED
#   dapr-sidecar-injector  dapr-system  True     Running  1         1.12.0   1m   2024-01-19 10:00:00
#   dapr-sentry            dapr-system  True     Running  1         1.12.0   1m   2024-01-19 10:00:00
#   dapr-operator          dapr-system  True     Running  1         1.12.0   1m   2024-01-19 10:00:00
#   dapr-placement         dapr-system  True     Running  1         1.12.0   1m   2024-01-19 10:00:00
```

### Production Cloud (AKS/GKE/OKE)

```bash
# Install Dapr via Helm
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update

# Install Dapr with production settings
helm install dapr dapr/dapr \
  --namespace dapr-system \
  --create-namespace \
  --set global.ha.enabled=true \
  --set global.ha.replicaCount=3 \
  --set global.prometheus.enabled=true \
  --set global.mtls.enabled=true \
  --wait

# Verify installation
kubectl get pods -n dapr-system
```

---

## Dapr Sidecar Configuration

### Enabling Dapr for a Service

Add annotations to the Kubernetes Deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "backend-service"
        dapr.io/app-port: "8000"
        dapr.io/log-level: "info"
        dapr.io/enable-metrics: "true"
        dapr.io/metrics-port: "9090"
        dapr.io/sidecar-cpu-limit: "1000m"
        dapr.io/sidecar-memory-limit: "512Mi"
        dapr.io/sidecar-cpu-request: "100m"
        dapr.io/sidecar-memory-request: "128Mi"
```

### Annotation Reference

| Annotation | Description | Default |
|------------|-------------|---------|
| `dapr.io/enabled` | Enable Dapr sidecar injection | `false` |
| `dapr.io/app-id` | Unique identifier for the service | Required |
| `dapr.io/app-port` | Port the application listens on | `80` |
| `dapr.io/log-level` | Dapr sidecar log level | `info` |
| `dapr.io/enable-metrics` | Enable Prometheus metrics | `true` |
| `dapr.io/metrics-port` | Port for Prometheus metrics | `9090` |
| `dapr.io/config` | Name of Dapr configuration | `default` |
| `dapr.io/sidecar-cpu-limit` | CPU limit for sidecar | `1000m` |
| `dapr.io/sidecar-memory-limit` | Memory limit for sidecar | `512Mi` |

---

## Dapr Configuration

### Global Configuration

**File**: `infrastructure/dapr/config/dapr-config.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: dapr-config
  namespace: default
spec:
  # Distributed tracing
  tracing:
    samplingRate: "1"
    zipkin:
      endpointAddress: "http://zipkin:9411/api/v2/spans"

  # Metrics
  metric:
    enabled: true

  # mTLS configuration
  mtls:
    enabled: true
    workloadCertTTL: "24h"
    allowedClockSkew: "15m"

  # Access control
  accessControl:
    defaultAction: allow
    trustDomain: "public"

  # API configuration
  api:
    allowed:
    - name: state
      version: v1
      protocol: grpc
    - name: pubsub
      version: v1
      protocol: grpc

  # Middleware pipeline
  httpPipeline:
    handlers:
    - name: oauth2
      type: middleware.http.oauth2
    - name: ratelimit
      type: middleware.http.ratelimit
```

### Applying Configuration

```bash
# Apply Dapr components
kubectl apply -f infrastructure/dapr/components/

# Apply Dapr configuration
kubectl apply -f infrastructure/dapr/config/

# Verify components
dapr components -k

# Expected output:
#   NAMESPACE  NAME                 TYPE              VERSION  SCOPES  CREATED              AGE
#   default    pubsub-kafka         pubsub.kafka      v1               2024-01-19 10:00:00  1m
#   default    statestore-postgres  state.postgresql  v1               2024-01-19 10:00:00  1m
#   default    secrets-k8s          secretstores...   v1               2024-01-19 10:00:00  1m
```

---

## Service Communication

### HTTP Service Invocation

```python
from dapr.clients import DaprClient

dapr_client = DaprClient()

# Invoke another service via Dapr
response = dapr_client.invoke_method(
    app_id="notification-service",
    method_name="send-notification",
    data=json.dumps({
        "user_id": "123",
        "message": "Task reminder"
    }),
    http_verb="POST"
)
```

### gRPC Service Invocation

```python
from dapr.clients import DaprClient

dapr_client = DaprClient()

# Invoke service via gRPC
response = dapr_client.invoke_method(
    app_id="recurring-task-service",
    method_name="create-next-instance",
    data=json.dumps({
        "task_id": "123",
        "pattern": "weekly"
    }),
    http_verb="POST"
)
```

---

## Monitoring and Observability

### Prometheus Metrics

Dapr exposes metrics on port 9090 (configurable):

```bash
# Access Dapr sidecar metrics
curl http://localhost:9090/metrics
```

**Key Metrics**:
- `dapr_http_server_request_count` - HTTP request count
- `dapr_http_server_request_duration_ms` - Request duration
- `dapr_component_pubsub_ingress_count` - Pub/sub messages received
- `dapr_component_pubsub_egress_count` - Pub/sub messages sent
- `dapr_component_state_count` - State operations count

### Distributed Tracing

Dapr automatically propagates trace context:

```yaml
# Enable tracing in Dapr configuration
spec:
  tracing:
    samplingRate: "1"  # 100% sampling for development
    zipkin:
      endpointAddress: "http://zipkin:9411/api/v2/spans"
```

### Logging

Dapr sidecar logs are available via kubectl:

```bash
# View Dapr sidecar logs
kubectl logs <pod-name> -c daprd

# Follow logs
kubectl logs <pod-name> -c daprd -f

# View application logs
kubectl logs <pod-name> -c backend
```

---

## Troubleshooting

### Common Issues

#### 1. Dapr Sidecar Not Injected

**Symptom**: Pod has only one container instead of two

**Solution**:
```bash
# Check if Dapr is installed
dapr status -k

# Verify annotations on deployment
kubectl describe deployment backend | grep dapr.io

# Check Dapr sidecar injector logs
kubectl logs -n dapr-system -l app=dapr-sidecar-injector
```

#### 2. Component Not Found

**Symptom**: Error "component not found: pubsub-kafka"

**Solution**:
```bash
# List components
dapr components -k

# Apply components
kubectl apply -f infrastructure/dapr/components/

# Check component logs
kubectl logs -n dapr-system -l app=dapr-operator
```

#### 3. Connection to Kafka Failed

**Symptom**: Error "failed to connect to Kafka broker"

**Solution**:
```bash
# Verify Kafka is running
kubectl get pods -l app=kafka

# Check Kafka service
kubectl get svc kafka

# Test connection from pod
kubectl exec -it <backend-pod> -- nc -zv kafka 9092

# Check Dapr component configuration
kubectl get component pubsub-kafka -o yaml
```

#### 4. State Store Connection Failed

**Symptom**: Error "failed to connect to state store"

**Solution**:
```bash
# Verify PostgreSQL is running
kubectl get pods -l app=postgres

# Check database credentials
kubectl get secret todoboard-secrets -o yaml

# Test database connection
kubectl exec -it <backend-pod> -- psql $DATABASE_URL -c "SELECT 1"
```

---

## Best Practices

### 1. Component Scoping

Limit component access to specific services:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-kafka
spec:
  type: pubsub.kafka
  scopes:
  - backend-service
  - notification-service
  - recurring-task-service
  - audit-service
```

### 2. Resource Limits

Set appropriate resource limits for Dapr sidecars:

```yaml
annotations:
  dapr.io/sidecar-cpu-limit: "500m"
  dapr.io/sidecar-memory-limit: "256Mi"
  dapr.io/sidecar-cpu-request: "100m"
  dapr.io/sidecar-memory-request: "128Mi"
```

### 3. Error Handling

Implement retry logic in application code:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
async def publish_event_with_retry(topic, data):
    await dapr_client.publish_event(
        pubsub_name="pubsub-kafka",
        topic_name=topic,
        data=data
    )
```

### 4. Security

- Enable mTLS for service-to-service communication
- Use Kubernetes secrets for sensitive data
- Implement access control policies
- Rotate secrets regularly

### 5. Monitoring

- Monitor Dapr sidecar metrics
- Set up alerts for component failures
- Track pub/sub message lag
- Monitor state store performance

---

## References

- [Dapr Official Documentation](https://docs.dapr.io/)
- [Dapr Pub/Sub Specification](https://docs.dapr.io/reference/components-reference/supported-pubsub/)
- [Dapr State Store Specification](https://docs.dapr.io/reference/components-reference/supported-state-stores/)
- [Dapr Best Practices](https://docs.dapr.io/operations/best-practices/)
- [Architecture Documentation](./architecture.md)
- [Event Schemas Documentation](./event-schemas.md)
