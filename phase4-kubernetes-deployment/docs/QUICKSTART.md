# TodoBoard Kubernetes Deployment - Quick Start Guide

This guide will help you deploy the TodoBoard application to a local Kubernetes cluster using Minikube and Helm in under 5 minutes.

## Prerequisites

Before you begin, ensure you have the following tools installed:

| Tool | Minimum Version | Installation |
|------|----------------|--------------|
| Docker Desktop | 4.25+ | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop) |
| Minikube | 1.32+ | [minikube.sigs.k8s.io/docs/start](https://minikube.sigs.k8s.io/docs/start/) |
| kubectl | 1.28+ | [kubernetes.io/docs/tasks/tools](https://kubernetes.io/docs/tasks/tools/) |
| Helm | 3.13+ | [helm.sh/docs/intro/install](https://helm.sh/docs/intro/install/) |

**System Requirements:**
- CPU: 2 cores minimum, 4 cores recommended
- RAM: 4GB minimum, 8GB recommended
- Disk: 20GB free space
- OS: Windows 10+, macOS 12+, or Linux (Ubuntu 20.04+)

## Quick Start (5 Minutes)

### Step 1: Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start --cpus=2 --memory=4096 --driver=docker

# Verify cluster is running
kubectl cluster-info
kubectl get nodes
```

**Expected Output:**
```
Kubernetes control plane is running at https://127.0.0.1:xxxxx
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   30s   v1.28.x
```

### Step 2: Build and Load Container Images

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

### Step 3: Create Secrets

```bash
# Create secrets for sensitive data
kubectl create secret generic app-secrets \
  --from-literal=POSTGRES_PASSWORD=changeme \
  --from-literal=JWT_SECRET=your-jwt-secret-key \
  --from-literal=GROQ_API_KEY=your-groq-api-key

# Verify secret created
kubectl get secrets
```

### Step 4: Deploy with Helm

```bash
# Navigate to Helm chart directory
cd k8s/charts/todoboard

# Install the chart
helm install todoboard . -f values-minikube.yaml

# Watch deployment progress
kubectl get pods -w
```

**Expected Output:**
```
NAME                                  READY   STATUS    RESTARTS   AGE
todoboard-backend-xxxxxxxxxx-xxxxx    1/1     Running   0          30s
todoboard-frontend-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
todoboard-postgres-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
```

### Step 5: Access the Application

```bash
# Get Minikube IP
minikube ip

# Get frontend NodePort
kubectl get service todoboard-frontend

# Access application in browser
# URL: http://<minikube-ip>:30000
```

**Alternative (automatic browser opening):**
```bash
minikube service todoboard-frontend
```

## Verification

### Check Deployment Status

```bash
# Check all pods are running
kubectl get pods

# Check services are created
kubectl get services

# Check persistent volumes
kubectl get pvc
```

### Test Application Features

1. Open the application in your browser
2. Register a new user account
3. Login with your credentials
4. Create a new task
5. Test the AI chatbot feature
6. Verify task persists after pod restart:
   ```bash
   kubectl delete pod -l app=todoboard-backend
   kubectl get pods -w
   # Refresh browser and verify task still exists
   ```

## Common Commands

### View Logs

```bash
# Backend logs
kubectl logs -f -l app=todoboard-backend

# Frontend logs
kubectl logs -f -l app=todoboard-frontend

# Database logs
kubectl logs -f -l app=todoboard-postgres
```

### Update Deployment

```bash
# Modify values-minikube.yaml
vim values-minikube.yaml

# Upgrade deployment
helm upgrade todoboard . -f values-minikube.yaml

# Check rollout status
kubectl rollout status deployment/todoboard-backend
```

### Cleanup

```bash
# Uninstall application
helm uninstall todoboard

# Delete secrets
kubectl delete secret app-secrets

# Delete PVC (WARNING: deletes data)
kubectl delete pvc todoboard-postgres-data

# Stop Minikube
minikube stop

# Delete Minikube cluster
minikube delete
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod events
kubectl describe pod <pod-name>

# Common issues:
# 1. Image not found - reload images into Minikube
# 2. Insufficient resources - increase Minikube memory
# 3. Missing secrets - create app-secrets
```

### Cannot Access Application

```bash
# Check service
kubectl get service todoboard-frontend

# Get Minikube IP
minikube ip

# Use minikube service (automatic)
minikube service todoboard-frontend
```

### Database Connection Errors

```bash
# Check database pod
kubectl get pod -l app=todoboard-postgres

# Check database logs
kubectl logs -l app=todoboard-postgres

# Verify secret
kubectl get secret app-secrets -o yaml
```

## Next Steps

- Read the [Environment Setup Guide](./ENVIRONMENT_SETUP.md) for detailed configuration
- Check [Troubleshooting Guide](./TROUBLESHOOTING.md) for common issues
- Explore [AI-Assisted Operations](./KUBECTL_AI.md) for enhanced productivity

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review Kubernetes events: `kubectl get events --sort-by='.lastTimestamp'`
3. Check application logs: `kubectl logs -l app=todoboard-backend`
4. Consult project documentation in `specs/004-kubernetes-deployment/`

**Deployment Time:** ~5 minutes (after prerequisites installed)
**Success Criteria:** Application accessible at `http://<minikube-ip>:30000` with all Phase III features functional
