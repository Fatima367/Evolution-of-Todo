# Kubernetes Deployment for TodoBoard

This document provides an overview of the TodoBoard Kubernetes deployment architecture and troubleshooting guide.

## Architecture Overview

The TodoBoard application is deployed as a three-tier architecture on Kubernetes:

1. **Frontend Service**: Next.js application serving the user interface
2. **Backend Service**: FastAPI application handling API requests and business logic
3. **PostgreSQL Database**: PostgreSQL database for data persistence

### Components

#### Frontend
- **Deployment**: `todoboard-frontend`
- **Service Type**: LoadBalancer (for external access via Minikube tunnel)
- **Port**: 3000
- **Image**: `todoboard-frontend:latest`
- **Environment**:
  - `NEXT_PUBLIC_API_URL`: Points to the backend service

#### Backend
- **Deployment**: `todoboard-backend`
- **Service Type**: ClusterIP (internal access only)
- **Port**: 8000
- **Image**: `todoboard-backend:latest`
- **Environment**:
  - `DATABASE_URL`: Connection string for PostgreSQL
  - `OPENAI_API_KEY`: API key for OpenAI integration
  - `PORT`: Application port

#### PostgreSQL
- **Deployment**: `todoboard-postgres`
- **Service Type**: ClusterIP (internal access only)
- **Port**: 5432
- **Image**: `postgres:16`
- **Persistent Storage**: 1Gi PersistentVolumeClaim
- **Environment**:
  - `POSTGRES_DB`: Database name (todoboard)
  - `POSTGRES_USER`: Database user (todoboard)
  - `POSTGRES_PASSWORD`: Database password (from secret)

### Networking

- Frontend service is exposed externally via LoadBalancer service type
- Backend and PostgreSQL services are internal only (ClusterIP)
- Service-to-service communication happens internally via Kubernetes DNS

### Storage

- PostgreSQL uses a PersistentVolumeClaim for data persistence
- Data is stored in `/var/lib/postgresql/data/pgdata` inside the container
- Storage class uses the default provisioner in Minikube

## Deployment Structure

```
k8s/
├── charts/
    └── todoboard/
        ├── Chart.yaml          # Chart metadata
        ├── values.yaml         # Default configuration values
        ├── values-minikube.yaml # Minikube-specific overrides
        ├── templates/
        │   ├── _helpers.tpl    # Template helper functions
        │   ├── NOTES.txt       # Installation notes
        │   ├── configmap.yaml  # Configuration data
        │   ├── secret.yaml     # Sensitive data
        │   ├── pvc.yaml        # Persistent volume claim
        │   ├── deployment-frontend.yaml
        │   ├── deployment-backend.yaml
        │   ├── deployment-postgres.yaml
        │   ├── service-frontend.yaml
        │   ├── service-backend.yaml
        │   └── service-postgres.yaml
```

## Configuration

### Values Override

The deployment uses two value files:
1. `values.yaml` - Default configuration for all environments
2. `values-minikube.yaml` - Minikube-specific overrides

Key configuration options:
- `frontend.replicaCount` - Number of frontend pods
- `backend.replicaCount` - Number of backend pods
- `postgres.replicaCount` - Number of postgres pods (should remain 1)
- `frontend.service.type` - Service type (LoadBalancer for Minikube)
- `postgres.persistence.size` - Database storage size

## Troubleshooting

### Common Issues

#### Pods Not Starting
1. Check pod status: `kubectl get pods -n todoboard`
2. Check pod logs: `kubectl logs -n todoboard <pod-name>`
3. Describe pod: `kubectl describe pod -n todoboard <pod-name>`
4. Verify Docker images exist in Minikube: `eval $(minikube docker-env) && docker images`

#### Service Not Accessible
1. Check service status: `kubectl get svc -n todoboard`
2. Verify LoadBalancer has external IP: `kubectl get svc todoboard-frontend -n todoboard`
3. Ensure minikube tunnel is running: `minikube tunnel`

#### Database Connection Issues
1. Check postgres pod status: `kubectl get pods -n todoboard -l app=todoboard-postgres`
2. Verify database is running: `kubectl logs -n todoboard -l app=todoboard-postgres`
3. Test connectivity from backend: `kubectl exec -it -n todoboard deploy/todoboard-backend -- nc -zv todoboard-postgres 5432`

#### Resource Constraints
1. Check node resources: `kubectl describe nodes`
2. Check pod resource usage: `kubectl top pods -n todoboard`
3. Adjust resource limits in values.yaml if needed

### Useful Commands

#### Status Checks
```bash
# Overall status
kubectl get all -n todoboard

# Pod status
kubectl get pods -n todoboard

# Service status
kubectl get svc -n todoboard

# Deployment status
kubectl get deployments -n todoboard
```

#### Logs
```bash
# View frontend logs
kubectl logs -n todoboard -l app=todoboard-frontend

# View backend logs
kubectl logs -n todoboard -l app=todoboard-backend

# Follow logs in real-time
kubectl logs -n todoboard -l app=todoboard-backend -f
```

#### Scaling
```bash
# Scale frontend
kubectl scale deployment todoboard-frontend -n todoboard --replicas=2

# Scale backend
kubectl scale deployment todoboard-backend -n todoboard --replicas=2
```

## Security Considerations

- Secrets are stored in Kubernetes secrets and mounted as environment variables
- Service-to-service communication happens internally via ClusterIP services
- Database credentials are not exposed in configuration files
- Pod security contexts are configured for minimal privileges

## Resource Usage

### Default Resource Requirements
- Frontend: requests 256Mi memory, 100m CPU; limits 512Mi memory, 500m CPU
- Backend: requests 512Mi memory, 200m CPU; limits 1Gi memory, 1000m CPU
- PostgreSQL: requests 256Mi memory, 100m CPU; limits 512Mi memory, 500m CPU

### Recommended Minikube Configuration
- 2 CPU cores
- 4GB RAM
- 20GB disk space

## Development Workflow

1. Build Docker images: `docker build -t <image-name> .`
2. Deploy with Helm: `helm install/upgrade`
3. Verify deployment: Check pods and services
4. Access application: Use external IP from LoadBalancer service
5. Debug issues: Check logs and pod descriptions