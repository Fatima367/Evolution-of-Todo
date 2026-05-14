# TodoBoard Operational Runbook

This runbook provides step-by-step procedures for common operational tasks, troubleshooting, and incident response for the TodoBoard application.

## Table of Contents

1. [System Overview](#system-overview)
2. [Common Operations](#common-operations)
3. [Monitoring and Alerting](#monitoring-and-alerting)
4. [Troubleshooting](#troubleshooting)
5. [Scaling Operations](#scaling-operations)
6. [Backup and Recovery](#backup-and-recovery)
7. [Incident Response](#incident-response)
8. [Maintenance Procedures](#maintenance-procedures)

---

## System Overview

### Architecture Components

- **Frontend**: Next.js application (3 replicas in production)
- **Backend**: FastAPI application (3 replicas in production)
- **Microservices**:
  - Notification Service (2 replicas)
  - Recurring Task Service (2 replicas)
  - Audit Service (2 replicas)
- **Infrastructure**:
  - Kafka (3 brokers with replication)
  - Dapr runtime (sidecar pattern)
  - PostgreSQL (Neon Serverless)
  - NGINX Ingress Controller
  - cert-manager for TLS

### Key Metrics

- **Target Availability**: 99.9% (8.76 hours downtime/year)
- **Target Response Time**: p95 < 500ms
- **Target Error Rate**: < 0.1%

---

## Common Operations

### Viewing Application Status

```bash
# Check all pods
kubectl get pods -n todoboard

# Check services
kubectl get svc -n todoboard

# Check ingress
kubectl get ingress -n todoboard

# Check HPA status
kubectl get hpa -n todoboard

# Check certificate status
kubectl get certificate -n todoboard
```

### Viewing Logs

```bash
# Backend logs
kubectl logs -f deployment/todoboard-backend -n todoboard

# Frontend logs
kubectl logs -f deployment/todoboard-frontend -n todoboard

# Notification service logs
kubectl logs -f deployment/todoboard-notification-service -n todoboard

# View logs from all pods with a label
kubectl logs -f -l app.kubernetes.io/name=todoboard -n todoboard

# View logs from last hour
kubectl logs --since=1h deployment/todoboard-backend -n todoboard

# View logs with timestamps
kubectl logs --timestamps deployment/todoboard-backend -n todoboard
```

### Viewing Metrics

```bash
# Pod resource usage
kubectl top pods -n todoboard

# Node resource usage
kubectl top nodes

# Detailed pod metrics
kubectl describe pod <pod-name> -n todoboard
```

### Restarting Services

```bash
# Restart backend (rolling restart)
kubectl rollout restart deployment/todoboard-backend -n todoboard

# Restart frontend
kubectl rollout restart deployment/todoboard-frontend -n todoboard

# Restart specific microservice
kubectl rollout restart deployment/todoboard-notification-service -n todoboard

# Check rollout status
kubectl rollout status deployment/todoboard-backend -n todoboard
```

### Accessing Pods

```bash
# Execute command in pod
kubectl exec -it <pod-name> -n todoboard -- /bin/bash

# Execute command in specific container (if multiple containers)
kubectl exec -it <pod-name> -c backend -n todoboard -- /bin/bash

# Run one-off command
kubectl exec <pod-name> -n todoboard -- env
```

---

## Monitoring and Alerting

### Prometheus Queries

Access Prometheus at: `http://<prometheus-url>:9090`

**Key Queries**:

```promql
# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m])

# Response time (p95)
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Pod CPU usage
container_cpu_usage_seconds_total{namespace="todoboard"}

# Pod memory usage
container_memory_usage_bytes{namespace="todoboard"}

# Kafka lag
kafka_consumergroup_lag{namespace="kafka"}
```

### Grafana Dashboards

Access Grafana at: `http://<grafana-url>:3000`

**Available Dashboards**:
- Cluster Overview
- Application Metrics
- Kafka Metrics
- Database Performance

### Alert Conditions

**Critical Alerts** (Page on-call):
- Pod crash loop (> 3 restarts in 5 minutes)
- High error rate (> 1% for 5 minutes)
- Database connection failures
- Kafka broker down

**Warning Alerts** (Slack notification):
- High response time (p95 > 1s for 10 minutes)
- High CPU usage (> 80% for 15 minutes)
- High memory usage (> 85% for 15 minutes)
- Certificate expiring (< 7 days)

---

## Troubleshooting

### Pods Not Starting

**Symptoms**: Pods stuck in `Pending`, `CrashLoopBackOff`, or `ImagePullBackOff`

**Diagnosis**:
```bash
# Check pod status
kubectl describe pod <pod-name> -n todoboard

# Check events
kubectl get events -n todoboard --sort-by=.metadata.creationTimestamp | tail -20

# Check pod logs
kubectl logs <pod-name> -n todoboard --previous
```

**Common Causes**:
1. **Insufficient resources**: Check node capacity
   ```bash
   kubectl describe nodes
   ```
   **Solution**: Scale cluster or reduce resource requests

2. **Image pull errors**: Check image name and registry access
   ```bash
   kubectl describe pod <pod-name> -n todoboard | grep -A 5 "Events"
   ```
   **Solution**: Verify image exists and credentials are correct

3. **Configuration errors**: Check environment variables and secrets
   ```bash
   kubectl get secret todoboard-secrets -n todoboard -o yaml
   ```
   **Solution**: Update secrets or configmaps

### High Error Rate

**Symptoms**: Increased 5xx errors in logs or metrics

**Diagnosis**:
```bash
# Check backend logs for errors
kubectl logs deployment/todoboard-backend -n todoboard | grep -i error

# Check error rate in Prometheus
# Query: rate(http_requests_total{status=~"5.."}[5m])
```

**Common Causes**:
1. **Database connection issues**
   ```bash
   # Test database connectivity
   kubectl run -it --rm debug --image=postgres:16-alpine --restart=Never -n todoboard -- \
     psql "$DATABASE_URL"
   ```
   **Solution**: Check database status, connection pool settings, or network connectivity

2. **Kafka connection issues**
   ```bash
   # Check Kafka cluster status
   kubectl get kafka -n kafka

   # Check Kafka pods
   kubectl get pods -n kafka
   ```
   **Solution**: Restart Kafka brokers or check Dapr configuration

3. **Memory leaks or OOM**
   ```bash
   # Check memory usage
   kubectl top pods -n todoboard

   # Check OOM kills
   kubectl get events -n todoboard | grep OOM
   ```
   **Solution**: Increase memory limits or investigate memory leak

### Slow Response Times

**Symptoms**: High latency, timeouts, or slow page loads

**Diagnosis**:
```bash
# Check response times in logs
kubectl logs deployment/todoboard-backend -n todoboard | grep "duration"

# Check database query performance
# Connect to database and run: EXPLAIN ANALYZE <query>
```

**Common Causes**:
1. **Database slow queries**
   **Solution**: Add indexes, optimize queries, or increase connection pool

2. **High CPU usage**
   ```bash
   kubectl top pods -n todoboard
   ```
   **Solution**: Scale horizontally or optimize code

3. **Network latency**
   ```bash
   # Test network connectivity
   kubectl exec -it <pod-name> -n todoboard -- ping <service-name>
   ```
   **Solution**: Check network policies or service mesh configuration

### Certificate Issues

**Symptoms**: TLS errors, certificate warnings, or HTTPS not working

**Diagnosis**:
```bash
# Check certificate status
kubectl describe certificate todoboard-tls -n todoboard

# Check cert-manager logs
kubectl logs -n cert-manager deployment/cert-manager

# Check certificate expiration
kubectl get certificate -n todoboard -o jsonpath='{.items[*].status.notAfter}'
```

**Common Causes**:
1. **Certificate not issued**
   ```bash
   # Check certificate request
   kubectl get certificaterequest -n todoboard

   # Check challenges
   kubectl get challenges -n todoboard
   ```
   **Solution**: Check DNS configuration, ACME server connectivity, or cert-manager logs

2. **Certificate expired**
   **Solution**: Delete certificate to trigger renewal
   ```bash
   kubectl delete certificate todoboard-tls -n todoboard
   ```

### Kafka Issues

**Symptoms**: Events not being processed, high consumer lag, or message loss

**Diagnosis**:
```bash
# Check Kafka cluster status
kubectl get kafka -n kafka

# Check Kafka topics
kubectl exec -it todoboard-kafka-0 -n kafka -- \
  bin/kafka-topics.sh --bootstrap-server localhost:9092 --list

# Check consumer groups
kubectl exec -it todoboard-kafka-0 -n kafka -- \
  bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list

# Check consumer lag
kubectl exec -it todoboard-kafka-0 -n kafka -- \
  bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --group <consumer-group> --describe
```

**Common Causes**:
1. **High consumer lag**
   **Solution**: Scale consumers or optimize processing logic

2. **Broker down**
   ```bash
   kubectl get pods -n kafka
   ```
   **Solution**: Restart broker or check storage

3. **Topic misconfiguration**
   **Solution**: Update topic configuration or recreate topic

---

## Scaling Operations

### Manual Scaling

```bash
# Scale backend
kubectl scale deployment/todoboard-backend --replicas=5 -n todoboard

# Scale frontend
kubectl scale deployment/todoboard-frontend --replicas=3 -n todoboard

# Scale microservice
kubectl scale deployment/todoboard-notification-service --replicas=4 -n todoboard
```

### Autoscaling Configuration

```bash
# View HPA status
kubectl get hpa -n todoboard

# Edit HPA
kubectl edit hpa todoboard-backend -n todoboard

# Example HPA configuration
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: todoboard-backend
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: todoboard-backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Cluster Scaling

**GKE**:
```bash
gcloud container clusters resize todoboard-cluster \
  --num-nodes=5 \
  --zone=us-central1-a
```

**AKS**:
```bash
az aks scale \
  --resource-group todoboard-rg \
  --name todoboard-cluster \
  --node-count 5
```

---

## Backup and Recovery

### Database Backups

**Neon Serverless PostgreSQL** provides automatic backups. To create manual backup:

```bash
# Export database
pg_dump "$DATABASE_URL" > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database
psql "$DATABASE_URL" < backup_20260201_120000.sql
```

### Configuration Backups

```bash
# Backup all Kubernetes resources
kubectl get all -n todoboard -o yaml > backup_k8s_$(date +%Y%m%d).yaml

# Backup secrets (encrypted)
kubectl get secrets -n todoboard -o yaml > backup_secrets_$(date +%Y%m%d).yaml

# Backup configmaps
kubectl get configmaps -n todoboard -o yaml > backup_configmaps_$(date +%Y%m%d).yaml
```

### Disaster Recovery

**RTO (Recovery Time Objective)**: 4 hours
**RPO (Recovery Point Objective)**: 1 hour

**Recovery Steps**:
1. Restore database from backup
2. Deploy application using Helm
3. Verify all services are running
4. Run smoke tests
5. Update DNS if needed

---

## Incident Response

### Severity Levels

**SEV1 (Critical)**: Complete service outage
- Response time: Immediate
- Escalation: Page on-call engineer

**SEV2 (High)**: Partial service degradation
- Response time: 15 minutes
- Escalation: Slack notification

**SEV3 (Medium)**: Minor issues, no user impact
- Response time: 1 hour
- Escalation: Create ticket

### Incident Response Checklist

1. **Acknowledge**: Acknowledge alert in PagerDuty/Slack
2. **Assess**: Determine severity and impact
3. **Communicate**: Update status page and notify stakeholders
4. **Investigate**: Use troubleshooting procedures above
5. **Mitigate**: Apply temporary fix if needed
6. **Resolve**: Implement permanent fix
7. **Document**: Write post-mortem
8. **Follow-up**: Implement preventive measures

### Rollback Procedure

```bash
# List deployment history
kubectl rollout history deployment/todoboard-backend -n todoboard

# Rollback to previous version
kubectl rollout undo deployment/todoboard-backend -n todoboard

# Rollback to specific revision
kubectl rollout undo deployment/todoboard-backend --to-revision=3 -n todoboard

# Verify rollback
kubectl rollout status deployment/todoboard-backend -n todoboard
```

---

## Maintenance Procedures

### Updating Application

```bash
# Update Helm chart
cd infrastructure/helm/todo-app

# Upgrade release
helm upgrade todoboard . \
  -f values-cloud.yaml \
  -n todoboard \
  --wait

# Monitor rollout
kubectl rollout status deployment/todoboard-backend -n todoboard
```

### Updating Dependencies

```bash
# Update Dapr
dapr upgrade -k --runtime-version 1.13.0

# Update cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.0/cert-manager.yaml

# Update NGINX Ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.0/deploy/static/provider/cloud/deploy.yaml
```

### Certificate Renewal

Certificates are automatically renewed by cert-manager. To force renewal:

```bash
# Delete certificate to trigger renewal
kubectl delete certificate todoboard-tls -n todoboard

# Monitor renewal
kubectl get certificate -n todoboard -w
```

### Log Rotation

Logs are automatically rotated by Kubernetes. To manually clean up:

```bash
# Delete old pods (logs will be lost)
kubectl delete pod <old-pod-name> -n todoboard

# Archive logs before deletion
kubectl logs <pod-name> -n todoboard > archived_logs_$(date +%Y%m%d).log
```

---

## Contact Information

- **On-Call Engineer**: [PagerDuty rotation]
- **Team Lead**: [Contact info]
- **DevOps Team**: [Slack channel]
- **Status Page**: [URL]

## Additional Resources

- [Architecture Documentation](architecture.md)
- [Dapr Setup Guide](dapr-setup.md)
- [Event Schemas](event-schemas.md)
- [Quick Start Guide](../specs/005-advanced-cloud-deployment/quickstart.md)
