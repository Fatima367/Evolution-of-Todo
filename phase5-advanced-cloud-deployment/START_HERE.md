# 🚀 START HERE - Phase 5 Part B Deployment

**Quick Navigation**: This is your starting point for deploying TodoBoard to Minikube with Kafka and Dapr.

---

## 📍 You Are Here

```
Phase 5: Advanced Cloud Deployment
├── Part A: Advanced Features ✅ (Already implemented)
├── Part B: Local Deployment (Minikube) ← YOU ARE HERE
└── Part C: Cloud Deployment (GKE/AKS) → Next
```

---

## ⚡ Quick Deploy (3 Commands)

```bash
# 1. Set your API key
export GROQ_API_KEY="your-groq-api-key-here"

# 2. Verify prerequisites (optional but recommended)
./scripts/verify-prerequisites.sh

# 3. Deploy everything
./scripts/minikube/setup-minikube.sh
```

**Time**: 10-15 minutes
**Result**: http://todoboard.local

---

## 📚 Documentation Guide

Choose your path based on your needs:

### 🎯 For Quick Deployment
→ **[QUICK_START.md](./QUICK_START.md)**
- One-page reference
- Essential commands
- Quick troubleshooting

### 📖 For Detailed Instructions
→ **[MINIKUBE_DEPLOYMENT_GUIDE.md](./MINIKUBE_DEPLOYMENT_GUIDE.md)**
- Complete step-by-step guide
- Manual deployment option
- Comprehensive troubleshooting
- Testing procedures

### 📋 For Overview
→ **[DEPLOYMENT_SUMMARY.md](./DEPLOYMENT_SUMMARY.md)**
- What gets deployed
- Architecture diagrams
- Success criteria
- Next steps

---

## ✅ Pre-Flight Checklist

Before you start, ensure you have:

```bash
# Run this to check everything
./scripts/verify-prerequisites.sh
```

**Manual checklist**:
- [ ] Minikube installed (`minikube version`)
- [ ] kubectl installed (`kubectl version --client`)
- [ ] Helm installed (`helm version`)
- [ ] Docker installed and running (`docker ps`)
- [ ] 4+ CPU cores available
- [ ] 8+ GB RAM available
- [ ] 20+ GB disk space available
- [ ] GROQ_API_KEY set (`echo $GROQ_API_KEY`)

---

## 🎬 Step-by-Step Deployment

### Step 1: Navigate to Phase 5 Directory

```bash
cd phase5-advanced-cloud-deployment
```

### Step 2: Set Environment Variables

```bash
# Required: Set your Groq API key for AI chatbot
export GROQ_API_KEY="your-groq-api-key-here"

# Optional: Verify it's set
echo $GROQ_API_KEY
```

**Don't have a Groq API key?**
- Get one free at: https://console.groq.com/keys
- The app will work without it, but AI chatbot won't function

### Step 3: Verify Prerequisites (Recommended)

```bash
# Make script executable
chmod +x scripts/verify-prerequisites.sh

# Run verification
./scripts/verify-prerequisites.sh
```

**Expected output**: All checks should pass with green ✓

### Step 4: Run Deployment Script

```bash
# Make script executable (if not already)
chmod +x scripts/minikube/setup-minikube.sh

# Run deployment
./scripts/minikube/setup-minikube.sh
```

**What happens during deployment**:
1. ✅ Checks prerequisites
2. ✅ Starts Minikube (4 CPU, 8GB RAM)
3. ✅ Enables Ingress and Metrics Server
4. ✅ Builds Docker images (5 images)
5. ✅ Installs Kafka with Strimzi
6. ✅ Installs Dapr runtime
7. ✅ Deploys Dapr components
8. ✅ Deploys application with Helm
9. ✅ Configures /etc/hosts

**Expected time**: 10-15 minutes

### Step 5: Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n todoboard

# Expected: All pods in "Running" status with "2/2" or "1/1" ready

# Test health endpoint
curl http://todoboard.local/api/health

# Expected: {"status":"healthy"}
```

### Step 6: Access Application

Open in your browser:
- **Frontend**: http://todoboard.local
- **API Docs**: http://todoboard.local/api/docs
- **Kubernetes Dashboard**: Run `minikube dashboard`
- **Dapr Dashboard**: Run `dapr dashboard -k`

---

## 🎯 What You'll See After Deployment

### Pods Running
```bash
$ kubectl get pods -n todoboard

NAME                                    READY   STATUS    RESTARTS   AGE
audit-service-xxx                       2/2     Running   0          5m
notification-service-xxx                2/2     Running   0          5m
postgres-xxx                            1/1     Running   0          5m
recurring-task-service-xxx              2/2     Running   0          5m
todoboard-backend-xxx                   2/2     Running   0          5m
todoboard-frontend-xxx                  1/1     Running   0          5m
todoboard-kafka-kafka-0                 1/1     Running   0          8m
todoboard-kafka-kafka-1                 1/1     Running   0          8m
todoboard-kafka-kafka-2                 1/1     Running   0          8m
todoboard-kafka-zookeeper-0             1/1     Running   0          9m
```

**Note**: Pods with "2/2" have Dapr sidecars running alongside the application.

### Dapr Components
```bash
$ dapr components -k -n todoboard

NAMESPACE   NAME                  TYPE              VERSION  SCOPES
todoboard   pubsub-kafka          pubsub.kafka      v1       backend-service, notification-service, recurring-task-service, audit-service
todoboard   secrets-k8s           secretstores...   v1       backend-service, notification-service, recurring-task-service, audit-service
todoboard   statestore-postgres   state.postgresql  v1       backend-service, notification-service, recurring-task-service, audit-service
```

### Kafka Topics
```bash
$ kubectl get kafkatopic -n todoboard

NAME                 CLUSTER           PARTITIONS   REPLICATION FACTOR   READY
dead-letter-queue    todoboard-kafka   3            3                    True
reminders            todoboard-kafka   3            3                    True
task-events          todoboard-kafka   3            3                    True
task-updates         todoboard-kafka   3            3                    True
```

---

## 🧪 Test Dapr Integration

### Test 1: Publish Event via Dapr Pub/Sub

```bash
# Get backend pod name
BACKEND_POD=$(kubectl get pod -n todoboard -l app=backend -o jsonpath='{.items[0].metadata.name}')

# Publish test event
kubectl exec -it $BACKEND_POD -c backend -n todoboard -- \
  curl -X POST http://localhost:3500/v1.0/publish/pubsub-kafka/task-events \
  -H "Content-Type: application/json" \
  -d '{"event_type":"test","task_id":999,"message":"Hello from Dapr!"}'

# Check if notification service received it
kubectl logs -f deployment/notification-service -c notification-service -n todoboard | grep "test"
```

**Expected**: You should see the event logged by the notification service.

### Test 2: State Management

```bash
# Save state via Dapr
kubectl exec -it $BACKEND_POD -c backend -n todoboard -- \
  curl -X POST http://localhost:3500/v1.0/state/statestore-postgres \
  -H "Content-Type: application/json" \
  -d '[{"key":"demo","value":"Dapr state works!"}]'

# Retrieve state
kubectl exec -it $BACKEND_POD -c backend -n todoboard -- \
  curl http://localhost:3500/v1.0/state/statestore-postgres/demo

# Expected: "Dapr state works!"
```

### Test 3: Service Invocation

```bash
# Invoke notification service from backend via Dapr
kubectl exec -it $BACKEND_POD -c backend -n todoboard -- \
  curl http://localhost:3500/v1.0/invoke/notification-service/method/health

# Expected: {"status":"healthy"}
```

---

## 🐛 Troubleshooting Quick Fixes

### Problem: "Cannot access todoboard.local"

```bash
# Solution: Add to /etc/hosts
echo "$(minikube ip) todoboard.local" | sudo tee -a /etc/hosts
```

### Problem: "Pods stuck in ImagePullBackOff"

```bash
# Solution: Rebuild images in Minikube's Docker
eval $(minikube docker-env)
docker build -t todoboard-backend:latest ./backend
docker build -t todoboard-frontend:latest ./frontend
docker build -t notification-service:latest ./services/notification-service
docker build -t recurring-task-service:latest ./services/recurring-task-service
docker build -t audit-service:latest ./services/audit-service
kubectl rollout restart deployment -n todoboard
```

### Problem: "Kafka not ready after 10 minutes"

```bash
# Check status
kubectl get kafka todoboard-kafka -n todoboard

# Check logs
kubectl logs -n todoboard -l strimzi.io/name=todoboard-kafka-kafka

# If stuck, restart
kubectl delete kafka todoboard-kafka -n todoboard
kubectl apply -f infrastructure/kafka/kafka-cluster.yaml
```

### Problem: "Dapr components not working"

```bash
# Restart deployments
kubectl rollout restart deployment -n todoboard

# Check Dapr sidecar logs
kubectl logs <pod-name> -c daprd -n todoboard
```

**More troubleshooting**: See [MINIKUBE_DEPLOYMENT_GUIDE.md](./MINIKUBE_DEPLOYMENT_GUIDE.md#troubleshooting)

---

## 📊 Monitoring & Debugging

### View Logs

```bash
# Backend logs
kubectl logs -f deployment/todoboard-backend -c backend -n todoboard

# Backend Dapr sidecar logs
kubectl logs -f deployment/todoboard-backend -c daprd -n todoboard

# Notification service logs
kubectl logs -f deployment/notification-service -c notification-service -n todoboard

# All pods logs
kubectl logs -f -l app.kubernetes.io/part-of=todoboard -n todoboard
```

### Check Resource Usage

```bash
# Pod resource usage
kubectl top pods -n todoboard

# Node resource usage
kubectl top nodes
```

### Open Dashboards

```bash
# Kubernetes dashboard
minikube dashboard

# Dapr dashboard (opens on http://localhost:8080)
dapr dashboard -k
```

---

## 🧹 Cleanup

### Option 1: Remove Application Only

```bash
# Uninstall Helm release
helm uninstall todoboard -n todoboard

# Delete namespace
kubectl delete namespace todoboard
```

### Option 2: Remove Everything

```bash
# Delete Minikube cluster
minikube delete

# Remove /etc/hosts entry
sudo sed -i '/todoboard.local/d' /etc/hosts
```

---

## 📖 Additional Resources

### Documentation Files
- **[QUICK_START.md](./QUICK_START.md)** - Quick reference card
- **[MINIKUBE_DEPLOYMENT_GUIDE.md](./MINIKUBE_DEPLOYMENT_GUIDE.md)** - Complete guide
- **[DEPLOYMENT_SUMMARY.md](./DEPLOYMENT_SUMMARY.md)** - Overview and architecture
- **[README.md](./README.md)** - Project documentation

### Configuration Files
- **Dapr Components**: `infrastructure/dapr/components/`
- **Dapr Subscriptions**: `infrastructure/dapr/subscriptions/`
- **Kafka Config**: `infrastructure/kafka/`
- **Helm Chart**: `infrastructure/helm/todo-app/`

### Scripts
- **Main Setup**: `scripts/minikube/setup-minikube.sh`
- **Kafka Install**: `scripts/kafka/install-kafka.sh`
- **Dapr Install**: `scripts/dapr/install-dapr.sh`
- **Verification**: `scripts/verify-prerequisites.sh`

---

## 🎓 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Minikube Kubernetes Cluster                   │
│                         (4 CPU, 8GB RAM)                         │
│                                                                  │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐        │
│  │   Frontend   │   │   Backend    │   │ Notification │        │
│  │   Next.js    │──▶│   FastAPI    │──▶│   Service    │        │
│  │   Port 3000  │   │   + MCP      │   │   Port 8001  │        │
│  └──────────────┘   │   Port 8000  │   └──────┬───────┘        │
│                     └──────┬───────┘          │                 │
│                            │                  │                 │
│                            ▼                  ▼                 │
│                    ┌────────────────────────────┐               │
│                    │     Dapr Runtime           │               │
│                    │  ┌──────────────────────┐  │               │
│                    │  │ Pub/Sub (Kafka)      │──┼──▶ Kafka     │
│                    │  │ State (PostgreSQL)   │──┼──▶ PostgreSQL│
│                    │  │ Secrets (K8s)        │  │               │
│                    │  │ Service Invocation   │  │   (mTLS)     │
│                    │  └──────────────────────┘  │               │
│                    └────────────────────────────┘               │
│                                                                  │
│  Kafka Topics:                                                   │
│  • task-events (CRUD operations)                                │
│  • reminders (scheduled notifications)                          │
│  • task-updates (real-time sync)                                │
│  • dead-letter-queue (failed messages)                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✅ Success Checklist

Your deployment is successful when:

- [ ] All pods show `Running` status
- [ ] `curl http://todoboard.local/api/health` returns `{"status":"healthy"}`
- [ ] Frontend loads at http://todoboard.local
- [ ] You can register a new user
- [ ] You can create and manage tasks
- [ ] AI chatbot responds to queries
- [ ] `dapr components -k -n todoboard` shows 3 components
- [ ] `kubectl get kafkatopic -n todoboard` shows 4 topics
- [ ] Events are published to Kafka (check logs)

---

## 🚦 Next Steps

After successful deployment:

1. **Explore the Application**
   - Create tasks with different priorities
   - Test recurring tasks
   - Try the AI chatbot
   - Check favorites and calendar views

2. **Verify Event-Driven Architecture**
   - Create a task and check Kafka logs
   - Verify notification service receives events
   - Check audit service logs

3. **Monitor with Dashboards**
   - Open Kubernetes dashboard: `minikube dashboard`
   - Open Dapr dashboard: `dapr dashboard -k`
   - Check resource usage: `kubectl top pods -n todoboard`

4. **Proceed to Part C**
   - Deploy to cloud (GKE/AKS/OKE)
   - See [DEPLOYMENT.md](./DEPLOYMENT.md) for cloud deployment

---

## 💡 Pro Tips

1. **Save time on rebuilds**: Keep `eval $(minikube docker-env)` active in your terminal
2. **Quick logs**: Use `kubectl logs -f deployment/<name> -n todoboard` to follow logs
3. **Debug Dapr**: Check sidecar logs with `-c daprd` flag
4. **Test Kafka**: Use `kubectl get kafkatopic -n todoboard` to verify topics
5. **Resource issues**: Increase Minikube resources with `minikube start --cpus=6 --memory=12288`

---

## 📞 Need Help?

1. **Check logs**: `kubectl logs <pod-name> -n todoboard`
2. **Check events**: `kubectl get events -n todoboard --sort-by=.metadata.creationTimestamp`
3. **Run verification**: `./scripts/verify-prerequisites.sh`
4. **Review troubleshooting**: [MINIKUBE_DEPLOYMENT_GUIDE.md](./MINIKUBE_DEPLOYMENT_GUIDE.md#troubleshooting)

---

## 🎉 Ready to Deploy!

You have everything you need. Just run:

```bash
export GROQ_API_KEY="your-api-key"
./scripts/minikube/setup-minikube.sh
```

**See you at http://todoboard.local in 15 minutes! 🚀**

---

*Last updated: 2026-01-25*
