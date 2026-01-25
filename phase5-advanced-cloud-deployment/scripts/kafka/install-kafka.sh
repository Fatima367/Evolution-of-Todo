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
echo -e "${BLUE}║          Kafka Installation with Strimzi                  ║${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}✗ kubectl is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ kubectl is installed${NC}"

# Check if namespace exists
if ! kubectl get namespace todoboard &> /dev/null; then
    echo -e "${YELLOW}Creating namespace todoboard...${NC}"
    kubectl create namespace todoboard
fi
echo -e "${GREEN}✓ Namespace todoboard exists${NC}"

# Install Strimzi operator
echo -e "${YELLOW}Installing Strimzi Kafka operator...${NC}"
kubectl create namespace kafka 2>/dev/null || true
kubectl apply -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

# Wait for Strimzi operator to be ready
echo -e "${YELLOW}Waiting for Strimzi operator to be ready...${NC}"
kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s

echo -e "${GREEN}✓ Strimzi operator is ready${NC}"

# Apply Kafka metrics ConfigMap
echo -e "${YELLOW}Creating Kafka metrics configuration...${NC}"
kubectl apply -f infrastructure/kafka/kafka-metrics-config.yaml

# Deploy Kafka cluster
echo -e "${YELLOW}Deploying Kafka cluster (this may take 5-10 minutes)...${NC}"
kubectl apply -f infrastructure/kafka/kafka-cluster.yaml

# Wait for Kafka cluster to be ready
echo -e "${YELLOW}Waiting for Kafka cluster to be ready...${NC}"
kubectl wait kafka/todoboard-kafka --for=condition=Ready --timeout=600s -n todoboard

echo -e "${GREEN}✓ Kafka cluster is ready${NC}"

# Create Kafka topics
echo -e "${YELLOW}Creating Kafka topics...${NC}"
kubectl apply -f infrastructure/kafka/kafka-topics.yaml

# Wait for topics to be ready
echo -e "${YELLOW}Waiting for Kafka topics to be ready...${NC}"
sleep 10

# Verify topics
echo -e "${YELLOW}Verifying Kafka topics...${NC}"
kubectl get kafkatopic -n todoboard

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}║          Kafka Installation Complete!                     ║${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Kafka cluster details:${NC}"
echo -e "  Bootstrap servers: ${GREEN}todoboard-kafka-kafka-bootstrap.todoboard.svc:9092${NC}"
echo -e "  Topics created: ${GREEN}task-events, reminders, task-updates, dead-letter-queue${NC}"
echo ""
echo -e "${BLUE}Useful commands:${NC}"
echo -e "  View Kafka pods:    ${YELLOW}kubectl get pods -n todoboard -l strimzi.io/cluster=todoboard-kafka${NC}"
echo -e "  View topics:        ${YELLOW}kubectl get kafkatopic -n todoboard${NC}"
echo -e "  Kafka logs:         ${YELLOW}kubectl logs -n todoboard -l strimzi.io/name=todoboard-kafka-kafka${NC}"
echo ""
