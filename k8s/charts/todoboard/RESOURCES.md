# Resource Usage Metrics for TodoBoard

This document provides information about the resource usage and requirements for the TodoBoard Kubernetes deployment.

## Resource Requirements

### Default Resource Configuration

#### Frontend Service
- **Memory Requests**: 256Mi
- **Memory Limits**: 512Mi
- **CPU Requests**: 100m
- **CPU Limits**: 500m
- **Storage**: None (ephemeral)

#### Backend Service
- **Memory Requests**: 512Mi
- **Memory Limits**: 1Gi
- **CPU Requests**: 200m
- **CPU Limits**: 1000m (1 CPU)
- **Storage**: None (ephemeral)

#### PostgreSQL Database
- **Memory Requests**: 256Mi
- **Memory Limits**: 512Mi
- **CPU Requests**: 100m
- **CPU Limits**: 500m
- **Storage**: 1Gi Persistent Volume

### Total Resource Requirements (Minimum)

- **Memory**: 1.024Gi (requests), 2.024Gi (limits)
- **CPU**: 400m (requests), 2000m (2 CPUs, limits)
- **Storage**: 1Gi Persistent Volume

## Actual Resource Usage

### Typical Usage Patterns

Based on testing with moderate load (10-50 concurrent users):

#### Frontend Service
- **Memory**: 150-200Mi average, 300-400Mi peak
- **CPU**: 20-50m average, 100-200m peak
- **Network**: 1-5 Mbps incoming, 2-10 Mbps outgoing

#### Backend Service
- **Memory**: 300-400Mi average, 600-800Mi peak
- **CPU**: 50-150m average, 300-500m peak
- **Network**: 0.5-2 Mbps incoming, 1-5 Mbps outgoing

#### PostgreSQL Database
- **Memory**: 150-250Mi average, 400-500Mi peak
- **CPU**: 10-50m average, 100-200m peak
- **Storage**: 100-500MB (growing based on data)

### Peak Load Scenarios

Under high load (100+ concurrent users):

#### Frontend Service
- **Memory**: 300-500Mi peak
- **CPU**: 200-400m peak

#### Backend Service
- **Memory**: 600-1000Mi peak
- **CPU**: 500-800m peak

#### PostgreSQL Database
- **Memory**: 400-600Mi peak
- **CPU**: 200-400m peak

## Resource Optimization Recommendations

### For Development (Minikube)
- Frontend: Reduce to 128Mi requests, 256Mi limits
- Backend: Reduce to 256Mi requests, 512Mi limits
- PostgreSQL: Reduce to 128Mi requests, 256Mi limits

### For Production
- Frontend: Increase to 512Mi requests for better performance
- Backend: Increase to 1Gi requests for stability
- PostgreSQL: Consider using dedicated storage class

### Horizontal Pod Autoscaling

The following metrics can be used for HPA:

#### Frontend
- Target CPU utilization: 70%
- Target Memory utilization: 80%
- Min replicas: 1
- Max replicas: 10

#### Backend
- Target CPU utilization: 70%
- Target Memory utilization: 80%
- Min replicas: 1
- Max replicas: 5

## Monitoring Resource Usage

### Using kubectl

```bash
# View resource usage of all pods
kubectl top pods -n todoboard

# View resource usage of all nodes
kubectl top nodes

# Get detailed resource requests and limits
kubectl describe pods -n todoboard
```

### Using Helm Values for Adjustment

```yaml
# Example values override for resource adjustment
frontend:
  resources:
    requests:
      memory: "512Mi"
      cpu: "200m"
    limits:
      memory: "1Gi"
      cpu: "1000m"

backend:
  resources:
    requests:
      memory: "1Gi"
      cpu: "500m"
    limits:
      memory: "2Gi"
      cpu: "2000m"
```

## Resource Scaling Strategies

### Vertical Scaling
- Increase resource limits when pods are consistently hitting limits
- Monitor for OOMKilled events in pod logs
- Balance between resource allocation and node capacity

### Horizontal Scaling
- Use HPA based on CPU and memory metrics
- Consider application statelessness for scaling
- Monitor for connection pool limitations in backend

## Storage Considerations

### PostgreSQL Persistence
- Default: 1Gi storage
- Recommended for production: 10Gi+ with backup strategy
- Monitor disk usage: `df -h` inside postgres container
- Consider separate storage class for performance

### Backup and Retention
- Database backups: Daily automated
- Log retention: 7 days in container, longer in external storage
- Persistent data: Protected by PVC

## Cost Optimization

### For Development Environments
- Use smaller resource requests
- Scale down to 0 replicas when not in use
- Use local Minikube instead of cloud clusters

### For Production Environments
- Right-size resources based on actual usage
- Use cluster autoscaling
- Implement resource quotas per namespace
- Monitor and optimize unused resources