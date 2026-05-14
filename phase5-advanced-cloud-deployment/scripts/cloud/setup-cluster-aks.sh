#!/bin/bash
# Setup Azure Kubernetes Service (AKS) cluster for TodoBoard application
# Prerequisites: Azure CLI (az) installed and authenticated

set -e

# Configuration
RESOURCE_GROUP="${AZURE_RESOURCE_GROUP:-todoboard-rg}"
CLUSTER_NAME="${CLUSTER_NAME:-todoboard-cluster}"
LOCATION="${AZURE_LOCATION:-eastus}"
NODE_COUNT="${NODE_COUNT:-3}"
NODE_VM_SIZE="${NODE_VM_SIZE:-Standard_B2s}"
MIN_NODES="${MIN_NODES:-2}"
MAX_NODES="${MAX_NODES:-10}"

echo "=========================================="
echo "AKS Cluster Setup for TodoBoard"
echo "=========================================="
echo "Resource Group: $RESOURCE_GROUP"
echo "Cluster Name: $CLUSTER_NAME"
echo "Location: $LOCATION"
echo "Node Count: $NODE_COUNT"
echo "Node VM Size: $NODE_VM_SIZE"
echo "=========================================="

# Check if az CLI is installed
if ! command -v az &> /dev/null; then
    echo "Error: Azure CLI is not installed"
    echo "Install from: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged in
echo "Checking Azure login status..."
az account show &> /dev/null || {
    echo "Not logged in to Azure. Please run: az login"
    exit 1
}

# Create resource group
echo "Creating resource group..."
az group create \
    --name "$RESOURCE_GROUP" \
    --location "$LOCATION"

# Create AKS cluster with autoscaling
echo "Creating AKS cluster (this may take 10-15 minutes)..."
az aks create \
    --resource-group "$RESOURCE_GROUP" \
    --name "$CLUSTER_NAME" \
    --location "$LOCATION" \
    --node-count "$NODE_COUNT" \
    --node-vm-size "$NODE_VM_SIZE" \
    --enable-cluster-autoscaler \
    --min-count "$MIN_NODES" \
    --max-count "$MAX_NODES" \
    --enable-managed-identity \
    --network-plugin azure \
    --enable-addons monitoring \
    --generate-ssh-keys \
    --zones 1 2 3

echo "Cluster created successfully!"

# Get cluster credentials
echo "Getting cluster credentials..."
az aks get-credentials \
    --resource-group "$RESOURCE_GROUP" \
    --name "$CLUSTER_NAME" \
    --overwrite-existing

# Verify cluster access
echo "Verifying cluster access..."
kubectl cluster-info
kubectl get nodes

# Install NGINX Ingress Controller
echo "Installing NGINX Ingress Controller..."
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# Wait for ingress controller to be ready
echo "Waiting for ingress controller to be ready..."
kubectl wait --namespace ingress-nginx \
    --for=condition=ready pod \
    --selector=app.kubernetes.io/component=controller \
    --timeout=300s

# Install cert-manager for TLS certificates
echo "Installing cert-manager..."
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Wait for cert-manager to be ready
echo "Waiting for cert-manager to be ready..."
kubectl wait --namespace cert-manager \
    --for=condition=ready pod \
    --selector=app.kubernetes.io/instance=cert-manager \
    --timeout=300s

# Create namespace for application
echo "Creating application namespace..."
kubectl create namespace todoboard || echo "Namespace already exists"

# Enable Azure Monitor for containers (optional)
echo "Enabling Azure Monitor for containers..."
az aks enable-addons \
    --resource-group "$RESOURCE_GROUP" \
    --name "$CLUSTER_NAME" \
    --addons monitoring || echo "Monitoring already enabled"

echo "=========================================="
echo "AKS Cluster Setup Complete!"
echo "=========================================="
echo "Resource Group: $RESOURCE_GROUP"
echo "Cluster Name: $CLUSTER_NAME"
echo "Location: $LOCATION"
echo ""
echo "Next steps:"
echo "1. Configure your DNS to point to the ingress IP"
echo "2. Update values-cloud.yaml with your domain"
echo "3. Deploy the application: ./scripts/cloud/deploy-cloud.sh"
echo ""
echo "Get ingress IP:"
echo "kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}'"
echo ""
echo "View cluster in Azure Portal:"
echo "https://portal.azure.com/#@/resource/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.ContainerService/managedClusters/$CLUSTER_NAME"
echo "=========================================="
