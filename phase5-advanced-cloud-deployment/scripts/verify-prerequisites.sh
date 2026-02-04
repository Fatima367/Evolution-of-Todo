#!/bin/bash
# Pre-Deployment Verification Script
# Run this before deploying to ensure all prerequisites are met

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}║     Phase 5 Part B - Pre-Deployment Verification          ║${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

ERRORS=0

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check Minikube
if command -v minikube &> /dev/null; then
    VERSION=$(minikube version --short 2>/dev/null || echo "unknown")
    echo -e "${GREEN}✓ Minikube installed${NC} ($VERSION)"
else
    echo -e "${RED}✗ Minikube not installed${NC}"
    echo "  Install: https://minikube.sigs.k8s.io/docs/start/"
    ERRORS=$((ERRORS + 1))
fi

# Check kubectl
if command -v kubectl &> /dev/null; then
    VERSION=$(kubectl version --client --short 2>/dev/null | head -1 || echo "unknown")
    echo -e "${GREEN}✓ kubectl installed${NC} ($VERSION)"
else
    echo -e "${RED}✗ kubectl not installed${NC}"
    echo "  Install: https://kubernetes.io/docs/tasks/tools/"
    ERRORS=$((ERRORS + 1))
fi

# Check Helm
if command -v helm &> /dev/null; then
    VERSION=$(helm version --short 2>/dev/null || echo "unknown")
    echo -e "${GREEN}✓ Helm installed${NC} ($VERSION)"
else
    echo -e "${RED}✗ Helm not installed${NC}"
    echo "  Install: https://helm.sh/docs/intro/install/"
    ERRORS=$((ERRORS + 1))
fi

# Check Docker
if command -v docker &> /dev/null; then
    VERSION=$(docker --version | cut -d' ' -f3 | tr -d ',')
    echo -e "${GREEN}✓ Docker installed${NC} ($VERSION)"

    # Check if Docker is running
    if docker ps &> /dev/null; then
        echo -e "${GREEN}✓ Docker daemon is running${NC}"
    else
        echo -e "${RED}✗ Docker daemon is not running${NC}"
        echo "  Start Docker Desktop or run: sudo systemctl start docker"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${RED}✗ Docker not installed${NC}"
    echo "  Install: https://docs.docker.com/get-docker/"
    ERRORS=$((ERRORS + 1))
fi

# Check Dapr CLI
if command -v dapr &> /dev/null; then
    VERSION=$(dapr version 2>/dev/null | grep "CLI version" | cut -d':' -f2 | xargs || echo "unknown")
    echo -e "${GREEN}✓ Dapr CLI installed${NC} ($VERSION)"
else
    echo -e "${YELLOW}⚠ Dapr CLI not installed (will be installed during setup)${NC}"
fi

echo ""

# Check environment variables
echo -e "${YELLOW}Checking environment variables...${NC}"

if [ -n "$GROQ_API_KEY" ]; then
    echo -e "${GREEN}✓ GROQ_API_KEY is set${NC}"
else
    echo -e "${YELLOW}⚠ GROQ_API_KEY not set (AI chatbot will not work)${NC}"
    echo "  Set with: export GROQ_API_KEY='your-api-key'"
fi

echo ""

# Check infrastructure files
echo -e "${YELLOW}Checking infrastructure files...${NC}"

FILES_TO_CHECK=(
    "infrastructure/dapr/components/pubsub-kafka.yaml"
    "infrastructure/dapr/components/statestore-postgres.yaml"
    "infrastructure/dapr/components/secrets-k8s.yaml"
    "infrastructure/dapr/config/dapr-config.yaml"
    "infrastructure/kafka/kafka-cluster.yaml"
    "infrastructure/kafka/kafka-topics.yaml"
    "infrastructure/helm/todo-app/Chart.yaml"
    "infrastructure/helm/todo-app/values-minikube.yaml"
    "backend/Dockerfile"
    "frontend/Dockerfile"
    "services/notification-service/Dockerfile"
    "services/recurring-task-service/Dockerfile"
    "services/audit-service/Dockerfile"
)

for file in "${FILES_TO_CHECK[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file ${RED}MISSING${NC}"
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""

# Check scripts
echo -e "${YELLOW}Checking deployment scripts...${NC}"

SCRIPTS=(
    "scripts/minikube/setup-minikube.sh"
    "scripts/kafka/install-kafka.sh"
    "scripts/dapr/install-dapr.sh"
)

for script in "${SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        if [ -x "$script" ]; then
            echo -e "${GREEN}✓${NC} $script (executable)"
        else
            echo -e "${YELLOW}⚠${NC} $script (not executable, will chmod)"
            chmod +x "$script"
        fi
    else
        echo -e "${RED}✗${NC} $script ${RED}MISSING${NC}"
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""

# Check system resources
echo -e "${YELLOW}Checking system resources...${NC}"

# Check available memory (Linux/macOS)
if command -v free &> /dev/null; then
    TOTAL_MEM=$(free -g | awk '/^Mem:/{print $2}')
    if [ "$TOTAL_MEM" -ge 8 ]; then
        echo -e "${GREEN}✓ RAM: ${TOTAL_MEM}GB (sufficient)${NC}"
    else
        echo -e "${YELLOW}⚠ RAM: ${TOTAL_MEM}GB (8GB recommended)${NC}"
    fi
elif command -v sysctl &> /dev/null; then
    TOTAL_MEM=$(($(sysctl -n hw.memsize 2>/dev/null || echo 0) / 1024 / 1024 / 1024))
    if [ "$TOTAL_MEM" -ge 8 ]; then
        echo -e "${GREEN}✓ RAM: ${TOTAL_MEM}GB (sufficient)${NC}"
    else
        echo -e "${YELLOW}⚠ RAM: ${TOTAL_MEM}GB (8GB recommended)${NC}"
    fi
fi

# Check CPU cores
if command -v nproc &> /dev/null; then
    CPU_CORES=$(nproc)
elif command -v sysctl &> /dev/null; then
    CPU_CORES=$(sysctl -n hw.ncpu 2>/dev/null || echo "unknown")
else
    CPU_CORES="unknown"
fi

if [ "$CPU_CORES" != "unknown" ] && [ "$CPU_CORES" -ge 4 ]; then
    echo -e "${GREEN}✓ CPU cores: $CPU_CORES (sufficient)${NC}"
elif [ "$CPU_CORES" != "unknown" ]; then
    echo -e "${YELLOW}⚠ CPU cores: $CPU_CORES (4 recommended)${NC}"
else
    echo -e "${YELLOW}⚠ CPU cores: unknown${NC}"
fi

# Check disk space
DISK_SPACE=$(df -h . | awk 'NR==2 {print $4}')
echo -e "${GREEN}✓ Available disk space: $DISK_SPACE${NC}"

echo ""

# Check if Minikube is already running
if command -v minikube &> /dev/null; then
    if minikube status &> /dev/null; then
        echo -e "${YELLOW}⚠ Minikube is already running${NC}"
        echo "  Current status:"
        minikube status | sed 's/^/  /'
        echo ""
        echo -e "${YELLOW}  Options:${NC}"
        echo "    1. Continue with existing cluster: ./scripts/minikube/setup-minikube.sh"
        echo "    2. Delete and recreate: minikube delete && ./scripts/minikube/setup-minikube.sh"
    else
        echo -e "${GREEN}✓ Minikube is not running (ready for fresh start)${NC}"
    fi
fi

echo ""

# Summary
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    Verification Summary                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! Ready to deploy.${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "  1. Set GROQ_API_KEY (if not set):"
    echo "     ${YELLOW}export GROQ_API_KEY='your-api-key'${NC}"
    echo ""
    echo "  2. Run the deployment script:"
    echo "     ${YELLOW}./scripts/minikube/setup-minikube.sh${NC}"
    echo ""
    echo "  3. Wait 10-15 minutes for deployment to complete"
    echo ""
    echo "  4. Access your application:"
    echo "     ${GREEN}http://todoboard.local${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Found $ERRORS error(s). Please fix them before deploying.${NC}"
    echo ""
    exit 1
fi
