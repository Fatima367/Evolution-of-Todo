#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deploying TodoBoard to Cloud Kubernetes${NC}"
echo -e "${GREEN}========================================${NC}"

# Check prerequisites
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}Error: kubectl is not configured${NC}"
    exit 1
fi

# Configuration
NAMESPACE="todoboard"
HELM_RELEASE="todoboard"
VALUES_FILE="./infrastructure/helm/todoboard/values-cloud.yaml"

# Create namespace
echo -e "${GREEN}Creating namespace...${NC}"
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Install cert-manager if not already installed
if ! kubectl get namespace cert-manager &> /dev/null; then
    echo -e "${GREEN}Installing cert-manager...${NC}"
    kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
    kubectl wait --for=condition=ready pod --all -n cert-manager --timeout=300s
fi

# Create ClusterIssuer for Let's Encrypt
echo -e "${GREEN}Creating Let's Encrypt ClusterIssuer...${NC}"
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@todoboard.app
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF

# Install NGINX Ingress Controller if not already installed
if ! kubectl get namespace ingress-nginx &> /dev/null; then
    echo -e "${GREEN}Installing NGINX Ingress Controller...${NC}"
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.4/deploy/static/provider/cloud/deploy.yaml
    kubectl wait --for=condition=ready pod --all -n ingress-nginx --timeout=300s
fi

# Install Dapr if not already installed
if ! kubectl get namespace dapr-system &> /dev/null; then
    echo -e "${GREEN}Installing Dapr...${NC}"
    dapr init -k --wait --timeout 600
fi

# Install Kafka using Strimzi
if ! kubectl get namespace kafka &> /dev/null; then
    echo -e "${GREEN}Installing Kafka...${NC}"
    ./scripts/local/install-kafka.sh
fi

# Build and push Docker images
echo -e "${GREEN}Building and pushing Docker images...${NC}"
docker build -t ghcr.io/your-org/todoboard-backend:latest ./phase5-advanced-cloud-deployment/backend
docker push ghcr.io/your-org/todoboard-backend:latest

docker build -t ghcr.io/your-org/todoboard-frontend:latest ./phase5-advanced-cloud-deployment/frontend
docker push ghcr.io/your-org/todoboard-frontend:latest

docker build -t ghcr.io/your-org/notification-service:latest ./services/notification-service
docker push ghcr.io/your-org/notification-service:latest

docker build -t ghcr.io/your-org/recurring-task-service:latest ./services/recurring-task-service
docker push ghcr.io/your-org/recurring-task-service:latest

docker build -t ghcr.io/your-org/audit-service:latest ./services/audit-service
docker push ghcr.io/your-org/audit-service:latest

# Deploy with Helm
echo -e "${GREEN}Deploying application with Helm...${NC}"
helm upgrade --install $HELM_RELEASE ./infrastructure/helm/todoboard \
    --namespace $NAMESPACE \
    --values $VALUES_FILE \
    --wait --timeout 600s

# Wait for all pods to be ready
echo -e "${GREEN}Waiting for all pods to be ready...${NC}"
kubectl wait --for=condition=ready pod --all -n $NAMESPACE --timeout=600s

# Run database migrations
echo -e "${GREEN}Running database migrations...${NC}"
BACKEND_POD=$(kubectl get pod -n $NAMESPACE -l app.kubernetes.io/component=backend -o jsonpath="{.items[0].metadata.name}")
kubectl exec -n $NAMESPACE $BACKEND_POD -- alembic upgrade head

# Get ingress IP
echo -e "${GREEN}Getting ingress information...${NC}"
INGRESS_IP=$(kubectl get ingress -n $NAMESPACE -o jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}')

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Application URLs:"
echo "  - Frontend: https://todoboard.app"
echo "  - Backend API: https://todoboard.app/api"
echo ""
echo "Ingress IP: $INGRESS_IP"
echo ""
echo "Configure DNS:"
echo "  - Add A record: todoboard.app -> $INGRESS_IP"
echo ""
echo "Useful commands:"
echo "  - kubectl get pods -n $NAMESPACE"
echo "  - kubectl logs -n $NAMESPACE <pod-name>"
echo "  - helm list -n $NAMESPACE"
