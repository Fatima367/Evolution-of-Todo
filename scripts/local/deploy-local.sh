#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deploying TodoBoard to Minikube${NC}"
echo -e "${GREEN}========================================${NC}"

# Check prerequisites
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}Error: Kubernetes cluster is not running${NC}"
    echo "Please run ./scripts/local/setup-minikube.sh first"
    exit 1
fi

if ! kubectl get namespace dapr-system &> /dev/null; then
    echo -e "${RED}Error: Dapr is not installed${NC}"
    echo "Please run ./scripts/local/install-dapr.sh first"
    exit 1
fi

if ! kubectl get kafka todoboard-kafka -n kafka &> /dev/null; then
    echo -e "${RED}Error: Kafka is not installed${NC}"
    echo "Please run ./scripts/local/install-kafka.sh first"
    exit 1
fi

# Build Docker images in Minikube
echo -e "${GREEN}Building Docker images...${NC}"
eval $(minikube docker-env)

# Build backend image
echo -e "${YELLOW}Building backend image...${NC}"
docker build -t todoboard-backend:latest ./phase5-advanced-cloud-deployment/backend

# Build frontend image
echo -e "${YELLOW}Building frontend image...${NC}"
docker build -t todoboard-frontend:latest ./phase5-advanced-cloud-deployment/frontend

# Build microservice images
echo -e "${YELLOW}Building notification service image...${NC}"
docker build -t notification-service:latest ./services/notification-service

echo -e "${YELLOW}Building recurring task service image...${NC}"
docker build -t recurring-task-service:latest ./services/recurring-task-service

echo -e "${YELLOW}Building audit service image...${NC}"
docker build -t audit-service:latest ./services/audit-service

# Install/upgrade Helm chart
echo -e "${GREEN}Deploying application with Helm...${NC}"
helm upgrade --install todoboard ./infrastructure/helm/todoboard \
    --namespace todoboard \
    --create-namespace \
    --values ./infrastructure/helm/todoboard/values-local.yaml \
    --wait --timeout 600s

# Wait for all pods to be ready
echo -e "${GREEN}Waiting for all pods to be ready...${NC}"
kubectl wait --for=condition=ready pod --all -n todoboard --timeout=600s

# Run database migrations
echo -e "${GREEN}Running database migrations...${NC}"
BACKEND_POD=$(kubectl get pod -n todoboard -l app.kubernetes.io/component=backend -o jsonpath="{.items[0].metadata.name}")
kubectl exec -n todoboard $BACKEND_POD -- alembic upgrade head

# Get ingress IP
echo -e "${GREEN}Getting ingress information...${NC}"
INGRESS_IP=$(minikube ip)

# Add to /etc/hosts if not already present
if ! grep -q "todoboard.local" /etc/hosts; then
    echo -e "${YELLOW}Adding todoboard.local to /etc/hosts...${NC}"
    echo "$INGRESS_IP todoboard.local" | sudo tee -a /etc/hosts
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Application URLs:"
echo "  - Frontend: http://todoboard.local"
echo "  - Backend API: http://todoboard.local/api"
echo "  - WebSocket: ws://todoboard.local/ws"
echo ""
echo "Kubernetes resources:"
kubectl get pods -n todoboard
echo ""
echo "To access the application:"
echo "  1. Run 'minikube tunnel' in a separate terminal"
echo "  2. Open http://todoboard.local in your browser"
echo ""
echo "Useful commands:"
echo "  - kubectl get pods -n todoboard: List all pods"
echo "  - kubectl logs -n todoboard <pod-name>: View pod logs"
echo "  - kubectl logs -n todoboard <pod-name> -c daprd: View Dapr sidecar logs"
echo "  - dapr dashboard -k: Open Dapr dashboard"
echo "  - minikube dashboard: Open Kubernetes dashboard"
