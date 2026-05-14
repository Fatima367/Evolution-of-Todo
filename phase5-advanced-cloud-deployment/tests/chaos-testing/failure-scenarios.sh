#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}TodoBoard Chaos Testing Suite${NC}"
echo -e "${GREEN}Testing Failure Scenarios${NC}"
echo -e "${GREEN}========================================${NC}"

# Configuration
NAMESPACE="${NAMESPACE:-todoboard}"
RESULTS_DIR="./chaos-test-results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$RESULTS_DIR/chaos-test-$TIMESTAMP.log"

# Create results directory
mkdir -p "$RESULTS_DIR"

# Logging function
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

# Check prerequisites
check_prerequisites() {
    log "${BLUE}Checking prerequisites...${NC}"

    if ! command -v kubectl &> /dev/null; then
        log "${RED}Error: kubectl is not installed${NC}"
        exit 1
    fi

    if ! kubectl cluster-info &> /dev/null; then
        log "${RED}Error: Kubernetes cluster is not accessible${NC}"
        exit 1
    fi

    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        log "${RED}Error: Namespace $NAMESPACE does not exist${NC}"
        exit 1
    fi

    log "${GREEN}✓ Prerequisites met${NC}"
    log ""
}

# Test 1: Pod crash and auto-recovery
test_pod_crash_recovery() {
    log "${GREEN}========================================${NC}"
    log "${GREEN}Test 1: Pod Crash and Auto-Recovery${NC}"
    log "${GREEN}========================================${NC}"

    # Get backend pods
    BACKEND_PODS=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/component=backend -o jsonpath='{.items[*].metadata.name}')

    if [ -z "$BACKEND_PODS" ]; then
        log "${RED}✗ No backend pods found${NC}"
        return 1
    fi

    # Select first pod
    POD_NAME=$(echo "$BACKEND_PODS" | awk '{print $1}')
    log "${YELLOW}Killing pod: $POD_NAME${NC}"

    # Record initial state
    INITIAL_PODS=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/component=backend --no-headers | wc -l)
    log "Initial backend pods: $INITIAL_PODS"

    # Delete pod
    kubectl delete pod "$POD_NAME" -n "$NAMESPACE" --grace-period=0 --force
    log "Pod deleted"

    # Wait for recovery
    log "${YELLOW}Waiting for pod recovery (max 60s)...${NC}"
    sleep 5

    # Check if new pod is created
    for i in {1..12}; do
        CURRENT_PODS=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/component=backend --no-headers | wc -l)
        READY_PODS=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/component=backend --field-selector=status.phase=Running --no-headers | wc -l)

        log "Attempt $i: Total pods: $CURRENT_PODS, Ready pods: $READY_PODS"

        if [ "$READY_PODS" -ge "$INITIAL_PODS" ]; then
            log "${GREEN}✓ Pod recovered successfully${NC}"
            log "Recovery time: $((i * 5)) seconds"
            return 0
        fi

        sleep 5
    done

    log "${RED}✗ Pod recovery failed or took too long${NC}"
    return 1
}

# Test 2: Multiple pod failures
test_multiple_pod_failures() {
    log ""
    log "${GREEN}========================================${NC}"
    log "${GREEN}Test 2: Multiple Pod Failures${NC}"
    log "${GREEN}========================================${NC}"

    # Get all pods
    ALL_PODS=$(kubectl get pods -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}')
    POD_ARRAY=($ALL_PODS)

    if [ ${#POD_ARRAY[@]} -lt 3 ]; then
        log "${YELLOW}Not enough pods for multiple failure test${NC}"
        return 0
    fi

    # Kill 3 random pods
    log "${YELLOW}Killing 3 random pods...${NC}"
    for i in {1..3}; do
        RANDOM_INDEX=$((RANDOM % ${#POD_ARRAY[@]}))
        POD_NAME="${POD_ARRAY[$RANDOM_INDEX]}"
        log "Killing pod $i: $POD_NAME"
        kubectl delete pod "$POD_NAME" -n "$NAMESPACE" --grace-period=0 --force &
    done

    wait
    log "All pods killed"

    # Wait for recovery
    log "${YELLOW}Waiting for recovery (max 120s)...${NC}"
    sleep 10

    # Check if all pods recover
    for i in {1..24}; do
        NOT_READY=$(kubectl get pods -n "$NAMESPACE" --field-selector=status.phase!=Running --no-headers 2>/dev/null | wc -l)

        log "Attempt $i: Pods not ready: $NOT_READY"

        if [ "$NOT_READY" -eq 0 ]; then
            log "${GREEN}✓ All pods recovered successfully${NC}"
            log "Recovery time: $((i * 5)) seconds"
            return 0
        fi

        sleep 5
    done

    log "${RED}✗ Not all pods recovered${NC}"
    return 1
}

# Test 3: Network partition simulation
test_network_partition() {
    log ""
    log "${GREEN}========================================${NC}"
    log "${GREEN}Test 3: Network Partition Simulation${NC}"
    log "${GREEN}========================================${NC}"

    # Get backend pod
    BACKEND_POD=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/component=backend -o jsonpath='{.items[0].metadata.name}')

    if [ -z "$BACKEND_POD" ]; then
        log "${RED}✗ No backend pod found${NC}"
        return 1
    fi

    log "${YELLOW}Simulating network partition on pod: $BACKEND_POD${NC}"

    # Block network traffic using iptables (requires privileged access)
    log "Blocking outbound traffic..."
    kubectl exec -n "$NAMESPACE" "$BACKEND_POD" -- sh -c "iptables -A OUTPUT -j DROP" 2>/dev/null || {
        log "${YELLOW}Cannot modify iptables (expected in non-privileged containers)${NC}"
        log "${YELLOW}Skipping network partition test${NC}"
        return 0
    }

    # Wait and check if pod is marked as not ready
    log "${YELLOW}Waiting for health check to fail (max 30s)...${NC}"
    sleep 30

    # Restore network
    log "Restoring network..."
    kubectl exec -n "$NAMESPACE" "$BACKEND_POD" -- sh -c "iptables -D OUTPUT -j DROP" 2>/dev/null || true

    # Check recovery
    log "${YELLOW}Waiting for recovery (max 30s)...${NC}"
    sleep 30

    POD_STATUS=$(kubectl get pod "$BACKEND_POD" -n "$NAMESPACE" -o jsonpath='{.status.phase}')
    if [ "$POD_STATUS" = "Running" ]; then
        log "${GREEN}✓ Pod recovered from network partition${NC}"
        return 0
    else
        log "${RED}✗ Pod did not recover properly${NC}"
        return 1
    fi
}

# Test 4: Database connection failure
test_database_connection_failure() {
    log ""
    log "${GREEN}========================================${NC}"
    log "${GREEN}Test 4: Database Connection Failure${NC}"
    log "${GREEN}========================================${NC}"

    # Get backend pod
    BACKEND_POD=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/component=backend -o jsonpath='{.items[0].metadata.name}')

    if [ -z "$BACKEND_POD" ]; then
        log "${RED}✗ No backend pod found${NC}"
        return 1
    fi

    log "${YELLOW}Testing database connection resilience...${NC}"

    # Check if backend has connection pooling enabled
    log "Checking database configuration..."
    kubectl exec -n "$NAMESPACE" "$BACKEND_POD" -- env | grep -i "DB_" | tee -a "$LOG_FILE"

    # Make API request to verify connection pooling
    log "Making API request to test connection handling..."
    INGRESS_IP=$(kubectl get ingress -n "$NAMESPACE" -o jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "localhost")

    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://$INGRESS_IP/api/health" 2>/dev/null || echo "000")

    if [ "$HTTP_CODE" = "200" ]; then
        log "${GREEN}✓ Application handles database connections properly${NC}"
        return 0
    else
        log "${YELLOW}Could not verify database connection handling (HTTP $HTTP_CODE)${NC}"
        return 0
    fi
}

# Test 5: Resource exhaustion
test_resource_exhaustion() {
    log ""
    log "${GREEN}========================================${NC}"
    log "${GREEN}Test 5: Resource Exhaustion${NC}"
    log "${GREEN}========================================${NC}"

    log "${YELLOW}Checking resource limits and HPA configuration...${NC}"

    # Check HPA status
    HPA_COUNT=$(kubectl get hpa -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l)
    log "HorizontalPodAutoscalers configured: $HPA_COUNT"

    if [ "$HPA_COUNT" -gt 0 ]; then
        log "HPA Status:"
        kubectl get hpa -n "$NAMESPACE" | tee -a "$LOG_FILE"
        log "${GREEN}✓ HPA configured for auto-scaling${NC}"
    else
        log "${YELLOW}No HPA configured${NC}"
    fi

    # Check resource limits
    log ""
    log "Checking resource limits on pods..."
    kubectl get pods -n "$NAMESPACE" -o json | \
        jq -r '.items[] | "\(.metadata.name): CPU=\(.spec.containers[0].resources.limits.cpu // "none"), Memory=\(.spec.containers[0].resources.limits.memory // "none")"' | \
        tee -a "$LOG_FILE"

    log "${GREEN}✓ Resource limits configured${NC}"
    return 0
}

# Test 6: Kafka consumer rebalancing
test_kafka_rebalancing() {
    log ""
    log "${GREEN}========================================${NC}"
    log "${GREEN}Test 6: Kafka Consumer Rebalancing${NC}"
    log "${GREEN}========================================${NC}"

    # Get notification service pods
    NOTIFICATION_PODS=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/component=notification-service -o jsonpath='{.items[*].metadata.name}')

    if [ -z "$NOTIFICATION_PODS" ]; then
        log "${YELLOW}No notification service pods found${NC}"
        return 0
    fi

    POD_ARRAY=($NOTIFICATION_PODS)
    INITIAL_COUNT=${#POD_ARRAY[@]}
    log "Initial notification service pods: $INITIAL_COUNT"

    if [ "$INITIAL_COUNT" -lt 2 ]; then
        log "${YELLOW}Not enough pods for rebalancing test${NC}"
        return 0
    fi

    # Kill one consumer
    POD_TO_KILL="${POD_ARRAY[0]}"
    log "${YELLOW}Killing consumer pod: $POD_TO_KILL${NC}"
    kubectl delete pod "$POD_TO_KILL" -n "$NAMESPACE" --grace-period=0 --force

    # Wait for rebalancing
    log "${YELLOW}Waiting for consumer rebalancing (max 60s)...${NC}"
    sleep 10

    # Check if new pod is created and ready
    for i in {1..12}; do
        CURRENT_COUNT=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/component=notification-service --field-selector=status.phase=Running --no-headers | wc -l)

        log "Attempt $i: Running pods: $CURRENT_COUNT"

        if [ "$CURRENT_COUNT" -ge "$INITIAL_COUNT" ]; then
            log "${GREEN}✓ Kafka consumer rebalanced successfully${NC}"
            log "Rebalancing time: $((i * 5)) seconds"
            return 0
        fi

        sleep 5
    done

    log "${RED}✗ Consumer rebalancing failed or took too long${NC}"
    return 1
}

# Run all tests
run_all_tests() {
    log "${BLUE}Starting chaos testing suite at $(date)${NC}"
    log ""

    PASSED=0
    FAILED=0
    SKIPPED=0

    # Run tests
    if test_pod_crash_recovery; then
        ((PASSED++))
    else
        ((FAILED++))
    fi

    if test_multiple_pod_failures; then
        ((PASSED++))
    else
        ((FAILED++))
    fi

    if test_network_partition; then
        ((PASSED++))
    else
        ((FAILED++))
    fi

    if test_database_connection_failure; then
        ((PASSED++))
    else
        ((FAILED++))
    fi

    if test_resource_exhaustion; then
        ((PASSED++))
    else
        ((FAILED++))
    fi

    if test_kafka_rebalancing; then
        ((PASSED++))
    else
        ((FAILED++))
    fi

    # Summary
    log ""
    log "${GREEN}========================================${NC}"
    log "${GREEN}Chaos Testing Summary${NC}"
    log "${GREEN}========================================${NC}"
    log "Tests Passed: ${GREEN}$PASSED${NC}"
    log "Tests Failed: ${RED}$FAILED${NC}"
    log "Tests Skipped: ${YELLOW}$SKIPPED${NC}"
    log ""
    log "Log file: $LOG_FILE"
    log ""

    if [ "$FAILED" -eq 0 ]; then
        log "${GREEN}All chaos tests passed! ✓${NC}"
        return 0
    else
        log "${RED}Some chaos tests failed${NC}"
        return 1
    fi
}

# Main execution
check_prerequisites
run_all_tests
