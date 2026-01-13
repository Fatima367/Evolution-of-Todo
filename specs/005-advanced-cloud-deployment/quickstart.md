# TodoBoard Local Development Quickstart

This guide will help you set up and run the complete TodoBoard application stack locally on Minikube.

## Prerequisites

- **Docker Desktop**: [Install Docker](https://docs.docker.com/get-docker/)
- **Minikube**: [Install Minikube](https://minikube.sigs.k8s.io/docs/start/)
- **kubectl**: [Install kubectl](https://kubernetes.io/docs/tasks/tools/)
- **Helm**: [Install Helm](https://helm.sh/docs/intro/install/)

### System Requirements

- **CPU**: 4 cores minimum
- **Memory**: 8GB RAM minimum
- **Disk**: 20GB free space

## Quick Start

### 1. Set Up Minikube
```bash
chmod +x scripts/local/*.sh
./scripts/local/setup-minikube.sh
```

### 2. Install Dapr
```bash
./scripts/local/install-dapr.sh
```

### 3. Install Kafka
```bash
./scripts/local/install-kafka.sh
```

### 4. Deploy the Application
```bash
./scripts/local/deploy-local.sh
```

### 5. Access the Application
```bash
minikube tunnel  # In separate terminal
```

Open browser to: http://todoboard.local

## Cleanup
```bash
./scripts/local/teardown-local.sh
```
