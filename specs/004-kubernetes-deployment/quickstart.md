# Quickstart Guide: Local Kubernetes Deployment

**Feature**: 004-kubernetes-deployment
**Date**: 2026-01-11
**Purpose**: Step-by-step guide for deploying the TodoBoard application to a local Kubernetes cluster using Minikube and Helm.

## Prerequisites

### Required Tools

| Tool | Minimum Version | Purpose | Installation |
|------|----------------|---------|--------------|
| Docker Desktop | 4.25+ | Container runtime | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop) |
| Minikube | 1.32+ | Local Kubernetes cluster | [minikube.sigs.k8s.io/docs/start](https://minikube.sigs.k8s.io/docs/start/) |
| kubectl | 1.28+ | Kubernetes CLI | [kubernetes.io/docs/tasks/tools](https://kubernetes.io/docs/tasks/tools/) |
| Helm | 3.13+ | Kubernetes package manager | [helm.sh/docs/intro/install](https://helm.sh/docs/intro/install/) |

### System Requirements

- **CPU**: 2 cores minimum, 4 cores recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 20GB free space
- **OS**: Windows 10+, macOS 12+, or Linux (Ubuntu 20.04+)

### Optional Tools (AI-Assisted Operations)

| Tool | Purpose | Installation |
|------|---------|--------------|
| kubectl-ai | Natural language Kubernetes queries | [github.com/GoogleCloudPlatform/kubectl-ai](https://github.com/GoogleCloudPlatform/kubectl-ai) |
| kagent | Cluster analysis and optimization | [github.com/kagent-dev/kagent](https://github.com/kagent-dev/kagent) |
| Gordon (Docker AI) | AI-assisted Docker operations | Enable in Docker Desktop Settings > Beta features |

---

## Quick Start (5 Minutes)

### 1. Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start --cpus=2 --memory=4096 --driver=docker

# Verify cluster is running
kubectl cluster-info
kubectl get nodes
```

**Expected Output**:
```
Kubernetes control plane is running at https://127.0.0.1:xxxxx
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   30s   v1.28.x
```

### 2. Build Container Images

```bash
# Navigate to project directory
cd phase4-kubernetes-deployment

# Build backend image
docker build -t todoboard-backend:0.1.0 ./backend

# Build frontend image
docker build -t todoboard-frontend:0.1.0 ./frontend

# Load images into Minikube
minikube image load todoboard-backend:0.1.0
minikube image load todoboard-frontend:0.1.0

# Verify images are loaded
minikube image ls | grep todoboard
```

### 3. Create Secrets

```bash
# Create namespace (optional, uses 'default' if skipped)
kubectl create namespace todoboard

# Create secrets for sensitive data
kubectl create secret generic app-secrets \
  --from-literal=POSTGRES_PASSWORD=changeme \
  --from-literal=JWT_SECRET=your-jwt-secret-key \
  --from-literal=OPENAI_API_KEY=your-openai-key \
  --from-literal=GROQ_API_KEY=your-groq-key

# Verify secret created
kubectl get secrets
```

### 4. Deploy with Helm

```bash
# Navigate to Helm chart directory
cd k8s/charts/todoboard

# Install the chart
helm install todoboard . -f values-minikube.yaml

# Watch deployment progress
kubectl get pods -w
```

**Expected Output**:
```
NAME                                  READY   STATUS    RESTARTS   AGE
todoboard-backend-xxxxxxxxxx-xxxxx    1/1     Running   0          30s
todoboard-frontend-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
todoboard-postgres-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
```

### 5. Access the Application

```bash
# Get Minikube IP
minikube ip

# Get frontend NodePort
kubectl get service todoboard-frontend

# Access application in browser
# URL: http://<minikube-ip>:30000
```

**Alternative (using minikube service)**:
```bash
# Automatically open application in browser
minikube service todoboard-frontend
```

---

## Detailed Setup Guide

### Step 1: Verify Prerequisites

```bash
# Check Docker
docker --version
docker ps

# Check Minikube
minikube version

# Check kubectl
kubectl version --client

# Check Helm
helm version
```

### Step 2: Configure Minikube

```bash
# Start Minikube with custom configuration
minikube start \
  --cpus=2 \
  --memory=4096 \
  --disk-size=20g \
  --driver=docker \
  --kubernetes-version=v1.28.3

# Enable useful addons
minikube addons enable metrics-server
minikube addons enable dashboard

# Verify addons
minikube addons list
```

**Troubleshooting**:
- **Windows**: If using Hyper-V, run PowerShell as Administrator
- **macOS**: If using VirtualBox, ensure virtualization is enabled in BIOS
- **Linux**: Ensure Docker daemon is running (`sudo systemctl start docker`)

### Step 3: Build and Load Images

#### Backend Image

```bash
cd phase4-kubernetes-deployment/backend

# Build with multi-stage Dockerfile
docker build -t todoboard-backend:0.1.0 .

# Verify image
docker images | grep todoboard-backend

# Load into Minikube
minikube image load todoboard-backend:0.1.0
```

#### Frontend Image

```bash
cd ../frontend

# Build with multi-stage Dockerfile
docker build -t todoboard-frontend:0.1.0 .

# Verify image
docker images | grep todoboard-frontend

# Load into Minikube
minikube image load todoboard-frontend:0.1.0
```

**Image Build Tips**:
- First build may take 5-10 minutes (downloads dependencies)
- Subsequent builds are faster (layer caching)
- Use `.dockerignore` to exclude unnecessary files
- Multi-stage builds reduce final image size

### Step 4: Prepare Configuration

#### Create .env File (for reference)

```bash
# Create .env file with secrets (DO NOT COMMIT)
cat > .env << EOF
POSTGRES_PASSWORD=changeme
JWT_SECRET=$(openssl rand -base64 32)
OPENAI_API_KEY=sk-your-openai-key
GROQ_API_KEY=gsk_your-groq-key
EOF
```

#### Create Kubernetes Secrets

```bash
# Option 1: From .env file
kubectl create secret generic app-secrets --from-env-file=.env

# Option 2: From literal values
kubectl create secret generic app-secrets \
  --from-literal=POSTGRES_PASSWORD=changeme \
  --from-literal=JWT_SECRET=$(openssl rand -base64 32) \
  --from-literal=OPENAI_API_KEY=sk-your-key \
  --from-literal=GROQ_API_KEY=gsk-your-key

# Verify secret (values are base64 encoded)
kubectl get secret app-secrets -o yaml
```

### Step 5: Deploy with Helm

#### Validate Chart

```bash
cd k8s/charts/todoboard

# Lint chart for errors
helm lint .

# Dry-run to see generated manifests
helm install todoboard . -f values-minikube.yaml --dry-run --debug

# Template to see final YAML
helm template todoboard . -f values-minikube.yaml > /tmp/manifests.yaml
```

#### Install Chart

```bash
# Install with default values
helm install todoboard . -f values-minikube.yaml

# Install with custom values
helm install todoboard . -f values-minikube.yaml \
  --set backend.replicaCount=2 \
  --set postgresql.persistence.size=10Gi

# Install in specific namespace
helm install todoboard . -f values-minikube.yaml --namespace todoboard --create-namespace
```

#### Monitor Deployment

```bash
# Watch pods starting
kubectl get pods -w

# Check deployment status
kubectl get deployments

# Check services
kubectl get services

# Check persistent volumes
kubectl get pvc

# View logs
kubectl logs -l app=todoboard-backend
kubectl logs -l app=todoboard-frontend
kubectl logs -l app=todoboard-postgres
```

### Step 6: Verify Deployment

#### Health Checks

```bash
# Check backend health
kubectl port-forward service/todoboard-backend 8000:8000
curl http://localhost:8000/health

# Check frontend health
kubectl port-forward service/todoboard-frontend 3000:3000
curl http://localhost:3000/api/health

# Check database connectivity
kubectl exec -it deployment/todoboard-postgres -- psql -U postgres -d todoboard -c "SELECT 1;"
```

#### Functional Testing

```bash
# Get application URL
minikube service todoboard-frontend --url

# Open in browser
minikube service todoboard-frontend

# Test features:
# 1. Register new user
# 2. Login
# 3. Create task
# 4. Use AI chatbot
# 5. Verify task persists after pod restart
```

#### Data Persistence Test

```bash
# Create a task via UI or API
# Then restart backend pod
kubectl delete pod -l app=todoboard-backend

# Wait for new pod to start
kubectl get pods -w

# Verify task still exists (refresh browser)
```

---

## Configuration Management

### Environment-Specific Values

**Minikube (values-minikube.yaml)**:
```yaml
frontend:
  service:
    type: NodePort
    nodePort: 30000

postgresql:
  persistence:
    storageClass: standard
    size: 5Gi

backend:
  replicaCount: 1
  resources:
    limits:
      memory: 512Mi
```

**Production (values-production.yaml)** - Phase V:
```yaml
frontend:
  service:
    type: LoadBalancer

postgresql:
  persistence:
    storageClass: gp3
    size: 20Gi

backend:
  replicaCount: 3
  resources:
    limits:
      memory: 1Gi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
```

### Updating Configuration

```bash
# Update values file
vim values-minikube.yaml

# Upgrade deployment
helm upgrade todoboard . -f values-minikube.yaml

# Rollback if needed
helm rollback todoboard

# View revision history
helm history todoboard
```

---

## Common Operations

### Scaling

```bash
# Scale backend manually
kubectl scale deployment todoboard-backend --replicas=3

# Scale via Helm
helm upgrade todoboard . --set backend.replicaCount=3

# Verify scaling
kubectl get pods -l app=todoboard-backend
```

### Updating Images

```bash
# Build new image version
docker build -t todoboard-backend:0.2.0 ./backend

# Load into Minikube
minikube image load todoboard-backend:0.2.0

# Update deployment
helm upgrade todoboard . --set backend.image.tag=0.2.0

# Watch rolling update
kubectl rollout status deployment/todoboard-backend
```

### Viewing Logs

```bash
# Stream logs from all backend pods
kubectl logs -f -l app=todoboard-backend

# View logs from specific pod
kubectl logs todoboard-backend-xxxxxxxxxx-xxxxx

# View logs from previous container (if crashed)
kubectl logs todoboard-backend-xxxxxxxxxx-xxxxx --previous

# View logs from all containers in pod
kubectl logs todoboard-backend-xxxxxxxxxx-xxxxx --all-containers
```

### Debugging

```bash
# Describe pod (shows events and status)
kubectl describe pod todoboard-backend-xxxxxxxxxx-xxxxx

# Execute command in pod
kubectl exec -it todoboard-backend-xxxxxxxxxx-xxxxx -- /bin/bash

# Check environment variables
kubectl exec todoboard-backend-xxxxxxxxxx-xxxxx -- env

# Check mounted volumes
kubectl exec todoboard-backend-xxxxxxxxxx-xxxxx -- ls -la /var/lib/postgresql/data

# Port forward for local testing
kubectl port-forward service/todoboard-backend 8000:8000
```

### Database Operations

```bash
# Connect to database
kubectl exec -it deployment/todoboard-postgres -- psql -U postgres -d todoboard

# Backup database
kubectl exec deployment/todoboard-postgres -- pg_dump -U postgres todoboard > backup.sql

# Restore database
kubectl exec -i deployment/todoboard-postgres -- psql -U postgres todoboard < backup.sql

# View database size
kubectl exec deployment/todoboard-postgres -- psql -U postgres -c "SELECT pg_size_pretty(pg_database_size('todoboard'));"
```

---

## AI-Assisted Operations (Optional)

### Using kubectl-ai

```bash
# Install kubectl-ai
# Follow instructions at: https://github.com/GoogleCloudPlatform/kubectl-ai

# Natural language queries
kubectl-ai "show me all pods that are not running"
kubectl-ai "scale the backend to 3 replicas"
kubectl-ai "why is the frontend pod failing?"
kubectl-ai "show me resource usage for all pods"
```

### Using kagent

```bash
# Install kagent
# Follow instructions at: https://github.com/kagent-dev/kagent

# Cluster analysis
kagent "analyze cluster health"
kagent "optimize resource allocation"
kagent "identify bottlenecks"
kagent "suggest improvements"
```

### Using Gordon (Docker AI)

```bash
# Enable Gordon in Docker Desktop Settings > Beta features

# AI-assisted Docker operations
docker ai "What can you do?"
docker ai "Build an optimized image for my FastAPI app"
docker ai "Why is my container using so much memory?"
docker ai "Show me best practices for multi-stage builds"
```

---

## Troubleshooting

### Pods Not Starting

**Symptom**: Pods stuck in `Pending`, `ImagePullBackOff`, or `CrashLoopBackOff`

**Solutions**:
```bash
# Check pod events
kubectl describe pod <pod-name>

# Common issues:
# 1. Image not found
minikube image ls | grep todoboard
minikube image load todoboard-backend:0.1.0

# 2. Insufficient resources
kubectl describe node minikube
minikube start --cpus=4 --memory=8192

# 3. Failed health checks
kubectl logs <pod-name>
# Increase initialDelaySeconds in values.yaml

# 4. Missing secrets
kubectl get secrets
kubectl create secret generic app-secrets --from-literal=POSTGRES_PASSWORD=changeme
```

### Cannot Access Application

**Symptom**: Browser cannot connect to application URL

**Solutions**:
```bash
# Check service
kubectl get service todoboard-frontend

# Get Minikube IP
minikube ip

# Check NodePort
kubectl get service todoboard-frontend -o jsonpath='{.spec.ports[0].nodePort}'

# Use minikube service (automatic)
minikube service todoboard-frontend

# Check firewall (Windows)
# Allow port 30000 in Windows Firewall

# Check network (macOS)
# Ensure Docker Desktop networking is enabled
```

### Database Connection Errors

**Symptom**: Backend logs show "could not connect to database"

**Solutions**:
```bash
# Check database pod
kubectl get pod -l app=todoboard-postgres

# Check database logs
kubectl logs -l app=todoboard-postgres

# Verify secret
kubectl get secret app-secrets -o jsonpath='{.data.POSTGRES_PASSWORD}' | base64 -d

# Test connection from backend pod
kubectl exec -it deployment/todoboard-backend -- env | grep DATABASE_URL

# Verify service DNS
kubectl exec -it deployment/todoboard-backend -- nslookup todoboard-postgres
```

### Persistent Data Loss

**Symptom**: Tasks disappear after pod restart

**Solutions**:
```bash
# Check PVC status
kubectl get pvc

# Check PV binding
kubectl get pv

# Verify mount in pod
kubectl exec deployment/todoboard-postgres -- df -h | grep postgresql

# Check storage class
kubectl get storageclass

# Recreate PVC if needed
kubectl delete pvc postgres-data
helm upgrade todoboard . -f values-minikube.yaml
```

---

## Cleanup

### Uninstall Application

```bash
# Uninstall Helm release
helm uninstall todoboard

# Verify pods are deleted
kubectl get pods

# Delete secrets
kubectl delete secret app-secrets

# Delete PVC (WARNING: deletes data)
kubectl delete pvc postgres-data
```

### Stop Minikube

```bash
# Stop cluster (preserves state)
minikube stop

# Delete cluster (removes all data)
minikube delete

# Delete all Minikube clusters
minikube delete --all
```

### Clean Docker Images

```bash
# Remove local images
docker rmi todoboard-backend:0.1.0
docker rmi todoboard-frontend:0.1.0

# Clean up unused images
docker image prune -a
```

---

## Next Steps

### Phase V: Cloud Kubernetes Deployment

After successfully deploying to Minikube, proceed to Phase V for cloud deployment:

1. **Choose Cloud Provider**: DigitalOcean (DOKS), Google Cloud (GKE), or Azure (AKS)
2. **Create Kubernetes Cluster**: Use cloud provider console or CLI
3. **Update Helm Values**: Use `values-production.yaml` with cloud-specific settings
4. **Configure Ingress**: Set up Ingress controller with TLS certificates
5. **Enable Autoscaling**: Configure HPA for automatic scaling
6. **Set Up Monitoring**: Deploy Prometheus and Grafana
7. **Implement CI/CD**: Automate deployments with GitOps (ArgoCD/Flux)

### Bonus Features

- **+200 points**: Create reusable Claude subagents/skills for Kubernetes deployment
- **+200 points**: Build Cloud-Native Blueprints for 1-click infrastructure setup
- **+100 points**: Add Urdu language support to chatbot
- **+200 points**: Implement voice commands via Web Speech API

---

## Resources

### Documentation
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Docker Documentation](https://docs.docker.com/)

### Tutorials
- [Kubernetes Basics](https://kubernetes.io/docs/tutorials/kubernetes-basics/)
- [Helm Getting Started](https://helm.sh/docs/intro/quickstart/)
- [Docker Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)

### Tools
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Helm Commands](https://helm.sh/docs/helm/helm/)
- [Minikube Commands](https://minikube.sigs.k8s.io/docs/commands/)

---

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review Kubernetes events: `kubectl get events --sort-by='.lastTimestamp'`
3. Check application logs: `kubectl logs -l app=todoboard-backend`
4. Consult project documentation in `specs/004-kubernetes-deployment/`

**Deployment Time**: ~5 minutes (after prerequisites installed)
**Success Criteria**: Application accessible at `http://<minikube-ip>:30000` with all Phase III features functional
