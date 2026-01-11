# Phase IV: Local Kubernetes Deployment

This directory contains the Kubernetes deployment configuration for the TodoBoard application, enabling local development and testing in a containerized, orchestrated environment.

## Overview

Phase IV implements local Kubernetes deployment using:
- **Docker**: Container runtime for packaging applications
- **Minikube**: Local Kubernetes cluster for development
- **Helm**: Package manager for Kubernetes resources
- **kubectl**: Command-line tool for cluster management

## Quick Start

### Prerequisites

- Docker Desktop 4.25+
- Minikube 1.32+
- kubectl 1.28+
- Helm 3.13+

### Deploy in 5 Minutes

```bash
# 1. Start Minikube
minikube start --cpus=2 --memory=4096 --driver=docker

# 2. Build and load images
docker build -t todoboard-backend:0.1.0 ./backend
docker build -t todoboard-frontend:0.1.0 ./frontend
minikube image load todoboard-backend:0.1.0
minikube image load todoboard-frontend:0.1.0

# 3. Create secrets
kubectl create secret generic app-secrets \
  --from-literal=POSTGRES_PASSWORD=changeme \
  --from-literal=JWT_SECRET=your-jwt-secret \
  --from-literal=OPENAI_API_KEY=your-key \
  --from-literal=GROQ_API_KEY=your-key

# 4. Deploy with Helm
cd k8s/charts/todoboard
helm install todoboard . -f values-minikube.yaml

# 5. Access application
minikube service todoboard-frontend
```

## Project Structure

```
phase4-kubernetes-deployment/
├── backend/
│   ├── src/                    # FastAPI application code
│   ├── Dockerfile              # Backend container image
│   ├── .dockerignore           # Docker build exclusions
│   └── requirements.txt        # Python dependencies
│
├── frontend/
│   ├── app/                    # Next.js application code
│   ├── Dockerfile              # Frontend container image
│   ├── .dockerignore           # Docker build exclusions
│   └── package.json            # Node.js dependencies
│
├── k8s/
│   └── charts/
│       └── todoboard/          # Helm chart
│           ├── Chart.yaml      # Chart metadata
│           ├── values.yaml     # Default configuration
│           ├── values-minikube.yaml  # Local dev overrides
│           └── templates/      # Kubernetes resource templates
│               ├── deployment-backend.yaml
│               ├── deployment-frontend.yaml
│               ├── deployment-postgres.yaml
│               ├── service-*.yaml
│               ├── configmap.yaml
│               ├── secret.yaml
│               ├── pvc.yaml
│               ├── ingress.yaml
│               ├── networkpolicy.yaml
│               └── hooks-db-migration.yaml
│
└── docs/
    ├── QUICKSTART.md           # Quick start guide
    ├── ENVIRONMENT_SETUP.md    # Detailed setup instructions
    ├── KUBECTL_AI.md           # AI-assisted kubectl usage
    ├── KAGENT.md               # Cluster analysis tool
    ├── GORDON.md               # Docker AI assistant
    └── TROUBLESHOOTING.md      # Common issues and solutions
```

## Architecture

### Components

1. **Backend (FastAPI)**
   - Python 3.13+ application
   - REST API for task management
   - AI chatbot integration (OpenAI/Groq)
   - PostgreSQL database connection

2. **Frontend (Next.js)**
   - TypeScript/React application
   - Server-side rendering
   - Responsive UI with Tailwind CSS
   - Better Auth integration

3. **Database (PostgreSQL)**
   - PostgreSQL 16 Alpine
   - Persistent storage via PVC
   - Automated migrations via Helm hooks

### Networking

- **Backend Service**: ClusterIP (internal only)
- **Frontend Service**: NodePort 30000 (external access)
- **Database Service**: ClusterIP (internal only)

### Storage

- **PersistentVolumeClaim**: 5Gi for PostgreSQL data
- **StorageClass**: standard (Minikube hostPath)
- **Data Persistence**: Survives pod restarts and redeployments

## Configuration

### Environment-Specific Values

**Minikube (values-minikube.yaml)**:
- NodePort service for frontend
- Single replicas for all services
- Reduced resource limits (4GB total)
- Local storage class

**Production (values-production.yaml)** - Phase V:
- LoadBalancer service for frontend
- Multiple replicas with autoscaling
- Higher resource limits
- Cloud storage class (gp3/pd-ssd)

### Secrets Management

**Phase IV (Local)**:
```bash
kubectl create secret generic app-secrets \
  --from-literal=POSTGRES_PASSWORD=<password> \
  --from-literal=JWT_SECRET=<secret> \
  --from-literal=OPENAI_API_KEY=<key> \
  --from-literal=GROQ_API_KEY=<key>
```

**Phase V (Cloud)**: External Secrets Operator + Cloud Secret Manager

## Common Operations

### View Status

```bash
# Check pods
kubectl get pods

# Check services
kubectl get services

# Check deployments
kubectl get deployments

# View logs
kubectl logs -f -l app=todoboard-backend
```

### Update Deployment

```bash
# Modify configuration
vim k8s/charts/todoboard/values-minikube.yaml

# Upgrade deployment
helm upgrade todoboard ./k8s/charts/todoboard -f values-minikube.yaml

# Check rollout status
kubectl rollout status deployment/todoboard-backend
```

### Scale Services

```bash
# Scale backend
kubectl scale deployment todoboard-backend --replicas=3

# Or via Helm
helm upgrade todoboard ./k8s/charts/todoboard --set backend.replicaCount=3
```

### Database Operations

```bash
# Connect to database
kubectl exec -it deployment/todoboard-postgres -- psql -U postgres -d todoboard

# Backup database
kubectl exec deployment/todoboard-postgres -- pg_dump -U postgres todoboard > backup.sql

# Restore database
kubectl exec -i deployment/todoboard-postgres -- psql -U postgres todoboard < backup.sql
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod events
kubectl describe pod <pod-name>

# Common fixes:
# - Reload images: minikube image load <image>
# - Increase resources: minikube start --memory=8192
# - Create secrets: kubectl create secret generic app-secrets
```

### Cannot Access Application

```bash
# Get Minikube IP
minikube ip

# Get NodePort
kubectl get service todoboard-frontend

# Or use automatic access
minikube service todoboard-frontend
```

### Database Connection Errors

```bash
# Check database pod
kubectl get pod -l app=todoboard-postgres

# Check database logs
kubectl logs -l app=todoboard-postgres

# Verify secret
kubectl get secret app-secrets -o yaml
```

## Documentation

- **[Quick Start Guide](./docs/QUICKSTART.md)**: Deploy in 5 minutes
- **[Environment Setup](./docs/ENVIRONMENT_SETUP.md)**: Detailed installation instructions
- **[Troubleshooting](./docs/TROUBLESHOOTING.md)**: Common issues and solutions
- **[kubectl-ai Guide](./docs/KUBECTL_AI.md)**: AI-assisted Kubernetes operations
- **[Specification](../specs/004-kubernetes-deployment/spec.md)**: Feature requirements
- **[Implementation Plan](../specs/004-kubernetes-deployment/plan.md)**: Technical design

## Success Criteria

- ✅ Deployment completes in under 5 minutes
- ✅ Application accessible via browser at `http://<minikube-ip>:30000`
- ✅ All Phase III features functional (task CRUD, AI chatbot, authentication)
- ✅ Data persists through pod restarts
- ✅ Configuration manageable via Helm values
- ✅ Reproducible across developer machines

## Next Steps

### Phase V: Cloud Kubernetes Deployment

After successful local deployment, proceed to Phase V for cloud deployment:

1. **Choose Cloud Provider**: DigitalOcean (DOKS), Google Cloud (GKE), or Azure (AKS)
2. **Create Kubernetes Cluster**: Use cloud provider console or CLI
3. **Update Helm Values**: Use `values-production.yaml` with cloud-specific settings
4. **Configure Ingress**: Set up Ingress controller with TLS certificates
5. **Enable Autoscaling**: Configure HPA for automatic scaling
6. **Set Up Monitoring**: Deploy Prometheus and Grafana
7. **Implement CI/CD**: Automate deployments with GitOps (ArgoCD/Flux)

### Bonus Features

- **+200 points**: Create reusable Claude subagents/skills for Kubernetes deployment
- **+200 points**: Build Cloud-Native Blueprints for 1-click infrastructure setup
- **+100 points**: Add Urdu language support to chatbot
- **+200 points**: Implement voice commands via Web Speech API

## Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs/)

## Support

For issues or questions:
1. Check [Troubleshooting Guide](./docs/TROUBLESHOOTING.md)
2. Review Kubernetes events: `kubectl get events --sort-by='.lastTimestamp'`
3. Check application logs: `kubectl logs -l app=todoboard-backend`
4. Consult project documentation in `specs/004-kubernetes-deployment/`

---

**Phase IV Status**: ✅ Complete
**Deployment Time**: ~5 minutes
**Feature Parity**: 100% with Phase III
**Cloud Ready**: Yes (Phase V)
