#!/bin/bash
set -e

# Deploy TodoBoard to Minikube
# This script deploys the complete application stack to a local Minikube cluster

echo "=========================================="
echo "TodoBoard Local Deployment (Minikube)"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Minikube is running
if ! minikube status &> /dev/null; then
    echo -e "${RED}Error: Minikube is not running${NC}"
    echo "Please run: ./setup-minikube.sh first"
    exit 1
fi

# Check if kubectl is configured for Minikube
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}Error: kubectl is not configured${NC}"
    echo "Please run: minikube kubectl -- config use-context minikube"
    exit 1
fi

echo -e "${GREEN}✓ Minikube is running${NC}"
echo ""

# Check if Dapr is installed
if ! kubectl get namespace dapr-system &> /dev/null; then
    echo -e "${YELLOW}Warning: Dapr is not installed${NC}"
    echo "Installing Dapr..."
    ./install-dapr.sh
fi

echo -e "${GREEN}✓ Dapr is installed${NC}"
echo ""

# Check if Kafka is installed
if ! kubectl get namespace kafka &> /dev/null; then
    echo -e "${YELLOW}Warning: Kafka is not installed${NC}"
    echo "Installing Kafka..."
    ../kafka/install-kafka.sh
fi

echo -e "${GREEN}✓ Kafka is installed${NC}"
echo ""

# Create namespace if it doesn't exist
echo "Creating namespace 'todoboard'..."
kubectl create namespace todoboard --dry-run=client -o yaml | kubectl apply -f -

echo -e "${GREEN}✓ Namespace created${NC}"
echo ""

# Create secrets
echo "Creating secrets..."
kubectl create secret generic todoboard-secrets \
  --from-literal=POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-todoboard_password}" \
  --from-literal=JWT_SECRET_KEY="${JWT_SECRET_KEY:-your-secret-key-change-in-production}" \
  --from-literal=GROQ_API_KEY="${GROQ_API_KEY:-your-groq-api-key}" \
  --namespace=todoboard \
  --dry-run=client -o yaml | kubectl apply -f -

echo -e "${GREEN}✓ Secrets created${NC}"
echo ""

# Deploy using Helm
echo "Deploying TodoBoard with Helm..."
cd ../../infrastructure/helm/todo-app

# Check if release exists
if helm list -n todoboard | grep -q todoboard; then
    echo "Upgrading existing release..."
    helm upgrade todoboard . \
      -f values-minikube.yaml \
      -n todoboard \
      --wait \
      --timeout 10m
else
    echo "Installing new release..."
    helm install todoboard . \
      -f values-minikube.yaml \
      -n todoboard \
      --create-namespace \
      --wait \
      --timeout 10m
fi

echo -e "${GREEN}✓ Helm deployment complete${NC}"
echo ""

# Wait for pods to be ready
echo "Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod \
  --all \
  -n todoboard \
  --timeout=300s

echo -e "${GREEN}✓ All pods are ready${NC}"
echo ""

# Get service URLs
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Access the application:"
echo ""

# Get Minikube IP
MINIKUBE_IP=$(minikube ip)

# Check if ingress is enabled
if kubectl get ingress -n todoboard &> /dev/null; then
    echo "Frontend: http://${MINIKUBE_IP}"
    echo "Backend API: http://${MINIKUBE_IP}/api"
    echo ""
    echo "Note: Add this to your /etc/hosts file:"
    echo "${MINIKUBE_IP} todoboard.local"
else
    # Use NodePort services
    FRONTEND_PORT=$(kubectl get svc todoboard-frontend -n todoboard -o jsonpath='{.spec.ports[0].nodePort}')
    BACKEND_PORT=$(kubectl get svc todoboard-backend -n todoboard -o jsonpath='{.spec.ports[0].nodePort}')

    echo "Frontend: http://${MINIKUBE_IP}:${FRONTEND_PORT}"
    echo "Backend API: http://${MINIKUBE_IP}:${BACKEND_PORT}"
fi

echo ""
echo "Useful commands:"
echo "  kubectl get pods -n todoboard          # View pod status"
echo "  kubectl logs -f <pod-name> -n todoboard # View logs"
echo "  kubectl port-forward svc/todoboard-frontend 3000:3000 -n todoboard"
echo "  kubectl port-forward svc/todoboard-backend 8000:8000 -n todoboard"
echo ""
echo "To teardown: ./teardown-local.sh"
echo ""
