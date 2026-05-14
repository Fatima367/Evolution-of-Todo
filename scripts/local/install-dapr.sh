#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Installing Dapr on Kubernetes${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}Error: kubectl is not configured or cluster is not running${NC}"
    echo "Please run ./scripts/local/setup-minikube.sh first"
    exit 1
fi

# Check if Dapr CLI is installed
if ! command -v dapr &> /dev/null; then
    echo -e "${YELLOW}Dapr CLI is not installed. Installing...${NC}"

    # Detect OS
    OS="$(uname -s)"
    case "${OS}" in
        Linux*)
            wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
            ;;
        Darwin*)
            curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | /bin/bash
            ;;
        MINGW*|MSYS*|CYGWIN*)
            echo -e "${YELLOW}Please install Dapr CLI manually on Windows:${NC}"
            echo "powershell -Command \"iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex\""
            exit 1
            ;;
        *)
            echo -e "${RED}Unsupported OS: ${OS}${NC}"
            exit 1
            ;;
    esac
fi

# Verify Dapr CLI installation
echo -e "${GREEN}Verifying Dapr CLI installation...${NC}"
dapr version

# Check if Dapr is already installed on Kubernetes
if kubectl get namespace dapr-system &> /dev/null; then
    echo -e "${YELLOW}Dapr is already installed on Kubernetes${NC}"
    read -p "Do you want to uninstall and reinstall? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Uninstalling Dapr...${NC}"
        dapr uninstall -k
    else
        echo -e "${GREEN}Using existing Dapr installation${NC}"
        dapr status -k
        exit 0
    fi
fi

# Install Dapr on Kubernetes
echo -e "${GREEN}Installing Dapr on Kubernetes...${NC}"
dapr init -k --wait --timeout 600

# Verify Dapr installation
echo -e "${GREEN}Verifying Dapr installation...${NC}"
dapr status -k

# Wait for all Dapr pods to be ready
echo -e "${GREEN}Waiting for Dapr pods to be ready...${NC}"
kubectl wait --for=condition=ready pod --all -n dapr-system --timeout=300s

# Create Dapr components directory in the cluster
echo -e "${GREEN}Creating Dapr components ConfigMap...${NC}"
kubectl create configmap dapr-components \
    --from-file=../../infrastructure/dapr/components/ \
    --namespace=todoboard \
    --dry-run=client -o yaml | kubectl apply -f -

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Dapr installation complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Dapr components:"
kubectl get pods -n dapr-system
echo ""
echo "Next steps:"
echo "  1. Run ./scripts/local/install-kafka.sh to install Kafka"
echo "  2. Run ./scripts/local/deploy-local.sh to deploy the application"
echo ""
echo "Useful commands:"
echo "  - dapr dashboard -k: Open Dapr dashboard"
echo "  - dapr status -k: Check Dapr status"
echo "  - kubectl logs -n dapr-system <pod-name>: View Dapr logs"
