#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}TodoBoard Load Testing Suite${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if k6 is installed
if ! command -v k6 &> /dev/null; then
    echo -e "${RED}Error: k6 is not installed${NC}"
    echo "Please install k6: https://k6.io/docs/getting-started/installation/"
    echo ""
    echo "Quick install options:"
    echo "  macOS: brew install k6"
    echo "  Linux: sudo apt-get install k6"
    echo "  Windows: choco install k6"
    exit 1
fi

# Configuration
BASE_URL="${BASE_URL:-http://todoboard.local/api}"
WS_URL="${WS_URL:-ws://todoboard.local/ws}"
RESULTS_DIR="./test-results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create results directory
mkdir -p "$RESULTS_DIR"

echo -e "${BLUE}Configuration:${NC}"
echo "  Base URL: $BASE_URL"
echo "  WebSocket URL: $WS_URL"
echo "  Results directory: $RESULTS_DIR"
echo ""

# Check if application is accessible
echo -e "${YELLOW}Checking application availability...${NC}"
if ! curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/health" | grep -q "200"; then
    echo -e "${RED}Error: Application is not accessible at $BASE_URL${NC}"
    echo "Please ensure the application is running and accessible"
    exit 1
fi
echo -e "${GREEN}✓ Application is accessible${NC}"
echo ""

# Run load test
echo -e "${GREEN}Starting load test with 1000 concurrent users...${NC}"
echo -e "${YELLOW}This will take approximately 22 minutes${NC}"
echo ""

k6 run \
    --out json="$RESULTS_DIR/load-test-$TIMESTAMP.json" \
    --summary-export="$RESULTS_DIR/summary-$TIMESTAMP.json" \
    -e BASE_URL="$BASE_URL" \
    -e WS_URL="$WS_URL" \
    ./k6-load-test.js

# Check test results
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Load Test Results${NC}"
echo -e "${GREEN}========================================${NC}"

# Parse results and check thresholds
SUMMARY_FILE="$RESULTS_DIR/summary-$TIMESTAMP.json"

if [ -f "$SUMMARY_FILE" ]; then
    echo -e "${BLUE}Performance Metrics:${NC}"

    # Extract key metrics using jq if available
    if command -v jq &> /dev/null; then
        API_P95=$(jq -r '.metrics.http_req_duration.values["p(95)"]' "$SUMMARY_FILE" 2>/dev/null || echo "N/A")
        SEARCH_P95=$(jq -r '.metrics."http_req_duration{type:search}".values["p(95)"]' "$SUMMARY_FILE" 2>/dev/null || echo "N/A")
        ERROR_RATE=$(jq -r '.metrics.http_req_failed.values.rate' "$SUMMARY_FILE" 2>/dev/null || echo "N/A")
        TOTAL_REQUESTS=$(jq -r '.metrics.http_reqs.values.count' "$SUMMARY_FILE" 2>/dev/null || echo "N/A")

        echo "  API Response Time (p95): ${API_P95}ms"
        echo "  Search Response Time (p95): ${SEARCH_P95}ms"
        echo "  Error Rate: $(echo "$ERROR_RATE * 100" | bc 2>/dev/null || echo "$ERROR_RATE")%"
        echo "  Total Requests: $TOTAL_REQUESTS"
        echo ""

        # Check if thresholds are met
        THRESHOLDS_MET=true

        if [ "$API_P95" != "N/A" ] && [ "$(echo "$API_P95 > 500" | bc -l 2>/dev/null)" = "1" ]; then
            echo -e "${RED}✗ API p95 response time exceeds 500ms threshold${NC}"
            THRESHOLDS_MET=false
        else
            echo -e "${GREEN}✓ API p95 response time meets <500ms threshold${NC}"
        fi

        if [ "$SEARCH_P95" != "N/A" ] && [ "$(echo "$SEARCH_P95 > 1000" | bc -l 2>/dev/null)" = "1" ]; then
            echo -e "${RED}✗ Search p95 response time exceeds 1000ms threshold${NC}"
            THRESHOLDS_MET=false
        else
            echo -e "${GREEN}✓ Search p95 response time meets <1s threshold${NC}"
        fi

        if [ "$ERROR_RATE" != "N/A" ] && [ "$(echo "$ERROR_RATE > 0.05" | bc -l 2>/dev/null)" = "1" ]; then
            echo -e "${RED}✗ Error rate exceeds 5% threshold${NC}"
            THRESHOLDS_MET=false
        else
            echo -e "${GREEN}✓ Error rate meets <5% threshold${NC}"
        fi

        echo ""

        if [ "$THRESHOLDS_MET" = true ]; then
            echo -e "${GREEN}========================================${NC}"
            echo -e "${GREEN}All performance thresholds met! ✓${NC}"
            echo -e "${GREEN}========================================${NC}"
        else
            echo -e "${RED}========================================${NC}"
            echo -e "${RED}Some performance thresholds not met${NC}"
            echo -e "${RED}========================================${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}Install jq for detailed metrics analysis${NC}"
        echo "Results saved to: $SUMMARY_FILE"
    fi
else
    echo -e "${YELLOW}Summary file not found${NC}"
fi

echo ""
echo "Results saved to:"
echo "  - JSON: $RESULTS_DIR/load-test-$TIMESTAMP.json"
echo "  - Summary: $RESULTS_DIR/summary-$TIMESTAMP.json"
echo ""
echo "To view detailed results:"
echo "  cat $SUMMARY_FILE | jq ."
echo ""
