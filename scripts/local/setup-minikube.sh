#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Setting up Minikube for TodoBoard${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if minikube is installed
if ! command -v minikube &> /dev/null; then
    echo -e "${RED}Error: minikube is not installed${NC}"
    echo "Please install minikube: https://minikube.sigs.k8s.io/docs/start/"
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed${NC}"
    echo "Please install kubectl: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}Error: Docker is not running${NC}"
    echo "Please start Docker Desktop"
    exit 1
fi

# Check if minikube is already running
if minikube status &> /dev/null; then
    echo -e "${YELLOW}Minikube is already running${NC}"
    read -p "Do you want to delete and recreate the cluster? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Deleting existing Minikube cluster...${NC}"
        minikube delete
    else
        echo -e "${GREEN}Using existing Minikube cluster${NC}"
        exit 0
    fi
fi

# Start Minikube with appropriate resources
echo -e "${GREEN}Starting Minikube cluster...${NC}"
minikube start \
    --cpus=4 \
    --memory=8192 \
    --disk-size=20g \
    --driver=docker \
    --kubernetes-version=v1.28.0

# Enable required addons
echo -e "${GREEN}Enabling Minikube addons...${NC}"
minikube addons enable ingress
minikube addons enable metrics-server
minikube addons enable dashboard

# Configure kubectl context
echo -e "${GREEN}Configuring kubectl context...${NC}"
kubectl config use-context minikube

# Create namespace for the application
echo -e "${GREEN}Creating todoboard namespace...${NC}"
kubectl create namespace todoboard --dry-run=client -o yaml | kubectl apply -f -

# Set default namespace
kubectl config set-context --current --namespace=todoboard

# Verify cluster is ready
echo -e "${GREEN}Verifying cluster status...${NC}"
kubectl cluster-info
kubectl get nodes

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Minikube setup complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Cluster info:"
echo "  - Kubernetes version: $(kubectl version --short | grep Server | awk '{print $3}')"
echo "  - Nodes: $(kubectl get nodes --no-headers | wc -l)"
echo "  - Namespace: todoboard"
echo ""
echo "Next steps:"
echo "  1. Run ./scripts/local/install-dapr.sh to install Dapr"
echo "  2. Run ./scripts/local/install-kafka.sh to install Kafka"
echo "  3. Run ./scripts/local/deploy-local.sh to deploy the application"
echo ""
echo "Useful commands:"
echo "  - minikube dashboard: Open Kubernetes dashboard"
echo "  - minikube tunnel: Expose LoadBalancer services"
echo "  - kubectl get pods: List all pods"
echo "  - kubectl logs <pod-name>: View pod logs"
