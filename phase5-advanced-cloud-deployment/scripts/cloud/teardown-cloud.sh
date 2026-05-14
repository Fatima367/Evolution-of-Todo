#!/bin/bash
# Teardown cloud Kubernetes cluster and all resources
# Supports: Oracle Cloud (OKE), Google Cloud (GKE), Azure (AKS)

set -e

# Configuration
CLOUD_PROVIDER="${CLOUD_PROVIDER:-}"
CLUSTER_NAME="${CLUSTER_NAME:-todoboard-cluster}"
NAMESPACE="${NAMESPACE:-todoboard}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Cloud Cluster Teardown for TodoBoard"
echo "=========================================="

# Detect cloud provider if not specified
if [ -z "$CLOUD_PROVIDER" ]; then
    echo "Detecting cloud provider..."

    if command -v oci &> /dev/null && oci ce cluster list &> /dev/null; then
        CLOUD_PROVIDER="oke"
        echo "Detected: Oracle Cloud (OKE)"
    elif command -v gcloud &> /dev/null && gcloud container clusters list &> /dev/null; then
        CLOUD_PROVIDER="gke"
        echo "Detected: Google Cloud (GKE)"
    elif command -v az &> /dev/null && az aks list &> /dev/null; then
        CLOUD_PROVIDER="aks"
        echo "Detected: Azure (AKS)"
    else
        echo -e "${RED}Error: Could not detect cloud provider${NC}"
        echo "Please set CLOUD_PROVIDER environment variable to: oke, gke, or aks"
        exit 1
    fi
fi

echo "Cloud Provider: $CLOUD_PROVIDER"
echo "Cluster Name: $CLUSTER_NAME"
echo "Namespace: $NAMESPACE"
echo "=========================================="

# Confirmation prompt
echo -e "${YELLOW}WARNING: This will delete all resources in the cluster!${NC}"
echo -e "${YELLOW}This action cannot be undone.${NC}"
read -p "Are you sure you want to continue? (yes/no): " -r
echo
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Teardown cancelled."
    exit 0
fi

# Function to delete Helm releases
delete_helm_releases() {
    echo "Deleting Helm releases..."

    if helm list -n "$NAMESPACE" &> /dev/null; then
        RELEASES=$(helm list -n "$NAMESPACE" -q)
        if [ -n "$RELEASES" ]; then
            for release in $RELEASES; do
                echo "Deleting Helm release: $release"
                helm uninstall "$release" -n "$NAMESPACE" || echo "Failed to delete $release"
            done
        else
            echo "No Helm releases found in namespace $NAMESPACE"
        fi
    fi
}

# Function to delete namespace and resources
delete_namespace() {
    echo "Deleting namespace: $NAMESPACE"

    if kubectl get namespace "$NAMESPACE" &> /dev/null; then
        # Delete all resources in namespace
        kubectl delete all --all -n "$NAMESPACE" --grace-period=30 --timeout=5m || true

        # Delete PVCs
        kubectl delete pvc --all -n "$NAMESPACE" --grace-period=30 --timeout=5m || true

        # Delete secrets
        kubectl delete secrets --all -n "$NAMESPACE" --grace-period=30 --timeout=5m || true

        # Delete configmaps
        kubectl delete configmaps --all -n "$NAMESPACE" --grace-period=30 --timeout=5m || true

        # Delete namespace
        kubectl delete namespace "$NAMESPACE" --grace-period=30 --timeout=5m || true
    else
        echo "Namespace $NAMESPACE does not exist"
    fi
}

# Function to delete cluster-wide resources
delete_cluster_resources() {
    echo "Deleting cluster-wide resources..."

    # Delete ClusterIssuers
    kubectl delete clusterissuer letsencrypt-prod letsencrypt-staging --ignore-not-found=true || true

    # Delete cert-manager
    echo "Deleting cert-manager..."
    kubectl delete -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml --ignore-not-found=true || true

    # Delete NGINX Ingress Controller
    echo "Deleting NGINX Ingress Controller..."
    kubectl delete -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml --ignore-not-found=true || true

    # Delete Dapr
    if command -v dapr &> /dev/null; then
        echo "Uninstalling Dapr..."
        dapr uninstall -k || true
    fi

    # Delete Strimzi Kafka operator (if installed)
    echo "Deleting Kafka resources..."
    kubectl delete kafka --all -n kafka --ignore-not-found=true || true
    kubectl delete -f https://strimzi.io/install/latest?namespace=kafka --ignore-not-found=true || true
    kubectl delete namespace kafka --ignore-not-found=true || true
}

# Function to delete OKE cluster
delete_oke_cluster() {
    echo "Deleting Oracle Cloud (OKE) cluster..."

    COMPARTMENT_ID="${OCI_COMPARTMENT_ID:-}"

    if [ -z "$COMPARTMENT_ID" ]; then
        echo -e "${RED}Error: OCI_COMPARTMENT_ID not set${NC}"
        exit 1
    fi

    # Get cluster OCID
    CLUSTER_ID=$(oci ce cluster list \
        --compartment-id "$COMPARTMENT_ID" \
        --name "$CLUSTER_NAME" \
        --query 'data[0].id' \
        --raw-output 2>/dev/null || echo "")

    if [ -n "$CLUSTER_ID" ] && [ "$CLUSTER_ID" != "null" ]; then
        echo "Deleting cluster: $CLUSTER_ID"
        oci ce cluster delete \
            --cluster-id "$CLUSTER_ID" \
            --force

        echo "Waiting for cluster deletion to complete..."
        oci ce cluster get \
            --cluster-id "$CLUSTER_ID" \
            --wait-for-state DELETED \
            --max-wait-seconds 1800 || true

        echo -e "${GREEN}OKE cluster deleted successfully${NC}"
    else
        echo "Cluster not found or already deleted"
    fi
}

# Function to delete GKE cluster
delete_gke_cluster() {
    echo "Deleting Google Cloud (GKE) cluster..."

    PROJECT_ID="${GCP_PROJECT_ID:-}"
    ZONE="${GCP_ZONE:-us-central1-a}"

    if [ -z "$PROJECT_ID" ]; then
        echo -e "${RED}Error: GCP_PROJECT_ID not set${NC}"
        exit 1
    fi

    gcloud config set project "$PROJECT_ID"

    if gcloud container clusters describe "$CLUSTER_NAME" --zone="$ZONE" &> /dev/null; then
        echo "Deleting cluster: $CLUSTER_NAME"
        gcloud container clusters delete "$CLUSTER_NAME" \
            --zone="$ZONE" \
            --quiet

        echo -e "${GREEN}GKE cluster deleted successfully${NC}"
    else
        echo "Cluster not found or already deleted"
    fi
}

# Function to delete AKS cluster
delete_aks_cluster() {
    echo "Deleting Azure (AKS) cluster..."

    RESOURCE_GROUP="${AZURE_RESOURCE_GROUP:-todoboard-rg}"

    if az aks show --resource-group "$RESOURCE_GROUP" --name "$CLUSTER_NAME" &> /dev/null; then
        echo "Deleting cluster: $CLUSTER_NAME"
        az aks delete \
            --resource-group "$RESOURCE_GROUP" \
            --name "$CLUSTER_NAME" \
            --yes \
            --no-wait

        echo "Waiting for cluster deletion to complete..."
        az aks wait \
            --resource-group "$RESOURCE_GROUP" \
            --name "$CLUSTER_NAME" \
            --deleted \
            --timeout 1800 || true

        # Optionally delete resource group
        read -p "Delete resource group $RESOURCE_GROUP? (yes/no): " -r
        if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
            echo "Deleting resource group..."
            az group delete \
                --name "$RESOURCE_GROUP" \
                --yes \
                --no-wait
        fi

        echo -e "${GREEN}AKS cluster deleted successfully${NC}"
    else
        echo "Cluster not found or already deleted"
    fi
}

# Main teardown sequence
echo "Starting teardown sequence..."

# Step 1: Delete Helm releases
delete_helm_releases

# Step 2: Delete namespace
delete_namespace

# Step 3: Delete cluster-wide resources
delete_cluster_resources

# Step 4: Delete cluster based on provider
case "$CLOUD_PROVIDER" in
    oke)
        delete_oke_cluster
        ;;
    gke)
        delete_gke_cluster
        ;;
    aks)
        delete_aks_cluster
        ;;
    *)
        echo -e "${RED}Error: Unknown cloud provider: $CLOUD_PROVIDER${NC}"
        exit 1
        ;;
esac

echo "=========================================="
echo -e "${GREEN}Teardown Complete!${NC}"
echo "=========================================="
echo "All resources have been deleted."
echo ""
echo "Note: Some resources may take a few minutes to fully terminate."
echo "Check your cloud provider console to verify all resources are deleted."
echo "=========================================="
