# Phase 4 - Kubernetes Deployment

This repository contains the Kubernetes deployment configuration for the fullstack Todo Web application, with an AI-powered todo chatbot. This is Phase 4 of the Evolution of Todo project, focusing on containerization and Kubernetes deployment.

## Overview

A full-stack Todo web application that combines:
- Frontend: Next.js UI with chatbot interface
- Backend: FastAPI server with AI integration
- Database: PostgreSQL for persistent storage

## Required Environment Variables for Kubernetes Deployment

The application requires the following environment variables to be configured in Kubernetes secrets and deployments:

### Backend Environment Variables (Configured in Kubernetes Secret)
- `DATABASE_URL`: PostgreSQL connection string (configured in secret)
- `GROQ_API_KEY`: Groq API key for AI functionality (configured in secret as `openai-api-key`)
- `JWT_SECRET_KEY`: Secret key for JWT token generation (configured in secret as `better-auth-secret`)
- `JWT_ALGORITHM`: Algorithm for JWT signing (default: `HS256`)
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: `10080`)
- `CORS_ORIGINS`: Allowed origins for CORS (default: `["http://localhost:3000"]`)
- `APP_NAME`: Application name (default: `Todo Web Application`)
- `APP_VERSION`: Application version (default: `1.0.0`)
- `ENVIRONMENT`: Environment setting (default: `development`)

### Frontend Environment Variables (Configured in Kubernetes Secret)
- `NEXT_PUBLIC_CHATKIT_DOMAIN_KEY`: ChatKit domain key for chat functionality (configured in secret)
- `NEXT_PUBLIC_API_URL`: Backend API URL (default: `http://localhost:8000`)

### Kubernetes-Specific Environment Variables (Automatically Configured)
- `DATABASE_URL`: PostgreSQL connection string (from secret, value: `postgresql://todo:password@todo-postgres:5432/todoboard`)
- `OPENAI_API_KEY`: OpenAI API key (from secret as `openai-api-key`)
- `BETTER_AUTH_SECRET`: Better Auth secret (from secret as `better-auth-secret`)
- `NEXT_PUBLIC_BETTER_AUTH_URL`: Internal backend URL (value: `http://todo-backend:8000`)
- `BACKEND_URL`: Internal backend service URL (value: `http://todo-backend:8000`)
- `NEXTAUTH_URL`: NextAuth URL for the frontend in Kubernetes environment (value: `http://todo-frontend:3000`)


## Prerequisites

Before starting, ensure you have the following tools installed:

### 1. **Minikube** - Local Kubernetes cluster
```bash
# macOS
brew install minikube

# Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Windows (WSL2)
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

### 2. **Helm 3** - Kubernetes package manager
```bash
# macOS
brew install helm

# Linux/WSL2
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### 3. **Docker** - Container runtime
```bash
# macOS
brew install --cask docker

# Linux/WSL2
# Follow: https://docs.docker.com/engine/install/
```

### 4. **kubectl** - Kubernetes CLI
```bash
# macOS
brew install kubectl

# Linux/WSL2
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

## Quick Start

### One-Command Setup
For a quick setup, run these commands in sequence:

1. Start Minikube:
```bash
minikube start --cpus=2 --memory=4096 --driver=docker
eval $(minikube docker-env)
```

2. Build Docker images:
```bash
# Backend
docker build -t todoboard-backend:latest phase4-kubernetes-deployment/backend/

# Frontend
docker build -t todoboard-frontend:latest phase4-kubernetes-deployment/frontend/
```

3. Create namespace and secrets:
```bash
kubectl create namespace todoboard

# Create secrets (replace with your actual values)
kubectl create secret generic todoboard-secrets \
  --from-literal=postgres-password=your-secure-password \
  --from-literal=openai-api-key=your-api-key \
  --from-literal=better-auth-secret=your-auth-secret \
  --from-literal=postgres-db=todoboard \
  --from-literal=postgres-user=todoboard \
  --from-literal=postgres-url=postgresql://todoboard:your-secure-password@todoboard-postgres:5432/todoboard \
  --namespace=todoboard
```

4. Deploy with Helm:
```bash
helm install todoboard k8s/charts/todoboard \
  --namespace=todoboard \
  --values k8s/charts/todoboard/values-minikube.yaml
```

5. Access the application:
```bash
# Start tunnel to expose LoadBalancer services
minikube tunnel

# Get frontend URL
echo "Frontend: http://$(kubectl get svc todoboard-frontend -n todoboard -o jsonpath='{.status.loadBalancer.ingress[0].ip}'):3000"
```

### Alternative: Automated Setup Script
You can also use the following script to automate the setup:

```bash
#!/bin/bash

# Start Minikube
minikube start --cpus=2 --memory=4096 --driver=docker
eval $(minikube docker-env)

# Build Docker images
docker build -t todoboard-backend:latest phase4-kubernetes-deployment/backend/
docker build -t todoboard-frontend:latest phase4-kubernetes-deployment/frontend/

# Create namespace
kubectl create namespace todoboard

# Create secrets (update with your actual values)
kubectl create secret generic todoboard-secrets \
  --from-literal=postgres-password=your-secure-password \
  --from-literal=openai-api-key=your-api-key \
  --from-literal=better-auth-secret=your-auth-secret \
  --from-literal=postgres-db=todoboard \
  --from-literal=postgres-user=todoboard \
  --from-literal=postgres-url=postgresql://todoboard:your-secure-password@todoboard-postgres:5432/todoboard \
  --namespace=todoboard

# Deploy with Helm
helm install todoboard k8s/charts/todoboard \
  --namespace=todoboard \
  --values k8s/charts/todoboard/values-minikube.yaml

echo "Deployment complete! Starting tunnel..."
minikube tunnel
```

## Accessing the Application

The application will be available at:

**Frontend UI**: `http://<minikube-ip>:3000`
To get the Minikube IP:
```bash
minikube ip
```

Or directly access the service:
```bash
minikube service todoboard-frontend -n todoboard --url
```

## Helm Chart Configuration

The Helm chart supports the following configuration options:

### Global Values
- `global.imagePullPolicy`: Image pull policy (default: "IfNotPresent")
- `global.imageRegistry`: Registry prefix (default: "")
- `global.namespace`: Target namespace (default: "todoboard")

### Frontend Values
- `frontend.enabled`: Enable frontend deployment (default: true)
- `frontend.replicaCount`: Number of frontend replicas (default: 2)
- `frontend.image.repository`: Frontend image repository (default: "todoboard-frontend")
- `frontend.image.tag`: Frontend image tag (default: "latest")
- `frontend.service.type`: Service type (default: "LoadBalancer")
- `frontend.service.port`: Service port (default: 3000)

### Backend Values
- `backend.enabled`: Enable backend deployment (default: true)
- `backend.replicaCount`: Number of backend replicas (default: 2)
- `backend.image.repository`: Backend image repository (default: "todoboard-backend")
- `backend.image.tag`: Backend image tag (default: "latest")
- `backend.service.type`: Service type (default: "ClusterIP")
- `backend.service.port`: Service port (default: 8000)

### PostgreSQL Values
- `postgres.enabled`: Enable postgres deployment (default: true)
- `postgres.replicaCount`: Number of postgres replicas (default: 1)
- `postgres.image.repository`: Postgres image repository (default: "postgres")
- `postgres.image.tag`: Postgres image tag (default: "16")
- `postgres.persistence.enabled`: Enable persistent storage (default: true)
- `postgres.persistence.size`: Storage size (default: "1Gi")

## Minikube-Specific Configuration

The `values-minikube.yaml` file includes overrides suitable for Minikube:
- Uses LoadBalancer service type for frontend
- Reduced resource requirements for local development
- Standard storage class for persistence

## AI-Assisted Operations

This deployment supports AI-assisted Kubernetes operations:

### Using kubectl-ai
```bash
# Natural language kubectl commands
kubectl-ai "scale the frontend to 3 replicas"
kubectl-ai "show me recent errors in backend logs"
kubectl-ai "what's the status of all pods"
```

### Using Docker AI (Gordon)
```bash
# Get Docker assistance
docker ai "How do I optimize this Dockerfile?"
docker ai "Best practices for multi-stage builds"
```

## Troubleshooting

### Pods Not Starting
- Check events: `kubectl describe pod <pod-name> -n todoboard`
- Verify images exist: `docker images | grep todoboard`
- Check resource constraints: `kubectl describe nodes`

### Connection Issues
- Verify tunnel is running: `minikube tunnel`
- Check services: `kubectl get svc -n todoboard`
- Check endpoints: `kubectl get endpoints -n todoboard`

### Database Connection Issues
- Check postgres service: `kubectl get svc todoboard-postgres -n todoboard`
- Check postgres logs: `kubectl logs -n todoboard -l app=todoboard-postgres`

## Development

### Building Images
```bash
# Build backend
docker build -t todoboard-backend:dev phase4-kubernetes-deployment/backend/

# Build frontend
docker build -t todoboard-frontend:dev phase4-kubernetes-deployment/frontend/
```

### Updating Deployment
```bash
# Upgrade with new values
helm upgrade todoboard k8s/charts/todoboard \
  --namespace=todoboard \
  --values k8s/charts/todoboard/values-minikube.yaml \
  --set backend.image.tag=dev \
  --set frontend.image.tag=dev
```

### Cleanup
```bash
# Uninstall chart
helm uninstall todoboard -n todoboard

# Delete namespace
kubectl delete namespace todoboard

# Cleanup tunnel
minikube tunnel --cleanup
```