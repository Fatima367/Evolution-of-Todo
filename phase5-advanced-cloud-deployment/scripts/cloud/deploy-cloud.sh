#!/bin/bash
set -e

# Deploy TodoBoard to Cloud Kubernetes (GKE/AKS/OKE)
# This script deploys the complete application stack to a production cloud cluster

echo "=========================================="
echo "TodoBoard Cloud Deployment"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="${NAMESPACE:-todoboard}"
RELEASE_NAME="${RELEASE_NAME:-todoboard}"
DOMAIN="${DOMAIN:-todoboard.example.com}"
CLOUD_PROVIDER="${CLOUD_PROVIDER:-gke}" # gke, aks, or oke

# Check required environment variables
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}Error: DATABASE_URL environment variable is required${NC}"
    echo "Example: export DATABASE_URL='postgresql://user:pass@host/db?sslmode=require'"
    exit 1
fi

if [ -z "$JWT_SECRET_KEY" ]; then
    echo -e "${RED}Error: JWT_SECRET_KEY environment variable is required${NC}"
    echo "Example: export JWT_SECRET_KEY='your-secret-key-here'"
    exit 1
fi

if [ -z "$GROQ_API_KEY" ]; then
    echo -e "${YELLOW}Warning: GROQ_API_KEY not set. AI chatbot will not work.${NC}"
fi

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}Error: kubectl is not configured${NC}"
    echo "Please configure kubectl to connect to your cloud cluster first."
    exit 1
fi

echo -e "${GREEN}✓ kubectl is configured${NC}"
echo -e "${BLUE}Cluster: $(kubectl config current-context)${NC}"
echo ""

# Confirm deployment
echo "Deployment Configuration:"
echo "  Cloud Provider: ${CLOUD_PROVIDER}"
echo "  Namespace: ${NAMESPACE}"
echo "  Release Name: ${RELEASE_NAME}"
echo "  Domain: ${DOMAIN}"
echo ""
read -p "Continue with deployment? (y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

echo ""

# Create namespace if it doesn't exist
echo "Creating namespace '${NAMESPACE}'..."
kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
echo -e "${GREEN}✓ Namespace created${NC}"
echo ""

# Install cert-manager if not already installed
echo "Checking for cert-manager..."
if ! kubectl get namespace cert-manager &> /dev/null; then
    echo "Installing cert-manager..."
    kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
    echo "Waiting for cert-manager to be ready..."
    kubectl wait --for=condition=ready pod \
      -l app.kubernetes.io/instance=cert-manager \
      -n cert-manager \
      --timeout=300s
    echo -e "${GREEN}✓ cert-manager installed${NC}"
else
    echo -e "${GREEN}✓ cert-manager already installed${NC}"
fi
echo ""

# Install NGINX Ingress Controller if not already installed
echo "Checking for NGINX Ingress Controller..."
if ! kubectl get namespace ingress-nginx &> /dev/null; then
    echo "Installing NGINX Ingress Controller..."
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
    echo "Waiting for ingress controller to be ready..."
    kubectl wait --for=condition=ready pod \
      -l app.kubernetes.io/component=controller \
      -n ingress-nginx \
      --timeout=300s
    echo -e "${GREEN}✓ NGINX Ingress Controller installed${NC}"
else
    echo -e "${GREEN}✓ NGINX Ingress Controller already installed${NC}"
fi
echo ""

# Install Dapr
echo "Checking for Dapr..."
if ! kubectl get namespace dapr-system &> /dev/null; then
    echo "Installing Dapr..."
    dapr init -k --wait --timeout 300
    echo -e "${GREEN}✓ Dapr installed${NC}"
else
    echo -e "${GREEN}✓ Dapr already installed${NC}"
fi
echo ""

# Install Kafka using Strimzi
echo "Checking for Kafka..."
if ! kubectl get namespace kafka &> /dev/null; then
    echo "Installing Kafka with Strimzi..."
    kubectl create namespace kafka
    kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka
    echo "Waiting for Strimzi operator..."
    sleep 10
    kubectl apply -f ../../infrastructure/kafka/kafka-cluster.yaml -n kafka
    echo "Waiting for Kafka cluster to be ready (this may take a few minutes)..."
    kubectl wait kafka/todoboard-kafka --for=condition=Ready --timeout=600s -n kafka
    echo -e "${GREEN}✓ Kafka installed${NC}"
else
    echo -e "${GREEN}✓ Kafka already installed${NC}"
fi
echo ""

# Create secrets
echo "Creating secrets..."
kubectl create secret generic todoboard-secrets \
  --from-literal=DATABASE_URL="${DATABASE_URL}" \
  --from-literal=JWT_SECRET_KEY="${JWT_SECRET_KEY}" \
  --from-literal=GROQ_API_KEY="${GROQ_API_KEY:-}" \
  --namespace=${NAMESPACE} \
  --dry-run=client -o yaml | kubectl apply -f -
echo -e "${GREEN}✓ Secrets created${NC}"
echo ""

# Deploy using Helm
echo "Deploying TodoBoard with Helm..."
cd ../../infrastructure/helm/todo-app

# Update values for cloud deployment
cat > /tmp/cloud-values-override.yaml <<EOF
ingress:
  enabled: true
  hosts:
    - host: ${DOMAIN}
      paths:
        - path: /
          pathType: Prefix

  tls:
    enabled: true
    acme:
      email: "admin@${DOMAIN}"

configMap:
  backend:
    DATABASE_URL: "${DATABASE_URL}"
    CORS_ORIGINS: '["https://${DOMAIN}"]'

  frontend:
    NEXT_PUBLIC_API_URL: "https://${DOMAIN}/api"
EOF

# Check if release exists
if helm list -n ${NAMESPACE} | grep -q ${RELEASE_NAME}; then
    echo "Upgrading existing release..."
    helm upgrade ${RELEASE_NAME} . \
      -f values-cloud.yaml \
      -f /tmp/cloud-values-override.yaml \
      -n ${NAMESPACE} \
      --wait \
      --timeout 15m
else
    echo "Installing new release..."
    helm install ${RELEASE_NAME} . \
      -f values-cloud.yaml \
      -f /tmp/cloud-values-override.yaml \
      -n ${NAMESPACE} \
      --create-namespace \
      --wait \
      --timeout 15m
fi

echo -e "${GREEN}✓ Helm deployment complete${NC}"
echo ""

# Clean up temporary file
rm -f /tmp/cloud-values-override.yaml

# Wait for pods to be ready
echo "Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod \
  --all \
  -n ${NAMESPACE} \
  --timeout=600s

echo -e "${GREEN}✓ All pods are ready${NC}"
echo ""

# Get ingress IP/hostname
echo "Waiting for ingress to get an external IP..."
for i in {1..60}; do
    INGRESS_IP=$(kubectl get ingress -n ${NAMESPACE} ${RELEASE_NAME}-cloud -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
    INGRESS_HOSTNAME=$(kubectl get ingress -n ${NAMESPACE} ${RELEASE_NAME}-cloud -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "")

    if [ -n "$INGRESS_IP" ] || [ -n "$INGRESS_HOSTNAME" ]; then
        break
    fi

    echo "Waiting... ($i/60)"
    sleep 5
done

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""

if [ -n "$INGRESS_IP" ]; then
    echo "Ingress IP: ${INGRESS_IP}"
    echo ""
    echo "Configure your DNS:"
    echo "  Create an A record:"
    echo "    Name: ${DOMAIN}"
    echo "    Type: A"
    echo "    Value: ${INGRESS_IP}"
elif [ -n "$INGRESS_HOSTNAME" ]; then
    echo "Ingress Hostname: ${INGRESS_HOSTNAME}"
    echo ""
    echo "Configure your DNS:"
    echo "  Create a CNAME record:"
    echo "    Name: ${DOMAIN}"
    echo "    Type: CNAME"
    echo "    Value: ${INGRESS_HOSTNAME}"
else
    echo -e "${YELLOW}Warning: Could not get ingress IP/hostname${NC}"
    echo "Check manually with: kubectl get ingress -n ${NAMESPACE}"
fi

echo ""
echo "Once DNS is configured, access your application at:"
echo "  https://${DOMAIN}"
echo ""
echo "TLS certificate will be automatically provisioned by cert-manager."
echo "This may take 2-5 minutes after DNS propagation."
echo ""
echo "Useful commands:"
echo "  kubectl get pods -n ${NAMESPACE}                    # View pod status"
echo "  kubectl logs -f <pod-name> -n ${NAMESPACE}          # View logs"
echo "  kubectl get certificate -n ${NAMESPACE}             # Check TLS certificate status"
echo "  kubectl get hpa -n ${NAMESPACE}                     # Check autoscaling status"
echo ""
echo "To teardown: ./teardown-cloud.sh"
echo ""
