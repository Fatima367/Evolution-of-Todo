#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Tearing down TodoBoard from Minikube${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${YELLOW}Kubernetes cluster is not running${NC}"
    exit 0
fi

# Uninstall Helm release
echo -e "${GREEN}Uninstalling Helm release...${NC}"
helm uninstall todoboard -n todoboard || true

# Delete namespace
echo -e "${GREEN}Deleting todoboard namespace...${NC}"
kubectl delete namespace todoboard --wait=true || true

# Delete Kafka cluster
echo -e "${GREEN}Deleting Kafka cluster...${NC}"
kubectl delete kafka todoboard-kafka -n kafka --wait=true || true
kubectl delete kafkatopic --all -n kafka || true

# Uninstall Strimzi operator
echo -e "${GREEN}Uninstalling Strimzi operator...${NC}"
helm uninstall strimzi-kafka-operator -n kafka || true
kubectl delete namespace kafka --wait=true || true

# Uninstall Dapr
echo -e "${GREEN}Uninstalling Dapr...${NC}"
dapr uninstall -k || true

# Remove from /etc/hosts
if grep -q "todoboard.local" /etc/hosts; then
    echo -e "${YELLOW}Removing todoboard.local from /etc/hosts...${NC}"
    sudo sed -i '/todoboard.local/d' /etc/hosts
fi

# Optional: Delete Minikube cluster
read -p "Do you want to delete the entire Minikube cluster? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}Deleting Minikube cluster...${NC}"
    minikube delete
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Teardown complete!${NC}"
echo -e "${GREEN}========================================${NC}"
