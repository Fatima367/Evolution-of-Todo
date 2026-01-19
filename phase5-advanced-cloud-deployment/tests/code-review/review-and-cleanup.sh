#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}TodoBoard Code Review & Cleanup${NC}"
echo -e "${GREEN}========================================${NC}"

# Configuration
RESULTS_DIR="./code-review-results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$RESULTS_DIR/code-review-$TIMESTAMP.log"
PROJECT_ROOT="/mnt/d/Documents/Hackathons/Evolution-of-Todo/phase5-advanced-cloud-deployment"

# Create results directory
mkdir -p "$RESULTS_DIR"

# Logging function
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

# Track review results
ISSUES_FOUND=0
WARNINGS_FOUND=0
SUGGESTIONS=0

log "${BLUE}Starting code review at $(date)${NC}"
log "Project root: $PROJECT_ROOT"
log ""

# Review 1: Check for unused imports (Python)
review_python_imports() {
    log "${GREEN}========================================${NC}"
    log "${GREEN}Review 1: Python Unused Imports${NC}"
    log "${GREEN}========================================${NC}"

    if command -v autoflake &> /dev/null; then
        log "${YELLOW}Checking for unused imports in Python files...${NC}"

        UNUSED_IMPORTS=$(find "$PROJECT_ROOT" -name "*.py" -not -path "*/.*" -not -path "*/node_modules/*" -exec autoflake --check --remove-all-unused-imports {} \; 2>&1 | grep -c "would be reformatted" || echo "0")

        if [ "$UNUSED_IMPORTS" -gt 0 ]; then
            log "${YELLOW}⚠ Found $UNUSED_IMPORTS files with unused imports${NC}"
            ((WARNINGS_FOUND++))
            log "Run: autoflake --remove-all-unused-imports --in-place --recursive $PROJECT_ROOT"
        else
            log "${GREEN}✓ No unused imports found${NC}"
        fi
    else
        log "${YELLOW}⚠ autoflake not installed, skipping unused imports check${NC}"
        log "Install with: pip install autoflake"
    fi
    log ""
}

# Review 2: Check for dead code (Python)
review_dead_code() {
    log "${GREEN}========================================${NC}"
    log "${GREEN}Review 2: Dead Code Detection${NC}"
    log "${GREEN}========================================${NC}"

    if command -v vulture &> /dev/null; then
        log "${YELLOW}Checking for dead code in Python files...${NC}"

        cd "$PROJECT_ROOT" || exit 1
        DEAD_CODE=$(vulture backend/src --min-confidence 80 2>&1 | grep -c "unused" || echo "0")

        if [ "$DEAD_CODE" -gt 0 ]; then
            log "${YELLOW}⚠ Found potential dead code (confidence 80%+)${NC}"
            ((WARNINGS_FOUND++))
            vulture backend/src --min-confidence 80 | head -20 | tee -a "$LOG_FILE"
        else
            log "${GREEN}✓ No obvious dead code found${NC}"
        fi
    else
        log "${YELLOW}⚠ vulture not installed, skipping dead code check${NC}"
        log "Install with: pip install vulture"
    fi
    log ""
}

# Review 3: Check error handling consistency
review_error_handling() {
    log "${GREEN}========================================${NC}"
    log "${GREEN}Review 3: Error Handling Consistency${NC}"
    log "${GREEN}========================================${NC}"

    log "${YELLOW}Checking for bare except clauses...${NC}"
    BARE_EXCEPT=$(grep -r "except:" "$PROJECT_ROOT/backend/src" --include="*.py" 2>/dev/null | wc -l)

    if [ "$BARE_EXCEPT" -gt 0 ]; then
        log "${RED}✗ Found $BARE_EXCEPT bare except clauses${NC}"
        ((ISSUES_FOUND++))
        grep -rn "except:" "$PROJECT_ROOT/backend/src" --include="*.py" | head -10 | tee -a "$LOG_FILE"
        log "Replace with specific exception types"
    else
        log "${GREEN}✓ No bare except clauses found${NC}"
    fi

    log ""
    log "${YELLOW}Checking for proper exception logging...${NC}"
    EXCEPTION_WITHOUT_LOG=$(grep -r "except.*:" "$PROJECT_ROOT/backend/src" --include="*.py" -A 3 | grep -v "logger\|logging\|log\." | grep -c "except" || echo "0")

    if [ "$EXCEPTION_WITHOUT_LOG" -gt 5 ]; then
        log "${YELLOW}⚠ Some exceptions may not be properly logged${NC}"
        ((WARNINGS_FOUND++))
    else
        log "${GREEN}✓ Exception logging appears consistent${NC}"
    fi
    log ""
}

# Review 4: Check logging consistency
review_logging() {
    log "${GREEN}========================================${NC}"
    log "${GREEN}Review 4: Logging Consistency${NC}"
    log "${GREEN}========================================${NC}"

    log "${YELLOW}Checking for print statements (should use logger)...${NC}"
    PRINT_STATEMENTS=$(grep -r "print(" "$PROJECT_ROOT/backend/src" --include="*.py" 2>/dev/null | grep -v "# print" | wc -l)

    if [ "$PRINT_STATEMENTS" -gt 0 ]; then
        log "${YELLOW}⚠ Found $PRINT_STATEMENTS print statements${NC}"
        ((WARNINGS_FOUND++))
        grep -rn "print(" "$PROJECT_ROOT/backend/src" --include="*.py" | grep -v "# print" | head -10 | tee -a "$LOG_FILE"
        log "Consider using logger instead of print"
    else
        log "${GREEN}✓ No print statements found${NC}"
    fi

    log ""
    log "${YELLOW}Checking for consistent logger usage...${NC}"
    FILES_WITH_LOGGER=$(grep -rl "import logging\|from logging" "$PROJECT_ROOT/backend/src" --include="*.py" 2>/dev/null | wc -l)
    log "Files using logging: $FILES_WITH_LOGGER"
    log "${GREEN}✓ Logging module is being used${NC}"
    log ""
}

# Review 5: Security best practices
review_security() {
    log "${GREEN}========================================${NC}"
    log "${GREEN}Review 5: Security Best Practices${NC}"
    log "${GREEN}========================================${NC}"

    log "${YELLOW}Checking for hardcoded secrets...${NC}"
    POTENTIAL_SECRETS=$(grep -rE "(password|secret|api_key|token).*=.*['\"]" "$PROJECT_ROOT/backend/src" --include="*.py" | grep -v "os.getenv\|os.environ\|config\." | wc -l)

    if [ "$POTENTIAL_SECRETS" -gt 0 ]; then
        log "${RED}✗ Found potential hardcoded secrets${NC}"
        ((ISSUES_FOUND++))
        grep -rnE "(password|secret|api_key|token).*=.*['\"]" "$PROJECT_ROOT/backend/src" --include="*.py" | grep -v "os.getenv\|os.environ\|config\." | head -10 | tee -a "$LOG_FILE"
    else
        log "${GREEN}✓ No obvious hardcoded secrets found${NC}"
    fi

    log ""
    log "${YELLOW}Checking for SQL injection vulnerabilities...${NC}"
    SQL_CONCAT=$(grep -rE "execute.*\+.*|execute.*%.*|execute.*f\"" "$PROJECT_ROOT/backend/src" --include="*.py" 2>/dev/null | wc -l)

    if [ "$SQL_CONCAT" -gt 0 ]; then
        log "${RED}✗ Found potential SQL injection vulnerabilities${NC}"
        ((ISSUES_FOUND++))
        grep -rnE "execute.*\+.*|execute.*%.*|execute.*f\"" "$PROJECT_ROOT/backend/src" --include="*.py" | head -10 | tee -a "$LOG_FILE"
    else
        log "${GREEN}✓ No obvious SQL injection vulnerabilities${NC}"
    fi

    log ""
    log "${YELLOW}Checking for eval/exec usage...${NC}"
    EVAL_USAGE=$(grep -rE "\beval\(|\bexec\(" "$PROJECT_ROOT/backend/src" --include="*.py" 2>/dev/null | wc -l)

    if [ "$EVAL_USAGE" -gt 0 ]; then
        log "${RED}✗ Found eval/exec usage (security risk)${NC}"
        ((ISSUES_FOUND++))
        grep -rnE "\beval\(|\bexec\(" "$PROJECT_ROOT/backend/src" --include="*.py" | tee -a "$LOG_FILE"
    else
        log "${GREEN}✓ No eval/exec usage found${NC}"
    fi
    log ""
}

# Review 6: Code style consistency
review_code_style() {
    log "${GREEN}========================================${NC}"
    log "${GREEN}Review 6: Code Style Consistency${NC}"
    log "${GREEN}========================================${NC}"

    if command -v black &> /dev/null; then
        log "${YELLOW}Checking Python code formatting with black...${NC}"
        cd "$PROJECT_ROOT" || exit 1

        if black --check backend/src 2>&1 | grep -q "would be reformatted"; then
            log "${YELLOW}⚠ Some files need formatting${NC}"
            ((WARNINGS_FOUND++))
            log "Run: black backend/src"
        else
            log "${GREEN}✓ Python code is properly formatted${NC}"
        fi
    else
        log "${YELLOW}⚠ black not installed, skipping formatting check${NC}"
        log "Install with: pip install black"
    fi

    log ""
    if command -v eslint &> /dev/null; then
        log "${YELLOW}Checking TypeScript/JavaScript code style...${NC}"
        cd "$PROJECT_ROOT/frontend" || exit 1

        if npm run lint 2>&1 | grep -q "error\|warning"; then
            log "${YELLOW}⚠ ESLint found issues${NC}"
            ((WARNINGS_FOUND++))
            log "Run: npm run lint --fix"
        else
            log "${GREEN}✓ TypeScript/JavaScript code passes linting${NC}"
        fi
    else
        log "${YELLOW}⚠ eslint not available, skipping frontend linting${NC}"
    fi
    log ""
}

# Review 7: Documentation completeness
review_documentation() {
    log "${GREEN}========================================${NC}"
    log "${GREEN}Review 7: Documentation Completeness${NC}"
    log "${GREEN}========================================${NC}"

    log "${YELLOW}Checking for README files...${NC}"
    README_COUNT=$(find "$PROJECT_ROOT" -maxdepth 3 -name "README.md" | wc -l)
    log "README files found: $README_COUNT"

    if [ "$README_COUNT" -ge 2 ]; then
        log "${GREEN}✓ Multiple README files present${NC}"
    else
        log "${YELLOW}⚠ Consider adding more README files${NC}"
        ((SUGGESTIONS++))
    fi

    log ""
    log "${YELLOW}Checking for docstrings in Python modules...${NC}"
    MODULES_WITHOUT_DOCSTRING=$(find "$PROJECT_ROOT/backend/src" -name "*.py" -exec grep -L '"""' {} \; 2>/dev/null | wc -l)

    if [ "$MODULES_WITHOUT_DOCSTRING" -gt 5 ]; then
        log "${YELLOW}⚠ $MODULES_WITHOUT_DOCSTRING Python files lack docstrings${NC}"
        ((SUGGESTIONS++))
    else
        log "${GREEN}✓ Most Python files have docstrings${NC}"
    fi
    log ""
}

# Review 8: Dependency security
review_dependencies() {
    log "${GREEN}========================================${NC}"
    log "${GREEN}Review 8: Dependency Security${NC}"
    log "${GREEN}========================================${NC}"

    log "${YELLOW}Checking Python dependencies for vulnerabilities...${NC}"
    cd "$PROJECT_ROOT/backend" || exit 1

    if command -v safety &> /dev/null; then
        if safety check --json > "$RESULTS_DIR/safety-report.json" 2>&1; then
            log "${GREEN}✓ No known vulnerabilities in Python dependencies${NC}"
        else
            VULN_COUNT=$(jq length "$RESULTS_DIR/safety-report.json" 2>/dev/null || echo "unknown")
            log "${RED}✗ Found vulnerabilities in Python dependencies${NC}"
            ((ISSUES_FOUND++))
            log "See: $RESULTS_DIR/safety-report.json"
        fi
    else
        log "${YELLOW}⚠ safety not installed, skipping Python dependency check${NC}"
        log "Install with: pip install safety"
    fi

    log ""
    log "${YELLOW}Checking Node.js dependencies for vulnerabilities...${NC}"
    cd "$PROJECT_ROOT/frontend" || exit 1

    if npm audit --json > "$RESULTS_DIR/npm-audit.json" 2>&1; then
        VULN_COUNT=$(jq '.metadata.vulnerabilities.total' "$RESULTS_DIR/npm-audit.json" 2>/dev/null || echo "0")
        if [ "$VULN_COUNT" -eq 0 ]; then
            log "${GREEN}✓ No known vulnerabilities in Node.js dependencies${NC}"
        else
            log "${YELLOW}⚠ Found $VULN_COUNT vulnerabilities in Node.js dependencies${NC}"
            ((WARNINGS_FOUND++))
            log "Run: npm audit fix"
        fi
    fi
    log ""
}

# Review 9: Test coverage
review_test_coverage() {
    log "${GREEN}========================================${NC}"
    log "${GREEN}Review 9: Test Coverage${NC}"
    log "${GREEN}========================================${NC}"

    log "${YELLOW}Checking for test files...${NC}"
    BACKEND_TESTS=$(find "$PROJECT_ROOT/backend/tests" -name "test_*.py" 2>/dev/null | wc -l)
    FRONTEND_TESTS=$(find "$PROJECT_ROOT/frontend" -name "*.test.ts" -o -name "*.test.tsx" -o -name "*.spec.ts" 2>/dev/null | wc -l)

    log "Backend test files: $BACKEND_TESTS"
    log "Frontend test files: $FRONTEND_TESTS"

    if [ "$BACKEND_TESTS" -gt 10 ]; then
        log "${GREEN}✓ Good backend test coverage${NC}"
    else
        log "${YELLOW}⚠ Consider adding more backend tests${NC}"
        ((SUGGESTIONS++))
    fi

    if [ "$FRONTEND_TESTS" -gt 5 ]; then
        log "${GREEN}✓ Good frontend test coverage${NC}"
    else
        log "${YELLOW}⚠ Consider adding more frontend tests${NC}"
        ((SUGGESTIONS++))
    fi
    log ""
}

# Review 10: Configuration management
review_configuration() {
    log "${GREEN}========================================${NC}"
    log "${GREEN}Review 10: Configuration Management${NC}"
    log "${GREEN}========================================${NC}"

    log "${YELLOW}Checking for .env.example files...${NC}"
    ENV_EXAMPLES=$(find "$PROJECT_ROOT" -name ".env.example" | wc -l)

    if [ "$ENV_EXAMPLES" -ge 1 ]; then
        log "${GREEN}✓ .env.example files present${NC}"
    else
        log "${YELLOW}⚠ No .env.example files found${NC}"
        ((SUGGESTIONS++))
    fi

    log ""
    log "${YELLOW}Checking for .env files in git...${NC}"
    if git ls-files "$PROJECT_ROOT" | grep -q "\.env$"; then
        log "${RED}✗ .env files are tracked in git (security risk)${NC}"
        ((ISSUES_FOUND++))
    else
        log "${GREEN}✓ .env files are not tracked in git${NC}"
    fi
    log ""
}

# Run all reviews
run_all_reviews() {
    review_python_imports
    review_dead_code
    review_error_handling
    review_logging
    review_security
    review_code_style
    review_documentation
    review_dependencies
    review_test_coverage
    review_configuration
}

# Generate summary
generate_summary() {
    log "${GREEN}========================================${NC}"
    log "${GREEN}Code Review Summary${NC}"
    log "${GREEN}========================================${NC}"
    log "Critical Issues: ${RED}$ISSUES_FOUND${NC}"
    log "Warnings: ${YELLOW}$WARNINGS_FOUND${NC}"
    log "Suggestions: ${BLUE}$SUGGESTIONS${NC}"
    log ""
    log "Log file: $LOG_FILE"
    log ""

    if [ "$ISSUES_FOUND" -eq 0 ] && [ "$WARNINGS_FOUND" -eq 0 ]; then
        log "${GREEN}========================================${NC}"
        log "${GREEN}Code review passed! ✓${NC}"
        log "${GREEN}Code is clean and production-ready${NC}"
        log "${GREEN}========================================${NC}"
        return 0
    elif [ "$ISSUES_FOUND" -eq 0 ]; then
        log "${YELLOW}========================================${NC}"
        log "${YELLOW}Code review passed with warnings${NC}"
        log "${YELLOW}Consider addressing warnings before production${NC}"
        log "${YELLOW}========================================${NC}"
        return 0
    else
        log "${RED}========================================${NC}"
        log "${RED}Code review found critical issues${NC}"
        log "${RED}Please address issues before production${NC}"
        log "${RED}========================================${NC}"
        return 1
    fi
}

# Main execution
cd "$PROJECT_ROOT" || exit 1
run_all_reviews
generate_summary
