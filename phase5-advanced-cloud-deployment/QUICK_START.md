# Phase 5 Part B - Quick Start Guide

## 🚀 One-Command Deployment

```bash
cd phase5-advanced-cloud-deployment
chmod +x scripts/minikube/setup-minikube.sh
export GROQ_API_KEY="your-api-key-here"
./scripts/minikube/setup-minikube.sh
```

**Time**: ~10-15 minutes
**Access**: http://todoboard.local

---

## 📋 Prerequisites Checklist

- [ ] Minikube installed (`minikube version`)
- [ ] kubectl installed (`kubectl version --client`)
- [ ] Helm installed (`helm version`)
- [ ] Docker installed (`docker --version`)
- [ ] Dapr CLI installed (`dapr --version`)
- [ ] 4 CPU cores available
- [ ] 8GB RAM available
- [ ] GROQ_API_KEY environment variable set

---

## 🎯 What Gets Deployed

### Infrastructure
- ✅ Minikube cluster (4 CPU, 8GB RAM)
- ✅ Kafka cluster (Strimzi) with 3 brokers
- ✅ Dapr runtime with HA mode
- ✅ PostgreSQL database
- ✅ Ingress controller

### Dapr Components
- ✅ **Pub/Sub**: Kafka integration
- ✅ **State Store**: PostgreSQL
- ✅ **Secrets**: Kubernetes secrets
- ✅ **Service Invocation**: mTLS enabled

### Kafka Topics
- ✅ `task-events` - Task CRUD operations
- ✅ `reminders` - Scheduled reminders
- ✅ `task-updates` - Real-time sync
- ✅ `dead-letter-queue` - Failed messages

### Microservices
- ✅ **Backend** (FastAPI + MCP) - Port 8000
- ✅ **Frontend** (Next.js) - Port 3000
- ✅ **Notification Service** - Port 8001
- ✅ **Recurring Task Service** - Port 8002
- ✅ **Audit Service** - Port 8003

---

## 🔍 Verification Commands

```bash
# Check all pods are running
kubectl get pods -n todoboard

# Check Dapr components
dapr components -k -n todoboard

# Check Kafka topics
kubectl get kafkatopic -n todoboard

# Test application
curl http://todoboard.local/api/health
```

---

## 🌐 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://todoboard.local | Main web interface |
| **Backend API** | http://todoboard.local/api | REST API |
| **API Docs** | http://todoboard.local/api/docs | Swagger UI |
| **Health Check** | http://todoboard.local/api/health | Health endpoint |
| **Kubernetes Dashboard** | `minikube dashboard` | K8s dashboard |
| **Dapr Dashboard** | `dapr dashboard -k` | Dapr dashboard |

---

## 🧪 Test Dapr Features

### Test Pub/Sub (Kafka)

```bash
# Get backend pod name
BACKEND_POD=$(kubectl get pod -n todoboard -l app=backend -o jsonpath='{.items[0].metadata.name}')

# Publish test event via Dapr
kubectl exec -it $BACKEND_POD -c backend -n todoboard -- \
  curl -X POST http://localhost:3500/v1.0/publish/pubsub-kafka/task-events \
  -H "Content-Type: application/json" \
  -d '{"event_type":"test","task_id":999}'

# Check consumer logs
kubectl logs -f deployment/notification-service -c notification-service -n todoboard
```

### Test State Store

```bash
# Save state
kubectl exec -it $BACKEND_POD -c backend -n todoboard -- \
  curl -X POST http://localhost:3500/v1.0/state/statestore-postgres \
  -H "Content-Type: application/json" \
  -d '[{"key":"test","value":"hello"}]'

# Retrieve state
kubectl exec -it $BACKEND_POD -c backend -n todoboard -- \
  curl http://localhost:3500/v1.0/state/statestore-postgres/test
```

### Test Service Invocation

```bash
# Invoke notification service from backend via Dapr
kubectl exec -it $BACKEND_POD -c backend -n todoboard -- \
  curl http://localhost:3500/v1.0/invoke/notification-service/method/health
```

---

## 🐛 Common Issues & Fixes

### Issue: Pods stuck in ImagePullBackOff

```bash
# Solution: Rebuild images in Minikube's Docker
eval $(minikube docker-env)
docker build -t todoboard-backend:latest ./backend
docker build -t todoboard-frontend:latest ./frontend
# ... rebuild other images
kubectl rollout restart deployment -n todoboard
```

### Issue: Cannot access todoboard.local

```bash
# Solution: Add to /etc/hosts
echo "$(minikube ip) todoboard.local" | sudo tee -a /etc/hosts
```

### Issue: Kafka not ready

```bash
# Solution: Wait longer or check logs
kubectl wait kafka/todoboard-kafka --for=condition=Ready --timeout=600s -n todoboard
kubectl logs -n todoboard -l strimzi.io/name=todoboard-kafka-kafka
```

### Issue: Dapr components not working

```bash
# Solution: Restart deployments
kubectl rollout restart deployment -n todoboard
```

---

## 🧹 Cleanup

### Remove application only
```bash
helm uninstall todoboard -n todoboard
kubectl delete namespace todoboard
```

### Remove everything
```bash
minikube delete
sudo sed -i '/todoboard.local/d' /etc/hosts
```

---

## 📚 Full Documentation

For detailed step-by-step instructions, see:
- **[MINIKUBE_DEPLOYMENT_GUIDE.md](./MINIKUBE_DEPLOYMENT_GUIDE.md)** - Complete deployment guide
- **[README.md](./README.md)** - Project overview
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Cloud deployment guide

---

## 🎓 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Minikube Cluster                          │
│                                                              │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐ │
│  │ Frontend │   │ Backend  │   │  Notif   │   │Recurring │ │
│  │ (Next.js)│──▶│(FastAPI) │──▶│ Service  │   │  Task    │ │
│  │          │   │  + MCP   │   │          │   │ Service  │ │
│  └──────────┘   └────┬─────┘   └──────────┘   └──────────┘ │
│                      │                                       │
│                      ▼                                       │
│              ┌───────────────┐                               │
│              │ Dapr Runtime  │                               │
│              │ ┌───────────┐ │                               │
│              │ │ Pub/Sub   │─┼──▶ Kafka (3 brokers)         │
│              │ │ State     │─┼──▶ PostgreSQL                │
│              │ │ Secrets   │─┼──▶ K8s Secrets               │
│              │ └───────────┘ │                               │
│              └───────────────┘                               │
│                                                              │
│  Kafka Topics: task-events, reminders, task-updates         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Success Criteria

Your deployment is successful when:

- ✅ All pods show `Running` status
- ✅ `curl http://todoboard.local/api/health` returns `{"status":"healthy"}`
- ✅ Frontend loads at http://todoboard.local
- ✅ `dapr components -k -n todoboard` shows 3 components
- ✅ `kubectl get kafkatopic -n todoboard` shows 4 topics
- ✅ You can create and manage tasks via the web UI
- ✅ AI chatbot responds to queries

---

## 💡 Tips

1. **First time setup**: Allow 15 minutes for all components to initialize
2. **Resource monitoring**: Use `kubectl top pods -n todoboard` to check usage
3. **Logs**: Use `kubectl logs -f <pod-name> -n todoboard` for debugging
4. **Dapr dashboard**: Run `dapr dashboard -k` for visual monitoring
5. **Kafka messages**: Check topics with `kubectl get kafkatopic -n todoboard`

---

## 🚦 Next Steps

After successful deployment:

1. **Test the application**: Create tasks, test AI chatbot
2. **Verify event-driven features**: Check Kafka topics for messages
3. **Monitor Dapr**: Use Dapr dashboard to see component health
4. **Proceed to Part C**: Deploy to cloud (GKE/AKS/OKE)

---

## 📞 Support

If you encounter issues:
1. Check the [troubleshooting section](./MINIKUBE_DEPLOYMENT_GUIDE.md#troubleshooting)
2. Review pod logs: `kubectl logs <pod-name> -n todoboard`
3. Check events: `kubectl get events -n todoboard --sort-by=.metadata.creationTimestamp`
4. Verify Dapr: `dapr dashboard -k`

---

**Ready to deploy? Run the setup script and you'll be up in 15 minutes! 🚀**
