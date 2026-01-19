#!/bin/bash
# Security audit script for Phase V - Advanced Cloud Deployment
# This script runs security audits on all dependencies

set -e

echo "=========================================="
echo "Security Audit for TodoBoard Application"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track overall status
VULNERABILITIES_FOUND=0

# Function to print section header
print_section() {
    echo ""
    echo "=========================================="
    echo "$1"
    echo "=========================================="
    echo ""
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 1. Python Backend Security Audit
print_section "1. Python Backend Dependencies (safety)"

cd backend

if command_exists safety; then
    echo "Running safety check on Python dependencies..."
    if safety check --file requirements.txt --json > safety-report.json 2>&1; then
        echo -e "${GREEN}✓ No known vulnerabilities found in Python dependencies${NC}"
    else
        echo -e "${RED}✗ Vulnerabilities found in Python dependencies${NC}"
        echo "See safety-report.json for details"
        VULNERABILITIES_FOUND=1

        # Show summary
        if [ -f safety-report.json ]; then
            echo ""
            echo "Summary of vulnerabilities:"
            cat safety-report.json | grep -E "(package|vulnerability)" || true
        fi
    fi
else
    echo -e "${YELLOW}⚠ safety not installed. Installing...${NC}"
    pip install safety
    safety check --file requirements.txt
fi

cd ..

# 2. Frontend Dependencies Security Audit
print_section "2. Frontend Dependencies (npm audit)"

cd frontend

if command_exists npm; then
    echo "Running npm audit on frontend dependencies..."

    # Run npm audit and capture output
    if npm audit --json > npm-audit-report.json 2>&1; then
        echo -e "${GREEN}✓ No vulnerabilities found in npm dependencies${NC}"
    else
        AUDIT_EXIT_CODE=$?

        # npm audit returns non-zero if vulnerabilities found
        if [ $AUDIT_EXIT_CODE -ne 0 ]; then
            echo -e "${RED}✗ Vulnerabilities found in npm dependencies${NC}"
            echo "See npm-audit-report.json for details"
            VULNERABILITIES_FOUND=1

            # Show summary
            echo ""
            echo "Summary:"
            npm audit || true

            echo ""
            echo -e "${YELLOW}To fix vulnerabilities, run:${NC}"
            echo "  npm audit fix"
            echo "  npm audit fix --force  (for breaking changes)"
        fi
    fi
else
    echo -e "${RED}✗ npm not found. Please install Node.js and npm${NC}"
    VULNERABILITIES_FOUND=1
fi

cd ..

# 3. Docker Image Security Scan (if Trivy is available)
print_section "3. Docker Image Security Scan (trivy)"

if command_exists trivy; then
    echo "Scanning Docker images for vulnerabilities..."

    # Scan backend image
    if [ -f backend/Dockerfile ]; then
        echo "Scanning backend Docker image..."
        trivy image --severity HIGH,CRITICAL todoboard-backend:latest || true
    fi

    # Scan frontend image
    if [ -f frontend/Dockerfile ]; then
        echo "Scanning frontend Docker image..."
        trivy image --severity HIGH,CRITICAL todoboard-frontend:latest || true
    fi
else
    echo -e "${YELLOW}⚠ trivy not installed. Skipping Docker image scan${NC}"
    echo "To install trivy: https://aquasecurity.github.io/trivy/latest/getting-started/installation/"
fi

# 4. Check for common security issues
print_section "4. Security Configuration Checks"

echo "Checking for common security issues..."

# Check for exposed secrets in .env files
echo ""
echo "Checking for .env files in git..."
if git ls-files | grep -E "\.env$" > /dev/null 2>&1; then
    echo -e "${RED}✗ .env files found in git repository${NC}"
    git ls-files | grep -E "\.env$"
    VULNERABILITIES_FOUND=1
else
    echo -e "${GREEN}✓ No .env files in git repository${NC}"
fi

# Check for hardcoded secrets
echo ""
echo "Checking for potential hardcoded secrets..."
if git grep -E "(password|secret|api_key|token)\s*=\s*['\"][^'\"]{8,}" -- "*.py" "*.ts" "*.tsx" "*.js" "*.jsx" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠ Potential hardcoded secrets found${NC}"
    echo "Review the following files:"
    git grep -l -E "(password|secret|api_key|token)\s*=\s*['\"][^'\"]{8,}" -- "*.py" "*.ts" "*.tsx" "*.js" "*.jsx" || true
else
    echo -e "${GREEN}✓ No obvious hardcoded secrets found${NC}"
fi

# Check for CORS wildcard in production
echo ""
echo "Checking CORS configuration..."
if grep -r "allow_origins.*\*" backend/src/ > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠ Wildcard CORS origin found in code${NC}"
    echo "Ensure this is not used in production"
else
    echo -e "${GREEN}✓ No wildcard CORS origins in code${NC}"
fi

# 5. Summary
print_section "Security Audit Summary"

if [ $VULNERABILITIES_FOUND -eq 0 ]; then
    echo -e "${GREEN}✓ Security audit completed successfully${NC}"
    echo "No critical vulnerabilities found"
    exit 0
else
    echo -e "${RED}✗ Security audit found issues${NC}"
    echo "Please review the reports and fix vulnerabilities"
    echo ""
    echo "Reports generated:"
    echo "  - backend/safety-report.json (Python dependencies)"
    echo "  - frontend/npm-audit-report.json (npm dependencies)"
    exit 1
fi
