# Kubernetes Deployment for TodoBoard

This directory contains the Helm charts and Kubernetes manifests for deploying the TodoBoard application to Kubernetes.

## Overview

The TodoBoard application is packaged as a Helm chart with the following components:

- **Frontend**: Next.js application serving the user interface
- **Backend**: FastAPI application handling API requests and business logic
- **PostgreSQL**: PostgreSQL database for data persistence

## Chart Structure

```
k8s/
├── charts/
    └── todoboard/
        ├── Chart.yaml          # Chart metadata
        ├── values.yaml         # Default configuration values
        ├── values-minikube.yaml # Minikube-specific overrides
        ├── templates/          # Kubernetes manifest templates
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

## Quick Start

### Prerequisites

- Kubernetes cluster (tested with Minikube)
- Helm 3.x
- kubectl

### Installation

1. **Start Minikube** (for local development):
   ```bash
   minikube start --cpus=2 --memory=4096 --driver=docker
   ```

2. **Build Docker images**:
   ```bash
   eval $(minikube docker-env)
   docker build -t todoboard-frontend:latest ../phase3-todo-ai-chatbot/frontend/
   docker build -t todoboard-backend:latest ../phase3-todo-ai-chatbot/backend/
   ```

3. **Create namespace and secrets**:
   ```bash
   kubectl create namespace todoboard
   kubectl create secret generic todoboard-secrets \
     --from-literal=postgres-password=your-secure-password \
     --from-literal=openai-api-key=your-api-key \
     --namespace=todoboard
   ```

4. **Install the chart**:
   ```bash
   helm install todoboard . --namespace=todoboard --create-namespace
   ```

5. **Access the application**:
   ```bash
   # For LoadBalancer services, you may need to run:
   minikube tunnel
   ```

## Configuration

The chart supports various configuration options through `values.yaml`. Key parameters include:

- `frontend.replicaCount`: Number of frontend pods
- `backend.replicaCount`: Number of backend pods
- `postgres.persistence.size`: Database storage size
- Resource requests and limits for all components

## Documentation

- `KUBERNETES.md`: Architecture overview and troubleshooting
- `KUBECTL_AI.md`: Examples for kubectl-ai operations
- `KAGENT.md`: Examples for Kagent cluster management
- `RESOURCES.md`: Resource usage metrics
- `../specs/004-kubernetes-deployment/`: Complete specification and plan

## Uninstall

```bash
helm uninstall todoboard -n todoboard
kubectl delete namespace todoboard
```