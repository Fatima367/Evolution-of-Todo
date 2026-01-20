# TodoBoard Cloud Deployment Guide

Complete step-by-step guide to deploy TodoBoard application on cloud Kubernetes for free.

## Table of Contents

- [Overview](#overview)
- [Cloud Provider Options](#cloud-provider-options)
- [Prerequisites](#prerequisites)
- [Deployment Steps](#deployment-steps)
  - [Option 1: Oracle Cloud (OKE) - Recommended](#option-1-oracle-cloud-oke---recommended)
  - [Option 2: Google Cloud (GKE)](#option-2-google-cloud-gke)
  - [Option 3: Azure (AKS)](#option-3-azure-aks)
- [Post-Deployment Configuration](#post-deployment-configuration)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Cost Breakdown](#cost-breakdown)
- [Cleanup](#cleanup)

---

## Overview

This guide walks you through deploying the TodoBoard application (Phase 5: Advanced Cloud Deployment) to a production-grade Kubernetes cluster on cloud infrastructure using free tier offerings.

**What you'll deploy:**
- Frontend (Next.js)
- Backend API (FastAPI)
- Notification Service
- Recurring Task Service
- Audit Service
- Kafka (event streaming)
- Dapr (microservices runtime)
- PostgreSQL (Neon Serverless)

---

## Cloud Provider Options

### Recommended: Oracle Cloud (OKE)
- **Cost**: $0/month (Always Free tier)
- **Resources**: 4 OCPUs, 24GB RAM
- **Duration**: Forever free
- **Best for**: Long-term hosting without costs

### Alternative: Google Cloud (GKE)
- **Cost**: $300 credit
- **Duration**: 90 days
- **Best for**: Testing with higher resources

### Alternative: Azure (AKS)
- **Cost**: $200 credit
- **Duration**: 30 days
- **Best for**: Azure ecosystem integration

---

## Prerequisites

### 1. Install Required Tools

#### kubectl (Kubernetes CLI)
```bash
# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# macOS
brew install kubectl

# Windows (PowerShell)
choco install kubernetes-cli

# Verify installation
kubectl version --client
```

#### Helm (Kubernetes Package Manager)
```bash
# Linux/macOS
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Windows (PowerShell)
choco install kubernetes-helm

# Verify installation
helm version
```

#### Cloud Provider CLI

**Oracle Cloud CLI:**
```bash
bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"
```

**Google Cloud CLI:**
```bash
# Linux
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# macOS
brew install --cask google-cloud-sdk

# Windows
# Download from: https://cloud.google.com/sdk/docs/install
```

**Azure CLI:**
```bash
# Linux
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# macOS
brew install azure-cli

# Windows
# Download from: https://aka.ms/installazurecliwindows
```

### 2. Create Cloud Accounts

#### Oracle Cloud Account
1. Go to https://www.oracle.com/cloud/free/
2. Click "Start for free"
3. Fill in registration details (no credit card required)
4. Verify email
5. Complete account setup
6. Note your **Compartment OCID** from the console

#### Google Cloud Account
1. Go to https://cloud.google.com/free
2. Click "Get started for free"
3. Sign in with Google account
4. Add payment method (won't be charged, $300 credit)
5. Create a new project
6. Note your **Project ID**

#### Azure Account
1. Go to https://azure.microsoft.com/free/
2. Click "Start free"
3. Sign in with Microsoft account
4. Add payment method (won't be charged, $200 credit)
5. Complete verification
6. Note your **Subscription ID**

### 3. Setup External Services

#### Neon PostgreSQL (Free Database)
1. Go to https://neon.tech
2. Sign up for free account
3. Create new project: "todoboard"
4. Copy connection string:
   ```
   postgresql://user:pass@ep-xxx.region.aws.neon.tech/neondb?sslmode=require
   ```
5. Save this for later

#### Groq API (Free LLM API)
1. Go to https://console.groq.com
2. Sign up for free account
3. Navigate to API Keys
4. Create new API key
5. Copy and save the key

---

## Deployment Steps

### Option 1: Oracle Cloud (OKE) - Recommended

#### Step 1: Configure OCI CLI

```bash
# Configure OCI CLI
oci setup config

# Follow prompts:
# - Enter user OCID (from Oracle Cloud Console > Profile > User Settings)
# - Enter tenancy OCID (from Console > Tenancy Details)
# - Enter region (e.g., us-ashburn-1)
# - Generate API key pair (Y)

# Test configuration
oci iam region list
```

#### Step 2: Setup Kubernetes Cluster

```bash
# Navigate to scripts directory
cd /mnt/d/Documents/Hackathons/Evolution-of-Todo/phase4-kubernetes-deployment/scripts/cloud

# Set environment variables
export OCI_COMPARTMENT_ID="ocid1.compartment.oc1..xxx"  # Your compartment OCID
export CLUSTER_NAME="todoboard-cluster"
export OCI_REGION="us-ashburn-1"  # Your region

# Make script executable
chmod +x setup-cluster-oke.sh

# Run setup script
./setup-cluster-oke.sh
```

**What this script does:**
- Creates VCN (Virtual Cloud Network)
- Creates OKE cluster with 2 nodes
- Configures kubectl context
- Installs NGINX Ingress Controller
- Installs cert-manager for TLS

**Expected output:**
```
✓ VCN created
✓ OKE cluster created
✓ Nodes ready
✓ Ingress controller installed
✓ cert-manager installed
```

#### Step 3: Verify Cluster

```bash
# Check cluster connection
kubectl cluster-info

# Check nodes
kubectl get nodes

# Expected output:
# NAME                                STATUS   ROLES    AGE   VERSION
# oke-cxxxxx-node-pool-1-xxxxx       Ready    <none>   5m    v1.28.x
# oke-cxxxxx-node-pool-1-xxxxx       Ready    <none>   5m    v1.28.x
```

---

### Option 2: Google Cloud (GKE)

#### Step 1: Configure gcloud CLI

```bash
# Initialize gcloud
gcloud init

# Login
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID
```

#### Step 2: Setup Kubernetes Cluster

```bash
# Navigate to scripts directory
cd /mnt/d/Documents/Hackathons/Evolution-of-Todo/phase5-advanced-cloud-deployment/scripts/cloud

# Set environment variables
export GCP_PROJECT_ID="your-project-id"
export CLUSTER_NAME="todoboard-cluster"
export GCP_ZONE="us-central1-a"

# Make script executable
chmod +x setup-cluster-gke.sh

# Run setup script
./setup-cluster-gke.sh
```

#### Step 3: Verify Cluster

```bash
# Get cluster credentials
gcloud container clusters get-credentials $CLUSTER_NAME --zone $GCP_ZONE

# Check nodes
kubectl get nodes
```

---

### Option 3: Azure (AKS)

#### Step 1: Configure Azure CLI

```bash
# Login to Azure
az login

# Set subscription
az account set --subscription YOUR_SUBSCRIPTION_ID
```

#### Step 2: Setup Kubernetes Cluster

```bash
# Navigate to scripts directory
cd /mnt/d/Documents/Hackathons/Evolution-of-Todo/phase5-advanced-cloud-deployment/scripts/cloud

# Set environment variables
export AZURE_RESOURCE_GROUP="todoboard-rg"
export CLUSTER_NAME="todoboard-cluster"
export AZURE_LOCATION="eastus"

# Make script executable
chmod +x setup-cluster-aks.sh

# Run setup script
./setup-cluster-aks.sh
```

#### Step 3: Verify Cluster

```bash
# Get cluster credentials
az aks get-credentials --resource-group $AZURE_RESOURCE_GROUP --name $CLUSTER_NAME

# Check nodes
kubectl get nodes
```

---

## Post-Deployment Configuration

### Step 1: Create Kubernetes Namespace

```bash
# Create namespace
kubectl create namespace todoboard

# Verify
kubectl get namespaces
```

### Step 2: Configure Secrets

```bash
# Generate JWT secret (32+ characters)
JWT_SECRET=$(openssl rand -base64 32)

# Create Kubernetes secrets
kubectl create secret generic todoboard-secrets \
  --from-literal=POSTGRES_PASSWORD='your-neon-db-password' \
  --from-literal=JWT_SECRET_KEY="$JWT_SECRET" \
  --from-literal=GROQ_API_KEY='your-groq-api-key' \
  -n todoboard

# Verify secrets
kubectl get secrets -n todoboard
```

### Step 3: Update Helm Values

Navigate to phase5 directory:
```bash
cd /mnt/d/Documents/Hackathons/Evolution-of-Todo/phase5-advanced-cloud-deployment
```

Edit `infrastructure/helm/todo-app/values-cloud.yaml`:

```bash
# Open with your preferred editor
nano infrastructure/helm/todo-app/values-cloud.yaml
# or
vim infrastructure/helm/todo-app/values-cloud.yaml
```

**⚠️ CRITICAL: CORS Configuration**

The CORS configuration is critical for cloud deployment. Incorrect configuration will cause connection errors between frontend and backend.

**Update these sections:**

```yaml
# Ingress configuration
ingress:
  enabled: true
  className: nginx
  hosts:
    - host: todoboard.yourdomain.com  # Change to your domain or use IP
      paths:
        - path: /
          pathType: Prefix

  tls:
    enabled: true
    acme:
      email: "your-email@example.com"  # Change to your email

# Backend configuration
configMap:
  backend:
    DATABASE_URL: "postgresql://user:pass@ep-xxx.region.aws.neon.tech/neondb?sslmode=require"
    # IMPORTANT: CORS_ORIGINS must match your frontend URL exactly
    CORS_ORIGINS: '["https://todoboard.yourdomain.com"]'
    ENVIRONMENT: "production"

  frontend:
    # IMPORTANT: NEXT_PUBLIC_API_URL must point to your backend
    NEXT_PUBLIC_API_URL: "https://todoboard.yourdomain.com/api"
```

**If you don't have a domain**, use nip.io:

First, get your ingress IP (you'll need to deploy first, then update):
```bash
# After initial deployment, get ingress IP
INGRESS_IP=$(kubectl get ingress -n todoboard -o jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}')
echo "Your URL will be: http://$INGRESS_IP.nip.io"
```

Then update values:
```yaml
ingress:
  hosts:
    - host: 34.123.45.67.nip.io  # Replace with your actual ingress IP

configMap:
  backend:
    CORS_ORIGINS: '["http://34.123.45.67.nip.io","https://34.123.45.67.nip.io"]'
  frontend:
    NEXT_PUBLIC_API_URL: "http://34.123.45.67.nip.io/api"
```

**📖 For detailed CORS configuration guide, see:** [docs/CORS_CONFIGURATION.md](./docs/CORS_CONFIGURATION.md)

### Step 4: Deploy Application

```bash
# Install Helm chart
helm install todoboard ./infrastructure/helm/todo-app \
  -f ./infrastructure/helm/todo-app/values-cloud.yaml \
  -n todoboard \
  --create-namespace

# Watch deployment progress
kubectl get pods -n todoboard -w
```

**Expected output:**
```
NAME                                          READY   STATUS    RESTARTS   AGE
todoboard-backend-xxxxx                       1/1     Running   0          2m
todoboard-frontend-xxxxx                      1/1     Running   0          2m
todoboard-notification-service-xxxxx          1/1     Running   0          2m
todoboard-recurring-task-service-xxxxx        1/1     Running   0          2m
todoboard-audit-service-xxxxx                 1/1     Running   0          2m
```

### Step 5: Get Access Information

```bash
# Get ingress IP address
kubectl get ingress -n todoboard

# Or use this command for just the IP
kubectl get ingress -n todoboard -o jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}'
```

**Save this IP address** - you'll need it for DNS configuration.

### Step 6: Configure DNS (Optional)

#### If you have a domain:

1. Go to your DNS provider (Namecheap, GoDaddy, Cloudflare, etc.)
2. Create an A record:
   - **Name**: `todoboard` (or `@` for root domain)
   - **Type**: `A`
   - **Value**: `<ingress-ip-address>`
   - **TTL**: 300 (5 minutes)
3. Wait for DNS propagation (5-30 minutes)

#### If you don't have a domain:

Use the free nip.io service:
```bash
# Access your app at:
http://<ingress-ip>.nip.io

# Example:
http://34.123.45.67.nip.io
```

### Step 7: Wait for TLS Certificate

If you enabled TLS, wait for Let's Encrypt certificate:

```bash
# Check certificate status
kubectl get certificate -n todoboard

# Watch certificate creation
kubectl get certificate -n todoboard -w

# Expected output:
# NAME              READY   SECRET            AGE
# todoboard-tls     True    todoboard-tls     2m
```

This usually takes 2-5 minutes.

---

## Verification

### Step 1: Check All Pods

```bash
# Check pod status
kubectl get pods -n todoboard

# All pods should show "Running" status
```

### Step 2: Check Services

```bash
# Check services
kubectl get services -n todoboard

# Expected output:
# NAME                           TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)
# todoboard-backend              ClusterIP   10.96.xxx.xxx   <none>        8000/TCP
# todoboard-frontend             ClusterIP   10.96.xxx.xxx   <none>        3000/TCP
# todoboard-notification-service ClusterIP   10.96.xxx.xxx   <none>        8001/TCP
```

### Step 3: Test Health Endpoints

```bash
# Get ingress IP
INGRESS_IP=$(kubectl get ingress -n todoboard -o jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}')

# Test backend health
curl http://$INGRESS_IP/api/health

# Expected output:
# {"status":"healthy","timestamp":"2026-01-19T..."}

# Test frontend (should return HTML)
curl http://$INGRESS_IP/
```

### Step 4: Access Application

Open your browser and navigate to:
- **With domain**: `https://todoboard.yourdomain.com`
- **Without domain**: `http://<ingress-ip>.nip.io`

You should see the TodoBoard landing page.

### Step 5: Test Registration and Login

1. Click "Sign Up"
2. Create a new account
3. Login with credentials
4. Create a test task
5. Verify task appears in dashboard

---

## Troubleshooting

### Pods Not Starting

**Check pod status:**
```bash
kubectl get pods -n todoboard
```

**Describe problematic pod:**
```bash
kubectl describe pod <pod-name> -n todoboard
```

**Check pod logs:**
```bash
kubectl logs <pod-name> -n todoboard

# Follow logs in real-time
kubectl logs -f <pod-name> -n todoboard
```

**Common issues:**
- **ImagePullBackOff**: Docker image not found or registry authentication failed
- **CrashLoopBackOff**: Application crashing on startup (check logs)
- **Pending**: Insufficient resources or scheduling issues

### Database Connection Issues

**Test database connection:**
```bash
# Run temporary PostgreSQL client pod
kubectl run -it --rm debug --image=postgres:16-alpine --restart=Never -n todoboard -- \
  psql "postgresql://user:pass@ep-xxx.region.aws.neon.tech/neondb?sslmode=require"

# If successful, you'll see:
# psql (16.x)
# SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, bits: 256, compression: off)
# Type "help" for help.
# neondb=>
```

**Check backend logs for database errors:**
```bash
kubectl logs deployment/todoboard-backend -n todoboard | grep -i database
```

### Ingress Not Working

**Check ingress status:**
```bash
kubectl describe ingress todoboard-cloud -n todoboard
```

**Check ingress controller logs:**
```bash
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller
```

**Verify ingress controller is running:**
```bash
kubectl get pods -n ingress-nginx
```

### Certificate Issues

**Check certificate status:**
```bash
kubectl describe certificate todoboard-tls -n todoboard
```

**Check cert-manager logs:**
```bash
kubectl logs -n cert-manager deployment/cert-manager
```

**Common issues:**
- DNS not pointing to ingress IP
- Email not configured in certificate
- Rate limit hit (use staging issuer for testing)

### View All Events

```bash
# View recent events
kubectl get events -n todoboard --sort-by=.metadata.creationTimestamp

# Watch events in real-time
kubectl get events -n todoboard -w
```

### Check Resource Usage

```bash
# Check pod resource usage
kubectl top pods -n todoboard

# Check node resource usage
kubectl top nodes
```

### Access Pod Shell

```bash
# Get shell access to a pod
kubectl exec -it <pod-name> -n todoboard -- /bin/sh

# Example: Access backend pod
kubectl exec -it deployment/todoboard-backend -n todoboard -- /bin/sh
```

---

## Cost Breakdown

### Oracle Cloud (OKE) - Always Free

| Resource | Quantity | Cost |
|----------|----------|------|
| OKE Cluster | 1 | $0 |
| Compute Instances | 2 nodes (2 OCPUs each) | $0 |
| Block Storage | 100GB | $0 |
| Load Balancer | 1 | $0 |
| **Total** | | **$0/month** |

**Additional Services:**
- Neon PostgreSQL: $0/month (Free tier: 0.5GB)
- Groq API: $0/month (Free tier with rate limits)
- **Grand Total**: **$0/month**

### Google Cloud (GKE) - $300 Credit

| Resource | Quantity | Monthly Cost | Credit Duration |
|----------|----------|--------------|-----------------|
| GKE Cluster | 1 | $73 | 90 days |
| Compute (e2-medium) | 3 nodes | $75 | 90 days |
| Load Balancer | 1 | $18 | 90 days |
| **Total** | | **~$166/month** | **~2 months free** |

### Azure (AKS) - $200 Credit

| Resource | Quantity | Monthly Cost | Credit Duration |
|----------|----------|--------------|-----------------|
| AKS Cluster | 1 | $0 | 30 days |
| VMs (Standard_B2s) | 3 nodes | $60 | 30 days |
| Load Balancer | 1 | $18 | 30 days |
| **Total** | | **~$78/month** | **~2.5 months free** |

---

## Cleanup

### Delete Application

```bash
# Uninstall Helm release
helm uninstall todoboard -n todoboard

# Delete namespace
kubectl delete namespace todoboard
```

### Delete Kubernetes Cluster

#### Oracle Cloud (OKE)
```bash
cd /mnt/d/Documents/Hackathons/Evolution-of-Todo/phase5-advanced-cloud-deployment/scripts/cloud

export CLOUD_PROVIDER=oke
chmod +x teardown-cloud.sh
./teardown-cloud.sh
```

#### Google Cloud (GKE)
```bash
cd /mnt/d/Documents/Hackathons/Evolution-of-Todo/phase5-advanced-cloud-deployment/scripts/cloud

export CLOUD_PROVIDER=gke
export GCP_PROJECT_ID="your-project-id"
export CLUSTER_NAME="todoboard-cluster"
export GCP_ZONE="us-central1-a"

chmod +x teardown-cloud.sh
./teardown-cloud.sh
```

#### Azure (AKS)
```bash
cd /mnt/d/Documents/Hackathons/Evolution-of-Todo/phase5-advanced-cloud-deployment/scripts/cloud

export CLOUD_PROVIDER=aks
export AZURE_RESOURCE_GROUP="todoboard-rg"

chmod +x teardown-cloud.sh
./teardown-cloud.sh
```

### Delete External Services

**Neon PostgreSQL:**
1. Go to https://console.neon.tech
2. Select your project
3. Click "Settings" > "Delete Project"

**Groq API:**
1. Go to https://console.groq.com
2. Navigate to API Keys
3. Delete your API key

---

## Additional Resources

### Documentation
- [Phase 5 README](./README.md)
- [Architecture Documentation](./docs/architecture.md)
- [Dapr Setup Guide](./docs/dapr-setup.md)
- [Event Schemas](./docs/event-schemas.md)

### Kubernetes Resources
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)

### Cloud Provider Documentation
- [Oracle Cloud OKE](https://docs.oracle.com/en-us/iaas/Content/ContEng/home.htm)
- [Google Cloud GKE](https://cloud.google.com/kubernetes-engine/docs)
- [Azure AKS](https://docs.microsoft.com/en-us/azure/aks/)

### Monitoring and Debugging
- [Kubernetes Debugging Guide](https://kubernetes.io/docs/tasks/debug/)
- [Helm Debugging](https://helm.sh/docs/chart_template_guide/debugging/)

---

## Support

For issues or questions:
1. Check the [troubleshooting section](#troubleshooting)
2. Review Kubernetes events: `kubectl get events -n todoboard`
3. Check application logs: `kubectl logs -f <pod-name> -n todoboard`
4. Review the [Phase 5 README](./README.md)

---

## Next Steps

After successful deployment:
1. **Setup Monitoring**: Implement Prometheus and Grafana (Phase 8)
2. **Configure CI/CD**: Setup GitHub Actions for automated deployments (Phase 7)
3. **Load Testing**: Test with 1000+ concurrent users
4. **Backup Strategy**: Configure database backups
5. **Custom Domain**: Setup your own domain with TLS

---

**Last Updated**: 2026-01-19
**Phase**: V - Advanced Cloud Deployment
**Status**: Production Ready
