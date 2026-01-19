#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}TodoBoard Quickstart Validation${NC}"
echo -e "${GREEN}========================================${NC}"

# Configuration
RESULTS_DIR="./validation-results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$RESULTS_DIR/quickstart-validation-$TIMESTAMP.log"
QUICKSTART_FILE="../../specs/005-advanced-cloud-deployment/quickstart.md"

# Create results directory
mkdir -p "$RESULTS_DIR"

# Logging function
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

# Track validation results
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_SKIPPED=0

# Validation check function
validate_check() {
    local check_name="$1"
    local check_command="$2"
    local required="$3"  # true or false

    log ""
    log "${BLUE}Checking: $check_name${NC}"

    if eval "$check_command" >> "$LOG_FILE" 2>&1; then
        log "${GREEN}✓ $check_name${NC}"
        ((CHECKS_PASSED++))
        return 0
    else
        if [ "$required" = "true" ]; then
            log "${RED}✗ $check_name (REQUIRED)${NC}"
            ((CHECKS_FAILED++))
            return 1
        else
            log "${YELLOW}⚠ $check_name (OPTIONAL)${NC}"
            ((CHECKS_SKIPPED++))
            return 0
        fi
    fi
}

log "${BLUE}Starting quickstart validation at $(date)${NC}"
log ""

# Step 1: Validate prerequisites
log "${GREEN}========================================${NC}"
log "${GREEN}Step 1: Validating Prerequisites${NC}"
log "${GREEN}========================================${NC}"

validate_check "Docker is installed" "command -v docker" "true"
validate_check "Docker is running" "docker info" "true"
validate_check "Minikube is installed" "command -v minikube" "true"
validate_check "kubectl is installed" "command -v kubectl" "true"
validate_check "Helm is installed" "command -v helm" "true"

# Step 2: Check system requirements
log ""
log "${GREEN}========================================${NC}"
log "${GREEN}Step 2: Checking System Requirements${NC}"
log "${GREEN}========================================${NC}"

# Check CPU cores
CPU_CORES=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo "0")
log "CPU cores available: $CPU_CORES"
if [ "$CPU_CORES" -ge 4 ]; then
    log "${GREEN}✓ CPU cores meet minimum requirement (4+)${NC}"
    ((CHECKS_PASSED++))
else
    log "${RED}✗ CPU cores below minimum requirement (need 4, have $CPU_CORES)${NC}"
    ((CHECKS_FAILED++))
fi

# Check available memory
if command -v free &> /dev/null; then
    MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
    log "Memory available: ${MEMORY_GB}GB"
    if [ "$MEMORY_GB" -ge 8 ]; then
        log "${GREEN}✓ Memory meets minimum requirement (8GB+)${NC}"
        ((CHECKS_PASSED++))
    else
        log "${RED}✗ Memory below minimum requirement (need 8GB, have ${MEMORY_GB}GB)${NC}"
        ((CHECKS_FAILED++))
    fi
fi

# Check disk space
DISK_SPACE=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
log "Disk space available: ${DISK_SPACE}GB"
if [ "$DISK_SPACE" -ge 20 ]; then
    log "${GREEN}✓ Disk space meets minimum requirement (20GB+)${NC}"
    ((CHECKS_PASSED++))
else
    log "${YELLOW}⚠ Disk space below recommended (need 20GB, have ${DISK_SPACE}GB)${NC}"
    ((CHECKS_SKIPPED++))
fi

# Step 3: Validate Minikube setup
log ""
log "${GREEN}========================================${NC}"
log "${GREEN}Step 3: Validating Minikube Setup${NC}"
log "${GREEN}========================================${NC}"

if minikube status &> /dev/null; then
    log "${GREEN}✓ Minikube is running${NC}"
    ((CHECKS_PASSED++))

    # Check Minikube configuration
    MINIKUBE_CPUS=$(minikube config get cpus 2>/dev/null || echo "0")
    MINIKUBE_MEMORY=$(minikube config get memory 2>/dev/null || echo "0")

    log "Minikube CPUs: $MINIKUBE_CPUS"
    log "Minikube Memory: ${MINIKUBE_MEMORY}MB"

    if [ "$MINIKUBE_CPUS" -ge 4 ]; then
        log "${GREEN}✓ Minikube CPU allocation is adequate${NC}"
        ((CHECKS_PASSED++))
    else
        log "${YELLOW}⚠ Minikube CPU allocation may be insufficient${NC}"
        ((CHECKS_SKIPPED++))
    fi

    if [ "$MINIKUBE_MEMORY" -ge 8192 ]; then
        log "${GREEN}✓ Minikube memory allocation is adequate${NC}"
        ((CHECKS_PASSED++))
    else
        log "${YELLOW}⚠ Minikube memory allocation may be insufficient${NC}"
        ((CHECKS_SKIPPED++))
    fi

    # Check addons
    validate_check "Ingress addon is enabled" "minikube addons list | grep -q 'ingress.*enabled'" "true"
    validate_check "Metrics-server addon is enabled" "minikube addons list | grep -q 'metrics-server.*enabled'" "true"
else
    log "${YELLOW}⚠ Minikube is not running (will be started by setup script)${NC}"
    ((CHECKS_SKIPPED++))
fi

# Step 4: Validate Dapr installation
log ""
log "${GREEN}========================================${NC}"
log "${GREEN}Step 4: Validating Dapr Installation${NC}"
log "${GREEN}========================================${NC}"

if kubectl get namespace dapr-system &> /dev/null; then
    log "${GREEN}✓ Dapr namespace exists${NC}"
    ((CHECKS_PASSED++))

    validate_check "Dapr control plane is running" "kubectl get pods -n dapr-system --field-selector=status.phase=Running --no-headers | wc -l | grep -q '[1-9]'" "true"
else
    log "${YELLOW}⚠ Dapr is not installed (will be installed by setup script)${NC}"
    ((CHECKS_SKIPPED++))
fi

# Step 5: Validate Kafka installation
log ""
log "${GREEN}========================================${NC}"
log "${GREEN}Step 5: Validating Kafka Installation${NC}"
log "${GREEN}========================================${NC}"

if kubectl get namespace kafka &> /dev/null; then
    log "${GREEN}✓ Kafka namespace exists${NC}"
    ((CHECKS_PASSED++))

    validate_check "Kafka cluster is running" "kubectl get kafka -n kafka --no-headers | wc -l | grep -q '[1-9]'" "false"
else
    log "${YELLOW}⚠ Kafka is not installed (will be installed by setup script)${NC}"
    ((CHECKS_SKIPPED++))
fi

# Step 6: Validate application deployment
log ""
log "${GREEN}========================================${NC}"
log "${GREEN}Step 6: Validating Application Deployment${NC}"
log "${GREEN}========================================${NC}"

if kubectl get namespace todoboard &> /dev/null; then
    log "${GREEN}✓ TodoBoard namespace exists${NC}"
    ((CHECKS_PASSED++))

    # Check deployments
    DEPLOYMENTS=$(kubectl get deployments -n todoboard --no-headers 2>/dev/null | wc -l)
    log "Deployments found: $DEPLOYMENTS"

    if [ "$DEPLOYMENTS" -gt 0 ]; then
        log "${GREEN}✓ Application deployments exist${NC}"
        ((CHECKS_PASSED++))

        # Check pod status
        RUNNING_PODS=$(kubectl get pods -n todoboard --field-selector=status.phase=Running --no-headers 2>/dev/null | wc -l)
        TOTAL_PODS=$(kubectl get pods -n todoboard --no-headers 2>/dev/null | wc -l)

        log "Running pods: $RUNNING_PODS / $TOTAL_PODS"

        if [ "$RUNNING_PODS" -eq "$TOTAL_PODS" ] && [ "$TOTAL_PODS" -gt 0 ]; then
            log "${GREEN}✓ All pods are running${NC}"
            ((CHECKS_PASSED++))
        else
            log "${YELLOW}⚠ Not all pods are running${NC}"
            ((CHECKS_SKIPPED++))
        fi
    else
        log "${YELLOW}⚠ No deployments found (application not deployed)${NC}"
        ((CHECKS_SKIPPED++))
    fi

    # Check services
    validate_check "Backend service exists" "kubectl get service -n todoboard | grep -q backend" "false"
    validate_check "Frontend service exists" "kubectl get service -n todoboard | grep -q frontend" "false"

    # Check ingress
    validate_check "Ingress is configured" "kubectl get ingress -n todoboard --no-headers | wc -l | grep -q '[1-9]'" "false"
else
    log "${YELLOW}⚠ TodoBoard namespace does not exist (application not deployed)${NC}"
    ((CHECKS_SKIPPED++))
fi

# Step 7: Validate application accessibility
log ""
log "${GREEN}========================================${NC}"
log "${GREEN}Step 7: Validating Application Accessibility${NC}"
log "${GREEN}========================================${NC}"

if kubectl get ingress -n todoboard &> /dev/null; then
    INGRESS_IP=$(minikube ip 2>/dev/null || echo "")

    if [ -n "$INGRESS_IP" ]; then
        log "Ingress IP: $INGRESS_IP"

        # Check if todoboard.local is in /etc/hosts
        if grep -q "todoboard.local" /etc/hosts 2>/dev/null; then
            log "${GREEN}✓ todoboard.local is configured in /etc/hosts${NC}"
            ((CHECKS_PASSED++))
        else
            log "${YELLOW}⚠ todoboard.local is not in /etc/hosts${NC}"
            ((CHECKS_SKIPPED++))
        fi

        # Try to access the application
        if curl -s -o /dev/null -w "%{http_code}" "http://todoboard.local" 2>/dev/null | grep -q "200\|301\|302"; then
            log "${GREEN}✓ Application is accessible at http://todoboard.local${NC}"
            ((CHECKS_PASSED++))
        else
            log "${YELLOW}⚠ Application is not accessible (may need 'minikube tunnel')${NC}"
            ((CHECKS_SKIPPED++))
        fi

        # Check API health endpoint
        if curl -s -o /dev/null -w "%{http_code}" "http://todoboard.local/api/health" 2>/dev/null | grep -q "200"; then
            log "${GREEN}✓ Backend API health check passed${NC}"
            ((CHECKS_PASSED++))
        else
            log "${YELLOW}⚠ Backend API health check failed${NC}"
            ((CHECKS_SKIPPED++))
        fi
    fi
else
    log "${YELLOW}⚠ No ingress configured${NC}"
    ((CHECKS_SKIPPED++))
fi

# Step 8: Validate quickstart documentation
log ""
log "${GREEN}========================================${NC}"
log "${GREEN}Step 8: Validating Quickstart Documentation${NC}"
log "${GREEN}========================================${NC}"

if [ -f "$QUICKSTART_FILE" ]; then
    log "${GREEN}✓ Quickstart documentation exists${NC}"
    ((CHECKS_PASSED++))

    # Check for required sections
    if grep -q "Prerequisites" "$QUICKSTART_FILE"; then
        log "${GREEN}✓ Prerequisites section exists${NC}"
        ((CHECKS_PASSED++))
    else
        log "${RED}✗ Prerequisites section missing${NC}"
        ((CHECKS_FAILED++))
    fi

    if grep -q "Quick Start" "$QUICKSTART_FILE"; then
        log "${GREEN}✓ Quick Start section exists${NC}"
        ((CHECKS_PASSED++))
    else
        log "${RED}✗ Quick Start section missing${NC}"
        ((CHECKS_FAILED++))
    fi

    if grep -q "setup-minikube.sh" "$QUICKSTART_FILE"; then
        log "${GREEN}✓ Minikube setup instructions exist${NC}"
        ((CHECKS_PASSED++))
    else
        log "${RED}✗ Minikube setup instructions missing${NC}"
        ((CHECKS_FAILED++))
    fi

    if grep -q "install-dapr.sh" "$QUICKSTART_FILE"; then
        log "${GREEN}✓ Dapr installation instructions exist${NC}"
        ((CHECKS_PASSED++))
    else
        log "${RED}✗ Dapr installation instructions missing${NC}"
        ((CHECKS_FAILED++))
    fi

    if grep -q "install-kafka.sh" "$QUICKSTART_FILE"; then
        log "${GREEN}✓ Kafka installation instructions exist${NC}"
        ((CHECKS_PASSED++))
    else
        log "${RED}✗ Kafka installation instructions missing${NC}"
        ((CHECKS_FAILED++))
    fi

    if grep -q "deploy-local.sh" "$QUICKSTART_FILE"; then
        log "${GREEN}✓ Deployment instructions exist${NC}"
        ((CHECKS_PASSED++))
    else
        log "${RED}✗ Deployment instructions missing${NC}"
        ((CHECKS_FAILED++))
    fi
else
    log "${RED}✗ Quickstart documentation not found at $QUICKSTART_FILE${NC}"
    ((CHECKS_FAILED++))
fi

# Summary
log ""
log "${GREEN}========================================${NC}"
log "${GREEN}Validation Summary${NC}"
log "${GREEN}========================================${NC}"
log "Checks Passed: ${GREEN}$CHECKS_PASSED${NC}"
log "Checks Failed: ${RED}$CHECKS_FAILED${NC}"
log "Checks Skipped: ${YELLOW}$CHECKS_SKIPPED${NC}"
log ""
log "Log file: $LOG_FILE"
log ""

if [ "$CHECKS_FAILED" -eq 0 ]; then
    log "${GREEN}========================================${NC}"
    log "${GREEN}Quickstart validation passed! ✓${NC}"
    log "${GREEN}========================================${NC}"
    exit 0
else
    log "${RED}========================================${NC}"
    log "${RED}Quickstart validation failed${NC}"
    log "${RED}Please review the failed checks above${NC}"
    log "${RED}========================================${NC}"
    exit 1
fi
