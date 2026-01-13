#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Setting up Oracle Cloud Kubernetes (OKE)${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if OCI CLI is installed
if ! command -v oci &> /dev/null; then
    echo -e "${RED}Error: OCI CLI is not installed${NC}"
    echo "Please install OCI CLI: https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm"
    exit 1
fi

# Configuration
CLUSTER_NAME="todoboard-cluster"
COMPARTMENT_ID="${OCI_COMPARTMENT_ID}"
REGION="${OCI_REGION:-us-ashburn-1}"
K8S_VERSION="v1.28.2"
NODE_POOL_SIZE=3
NODE_SHAPE="VM.Standard.E4.Flex"
NODE_OCPUS=2
NODE_MEMORY_GB=16

echo -e "${GREEN}Creating OKE cluster...${NC}"
oci ce cluster create \
    --compartment-id "$COMPARTMENT_ID" \
    --name "$CLUSTER_NAME" \
    --kubernetes-version "$K8S_VERSION" \
    --vcn-id "$OCI_VCN_ID" \
    --region "$REGION" \
    --wait-for-state ACTIVE

# Get cluster ID
CLUSTER_ID=$(oci ce cluster list \
    --compartment-id "$COMPARTMENT_ID" \
    --name "$CLUSTER_NAME" \
    --query 'data[0].id' \
    --raw-output)

echo -e "${GREEN}Creating node pool...${NC}"
oci ce node-pool create \
    --cluster-id "$CLUSTER_ID" \
    --compartment-id "$COMPARTMENT_ID" \
    --name "${CLUSTER_NAME}-pool" \
    --kubernetes-version "$K8S_VERSION" \
    --node-shape "$NODE_SHAPE" \
    --node-shape-config '{"ocpus":'$NODE_OCPUS',"memoryInGBs":'$NODE_MEMORY_GB'}' \
    --size "$NODE_POOL_SIZE" \
    --wait-for-state ACTIVE

echo -e "${GREEN}Configuring kubectl...${NC}"
oci ce cluster create-kubeconfig \
    --cluster-id "$CLUSTER_ID" \
    --file ~/.kube/config \
    --region "$REGION" \
    --token-version 2.0.0

kubectl config use-context "$CLUSTER_NAME"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}OKE cluster setup complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Cluster: $CLUSTER_NAME"
echo "Region: $REGION"
echo "Nodes: $NODE_POOL_SIZE"
echo ""
echo "Next steps:"
echo "  1. Install cert-manager: kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml"
echo "  2. Install Dapr: dapr init -k"
echo "  3. Install Kafka: ./scripts/local/install-kafka.sh"
echo "  4. Deploy application: ./scripts/cloud/deploy-cloud.sh"
