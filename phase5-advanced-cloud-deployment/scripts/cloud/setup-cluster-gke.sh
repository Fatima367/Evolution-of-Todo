#!/bin/bash
# Setup Google Kubernetes Engine (GKE) cluster for TodoBoard application
# Prerequisites: gcloud CLI installed and authenticated

set -e

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-todoboard-project}"
CLUSTER_NAME="${CLUSTER_NAME:-todoboard-cluster}"
REGION="${GCP_REGION:-us-central1}"
ZONE="${GCP_ZONE:-us-central1-a}"
NODE_COUNT="${NODE_COUNT:-3}"
MACHINE_TYPE="${MACHINE_TYPE:-e2-standard-2}"
DISK_SIZE="${DISK_SIZE:-50}"
MIN_NODES="${MIN_NODES:-2}"
MAX_NODES="${MAX_NODES:-10}"

echo "=========================================="
echo "GKE Cluster Setup for TodoBoard"
echo "=========================================="
echo "Project ID: $PROJECT_ID"
echo "Cluster Name: $CLUSTER_NAME"
echo "Region: $REGION"
echo "Zone: $ZONE"
echo "Node Count: $NODE_COUNT"
echo "Machine Type: $MACHINE_TYPE"
echo "=========================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI is not installed"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set project
echo "Setting GCP project..."
gcloud config set project "$PROJECT_ID"

# Enable required APIs
echo "Enabling required GCP APIs..."
gcloud services enable container.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable servicenetworking.googleapis.com

# Create GKE cluster with autoscaling
echo "Creating GKE cluster..."
gcloud container clusters create "$CLUSTER_NAME" \
    --zone="$ZONE" \
    --num-nodes="$NODE_COUNT" \
    --machine-type="$MACHINE_TYPE" \
    --disk-size="$DISK_SIZE" \
    --enable-autoscaling \
    --min-nodes="$MIN_NODES" \
    --max-nodes="$MAX_NODES" \
    --enable-autorepair \
    --enable-autoupgrade \
    --enable-ip-alias \
    --network="default" \
    --subnetwork="default" \
    --addons=HorizontalPodAutoscaling,HttpLoadBalancing,GcePersistentDiskCsiDriver \
    --workload-pool="$PROJECT_ID.svc.id.goog" \
    --enable-stackdriver-kubernetes \
    --logging=SYSTEM,WORKLOAD \
    --monitoring=SYSTEM

echo "Cluster created successfully!"

# Get cluster credentials
echo "Getting cluster credentials..."
gcloud container clusters get-credentials "$CLUSTER_NAME" --zone="$ZONE"

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

# Install metrics-server (if not already installed)
echo "Verifying metrics-server..."
kubectl get deployment metrics-server -n kube-system || {
    echo "Installing metrics-server..."
    kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
}

echo "=========================================="
echo "GKE Cluster Setup Complete!"
echo "=========================================="
echo "Cluster Name: $CLUSTER_NAME"
echo "Zone: $ZONE"
echo ""
echo "Next steps:"
echo "1. Configure your DNS to point to the ingress IP"
echo "2. Update values-cloud.yaml with your domain"
echo "3. Deploy the application: ./scripts/cloud/deploy-cloud.sh"
echo ""
echo "Get ingress IP:"
echo "kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}'"
echo "=========================================="
