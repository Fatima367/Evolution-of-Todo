# TodoBoard Runbook

This runbook provides operational procedures for common tasks and incident response for the TodoBoard application.

## Table of Contents

1. [Emergency Contacts](#emergency-contacts)
2. [Common Operations](#common-operations)
3. [Incident Response](#incident-response)
4. [Troubleshooting](#troubleshooting)
5. [Maintenance Procedures](#maintenance-procedures)

## Emergency Contacts

- **On-Call Engineer**: Check PagerDuty rotation
- **Platform Team**: platform-team@todoboard.app
- **Database Team**: database-team@todoboard.app
- **Security Team**: security-team@todoboard.app

## Common Operations

### Scaling Services

**Scale backend replicas:**
```bash
kubectl scale deployment todoboard-backend -n todoboard --replicas=5
```

**Update HPA limits:**
```bash
kubectl patch hpa todoboard-backend -n todoboard -p '{"spec":{"maxReplicas":20}}'
```

### Database Operations

**Run migrations:**
```bash
BACKEND_POD=$(kubectl get pod -n todoboard -l app.kubernetes.io/component=backend -o jsonpath="{.items[0].metadata.name}")
kubectl exec -n todoboard $BACKEND_POD -- alembic upgrade head
```

**Rollback migration:**
```bash
kubectl exec -n todoboard $BACKEND_POD -- alembic downgrade -1
```

**Database backup:**
```bash
kubectl exec -n todoboard postgres-0 -- pg_dump -U todoboard todoboard > backup-$(date +%Y%m%d).sql
```

### Deployment Operations

**Deploy new version:**
```bash
helm upgrade todoboard ./infrastructure/helm/todoboard \
  --namespace todoboard \
  --set backend.image.tag=v1.2.3 \
  --wait
```

**Rollback deployment:**
```bash
helm rollback todoboard -n todoboard
```

**Check deployment status:**
```bash
kubectl rollout status deployment/todoboard-backend -n todoboard
```

### Kafka Operations

**List topics:**
```bash
kubectl exec -it -n kafka todoboard-kafka-kafka-0 -- \
  bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

**Check consumer lag:**
```bash
kubectl exec -it -n kafka todoboard-kafka-kafka-0 -- \
  bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --group todoboard --describe
```

**Reset consumer offset:**
```bash
kubectl exec -it -n kafka todoboard-kafka-kafka-0 -- \
  bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --group todoboard --topic task-events --reset-offsets --to-earliest --execute
```

## Incident Response

### High Error Rate

**Symptoms:**
- Alert: HighErrorRate
- Users reporting 500 errors
- Error rate > 5%

**Investigation:**
1. Check recent deployments:
   ```bash
   kubectl rollout history deployment/todoboard-backend -n todoboard
   ```

2. Check pod logs:
   ```bash
   kubectl logs -n todoboard -l app.kubernetes.io/component=backend --tail=100
   ```

3. Check database connectivity:
   ```bash
   kubectl exec -n todoboard $BACKEND_POD -- curl http://localhost:8000/health/ready
   ```

**Resolution:**
- If recent deployment: Rollback
- If database issue: Check database status and connections
- If external service: Check service status

### High Latency

**Symptoms:**
- Alert: HighLatency
- p95 latency > 1s
- Users reporting slow responses

**Investigation:**
1. Check resource usage:
   ```bash
   kubectl top pods -n todoboard
   ```

2. Check database query performance:
   ```bash
   # Access database and check slow queries
   kubectl exec -it -n todoboard postgres-0 -- psql -U todoboard
   SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;
   ```

3. Check Kafka lag:
   ```bash
   kubectl exec -it -n kafka todoboard-kafka-kafka-0 -- \
     bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --all-groups
   ```

**Resolution:**
- Scale up if resource constrained
- Optimize slow queries
- Clear Kafka lag if blocking

### Pod Crash Loop

**Symptoms:**
- Alert: PodNotReady
- Pod status: CrashLoopBackOff
- Service unavailable

**Investigation:**
1. Check pod status:
   ```bash
   kubectl describe pod -n todoboard <pod-name>
   ```

2. Check logs:
   ```bash
   kubectl logs -n todoboard <pod-name> --previous
   ```

3. Check events:
   ```bash
   kubectl get events -n todoboard --sort-by='.lastTimestamp'
   ```

**Resolution:**
- Fix configuration issues
- Check resource limits
- Verify dependencies (database, Kafka)

### Database Connection Pool Exhausted

**Symptoms:**
- Alert: DatabaseConnectionPoolExhausted
- Errors: "connection pool exhausted"
- Slow responses

**Investigation:**
1. Check active connections:
   ```bash
   kubectl exec -it -n todoboard postgres-0 -- psql -U todoboard -c \
     "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"
   ```

2. Check long-running queries:
   ```bash
   kubectl exec -it -n todoboard postgres-0 -- psql -U todoboard -c \
     "SELECT pid, now() - query_start as duration, query FROM pg_stat_activity WHERE state = 'active' ORDER BY duration DESC;"
   ```

**Resolution:**
- Kill long-running queries if necessary
- Increase connection pool size
- Scale backend replicas

## Troubleshooting

### Service Not Responding

1. Check pod status:
   ```bash
   kubectl get pods -n todoboard
   ```

2. Check service endpoints:
   ```bash
   kubectl get endpoints -n todoboard
   ```

3. Check ingress:
   ```bash
   kubectl get ingress -n todoboard
   kubectl describe ingress todoboard -n todoboard
   ```

### WebSocket Connection Issues

1. Check WebSocket endpoint:
   ```bash
   curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Version: 13" -H "Sec-WebSocket-Key: test" \
     https://todoboard.app/ws
   ```

2. Check active connections:
   ```bash
   # Check metrics endpoint
   curl https://todoboard.app/api/metrics | grep websocket_connections_active
   ```

### Event Publishing Failures

1. Check Kafka cluster status:
   ```bash
   kubectl get kafka -n kafka
   kubectl get pods -n kafka
   ```

2. Check dead letter queue:
   ```bash
   kubectl exec -it -n kafka todoboard-kafka-kafka-0 -- \
     bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 \
     --topic dead-letter-queue --from-beginning --max-messages 10
   ```

3. Check Dapr sidecar logs:
   ```bash
   kubectl logs -n todoboard <pod-name> -c daprd
   ```

## Maintenance Procedures

### Planned Maintenance Window

1. Notify users of maintenance window
2. Scale down to minimum replicas
3. Perform maintenance (database upgrade, etc.)
4. Run smoke tests
5. Scale back up
6. Monitor for issues

### Certificate Renewal

Certificates are automatically renewed by cert-manager. To check status:

```bash
kubectl get certificate -n todoboard
kubectl describe certificate todoboard-tls -n todoboard
```

### Backup and Restore

**Backup:**
```bash
# Database backup
kubectl exec -n todoboard postgres-0 -- pg_dump -U todoboard todoboard | \
  gzip > backup-$(date +%Y%m%d-%H%M%S).sql.gz

# Upload to cloud storage
aws s3 cp backup-*.sql.gz s3://todoboard-backups/
```

**Restore:**
```bash
# Download from cloud storage
aws s3 cp s3://todoboard-backups/backup-20260113-120000.sql.gz .

# Restore database
gunzip < backup-20260113-120000.sql.gz | \
  kubectl exec -i -n todoboard postgres-0 -- psql -U todoboard todoboard
```

### Log Rotation

Logs are automatically rotated by Kubernetes. To manually clear logs:

```bash
# Clear logs for a specific pod
kubectl exec -n todoboard <pod-name> -- truncate -s 0 /var/log/app.log
```

## Monitoring and Alerts

### Access Monitoring Dashboards

- **Grafana**: https://grafana.todoboard.app
- **Prometheus**: https://prometheus.todoboard.app
- **Dapr Dashboard**: `dapr dashboard -k`
- **Kubernetes Dashboard**: `kubectl proxy` then access http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/

### Alert Acknowledgment

When an alert fires:
1. Acknowledge in PagerDuty
2. Investigate using procedures above
3. Document findings in incident ticket
4. Resolve alert when issue is fixed
5. Conduct post-mortem if necessary

## Post-Incident Review

After resolving an incident:
1. Document timeline of events
2. Identify root cause
3. List action items to prevent recurrence
4. Update runbook with new procedures
5. Share learnings with team
