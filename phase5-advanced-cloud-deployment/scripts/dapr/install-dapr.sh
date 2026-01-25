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
echo -e "${BLUE}║          Dapr Installation for Cloud                      ║${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}✗ kubectl is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ kubectl is installed${NC}"

# Check if helm is installed
if ! command -v helm &> /dev/null; then
    echo -e "${RED}✗ Helm is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Helm is installed${NC}"

# Check if namespace exists
if ! kubectl get namespace todoboard &> /dev/null; then
    echo -e "${YELLOW}Creating namespace todoboard...${NC}"
    kubectl create namespace todoboard
fi
echo -e "${GREEN}✓ Namespace todoboard exists${NC}"

# Add Dapr Helm repository
echo -e "${YELLOW}Adding Dapr Helm repository...${NC}"
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update

# Install Dapr with production settings
echo -e "${YELLOW}Installing Dapr with production settings...${NC}"
helm upgrade --install dapr dapr/dapr \
  --namespace dapr-system \
  --create-namespace \
  --set global.ha.enabled=true \
  --set global.ha.replicaCount=3 \
  --set global.prometheus.enabled=true \
  --set global.mtls.enabled=true \
  --set dapr_operator.replicaCount=3 \
  --set dapr_sidecar_injector.replicaCount=3 \
  --set dapr_sentry.replicaCount=3 \
  --set dapr_placement.replicaCount=3 \
  --wait \
  --timeout 10m

# Wait for Dapr to be ready
echo -e "${YELLOW}Waiting for Dapr to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=dapr -n dapr-system --timeout=300s

echo -e "${GREEN}✓ Dapr is ready${NC}"

# Apply Dapr components
echo -e "${YELLOW}Applying Dapr components...${NC}"
kubectl apply -f infrastructure/dapr/components/
echo -e "${GREEN}✓ Dapr components applied${NC}"

# Apply Dapr subscriptions
echo -e "${YELLOW}Applying Dapr subscriptions...${NC}"
kubectl apply -f infrastructure/dapr/subscriptions/
echo -e "${GREEN}✓ Dapr subscriptions applied${NC}"

# Apply Dapr configuration
echo -e "${YELLOW}Applying Dapr configuration...${NC}"
kubectl apply -f infrastructure/dapr/config/
echo -e "${GREEN}✓ Dapr configuration applied${NC}"

# Verify Dapr components
echo -e "${YELLOW}Verifying Dapr components...${NC}"
sleep 5

# Check if dapr CLI is installed
if command -v dapr &> /dev/null; then
    dapr components -k -n todoboard
else
    kubectl get components -n todoboard
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}║          Dapr Installation Complete!                      ║${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Dapr components installed:${NC}"
echo -e "  - ${GREEN}pubsub-kafka${NC} (Kafka pub/sub)"
echo -e "  - ${GREEN}statestore-postgres${NC} (PostgreSQL state store)"
echo -e "  - ${GREEN}secrets-k8s${NC} (Kubernetes secrets)"
echo ""
echo -e "${BLUE}Dapr subscriptions created:${NC}"
echo -e "  - ${GREEN}notification-service-reminders${NC}"
echo -e "  - ${GREEN}recurring-task-service-events${NC}"
echo -e "  - ${GREEN}audit-service-events${NC}"
echo ""
echo -e "${BLUE}Useful commands:${NC}"
echo -e "  View Dapr pods:       ${YELLOW}kubectl get pods -n dapr-system${NC}"
echo -e "  View components:      ${YELLOW}kubectl get components -n todoboard${NC}"
echo -e "  View subscriptions:   ${YELLOW}kubectl get subscriptions -n todoboard${NC}"
echo -e "  Dapr dashboard:       ${YELLOW}dapr dashboard -k${NC}"
echo ""
