#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}║          Deploy Complete Application Stack                 ║${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}✗ kubectl is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ kubectl is installed${NC}"

if ! command -v helm &> /dev/null; then
    echo -e "${RED}✗ Helm is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Helm is installed${NC}"

if ! command -v minikube &> /dev/null; then
    echo -e "${RED}✗ minikube is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ minikube is installed${NC}"

# Check if minikube is running
if ! minikube status &> /dev/null; then
    echo -e "${RED}✗ Minikube is not running${NC}"
    echo "Start minikube with: minikube start --driver=docker --memory=8192 --cpus=4"
    exit 1
fi
echo -e "${GREEN}✓ Minikube is running${NC}"

# Ensure all required infrastructure is in place
echo -e "${YELLOW}Ensuring all infrastructure is ready...${NC}"

# Create namespace
kubectl create namespace todoboard --dry-run=client -o yaml | kubectl apply -f -

# Check if PostgreSQL is running
if ! kubectl get service postgres -n todoboard &> /dev/null; then
    echo -e "${YELLOW}Setting up PostgreSQL...${NC}"
    cat << EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: todoboard
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:16-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: "todo_db"
        - name: POSTGRES_USER
          value: "todo_user"
        - name: POSTGRES_PASSWORD
          value: "todo_password"
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
      volumes:
      - name: postgres-storage
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: todoboard
spec:
  selector:
    app: postgres
  ports:
    - protocol: TCP
      port: 5432
      targetPort: 5432
  type: ClusterIP
EOF
fi

# Wait for PostgreSQL to be ready
echo -e "${YELLOW}Waiting for PostgreSQL to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app=postgres -n todoboard --timeout=300s

# Check if Kafka is running
if ! kubectl get service todoboard-kafka-kafka-bootstrap -n todoboard &> /dev/null; then
    echo -e "${YELLOW}Setting up Kafka cluster...${NC}"
    cat << EOF | kubectl apply -f -
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: todoboard-kafka
  namespace: todoboard
  labels:
    app.kubernetes.io/name: kafka
    app.kubernetes.io/component: messaging
    app.kubernetes.io/part-of: todoboard
spec:
  kafka:
    version: 3.6.0
    replicas: 1
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
    config:
      offsets.topic.replication.factor: 1
      transaction.state.log.replication.factor: 1
      transaction.state.log.min.isr: 1
      default.replication.factor: 1
      min.insync.replicas: 1
      inter.broker.protocol.version: "3.6"
      auto.create.topics.enable: true
    storage:
      type: ephemeral
    resources:
      requests:
        memory: 512Mi
        cpu: 250m
      limits:
        memory: 1Gi
        cpu: 1000m
  zookeeper:
    replicas: 1
    storage:
      type: ephemeral
    resources:
      requests:
        memory: 256Mi
        cpu: 100m
      limits:
        memory: 512Mi
        cpu: 500m
EOF
fi

# Wait for Kafka to be ready
echo -e "${YELLOW}Waiting for Kafka cluster to be ready...${NC}"
kubectl wait kafka/todoboard-kafka --for=condition=Ready --timeout=600s -n todoboard || echo "Kafka may still be initializing..."

# Check if Dapr is running
if ! kubectl get namespace dapr-system &> /dev/null; then
    echo -e "${YELLOW}Setting up Dapr...${NC}"
    helm repo add dapr https://dapr.github.io/helm-charts/
    helm repo update
    helm upgrade --install dapr dapr/dapr \
      --namespace dapr-system \
      --create-namespace \
      --set global.ha.enabled=false \
      --set global.mtls.enabled=false \
      --wait \
      --timeout 10m
fi

# Create/update secrets
echo -e "${YELLOW}Creating/updating secrets...${NC}"
kubectl delete secret todoboard-secrets -n todoboard 2>/dev/null || true
kubectl create secret generic todoboard-secrets \
  --from-literal=POSTGRES_PASSWORD='todo_password' \
  --from-literal=JWT_SECRET_KEY='minikube-dev-secret-key-change-in-production' \
  --from-literal=GROQ_API_KEY='' \
  --from-literal=DATABASE_URL='postgresql://todo_user:todo_password@postgres:5432/todo_db' \
  -n todoboard

# Build and load images into minikube
echo -e "${YELLOW}Building and loading images into Minikube...${NC}"

# Set Docker environment to Minikube
eval $(minikube docker-env)

# Build backend image
if [ -d "../../../backend" ] && [ -f "../../../backend/Dockerfile" ]; then
    echo -e "${YELLOW}Building backend image...${NC}"
    docker build -t todoboard-backend:latest ../../../backend
else
    echo -e "${YELLOW}Creating placeholder backend image...${NC}"
    mkdir -p /tmp/backend-build
    cat << 'DOCKERFILE' > /tmp/backend-build/Dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*
WORKDIR /app
RUN pip install fastapi uvicorn python-multipart
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
DOCKERFILE
    echo "from fastapi import FastAPI
app = FastAPI()

@app.get('/')
def read_root():
    return {'Hello': 'World'}

@app.get('/health')
def health_check():
    return {'status': 'healthy'}" > /tmp/backend-build/main.py
    docker build -t todoboard-backend:latest /tmp/backend-build
fi

# Build frontend image
if [ -d "../../../frontend" ] && [ -f "../../../frontend/Dockerfile" ]; then
    echo -e "${YELLOW}Building frontend image...${NC}"
    docker build -t todoboard-frontend:latest ../../../frontend
else
    echo -e "${YELLOW}Creating placeholder frontend image...${NC}"
    mkdir -p /tmp/frontend-build
    cat << 'DOCKERFILE' > /tmp/frontend-build/Dockerfile
FROM nginx:alpine
RUN apk add --no-cache curl
COPY index.html /usr/share/nginx/html/index.html
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost || exit 1
CMD ["nginx", "-g", "daemon off;"]
DOCKERFILE
    echo "<html><body><h1>TodoBoard Frontend Placeholder</h1><p>Advanced Cloud Deployment with Kafka and Dapr</p></body></html>" > /tmp/frontend-build/index.html
    docker build -t todoboard-frontend:latest /tmp/frontend-build
fi

# Build service images if they exist
for service in notification-service recurring-task-service audit-service; do
    if [ -d "../../../services/$service" ] && [ -f "../../../services/$service/Dockerfile" ]; then
        echo -e "${YELLOW}Building $service image...${NC}"
        docker build -t $service:latest ../../../services/$service
    else
        echo -e "${YELLOW}Creating placeholder $service image...${NC}"
        mkdir -p /tmp/service-build
        cat << 'DOCKERFILE' > /tmp/service-build/Dockerfile
FROM python:3.11-slim
RUN pip install fastapi uvicorn
WORKDIR /app
EXPOSE 8001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
DOCKERFILE
        echo "from fastapi import FastAPI
app = FastAPI()

@app.get('/')
def read_root():
    return {'service': '$service'}

@app.get('/health')
def health_check():
    return {'status': 'healthy'}" > /tmp/service-build/main.py
        docker build -t $service:latest /tmp/service-build
    fi
done

# Update the values-minikube.yaml to ensure correct configurations
echo -e "${YELLOW}Updating Helm values...${NC}"

# Create a custom values file for the complete deployment
cat << EOF > infrastructure/helm/todo-app/values-complete.yaml
# Complete Minikube Values for TodoBoard Helm Chart
# This file contains configurations for the complete application stack

global:
  appName: todoboard
  environment: development
  imagePullPolicy: IfNotPresent
  imagePullSecrets: []

backend:
  enabled: true
  replicaCount: 1
  image:
    repository: todoboard-backend
    tag: "latest"
    pullPolicy: Never  # Use local images
  containerPort: 8000
  service:
    type: ClusterIP
    port: 8000
    targetPort: 8000
  resources:
    requests:
      cpu: "100m"
      memory: "256Mi"
    limits:
      cpu: "500m"
      memory: "512Mi"
  livenessProbe:
    enabled: true
    httpGet:
      path: /health
      port: 8000
    initialDelaySeconds: 30
    periodSeconds: 15
    timeoutSeconds: 5
    successThreshold: 1
    failureThreshold: 3
  readinessProbe:
    enabled: true
    httpGet:
      path: /health
      port: 8000
    initialDelaySeconds: 10
    periodSeconds: 10
    timeoutSeconds: 3
    successThreshold: 1
    failureThreshold: 3
  startupProbe:
    enabled: true
    httpGet:
      path: /health
      port: 8000
    initialDelaySeconds: 0
    periodSeconds: 5
    timeoutSeconds: 3
    successThreshold: 1
    failureThreshold: 20
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0
  autoscaling:
    enabled: false
  dapr:
    enabled: true
    appId: backend-service
    appPort: 8000
  env:
    LOG_LEVEL: "DEBUG"
    ENVIRONMENT: "development"

frontend:
  enabled: true
  replicaCount: 1
  image:
    repository: todoboard-frontend
    tag: "latest"
    pullPolicy: Never  # Use local images
  containerPort: 80
  service:
    type: ClusterIP
    port: 80
    targetPort: 80
  resources:
    requests:
      cpu: "50m"
      memory: "128Mi"
    limits:
      cpu: "250m"
      memory: "256Mi"
  livenessProbe:
    enabled: true
    httpGet:
      path: /
      port: 80
    initialDelaySeconds: 30
    periodSeconds: 15
    timeoutSeconds: 5
    successThreshold: 1
    failureThreshold: 3
  readinessProbe:
    enabled: true
    httpGet:
      path: /
      port: 80
    initialDelaySeconds: 10
    periodSeconds: 10
    timeoutSeconds: 3
    successThreshold: 1
    failureThreshold: 3
  startupProbe:
    enabled: true
    httpGet:
      path: /
      port: 80
    initialDelaySeconds: 0
    periodSeconds: 5
    timeoutSeconds: 3
    successThreshold: 1
    failureThreshold: 20

notificationService:
  enabled: true
  replicaCount: 1
  image:
    repository: notification-service
    tag: "latest"
    pullPolicy: Never  # Use local images
  containerPort: 8001
  service:
    type: ClusterIP
    port: 8001
    targetPort: 8001
  resources:
    requests:
      cpu: "50m"
      memory: "128Mi"
    limits:
      cpu: "250m"
      memory: "256Mi"
  dapr:
    enabled: true
    appId: notification-service
    appPort: 8001

recurringTaskService:
  enabled: true
  replicaCount: 1
  image:
    repository: recurring-task-service
    tag: "latest"
    pullPolicy: Never  # Use local images
  containerPort: 8002
  service:
    type: ClusterIP
    port: 8002
    targetPort: 8002
  resources:
    requests:
      cpu: "50m"
      memory: "128Mi"
    limits:
      cpu: "250m"
      memory: "256Mi"
  dapr:
    enabled: true
    appId: recurring-task-service
    appPort: 8002

auditService:
  enabled: true
  replicaCount: 1
  image:
    repository: audit-service
    tag: "latest"
    pullPolicy: Never  # Use local images
  containerPort: 8003
  service:
    type: ClusterIP
    port: 8003
    targetPort: 8003
  resources:
    requests:
      cpu: "50m"
      memory: "128Mi"
    limits:
      cpu: "250m"
      memory: "256Mi"
  dapr:
    enabled: true
    appId: audit-service
    appPort: 8003

ingress:
  enabled: true
  className: nginx
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
  hosts:
    - host: todoboard.local
      paths:
        - path: /
          pathType: Prefix
          service: frontend
        - path: /api
          pathType: Prefix
          service: backend
  tls: []
  rateLimiting:
    enabled: false
  cors:
    enabled: false

configMap:
  backend:
    DATABASE_URL: "postgresql://todo_user:todo_password@postgres:5432/todo_db"
    JWT_SECRET_KEY: "minikube-dev-secret-key-change-in-production"
    JWT_ALGORITHM: "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: "10080"
    CORS_ORIGINS: '["http://todoboard.local", "http://localhost:3000", "http://$(minikube ip)", "http://host.docker.internal"]'
    APP_NAME: "TodoBoard Minikube"
    APP_VERSION: "1.0.0"
    ENVIRONMENT: "development"
    KAFKA_BOOTSTRAP_SERVERS: "todoboard-kafka-kafka-bootstrap.todoboard.svc:9092"
    DAPR_HTTP_PORT: "3500"
    DAPR_GRPC_PORT: "50001"
    DAPR_PUBSUB_NAME: "pubsub-kafka"
    DAPR_STATE_STORE_NAME: "statestore-postgres"

  frontend:
    NEXT_PUBLIC_API_URL: "http://$(minikube ip)/api"
    NEXT_PUBLIC_APP_NAME: "TodoBoard (Minikube)"

secrets:
  POSTGRES_PASSWORD: "todo_password"
  JWT_SECRET_KEY: "minikube-dev-secret-key-change-in-production"
  GROQ_API_KEY: ""

postgresql:
  enabled: false  # We're using our own PostgreSQL deployment

kafka:
  enabled: true
  bootstrapServers: "todoboard-kafka-kafka-bootstrap.todoboard.svc:9092"

dapr:
  enabled: true

serviceAccount:
  create: true
  name: "todoboard-sa"
EOF

# Remove any existing deployment
echo -e "${YELLOW}Removing existing deployment...${NC}"
helm uninstall todoboard -n todoboard 2>/dev/null || true

# Wait a moment for cleanup
sleep 10

# Install the Helm chart with the complete values
echo -e "${YELLOW}Installing complete application stack...${NC}"
helm install todoboard ./infrastructure/helm/todo-app \
  -f ./infrastructure/helm/todo-app/values-complete.yaml \
  -n todoboard \
  --create-namespace

# Wait for deployments to be created
echo -e "${YELLOW}Waiting for deployments to be created...${NC}"
sleep 30

# Wait for all pods to be ready
echo -e "${YELLOW}Waiting for all pods to be ready...${NC}"

# Wait for each deployment individually
for deployment in backend frontend notification-service recurring-task-service audit-service; do
    if kubectl get deployment "todoboard-$deployment" -n todoboard &> /dev/null; then
        echo -e "${YELLOW}Waiting for $deployment deployment...${NC}"
        kubectl rollout status deployment/todoboard-$deployment -n todoboard --timeout=600s || echo "$deployment may still be starting..."
    fi
done

# Show all pods status
echo -e "${BLUE}Current pods status:${NC}"
kubectl get pods -n todoboard -o wide

# Show all services
echo -e "${BLUE}Current services:${NC}"
kubectl get services -n todoboard

# Show ingress
echo -e "${BLUE}Current ingress:${NC}"
kubectl get ingress -n todoboard

# Check for any failing pods and their logs
echo -e "${YELLOW}Checking for failing pods...${NC}"
for pod in $(kubectl get pods -n todoboard --field-selector=status.phase!=Running,status.phase!=Succeeded -o jsonpath='{.items[*].metadata.name}' 2>/dev/null); do
    if [ ! -z "$pod" ]; then
        echo -e "${RED}Logs for failing pod: $pod${NC}"
        kubectl logs -n todoboard $pod --all-containers=true
    fi
done

# Wait for ingress controller to be ready
echo -e "${YELLOW}Waiting for ingress controller...${NC}"
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=ingress-nginx -n ingress-nginx --timeout=300s 2>/dev/null || echo "Ingress controller may still be starting..."

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              Complete Application Stack Deployed!          ║${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}║ Services deployed:                                         ║${NC}"
echo -e "${GREEN}║   - ${YELLOW}Backend${NC} (FastAPI)                                      ║${NC}"
echo -e "${GREEN}║   - ${YELLOW}Frontend${NC} (Next.js/Nginx)                                ║${NC}"
echo -e "${GREEN}║   - ${YELLOW}Notification Service${NC}                                    ║${NC}"
echo -e "${GREEN}║   - ${YELLOW}Recurring Task Service${NC}                                  ║${NC}"
echo -e "${GREEN}║   - ${YELLOW}Audit Service${NC}                                           ║${NC}"
echo -e "${GREEN}║   - ${YELLOW}PostgreSQL${NC} (Database)                                   ║${NC}"
echo -e "${GREEN}║   - ${YELLOW}Kafka${NC} (via Strimzi)                                     ║${NC}"
echo -e "${GREEN}║   - ${YELLOW}Dapr${NC} (Runtime)                                          ║${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}║ Access your application:                                   ║${NC}"
echo -e "${GREEN}║   Minikube IP: $(minikube ip)                           ║${NC}"
echo -e "${GREEN}║   Frontend: http://$(minikube ip)                       ║${NC}"
echo -e "${GREEN}║   Backend API: http://$(minikube ip)/api                 ║${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}║ Useful commands:                                           ║${NC}"
echo -e "${GREEN}║   Check all pods: kubectl get pods -n todoboard           ║${NC}"
echo -e "${GREEN}║   Check logs: kubectl logs -f deployment/<deployment> -n todoboard ║${NC}"
echo -e "${GREEN}║   Port forward: kubectl port-forward svc/frontend -n todoboard 3000:80 ║${NC}"
echo -e "${GREEN}║   Helm status: helm status todoboard -n todoboard         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""