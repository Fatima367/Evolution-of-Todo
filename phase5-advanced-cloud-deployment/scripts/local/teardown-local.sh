#!/bin/bash
set -e

# Teardown TodoBoard from Minikube
# This script removes the TodoBoard application from the local Minikube cluster

echo "=========================================="
echo "TodoBoard Local Teardown (Minikube)"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}Error: kubectl is not configured${NC}"
    exit 1
fi

# Check if namespace exists
if ! kubectl get namespace todoboard &> /dev/null; then
    echo -e "${YELLOW}Warning: todoboard namespace does not exist${NC}"
    echo "Nothing to teardown."
    exit 0
fi

echo "This will delete the TodoBoard application from Minikube."
echo ""
read -p "Are you sure you want to continue? (y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Teardown cancelled."
    exit 0
fi

echo ""
echo "Uninstalling Helm release..."

# Uninstall Helm release
if helm list -n todoboard | grep -q todoboard; then
    helm uninstall todoboard -n todoboard
    echo -e "${GREEN}✓ Helm release uninstalled${NC}"
else
    echo -e "${YELLOW}Warning: Helm release 'todoboard' not found${NC}"
fi

echo ""
echo "Deleting namespace..."

# Delete namespace (this will delete all resources in the namespace)
kubectl delete namespace todoboard --timeout=60s

echo -e "${GREEN}✓ Namespace deleted${NC}"
echo ""

# Optional: Clean up Dapr and Kafka
read -p "Do you want to also remove Dapr and Kafka? (y/N) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Removing Dapr..."
    if kubectl get namespace dapr-system &> /dev/null; then
        dapr uninstall -k
        echo -e "${GREEN}✓ Dapr removed${NC}"
    else
        echo -e "${YELLOW}Dapr not installed${NC}"
    fi

    echo ""
    echo "Removing Kafka..."
    if kubectl get namespace kafka &> /dev/null; then
        kubectl delete namespace kafka --timeout=60s
        echo -e "${GREEN}✓ Kafka removed${NC}"
    else
        echo -e "${YELLOW}Kafka not installed${NC}"
    fi
fi

echo ""
echo "=========================================="
echo "Teardown Complete!"
echo "=========================================="
echo ""
echo "The TodoBoard application has been removed from Minikube."
echo ""
echo "To redeploy: ./deploy-local.sh"
echo ""
