# Phase 4 - Kubernetes Deployment

This repository contains the Kubernetes deployment configuration for the fullstack Todo Web application, with an AI-powered todo chatbot. This is Phase 4 of the Evolution of Todo project, focusing on containerization, Kubernetes deployment and orchestration using Minikube and Helm.

## Overview

#### Architecture
A full-stack Todo web application that combines:
- **Frontend**: Next.js UI with chatbot interface, served via a NodePort service, making it accessible from outside the cluster.
- **Backend**: A FastAPI server with AI integration, running as a ClusterIP service, only accessible from within the cluster.
- **Database**: An external PostgreSQL database hosted on Neon.
- **LLM (AI Integration)**: An external API for AI-powered features. (OpenAI/Groq API)

**Phase 4 packages the application for local Kubernetes deployment using. The key technologies used in this deployment are:**
- **Minikube** - For running a local Kubernetes cluster.
- **Helm 3** - For managing the application's Kubernetes packages. (Kubernetes package manager)
- **Docker** - For containerizing the frontend and backend services.
- **kubectl** - For interacting with the Kubernetes cluster. (Kubernetes CLI)

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
# For macOS
brew install minikube

# For Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# For Windows (with WSL2)
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

### 2. **Helm 3** - Kubernetes package manager
```bash
# For macOS
brew install helm

# For Linux/WSL2
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### 3. **Docker** - Container runtime
```bash
# For macOS
brew install --cask docker

# For Linux/WSL2
# Follow the official installation guide: https://docs.docker.com/engine/install/
```

### 4. **kubectl** - Kubernetes CLI
```bash
# For macOS
brew install kubectl

# For Linux/WSL2
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

## Environment Setup

Before deploying the application, you need to set up your environment variables.

1.  **Create an environment file**: Copy the example file to create your own local environment configuration.
    ```bash
    cp .env.example .env
    ```

2.  **Edit the file**: Open the `.env` file and add your credentials .
    ```bash
    nano .env # Or use any other text editor to edit .env with your DATABASE_URL, OPENAI_API_KEY (or use GEMINI_API_KEY/GROQ_API_KEY), and BETTER_AUTH_SECRET
    ```

    You will need to provide values for the following:
    - `DATABASE_URL`: Your PostgreSQL connection string.
    - `BETTER_AUTH_SECRET`: A secret key for authentication, which you can generate with `openssl rand -base64 32`.
    - `OPENAI_API_KEY`: Your API key for the language model. You can replace this with another LLM provider key (`GEMINI_API_KEY`/`GROQ_API_KEY`)


## Quick Start

### One-Command Setup
For a quick and automated setup, run these commands in sequence:

### 1. Set up environment variables
Copy the example environment file and fill in your credentials:
```bash
cp .env.example .env
# Edit .env with your DATABASE_URL, OPENAI_API_KEY (or use GEMINI_API_KEY/GROQ_API_KEY), and BETTER_AUTH_SECRET
```

### 2. Run the deployment script
```bash
./scripts/deploy.sh
```
This script will handle all the necessary steps:
- ✅ Verify that all prerequisite tools are installed.
- ✅ Start Minikube cluster (if not running).
- ✅ Configure Docker to use Minikube's daemon.
- ✅ Build the Docker images for the frontend and backend.
- ✅ Load the environment variables from your `.env` file.
- ✅ Create a dedicated Kubernetes namespace for the application.
- ✅ Deploy the application using the Helm chart.
- ✅ Wait for all application pods to become ready.
- ✅ Provide you with the URL to access the application.

```
*Note: You may need to run `minikube tunnel` in a separate terminal to expose the LoadBalancer service.*

### Alternative: Automated Setup Script (Step-by-Step)
If you prefer to deploy manually, you can follow these instruction for the setup:

# 1. Start Minikube
minikube start --cpus=2 --memory=4096 --driver=docker

# Set up Docker Environment
# Configure your shell to use Minikube's Docker daemon.
eval $(minikube docker-env)

# 2. Build Docker images for the frontend and backend applications.
docker build -t todoboard-backend:latest phase4-kubernetes-deployment/backend/
docker build -t todoboard-frontend:latest phase4-kubernetes-deployment/frontend/

# 3. Create a separate namespace in Kubernetes for the application.
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

# 6. Verify the Deployment
# Check the status of your pods to ensure they are running correctly.
# Get the status of all pods in the namespace
kubectl get pods -n todo-app

# Wait for the pods to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=todo-app -n todo-app --timeout=120s
```

## Accessing the Application

After a successful deployment, the application will be available at:

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

## Kubernetes Management Useful Commands
We have provided several scripts in the `scripts/` directory to simplify common tasks.
Here are some useful commands for managing and observing your application in Kubernetes.

### Pods and Resources
```bash
# View all pods (shortcuts)
./scripts/get-pods.sh

# View all Cluster resources in the namespace
kubectl get all -n todoboard

# View specific resources

# List pods with more detailed information
kubectl get pods -n todoboard -o wide

# List all services in the namespace
kubectl get svc -n todoboard

# List all deployments
kubectl get deployments -n todoboard

# View the application's configuration maps
kubectl get configmaps -n todoboard

# View the application's secrets
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

- **Pods in ImagePullBackOff**: Image Not Found Errors. If you see `ImagePullBackOff` or `ErrImagePull`, make sure you have run `eval $(minikube docker-env)` in your terminal before building the Docker images.
- **Database Connection**: Check if `todoboard-postgres` pod is ready and logs show successful initialization.
- **Frontend Unreachable**: Ensure `minikube tunnel` is running if you are using LoadBalancer type on a system that doesn't support it natively.
- **Pod Crashes**: Use `kubectl describe pod -n todo-app <pod-name>` to see events and `kubectl logs -n todo-app <pod-name>` to check for application errors. This can often point to missing environment variables or database connection issues.
- **Connection Issues**: Ensure that your database URL is correct and that the database is accessible. For frontend connection issues, verify the service is correctly exposed.


### View logs using the scripts
`./scripts/check-logs.sh frontend`, `./scripts/check-logs.sh backend`

Manual log viewing: `kubectl logs -n todoboard <pod-name>`

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

### Inspecting Logs and Debugging Pods
```bash
# Stream the logs from the frontend application
kubectl logs -n todoboard -l app.kubernetes.io/component=frontend --tail=100 -f

# Stream the logs from the backend application
kubectl logs -n todoboard -l app.kubernetes.io/component=backend --tail=100 -f

# Execute a command inside a running pod (e.g., to see environment variables)
kubectl exec -n todoboard <your-pod-name> -- env
```


## Development

### Building Images
```bash
# Build backend
docker build -t todoboard-backend:dev phase4-kubernetes-deployment/backend/

# Build frontend
docker build -t todoboard-frontend:dev phase4-kubernetes-deployment/frontend/
```

### Application Scaling
```bash
# Scale the number of frontend replicas to 3
kubectl scale deployment -n todo-app todo-app-frontend --replicas=3

# Scale the number of backend replicas to 3
kubectl scale deployment -n todo-app todo-app-backend --replicas=3
```
Alternatively, you can manage scaling through Helm:
```bash
helm upgrade todo-app ./helm/todo-app \
  -f ./helm/todo-app/values-dev.yaml \
  -n todo-app \
  --set replicaCount.frontend=3 \
  --set replicaCount.backend=3
```

### Deploying Updates
To apply changes to your application:
```bash
# 1. After making code changes, rebuild images:
eval $(minikube docker-env)
docker build -t todoboard-frontend:latest ./frontend
# or
docker build -t todoboard-backend:latest ./backend

# 2. Trigger a rolling restart of the deployment to use new images
kubectl rollout restart deployment -n todoboard todoboard-frontend
# or
kubectl rollout restart deployment -n todoboard todoboard-backend

# 3. Monitor the status of the rollout
kubectl rollout status deployment -n todoboard todoboard-frontend
```
Updating Deployment:
```bash
# Upgrade with new values
helm upgrade todoboard k8s/charts/todoboard \
  --namespace=todoboard \
  --values k8s/charts/todoboard/values-minikube.yaml \
  --set backend.image.tag=dev \
  --set frontend.image.tag=dev
```

### Cleanup
To remove the application and shut down the local cluster, follow these steps.
```bash
# Uninstall chart
helm uninstall todoboard -n todoboard

# Delete the Kubernetes namespace
kubectl delete namespace todoboard

# Cleanup tunnel
minikube tunnel --cleanup

# Stop the Minikube cluster
minikube stop

# To delete the cluster and all its data
minikube delete
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
