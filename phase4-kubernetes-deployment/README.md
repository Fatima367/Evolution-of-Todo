# Phase 4 - Kubernetes Deployment

This repository contains the Kubernetes deployment configuration for the fullstack Todo Web application, with an AI-powered todo chatbot. This is Phase 4 of the Evolution of Todo project, focusing on containerization, Kubernetes deployment and orchestration using Minikube and Helm.

## Overview

A full-stack Todo web application that combines:
- Frontend: Next.js UI with chatbot interface
- Backend: FastAPI server with AI integration
- Database: PostgreSQL for persistent storage
- AI Integration: External OpenAI/Groq API

***Phase 4 packages the application for local Kubernetes deployment using:***
- **Minikube** - Local Kubernetes cluster
- **Helm 3** - Kubernetes package manager
- **Docker** - Container runtime
- **kubectl** - Kubernetes CLI


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

### 1. Set up environment variables
Copy the example environment file and fill in your credentials:
```bash
cp .env.example .env
# Edit .env with your DATABASE_URL, OPENAI_API_KEY (or use GEMINI_API_KEY / GROQ_API_KEY), and BETTER_AUTH_SECRET
```

### 2. Run the deployment script
```bash
./scripts/deploy.sh
```
This script will:
- ✅ Validate prerequisites
- ✅ Start Minikube (if not running)
- ✅ Configure Docker to use Minikube's daemon
- ✅ Build frontend and backend images
- ✅ Create the `todoboard` namespace
- ✅ Deploy the application using Helm
- ✅ Wait for pods to be ready

### 3. Access the application
Once deployment completes, the application will be available at:

**Frontend UI**: `http://<minikube-ip>:3000`
To get the Minikube IP:
```bash
minikube ip
```

Or directly access the service:
```bash
minikube service todoboard-frontend -n todoboard --url
```
*Note: You may need to run `minikube tunnel` in a separate terminal to expose the LoadBalancer service.*

### Alternative: Automated Setup Script (Step-by-Step)
If you prefer to deploy manually, you can use the following scripts to automate the setup:

```bash
#!/bin/bash

# 1. Start Minikube
minikube start --cpus=2 --memory=4096 --driver=docker
eval $(minikube docker-env)

# 2. Build Docker images
docker build -t todoboard-backend:latest phase4-kubernetes-deployment/backend/
docker build -t todoboard-frontend:latest phase4-kubernetes-deployment/frontend/

# 3. Create namespace
kubectl create namespace todoboard

# 4. Create secrets (update with your actual values)
kubectl create secret generic todoboard-secrets \
  --from-literal=postgres-password=your-secure-password \
  --from-literal=openai-api-key=your-api-key \
  --from-literal=better-auth-secret=your-auth-secret \
  --from-literal=postgres-db=todoboard \
  --from-literal=postgres-user=todoboard \
  --from-literal=postgres-url=postgresql://todoboard:your-secure-password@todoboard-postgres:5432/todoboard \
  --namespace=todoboard

# 5. Deploy with Helm
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

### Kubernetes Resources
- **Namespace**: `todoboard`
- **Deployments**: `todoboard-frontend`, `todoboard-backend`
- **StatefulSet**: `todoboard-postgres`
- **Services**: `todoboard-frontend` (LoadBalancer), `todoboard-backend` (ClusterIP), `todoboard-postgres` (ClusterIP)
- **ConfigMap**: `todoboard-config` for non-sensitive data
- **Secret**: `todoboard-secrets` for credentials

## Useful Commands

We have provided several scripts in the `scripts/` directory to simplify common tasks.

### Pods and Resources
```bash
# View all pods (shortcuts)
./scripts/get-pods.sh

# View all resources in the namespace
kubectl get all -n todoboard

# View specific resources
kubectl get pods -n todoboard -o wide
kubectl get svc -n todoboard
kubectl get deployments -n todoboard
kubectl get configmaps -n todoboard
kubectl get secrets -n todoboard
```


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

- **Pods in ImagePullBackOff**: Ensure you ran `eval $(minikube docker-env)` before building images.
- **Database Connection**: Check if `todoboard-postgres` pod is ready and logs show successful initialization.
- **Frontend Unreachable**: Ensure `minikube tunnel` is running if you are using LoadBalancer type on a system that doesn't support it natively.


### View logs using the scripts
./scripts/check-logs.sh frontend
./scripts/check-logs.sh backend

- Manual log viewing: `kubectl logs -n todoboard <pod-name>`

### Pods Not Starting
- Check events(Describe a pod for detailed events): `kubectl describe pod <pod-name> -n todoboard`
- Verify images exist: `docker images | grep todoboard`
- Check resource constraints: `kubectl describe nodes`
- Execute a command inside a pod: `kubectl exec -it -n todoboard <pod-name> -- /bin/sh`

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

### Scaling
```bash
# Scale backend to 3 replicas
kubectl scale deployment -n todoboard todoboard-backend --replicas=3

# Or update via Helm
helm upgrade todoboard k8s/charts/todoboard -n todoboard --set backend.replicaCount=3
```

### Updates
```bash
# After making code changes, rebuild images:
eval $(minikube docker-env)
docker build -t todoboard-frontend:latest ./frontend
docker build -t todoboard-backend:latest ./backend

# Restart deployments to use new images
kubectl rollout restart deployment -n todoboard todoboard-frontend
kubectl rollout restart deployment -n todoboard todoboard-backend
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

To completely remove the deployment:
```bash
./scripts/cleanup.sh
```

## AI DevOps Tools

Phase 4 includes documentation and support for AI-powered Kubernetes operations:

- **[kubectl-ai](./k8s/charts/todoboard/KUBECTL_AI.md)**: Natural language interface for Kubernetes operations.
  - `kubectl-ai "scale the frontend to 3 replicas"`
  - `kubectl-ai "show me recent errors in backend logs"`
- **[kagent](./k8s/charts/todoboard/KAGENT.md)**: Automated diagnostics and failure investigation workflows.
- **Docker AI (Gordon)**: AI assistance for Docker optimizations.
  - `docker ai "How do I optimize this Dockerfile?"`
  - `docker ai "Best practices for multi-stage builds"`
- **AI-Assisted Scaling**: Use LLMs to analyze resource usage and suggest scaling policies.

## Project Structure

```
phase4-kubernetes-deployment/
├── frontend/             # Next.js application & Dockerfile
├── backend/              # FastAPI application & Dockerfile
├── k8s/
│   └── charts/
│       └── todoboard/    # Helm chart
│           ├── templates/# K8s manifests
│           ├── values.yaml
│           └── values-minikube.yaml
├── scripts/              # Helper scripts
│   ├── deploy.sh         # One-command deployment
│   ├── get-pods.sh       # Pod status shortcut
│   ├── check-logs.sh     # Log streaming shortcut
│   └── cleanup.sh        # Full uninstall script
├── docs/                 # Environment setup documentation
└── README.md             # This file
```

## Security

- **Non-root Containers**: All application containers run as non-privileged users.
- **Secret Management**: Sensitive data is never hardcoded and is managed via Kubernetes Secrets.
- **Resource Quotas**: CPU and memory limits are enforced to prevent resource exhaustion.
- **Network Policies**: (Optional) Can be enabled to restrict traffic between components.
