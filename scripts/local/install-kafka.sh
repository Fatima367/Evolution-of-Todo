#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Installing Kafka using Strimzi Operator${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}Error: kubectl is not configured or cluster is not running${NC}"
    echo "Please run ./scripts/local/setup-minikube.sh first"
    exit 1
fi

# Check if Helm is installed
if ! command -v helm &> /dev/null; then
    echo -e "${RED}Error: Helm is not installed${NC}"
    echo "Please install Helm: https://helm.sh/docs/intro/install/"
    exit 1
fi

# Create Kafka namespace
echo -e "${GREEN}Creating kafka namespace...${NC}"
kubectl create namespace kafka --dry-run=client -o yaml | kubectl apply -f -

# Check if Strimzi is already installed
if kubectl get deployment strimzi-cluster-operator -n kafka &> /dev/null; then
    echo -e "${YELLOW}Strimzi operator is already installed${NC}"
    read -p "Do you want to reinstall? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Uninstalling Strimzi...${NC}"
        helm uninstall strimzi-kafka-operator -n kafka || true
        kubectl delete namespace kafka --wait=true || true
        kubectl create namespace kafka
    else
        echo -e "${GREEN}Using existing Strimzi installation${NC}"
        kubectl get kafka -n kafka
        exit 0
    fi
fi

# Add Strimzi Helm repository
echo -e "${GREEN}Adding Strimzi Helm repository...${NC}"
helm repo add strimzi https://strimzi.io/charts/
helm repo update

# Install Strimzi operator
echo -e "${GREEN}Installing Strimzi Kafka operator...${NC}"
helm install strimzi-kafka-operator strimzi/strimzi-kafka-operator \
    --namespace kafka \
    --set watchNamespaces="{kafka,todoboard}" \
    --wait --timeout 300s

# Wait for operator to be ready
echo -e "${GREEN}Waiting for Strimzi operator to be ready...${NC}"
kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s

# Create Kafka cluster
echo -e "${GREEN}Creating Kafka cluster...${NC}"
cat <<EOF | kubectl apply -f -
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: todoboard-kafka
  namespace: kafka
spec:
  kafka:
    version: 3.6.0
    replicas: 1
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
      - name: tls
        port: 9093
        type: internal
        tls: true
    config:
      offsets.topic.replication.factor: 1
      transaction.state.log.replication.factor: 1
      transaction.state.log.min.isr: 1
      default.replication.factor: 1
      min.insync.replicas: 1
      inter.broker.protocol.version: "3.6"
    storage:
      type: ephemeral
    resources:
      requests:
        memory: 1Gi
        cpu: 500m
      limits:
        memory: 2Gi
        cpu: 1000m
  zookeeper:
    replicas: 1
    storage:
      type: ephemeral
    resources:
      requests:
        memory: 512Mi
        cpu: 250m
      limits:
        memory: 1Gi
        cpu: 500m
  entityOperator:
    topicOperator:
      resources:
        requests:
          memory: 256Mi
          cpu: 100m
        limits:
          memory: 512Mi
          cpu: 500m
    userOperator:
      resources:
        requests:
          memory: 256Mi
          cpu: 100m
        limits:
          memory: 512Mi
          cpu: 500m
EOF

# Wait for Kafka cluster to be ready
echo -e "${GREEN}Waiting for Kafka cluster to be ready (this may take a few minutes)...${NC}"
kubectl wait kafka/todoboard-kafka --for=condition=Ready --timeout=600s -n kafka

# Create Kafka topics
echo -e "${GREEN}Creating Kafka topics...${NC}"
cat <<EOF | kubectl apply -f -
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-events
  namespace: kafka
  labels:
    strimzi.io/cluster: todoboard-kafka
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 604800000  # 7 days
    segment.bytes: 1073741824
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-updates
  namespace: kafka
  labels:
    strimzi.io/cluster: todoboard-kafka
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 86400000  # 1 day
    segment.bytes: 1073741824
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: reminders
  namespace: kafka
  labels:
    strimzi.io/cluster: todoboard-kafka
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 86400000  # 1 day
    segment.bytes: 1073741824
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: dead-letter-queue
  namespace: kafka
  labels:
    strimzi.io/cluster: todoboard-kafka
spec:
  partitions: 1
  replicas: 1
  config:
    retention.ms: 2592000000  # 30 days
    segment.bytes: 1073741824
EOF

# Wait for topics to be ready
echo -e "${GREEN}Waiting for Kafka topics to be ready...${NC}"
sleep 10
kubectl get kafkatopics -n kafka

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Kafka installation complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Kafka cluster:"
kubectl get kafka -n kafka
echo ""
echo "Kafka topics:"
kubectl get kafkatopics -n kafka
echo ""
echo "Kafka bootstrap server: todoboard-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092"
echo ""
echo "Next steps:"
echo "  1. Run ./scripts/local/deploy-local.sh to deploy the application"
echo ""
echo "Useful commands:"
echo "  - kubectl get pods -n kafka: List Kafka pods"
echo "  - kubectl logs -n kafka <pod-name>: View Kafka logs"
echo "  - kubectl exec -it <kafka-pod> -n kafka -- bin/kafka-topics.sh --list --bootstrap-server localhost:9092"
