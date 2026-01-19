# Phase 5: Advanced Cloud Deployment

This phase implements production-grade cloud deployment for the TodoBoard application with high availability, auto-scaling, and event-driven architecture using Kafka and Dapr.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Cloud Kubernetes Cluster                      │
│                                                                  │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐       │
│  │   Frontend   │   │   Backend    │   │ Notification │       │
│  │   (Next.js)  │──▶│   (FastAPI)  │──▶│   Service    │       │
│  │   + HPA      │   │   + HPA      │   │   + HPA      │       │
│  └──────────────┘   └──────────────┘   └──────────────┘       │
│         │                   │                   │               │
│         │                   │                   │               │
│         └───────────────────┼───────────────────┘               │
│                             │                                   │
│                    ┌────────▼────────┐                          │
│                    │  Kafka Cluster  │                          │
│                    │  (3 replicas)   │                          │
│                    │  + Replication  │                          │
│                    └─────────────────┘                          │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Dapr Runtime Components                      │  │
│  │  - Pub/Sub (Kafka)                                       │  │
│  │  - State Store (PostgreSQL)                              │  │
│  │  - Secrets Management                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  External: Neon Serverless PostgreSQL (with connection pooling) │
└─────────────────────────────────────────────────────────────────┘
```

## Features Implemented

### Phase 6: Production Cloud Deployment (User Story 4)

All tasks completed:

- ✅ **T082-T083**: Cloud cluster setup scripts for GKE and AKS
- ✅ **T086-T087**: HorizontalPodAutoscaler for all microservices
- ✅ **T088**: Liveness and readiness probes for all deployments
- ✅ **T089**: Rolling update strategies with maxSurge and maxUnavailable
- ✅ **T090**: NetworkPolicy for service-to-service communication
- ✅ **T091**: TLS/SSL certificates using cert-manager
- ✅ **T092**: Cloud Ingress configuration with TLS
- ✅ **T094**: Production resource requests and limits
- ✅ **T096**: Cloud teardown script
- ✅ **T097**: Kafka with replication for durability
- ✅ **T098**: Database connection pooling configuration

## Directory Structure

```
phase5-advanced-cloud-deployment/
├── backend/                          # FastAPI backend
│   └── src/
│       └── database.py              # ✅ Connection pooling added
├── frontend/                         # Next.js frontend
├── infrastructure/
│   └── helm/
│       └── todo-app/                # Helm chart
│           ├── Chart.yaml           # ✅ Chart metadata
│           ├── values-cloud.yaml    # ✅ Production values
│           └── templates/
│               ├── _helpers.tpl     # ✅ Template helpers
│               ├── backend/
│               │   ├── deployment.yaml  # ✅ With probes & rolling updates
│               │   ├── hpa.yaml         # ✅ Autoscaling
│               │   └── service.yaml     # ✅ Service definition
│               ├── frontend/
│               │   ├── deployment.yaml  # ✅ With probes & rolling updates
│               │   └── service.yaml     # ✅ Service definition
│               ├── notification-service/
│               │   ├── deployment.yaml  # ✅ With probes & rolling updates
│               │   ├── hpa.yaml         # ✅ Autoscaling
│               │   └── service.yaml     # ✅ Service definition
│               ├── recurring-task-service/
│               │   ├── deployment.yaml  # ✅ With probes & rolling updates
│               │   ├── hpa.yaml         # ✅ Autoscaling
│               │   └── service.yaml     # ✅ Service definition
│               ├── certificate.yaml     # ✅ TLS certificates
│               ├── configmap.yaml       # ✅ Configuration
│               ├── ingress-cloud.yaml   # ✅ Cloud ingress with TLS
│               ├── networkpolicy.yaml   # ✅ Network policies
│               ├── pdb.yaml             # ✅ Pod disruption budgets
│               ├── secret.yaml          # ✅ Secrets management
│               └── serviceaccount.yaml  # ✅ Service account
└── scripts/
    └── cloud/
        ├── setup-cluster-gke.sh     # ✅ GKE cluster setup
        ├── setup-cluster-aks.sh     # ✅ AKS cluster setup
        ├── deploy-cloud.sh          # ✅ Cloud deployment
        └── teardown-cloud.sh        # ✅ Cloud teardown
```

## Prerequisites

### Required Tools

- **kubectl** (v1.28+)
- **helm** (v3.12+)
- **Cloud CLI** (one of):
  - `gcloud` for Google Cloud (GKE)
  - `az` for Azure (AKS)
  - `oci` for Oracle Cloud (OKE)

### Cloud Provider Accounts

Choose one cloud provider:

1. **Google Cloud (GKE)** - $300 credit for 90 days
2. **Azure (AKS)** - $200 credit for 30 days
3. **Oracle Cloud (OKE)** - Always free tier (4 OCPUs, 24GB RAM)

## Quick Start

### 1. Setup Cloud Cluster

#### Option A: Google Cloud (GKE)

```bash
# Set environment variables
export GCP_PROJECT_ID="your-project-id"
export CLUSTER_NAME="todoboard-cluster"
export GCP_ZONE="us-central1-a"

# Run setup script
cd scripts/cloud
chmod +x setup-cluster-gke.sh
./setup-cluster-gke.sh
```

#### Option B: Azure (AKS)

```bash
# Set environment variables
export AZURE_RESOURCE_GROUP="todoboard-rg"
export CLUSTER_NAME="todoboard-cluster"
export AZURE_LOCATION="eastus"

# Run setup script
cd scripts/cloud
chmod +x setup-cluster-aks.sh
./setup-cluster-aks.sh
```

#### Option C: Oracle Cloud (OKE)

```bash
# Set environment variables
export OCI_COMPARTMENT_ID="your-compartment-id"
export CLUSTER_NAME="todoboard-cluster"

# Run setup script (from phase4)
cd ../phase4-kubernetes-deployment/scripts/cloud
chmod +x setup-cluster-oke.sh
./setup-cluster-oke.sh
```

### 2. Configure Secrets

Create a `secrets.yaml` file with your credentials:

```bash
kubectl create secret generic todoboard-secrets \
  --from-literal=POSTGRES_PASSWORD='your-db-password' \
  --from-literal=JWT_SECRET_KEY='your-jwt-secret' \
  --from-literal=GROQ_API_KEY='your-groq-api-key' \
  -n todoboard
```

### 3. Update Helm Values

Edit `infrastructure/helm/todo-app/values-cloud.yaml`:

```yaml
# Update these values
ingress:
  hosts:
    - host: todoboard.yourdomain.com  # Your domain

  tls:
    acme:
      email: "admin@yourdomain.com"   # Your email

configMap:
  backend:
    DATABASE_URL: "postgresql://user:pass@your-neon-host/todoboard?sslmode=require"
    CORS_ORIGINS: '["https://todoboard.yourdomain.com"]'

  frontend:
    NEXT_PUBLIC_API_URL: "https://todoboard.yourdomain.com/api"
```

### 4. Deploy Application

```bash
# Install Helm chart
helm install todoboard ./infrastructure/helm/todo-app \
  -f ./infrastructure/helm/todo-app/values-cloud.yaml \
  -n todoboard \
  --create-namespace

# Check deployment status
kubectl get pods -n todoboard
kubectl get ingress -n todoboard
```

### 5. Configure DNS

Get the ingress IP address:

```bash
kubectl get ingress -n todoboard todoboard-cloud -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

Create an A record in your DNS provider:
- **Name**: `todoboard` (or `@` for root domain)
- **Type**: `A`
- **Value**: `<ingress-ip-address>`

### 6. Verify Deployment

Wait for TLS certificate to be issued (2-5 minutes):

```bash
kubectl get certificate -n todoboard
```

Access your application:
- **Frontend**: `https://todoboard.yourdomain.com`
- **Backend API**: `https://todoboard.yourdomain.com/api`
- **Health Check**: `https://todoboard.yourdomain.com/health`

## Production Features

### High Availability

- **Multiple Replicas**: 3 backend, 2 frontend, 2 notification, 2 recurring task service
- **Pod Disruption Budgets**: Ensures minimum availability during updates
- **Anti-Affinity Rules**: Spreads pods across nodes
- **Rolling Updates**: Zero-downtime deployments

### Auto-Scaling

All services configured with HorizontalPodAutoscaler:

```yaml
backend:
  minReplicas: 3
  maxReplicas: 10
  targetCPU: 70%
  targetMemory: 80%
```

### Health Checks

All deployments include:
- **Liveness Probes**: Restart unhealthy pods
- **Readiness Probes**: Remove pods from service until ready
- **Startup Probes**: Allow slow-starting containers

### Security

- **Network Policies**: Restrict pod-to-pod communication
- **TLS/SSL**: Automatic certificate management with cert-manager
- **Security Contexts**: Run as non-root, drop capabilities
- **Secrets Management**: Kubernetes secrets for sensitive data

### Database Connection Pooling

Production-grade connection pooling for Neon PostgreSQL:

```python
# Enable in environment variables
DB_USE_POOLING=true
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
DB_POOL_PRE_PING=true
```

### Kafka Configuration

Production Kafka with replication:

```yaml
kafka:
  replicaCount: 3
  replicationFactor: 3
  minInsyncReplicas: 2
```

## Monitoring

### View Logs

```bash
# Backend logs
kubectl logs -f deployment/todoboard-backend -n todoboard

# Frontend logs
kubectl logs -f deployment/todoboard-frontend -n todoboard

# All pods
kubectl logs -f -l app.kubernetes.io/name=todoboard -n todoboard
```

### Check Resource Usage

```bash
# Pod metrics
kubectl top pods -n todoboard

# Node metrics
kubectl top nodes
```

### View HPA Status

```bash
kubectl get hpa -n todoboard
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n todoboard

# Check events
kubectl get events -n todoboard --sort-by=.metadata.creationTimestamp
```

### Certificate Issues

```bash
# Check certificate status
kubectl describe certificate todoboard-tls -n todoboard

# Check cert-manager logs
kubectl logs -n cert-manager deployment/cert-manager
```

### Ingress Not Working

```bash
# Check ingress status
kubectl describe ingress todoboard-cloud -n todoboard

# Check ingress controller logs
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller
```

### Database Connection Issues

```bash
# Test database connectivity
kubectl run -it --rm debug --image=postgres:16-alpine --restart=Never -n todoboard -- \
  psql "postgresql://user:pass@your-neon-host/todoboard?sslmode=require"
```

## Cleanup

To delete all resources and the cluster:

```bash
cd scripts/cloud
chmod +x teardown-cloud.sh

# Set cloud provider
export CLOUD_PROVIDER=gke  # or aks, oke

# Run teardown
./teardown-cloud.sh
```

## Cost Optimization

### Development/Testing

- Use smaller node sizes
- Reduce replica counts
- Disable autoscaling
- Use spot/preemptible instances

### Production

- Enable autoscaling
- Use reserved instances for base capacity
- Monitor and optimize resource requests/limits
- Set up budget alerts

## Next Steps

1. **CI/CD Pipeline** (Phase 7): Automate deployments with GitHub Actions
2. **Monitoring** (Phase 8): Add Prometheus, Grafana, and alerting
3. **Load Testing**: Verify performance under load
4. **Disaster Recovery**: Set up backups and recovery procedures

## Support

For issues or questions:
- Check the [troubleshooting guide](#troubleshooting)
- Review Kubernetes events: `kubectl get events -n todoboard`
- Check application logs: `kubectl logs -f <pod-name> -n todoboard`

## License

MIT License - See LICENSE file for details
