# Phase 5 Advanced Cloud Deployment - Complete Implementation Guide

## Overview

This guide provides comprehensive instructions for deploying the TodoBoard application with full event-driven architecture using Kafka, Dapr, and microservices on Kubernetes.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Local Development (Minikube)](#local-development-minikube)
4. [Cloud Deployment](#cloud-deployment)
5. [Component Details](#component-details)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

### Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         KUBERNETES CLUSTER                                   │
│                                                                              │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐                   │
│  │   Frontend   │   │   Backend    │   │  Microservices│                   │
│  │   (Next.js)  │──▶│   (FastAPI)  │   │  - Notification│                  │
│  │   + Dapr     │   │   + Dapr     │   │  - Recurring  │                   │
│  └──────────────┘   └──────┬───────┘   │  - Audit      │                   │
│                             │           └───────┬───────┘                   │
│                             │                   │                           │
│                             ▼                   ▼                           │
│                    ┌─────────────────────────────────┐                      │
│                    │      KAFKA CLUSTER (Strimzi)    │                      │
│                    │  Topics:                        │                      │
│                    │  - task-events                  │                      │
│                    │  - reminders                    │                      │
│                    │  - task-updates                 │                      │
│                    │  - dead-letter-queue            │                      │
│                    └─────────────────────────────────┘                      │
│                                                                              │
│                    ┌─────────────────────────────────┐                      │
│                    │      DAPR RUNTIME               │                      │
│                    │  Components:                    │                      │
│                    │  - pubsub-kafka                 │                      │
│                    │  - statestore-postgres          │                      │
│                    │  - secrets-k8s                  │                      │
│                    └─────────────────────────────────┘                      │
│                                                                              │
│  External: Neon Serverless PostgreSQL (Database)                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Event Flow

1. **Task Created** → Backend publishes to `task-events` → Audit Service logs
2. **Task Completed (Recurring)** → Backend publishes to `task-events` → Recurring Task Service creates next occurrence
3. **Reminder Due** → Backend publishes to `reminders` → Notification Service sends notification
4. **All Events** → Audit Service stores in state store for compliance

---

## Prerequisites

### Required Tools

- **kubectl** (v1.28+)
- **helm** (v3.12+)
- **docker** (v24.0+)
- **minikube** (v1.32+) - for local deployment
- **Cloud CLI** - for cloud deployment:
  - `gcloud` (GKE)
  - `az` (AKS)
  - `oci` (OKE)

### Installation Commands

```bash
# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Dapr CLI
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
```

---

## Local Development (Minikube)

### Quick Start

```bash
# Navigate to phase5 directory
cd phase5-advanced-cloud-deployment

# Set GROQ API key (optional, for AI chatbot)
export GROQ_API_KEY="your-groq-api-key"

# Run automated setup
./scripts/minikube/setup-minikube.sh
```

### What the Script Does

1. ✅ Starts Minikube with 4 CPUs and 8GB RAM
2. ✅ Enables Ingress and Metrics Server addons
3. ✅ Builds all Docker images locally
4. ✅ Installs Dapr runtime
5. ✅ Installs Kafka with Strimzi operator
6. ✅ Creates Kafka topics (task-events, reminders, task-updates, dead-letter-queue)
7. ✅ Applies Dapr components and subscriptions
8. ✅ Deploys application with Helm
9. ✅ Configures /etc/hosts for todoboard.local

### Access Application

After setup completes:

- **Frontend**: http://todoboard.local
- **Backend API**: http://todoboard.local/api
- **API Docs**: http://todoboard.local/api/docs

### Manual Steps (Alternative)

If you prefer manual setup:

```bash
# 1. Start Minikube
minikube start --cpus=4 --memory=8192

# 2. Enable addons
minikube addons enable ingress
minikube addons enable metrics-server

# 3. Set Docker environment
eval $(minikube docker-env)

# 4. Build images
docker build -t todoboard-backend:latest ./backend
docker build -t todoboard-frontend:latest ./frontend
docker build -t notification-service:latest ./services/notification-service
docker build -t recurring-task-service:latest ./services/recurring-task-service
docker build -t audit-service:latest ./services/audit-service

# 5. Install Dapr
dapr init --kubernetes --wait

# 6. Install Kafka
./scripts/kafka/install-kafka.sh

# 7. Apply Dapr components
kubectl apply -f infrastructure/dapr/components/
kubectl apply -f infrastructure/dapr/subscriptions/
kubectl apply -f infrastructure/dapr/config/

# 8. Create secrets
kubectl create secret generic todoboard-secrets \
  --from-literal=POSTGRES_PASSWORD='your-database-password' \
  --from-literal=JWT_SECRET_KEY='your-jwt-secret-key' \
  --from-literal=GROQ_API_KEY="${GROQ_API_KEY}" \
  -n todoboard

# 9. Deploy with Helm
helm install todoboard ./infrastructure/helm/todo-app \
  -f ./infrastructure/helm/todo-app/values-minikube.yaml \
  -n todoboard \
  --create-namespace

# 10. Add to /etc/hosts
echo "$(minikube ip) todoboard.local" | sudo tee -a /etc/hosts
```

---

## Cloud Deployment

### Option 1: Google Cloud (GKE)

```bash
# 1. Setup GKE cluster
cd scripts/cloud
export GCP_PROJECT_ID="your-project-id"
export CLUSTER_NAME="todoboard-cluster"
export GCP_ZONE="us-central1-a"
./setup-cluster-gke.sh

# 2. Install Kafka
cd ../..
./scripts/kafka/install-kafka.sh

# 3. Install Dapr
./scripts/dapr/install-dapr.sh

# 4. Create secrets
kubectl create secret generic todoboard-secrets \
  --from-literal=POSTGRES_PASSWORD='your-db-password' \
  --from-literal=JWT_SECRET_KEY='your-jwt-secret' \
  --from-literal=GROQ_API_KEY='your-groq-key' \
  -n todoboard

# 5. Update Helm values
# Edit infrastructure/helm/todo-app/values-cloud.yaml
# - Set your domain
# - Set DATABASE_URL
# - Set CORS_ORIGINS

# 6. Deploy application
helm install todoboard ./infrastructure/helm/todo-app \
  -f ./infrastructure/helm/todo-app/values-cloud.yaml \
  -n todoboard \
  --create-namespace

# 7. Get ingress IP
kubectl get ingress -n todoboard

# 8. Configure DNS
# Create A record: todoboard.yourdomain.com → <ingress-ip>
```

### Option 2: Azure (AKS)

```bash
# 1. Setup AKS cluster
cd scripts/cloud
export AZURE_RESOURCE_GROUP="todoboard-rg"
export CLUSTER_NAME="todoboard-cluster"
export AZURE_LOCATION="eastus"
./setup-cluster-aks.sh

# 2-8. Follow same steps as GKE above
```

### Option 3: Oracle Cloud (OKE) - Always Free

```bash
# 1. Setup OKE cluster
cd ../phase4-kubernetes-deployment/scripts/cloud
export OCI_COMPARTMENT_ID="your-compartment-id"
export CLUSTER_NAME="todoboard-cluster"
./setup-cluster-oke.sh

# 2-8. Follow same steps as GKE above
```

---

## Component Details

### 1. Kafka (Strimzi)

**Location**: `infrastructure/kafka/`

**Components**:
- `kafka-cluster.yaml` - 3-node Kafka cluster with ZooKeeper
- `kafka-topics.yaml` - Pre-configured topics with replication
- `kafka-metrics-config.yaml` - Prometheus metrics configuration

**Topics**:
- `task-events` - All task CRUD operations (30-day retention)
- `reminders` - Scheduled reminder triggers (7-day retention)
- `task-updates` - Real-time client sync (24-hour retention)
- `dead-letter-queue` - Failed message processing (90-day retention)

**Verification**:
```bash
# Check Kafka cluster
kubectl get kafka -n todoboard

# Check topics
kubectl get kafkatopic -n todoboard

# View Kafka logs
kubectl logs -n todoboard -l strimzi.io/name=todoboard-kafka-kafka
```

### 2. Dapr Components

**Location**: `infrastructure/dapr/`

**Components**:
- `pubsub-kafka.yaml` - Kafka pub/sub integration
- `statestore-postgres.yaml` - PostgreSQL state store
- `secrets-k8s.yaml` - Kubernetes secrets integration

**Subscriptions**:
- `notification-service-subscription.yaml` - Subscribes to `reminders` topic
- `recurring-task-service-subscription.yaml` - Subscribes to `task-events` topic
- `audit-service-subscription.yaml` - Subscribes to `task-events` topic

**Configuration**:
- `dapr-config.yaml` - Global Dapr configuration (tracing, mTLS, metrics)

**Verification**:
```bash
# Check Dapr components
kubectl get components -n todoboard

# Check Dapr subscriptions
kubectl get subscriptions -n todoboard

# View Dapr dashboard
dapr dashboard -k
```

### 3. Microservices

#### Notification Service

**Port**: 8001
**Purpose**: Sends reminder notifications
**Subscribes to**: `reminders` topic
**Publishes to**: `task-events` (notification.sent events)

**Endpoints**:
- `GET /health` - Health check
- `POST /events/reminders` - Dapr subscription endpoint

#### Recurring Task Service

**Port**: 8002
**Purpose**: Creates next occurrence of recurring tasks
**Subscribes to**: `task-events` topic
**Publishes to**: `task-events` (recurring.task.created events)

**Endpoints**:
- `GET /health` - Health check
- `POST /events/task-events` - Dapr subscription endpoint

#### Audit Service

**Port**: 8003
**Purpose**: Logs all task operations for audit trail
**Subscribes to**: `task-events` topic
**Stores in**: Dapr state store (PostgreSQL)

**Endpoints**:
- `GET /health` - Health check
- `POST /events/task-events` - Dapr subscription endpoint
- `GET /audit-logs/{user_id}` - Retrieve audit logs

---

## Verification

### 1. Check All Pods

```bash
kubectl get pods -n todoboard

# Expected output:
# NAME                                          READY   STATUS    RESTARTS   AGE
# todoboard-backend-xxx                         2/2     Running   0          5m
# todoboard-frontend-xxx                        1/1     Running   0          5m
# todoboard-notification-service-xxx            2/2     Running   0          5m
# todoboard-recurring-task-service-xxx          2/2     Running   0          5m
# todoboard-audit-service-xxx                   2/2     Running   0          5m
# todoboard-kafka-kafka-0                       1/1     Running   0          10m
# todoboard-kafka-kafka-1                       1/1     Running   0          10m
# todoboard-kafka-kafka-2                       1/1     Running   0          10m
# todoboard-kafka-zookeeper-0                   1/1     Running   0          10m
```

### 2. Test Event Flow

```bash
# Create a task via API
curl -X POST http://todoboard.local/api/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test recurring task",
    "recurring_type": "daily",
    "due_date": "2024-01-25T10:00:00Z"
  }'

# Check audit service logs
kubectl logs -n todoboard -l app=audit-service -c audit-service

# Check notification service logs
kubectl logs -n todoboard -l app=notification-service -c notification-service

# Check recurring task service logs
kubectl logs -n todoboard -l app=recurring-task-service -c recurring-task-service
```

### 3. Verify Kafka Topics

```bash
# List topics
kubectl get kafkatopic -n todoboard

# Check topic details
kubectl describe kafkatopic task-events -n todoboard
```

### 4. Verify Dapr Components

```bash
# List components
kubectl get components -n todoboard

# Check component status
kubectl describe component pubsub-kafka -n todoboard
```

---

## Troubleshooting

### Kafka Issues

**Problem**: Kafka pods not starting

```bash
# Check Strimzi operator
kubectl get pods -n kafka

# Check Kafka cluster status
kubectl get kafka -n todoboard -o yaml

# View Kafka logs
kubectl logs -n todoboard todoboard-kafka-kafka-0
```

**Problem**: Topics not created

```bash
# Manually create topics
kubectl apply -f infrastructure/kafka/kafka-topics.yaml

# Verify
kubectl get kafkatopic -n todoboard
```

### Dapr Issues

**Problem**: Dapr sidecar not injected

```bash
# Check Dapr installation
kubectl get pods -n dapr-system

# Verify deployment annotations
kubectl get deployment todoboard-backend -n todoboard -o yaml | grep dapr.io

# Check Dapr sidecar injector logs
kubectl logs -n dapr-system -l app=dapr-sidecar-injector
```

**Problem**: Component not found

```bash
# List components
kubectl get components -n todoboard

# Apply components
kubectl apply -f infrastructure/dapr/components/

# Check component logs
kubectl logs -n dapr-system -l app=dapr-operator
```

### Microservice Issues

**Problem**: Service not receiving events

```bash
# Check subscription
kubectl get subscription -n todoboard

# Check service logs
kubectl logs -n todoboard -l app=notification-service -c notification-service

# Check Dapr sidecar logs
kubectl logs -n todoboard -l app=notification-service -c daprd
```

**Problem**: Events not being published

```bash
# Check backend logs
kubectl logs -n todoboard -l app=backend -c backend

# Check Dapr sidecar logs
kubectl logs -n todoboard -l app=backend -c daprd

# Test Dapr pub/sub directly
kubectl exec -it <backend-pod> -c daprd -n todoboard -- \
  curl -X POST http://localhost:3500/v1.0/publish/pubsub-kafka/task-events \
  -H "Content-Type: application/json" \
  -d '{"test": "message"}'
```

---

## Performance Tuning

### Kafka

```yaml
# Increase partitions for higher throughput
spec:
  partitions: 6  # Default: 3

# Adjust retention
config:
  retention.ms: 604800000  # 7 days
```

### Dapr

```yaml
# Increase sidecar resources
annotations:
  dapr.io/sidecar-cpu-limit: "1000m"
  dapr.io/sidecar-memory-limit: "512Mi"
```

### Microservices

```yaml
# Increase replicas
replicaCount: 3

# Enable autoscaling
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
```

---

## Security Best Practices

1. **Enable mTLS** in Dapr configuration
2. **Use Kubernetes secrets** for sensitive data
3. **Enable network policies** to restrict pod-to-pod communication
4. **Use TLS** for Kafka connections in production
5. **Implement authentication** for Kafka (SASL/SCRAM)
6. **Regular security scans** with Trivy
7. **Rotate secrets** regularly

---

## Monitoring

### Prometheus Metrics

```bash
# Access Prometheus
kubectl port-forward -n todoboard svc/prometheus 9090:9090

# Open http://localhost:9090
```

### Grafana Dashboards

```bash
# Access Grafana
kubectl port-forward -n todoboard svc/grafana 3000:3000

# Open http://localhost:3000
# Default credentials: admin/admin
```

### Key Metrics to Monitor

- Kafka lag per consumer group
- Dapr pub/sub message throughput
- Microservice response times
- Pod CPU/Memory usage
- Error rates per service

---

## Cleanup

### Minikube

```bash
# Delete application
helm uninstall todoboard -n todoboard

# Delete namespace
kubectl delete namespace todoboard

# Stop Minikube
minikube stop

# Delete Minikube
minikube delete
```

### Cloud

```bash
# Delete application
helm uninstall todoboard -n todoboard

# Run teardown script
cd scripts/cloud
export CLOUD_PROVIDER=gke  # or aks, oke
./teardown-cloud.sh
```

---

## Additional Resources

- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Strimzi Documentation](https://strimzi.io/docs/)
- [Dapr Documentation](https://docs.dapr.io/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)

---

## Support

For issues or questions:
1. Check the [troubleshooting section](#troubleshooting)
2. Review logs: `kubectl logs -f <pod-name> -n todoboard`
3. Check events: `kubectl get events -n todoboard`
4. Review component status: `kubectl get all -n todoboard`

---

**Last Updated**: 2026-01-25
**Phase**: V - Advanced Cloud Deployment
**Status**: 100% Complete ✅
