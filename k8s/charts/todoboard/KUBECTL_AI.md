# kubectl-ai Examples for TodoBoard

This document provides examples of using kubectl-ai for managing the TodoBoard Kubernetes deployment.

## Installation

```bash
# Install kubectl-ai plugin
curl -sL https://run.kubectl.ai/install | bash
```

## Common Operations

### Scaling Services

```bash
# Scale frontend to 3 replicas
kubectl-ai "scale the frontend to 3 replicas"

# Scale backend to 2 replicas
kubectl-ai "scale todoboard-backend deployment to 2 replicas in todoboard namespace"

# Scale postgres to 1 replica (usually keep at 1 for single instance)
kubectl-ai "scale todoboard-postgres deployment to 1 replica"
```

### Troubleshooting

```bash
# Check why pods are not starting
kubectl-ai "check why pods are not starting in todoboard namespace"

# Show recent errors in logs
kubectl-ai "show me recent errors in backend logs"

# Describe why a specific pod is failing
kubectl-ai "describe pod todoboard-backend-xxxxx -n todoboard"

# Check resource usage
kubectl-ai "show me resource usage for all pods in todoboard namespace"
```

### Deployment Management

```bash
# Restart a deployment
kubectl-ai "restart the backend deployment"

# Check deployment status
kubectl-ai "show me the status of all deployments in todoboard namespace"

# Get service information
kubectl-ai "get me the external IP of the frontend service"
```

### Health Checks

```bash
# Check overall health
kubectl-ai "analyze the health of my todoboard deployment"

# Check specific pods
kubectl-ai "show me the status of all pods in todoboard namespace"

# Check service connectivity
kubectl-ai "check if frontend service can connect to backend service"
```

### Resource Management

```bash
# Update resource limits
kubectl-ai "increase memory limit of backend container to 2Gi"

# Check resource consumption
kubectl-ai "show me CPU and memory usage of all containers"
```

### Configuration Updates

```bash
# Update environment variables
kubectl-ai "update the OPENAI_API_KEY in backend deployment"

# Change service type
kubectl-ai "change frontend service type to NodePort"
```

## Advanced Operations

### Rolling Updates

```bash
# Perform rolling update
kubectl-ai "update the frontend image to tag v1.1"

# Check rollout status
kubectl-ai "check rollout status of frontend deployment"
```

### Backup and Recovery

```bash
# Get current configuration
kubectl-ai "export the current configuration of todoboard namespace"

# Describe PVC status
kubectl-ai "show me the status of all persistent volume claims"
```

## Best Practices

1. Always specify namespace when using kubectl-ai for TodoBoard operations
2. Use descriptive queries that clearly state your intent
3. Verify changes after applying them with kubectl-ai commands
4. Combine kubectl-ai with regular kubectl for complex operations