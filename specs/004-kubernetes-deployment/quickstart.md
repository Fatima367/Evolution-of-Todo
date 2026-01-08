# Quickstart: Local Kubernetes Deployment

Deploy the Todo Chatbot application stack to local Kubernetes using Minikube.

## Prerequisites

Check installed versions before starting:

```bash
# Check Docker (requires 4.53+ for Gordon)
docker --version

# Check Minikube
minikube version

# Check Helm (3.x required)
helm version

# Check kubectl
kubectl version --client

# Optional: Check kubectl-ai
kubectl-ai version
```

## Setup

### 1. Start Minikube

Start Minikube with adequate resources for the full stack:

```bash
# Start with 2 CPUs and 4GB RAM
minikube start --cpus=2 --memory=4096 --driver=docker

# Enable registry addon (optional, for local images)
minikube addons enable registry

# Verify cluster is running
minikube status
```

### 2. Build Docker Images

Point Docker to Minikube's daemon and build images:

```bash
# Point Docker to Minikube
eval $(minikube docker-env)

# Build frontend image
docker build -t todoboard-frontend:latest phase3-todo-ai-chatbot/frontend/

# Build backend image
docker build -t todoboard-backend:latest phase3-todo-ai-chatbot/backend/

# Verify images exist
docker images | grep todoboard
```

### 3. Create Kubernetes Namespace and Secrets

```bash
# Create namespace
kubectl create namespace todoboard

# Create secrets for sensitive data
kubectl create secret generic todoboard-secrets \
  --from-literal=postgres-password=your-secure-password \
  --from-literal=openai-api-key=your-api-key \
  --namespace=todoboard

# Verify secrets
kubectl get secrets -n todoboard
```

### 4. Deploy with Helm

```bash
# Install the todoboard chart
helm install todoboard ./k8s/charts/todoboard \
  --namespace=todoboard \
  --values ./k8s/charts/todoboard/values-minikube.yaml

# Wait for all pods to be ready
kubectl wait --for=condition=ready pod -l app=todoboard-frontend -n todoboard --timeout=300s
kubectl wait --for=condition=ready pod -l app=todoboard-backend -n todoboard --timeout=300s
kubectl wait --for=condition=ready pod -l app=todoboard-postgres -n todoboard --timeout=300s

# Check pod status
kubectl get pods -n todoboard
```

### 5. Access Application

Start Minikube tunnel in a separate terminal:

```bash
# In a new terminal
minikube tunnel
```

Get the frontend URL:

```bash
# Get frontend IP and port
echo "Frontend URL: http://$(kubectl get svc todoboard-frontend -n todoboard -o jsonpath='{.status.loadBalancer.ingress[0].ip}'):3000"

# Get backend cluster IP (internal only)
echo "Backend API: http://$(kubectl get svc todoboard-backend -n todoboard -o jsonpath='{.spec.clusterIP}'):8000"
```

## Verify Deployment

### Check All Resources

```bash
# View all resources in namespace
kubectl get all -n todoboard

# Check deployment status
kubectl get deployments -n todoboard

# Check service endpoints
kubectl get endpoints -n todoboard
```

### Test Health Endpoints

```bash
# Test frontend health (if health endpoint exists)
curl http://localhost:3000/api/health

# Test backend health
curl http://localhost:8000/health

# Test database connection
kubectl exec -it -n todoboard deploy/todoboard-postgres -- psql -U todoboard -d todoboard -c "\dt"
```

### View Logs

```bash
# Frontend logs
kubectl logs -n todoboard -l app=todoboard-frontend --tail=100

# Backend logs
kubectl logs -n todoboard -l app=todoboard-backend --tail=100

# Follow logs in real-time
kubectl logs -n todoboard -l app=todoboard-backend -f
```

## Common Operations

### Scale Services

```bash
# Scale frontend
kubectl scale deployment todoboard-frontend -n todoboard --replicas=3

# Scale backend
kubectl scale deployment todoboard-backend -n todoboard --replicas=3

# Verify scaling
kubectl get pods -n todoboard -l app=todoboard-frontend
```

### Rolling Restart

```bash
# Trigger rolling restart
kubectl rollout restart deployment/todoboard-backend -n todoboard

# Check rollout status
kubectl rollout status deployment/todoboard-backend -n todoboard
```

### Rollback

```bash
# List release history
helm history todoboard -n todoboard

# Rollback to previous version
helm rollback todoboard 1 -n todoboard
```

### Update Configuration

```bash
# Update with new values
helm upgrade todoboard ./k8s/charts/todoboard \
  --namespace=todoboard \
  --values ./k8s/charts/todoboard/values-minikube.yaml \
  --set backend.replicaCount=3
```

### Uninstall

```bash
# Uninstall chart
helm uninstall todoboard -n todoboard

# Delete namespace (removes all resources)
kubectl delete namespace todoboard

# Cleanup tunnel (if running)
minikube tunnel --cleanup
```

## AI-Assisted Operations

### Using kubectl-ai

Natural language kubectl commands:

```bash
# Scale services
kubectl-ai "scale the frontend to 3 replicas"

# Debug issues
kubectl-ai "check why pods are not starting"
kubectl-ai "show me recent errors in backend logs"

# Get information
kubectl-ai "what's the status of all pods"
kubectl-ai "describe the frontend deployment"
```

### Using Kagent

Cluster management commands:

```bash
# Health analysis
kagent "analyze cluster health"
kagent "check resource utilization"

# Optimization
kagent "optimize resource allocation"
kagent "suggest improvements for my deployment"

# Capacity planning
kagent "what's my current capacity"
kagent "show me resource usage by namespace"
```

### Using Gordon (Docker AI)

Docker operations assistance:

```bash
# Docker help
docker ai "How do I optimize this Dockerfile?"
docker ai "Best practices for multi-stage builds"
docker ai "Check my image for security issues"
```

## Troubleshooting

### Pods Not Starting

```bash
# Check events
kubectl describe pod <pod-name> -n todoboard

# Check image exists
docker images | grep todoboard

# Check resource constraints
kubectl describe nodes | grep -A5 "Allocated resources"
```

### Connection Refused

```bash
# Verify tunnel is running
minikube tunnel --cleanup

# Check services
kubectl get svc -n todoboard

# Check endpoints
kubectl get endpoints -n todoboard
```

### Image Pull Error

```bash
# Check image pull policy
kubectl get pods -n todoboard -o jsonpath='{.items[*].spec.containers[*].imagePullPolicy}'

# Verify image is in Minikube Docker
eval $(minikube docker-env)
docker images | grep todoboard
```

### Out of Resources

```bash
# Check node capacity
kubectl describe nodes | grep -A10 "Allocated resources"

# View resource usage
kubectl top pods -n todoboard
kubectl top nodes
```

### Database Connection Issues

```bash
# Check postgres service
kubectl get svc todoboard-postgres -n todoboard

# Test connection from backend pod
kubectl exec -it -n todoboard deploy/todoboard-backend -- nc -zv todoboard-postgres 5432

# Check postgres logs
kubectl logs -n todoboard -l app=todoboard-postgres
```

## Next Steps

Once deployment is verified:

1. **Run End-to-End Tests**: Test task creation, chatbot interactions
2. **Create Agent Skills**: Document kubectl-ai and Kagent commands
3. **Optimize Resources**: Tune based on observed usage
4. **Document**: Update README with local deployment instructions
