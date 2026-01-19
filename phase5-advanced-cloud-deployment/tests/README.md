# TodoBoard Testing Infrastructure

This directory contains comprehensive testing and validation tools for the TodoBoard Phase 5 Advanced Cloud Deployment.

## Directory Structure

```
tests/
├── load-testing/           # Performance and load testing
│   ├── k6-load-test.js    # K6 load test script
│   └── run-load-test.sh   # Load test runner
├── chaos-testing/          # Failure scenario testing
│   └── failure-scenarios.sh
├── validation/             # Quickstart and deployment validation
│   └── validate-quickstart.sh
├── code-review/            # Code quality and security review
│   └── review-and-cleanup.sh
└── README.md              # This file
```

## Test Suites

### 1. Load Testing (T148)

Tests application performance with 1000 concurrent users.

**Prerequisites:**
- K6 installed: https://k6.io/docs/getting-started/installation/
- Application deployed and accessible

**Run:**
```bash
cd tests/load-testing
chmod +x run-load-test.sh
./run-load-test.sh
```

**Validates:**
- ✓ API response time <500ms p95
- ✓ Search performance <1s for 10,000 tasks
- ✓ Real-time updates <2s latency
- ✓ Event processing 1,000+ events/minute

**Results:**
- JSON report: `test-results/load-test-<timestamp>.json`
- Summary: `test-results/summary-<timestamp>.json`

### 2. Chaos Testing (T149)

Tests system resilience under failure conditions.

**Prerequisites:**
- Kubernetes cluster running
- Application deployed
- kubectl configured

**Run:**
```bash
cd tests/chaos-testing
chmod +x failure-scenarios.sh
./failure-scenarios.sh
```

**Test Scenarios:**
1. **Pod Crash Recovery**: Kill random pods, verify auto-recovery
2. **Multiple Pod Failures**: Kill 3 pods simultaneously
3. **Network Partition**: Simulate network issues
4. **Database Connection Failure**: Test connection pooling resilience
5. **Resource Exhaustion**: Verify HPA scaling
6. **Kafka Consumer Rebalancing**: Test event processing recovery

**Results:**
- Log file: `chaos-test-results/chaos-test-<timestamp>.log`

### 3. Quickstart Validation (T147)

Validates the quickstart guide by checking all prerequisites and deployment steps.

**Prerequisites:**
- None (validates prerequisites as part of the test)

**Run:**
```bash
cd tests/validation
chmod +x validate-quickstart.sh
./validate-quickstart.sh
```

**Validates:**
- ✓ Prerequisites installed (Docker, Minikube, kubectl, Helm)
- ✓ System requirements met (CPU, Memory, Disk)
- ✓ Minikube configuration
- ✓ Dapr installation
- ✓ Kafka installation
- ✓ Application deployment
- ✓ Application accessibility
- ✓ Documentation completeness

**Results:**
- Log file: `validation-results/quickstart-validation-<timestamp>.log`

### 4. Code Review & Cleanup (T150)

Performs comprehensive code quality and security review.

**Prerequisites:**
- Python tools: `pip install autoflake vulture safety black`
- Node.js tools: `npm install -g eslint`

**Run:**
```bash
cd tests/code-review
chmod +x review-and-cleanup.sh
./review-and-cleanup.sh
```

**Reviews:**
1. **Unused Imports**: Detect unused Python imports
2. **Dead Code**: Find unreachable code
3. **Error Handling**: Check exception handling consistency
4. **Logging**: Verify proper logging usage
5. **Security**: Scan for hardcoded secrets, SQL injection, eval/exec
6. **Code Style**: Check formatting (black, eslint)
7. **Documentation**: Verify README and docstrings
8. **Dependencies**: Security audit (safety, npm audit)
9. **Test Coverage**: Check test file count
10. **Configuration**: Verify .env management

**Results:**
- Log file: `code-review-results/code-review-<timestamp>.log`
- Safety report: `code-review-results/safety-report.json`
- NPM audit: `code-review-results/npm-audit.json`

## Running All Tests

To run all test suites in sequence:

```bash
#!/bin/bash
set -e

echo "Running all TodoBoard tests..."

# 1. Quickstart validation
echo "1. Validating quickstart guide..."
cd tests/validation
./validate-quickstart.sh

# 2. Code review
echo "2. Running code review..."
cd ../code-review
./review-and-cleanup.sh

# 3. Load testing
echo "3. Running load tests..."
cd ../load-testing
./run-load-test.sh

# 4. Chaos testing
echo "4. Running chaos tests..."
cd ../chaos-testing
./failure-scenarios.sh

echo "All tests completed!"
```

## Performance Targets

### API Performance
- **p50 latency**: <200ms
- **p95 latency**: <500ms
- **p99 latency**: <1000ms
- **Error rate**: <5%

### Search Performance
- **p95 latency**: <1s for 10,000 tasks
- **Full-text search**: <500ms

### Real-time Updates
- **WebSocket latency**: <2s
- **Event propagation**: <3s end-to-end

### Event Processing
- **Throughput**: 1,000+ events/minute
- **Kafka lag**: <10s

### Scalability
- **Concurrent users**: 1,000+
- **Auto-scaling**: 3-10 pods based on load
- **Recovery time**: <60s for pod failures

## Continuous Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup Minikube
        run: |
          minikube start
          ./scripts/local/setup-minikube.sh

      - name: Deploy Application
        run: ./scripts/local/deploy-local.sh

      - name: Run Tests
        run: |
          cd tests
          ./validation/validate-quickstart.sh
          ./code-review/review-and-cleanup.sh
          ./load-testing/run-load-test.sh
          ./chaos-testing/failure-scenarios.sh
```

## Troubleshooting

### Load Testing Issues

**Problem**: K6 not found
```bash
# macOS
brew install k6

# Linux
sudo apt-get install k6

# Windows
choco install k6
```

**Problem**: Application not accessible
```bash
# Check if minikube tunnel is running
minikube tunnel

# Verify ingress
kubectl get ingress -n todoboard
```

### Chaos Testing Issues

**Problem**: Insufficient permissions
```bash
# Ensure kubectl has proper permissions
kubectl auth can-i delete pods -n todoboard
```

**Problem**: Pods not recovering
```bash
# Check deployment status
kubectl get deployments -n todoboard
kubectl describe deployment <deployment-name> -n todoboard
```

### Code Review Issues

**Problem**: Tools not installed
```bash
# Install Python tools
pip install autoflake vulture safety black

# Install Node.js tools
npm install -g eslint
```

## Best Practices

1. **Run tests regularly**: Before each deployment
2. **Monitor results**: Track performance trends over time
3. **Fix issues promptly**: Address critical issues before production
4. **Update tests**: Keep tests in sync with application changes
5. **Document failures**: Log and analyze test failures

## Support

For issues or questions:
- Check test logs in respective `*-results/` directories
- Review application logs: `kubectl logs -n todoboard <pod-name>`
- Check Kubernetes events: `kubectl get events -n todoboard`

## License

MIT License - See LICENSE file for details
