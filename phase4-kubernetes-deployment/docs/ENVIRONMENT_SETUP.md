# Environment Setup Guide

This guide provides detailed instructions for setting up your development environment for TodoBoard Kubernetes deployment.

## Table of Contents

1. [Prerequisites Installation](#prerequisites-installation)
2. [Minikube Configuration](#minikube-configuration)
3. [Docker Configuration](#docker-configuration)
4. [kubectl Configuration](#kubectl-configuration)
5. [Helm Configuration](#helm-configuration)
6. [Platform-Specific Setup](#platform-specific-setup)

## Prerequisites Installation

### Docker Desktop

**Windows:**
```powershell
# Download from https://www.docker.com/products/docker-desktop
# Run installer and follow prompts
# Restart computer after installation

# Verify installation
docker --version
docker ps
```

**macOS:**
```bash
# Download from https://www.docker.com/products/docker-desktop
# Drag Docker.app to Applications folder
# Launch Docker Desktop

# Verify installation
docker --version
docker ps
```

**Linux (Ubuntu/Debian):**
```bash
# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker.io

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker ps
```

### Minikube

**Windows:**
```powershell
# Using Chocolatey
choco install minikube

# Or download installer from https://minikube.sigs.k8s.io/docs/start/

# Verify installation
minikube version
```

**macOS:**
```bash
# Using Homebrew
brew install minikube

# Verify installation
minikube version
```

**Linux:**
```bash
# Download and install
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Verify installation
minikube version
```

### kubectl

**Windows:**
```powershell
# Using Chocolatey
choco install kubernetes-cli

# Or download from https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/

# Verify installation
kubectl version --client
```

**macOS:**
```bash
# Using Homebrew
brew install kubectl

# Verify installation
kubectl version --client
```

**Linux:**
```bash
# Download and install
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Verify installation
kubectl version --client
```

### Helm

**Windows:**
```powershell
# Using Chocolatey
choco install kubernetes-helm

# Or download from https://helm.sh/docs/intro/install/

# Verify installation
helm version
```

**macOS:**
```bash
# Using Homebrew
brew install helm

# Verify installation
helm version
```

**Linux:**
```bash
# Download and install
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify installation
helm version
```

## Minikube Configuration

### Basic Configuration

```bash
# Start Minikube with recommended settings
minikube start \
  --cpus=2 \
  --memory=4096 \
  --disk-size=20g \
  --driver=docker \
  --kubernetes-version=v1.28.3

# Enable useful addons
minikube addons enable metrics-server
minikube addons enable dashboard

# Verify configuration
minikube status
minikube profile list
```

### Advanced Configuration

```bash
# For development with more resources
minikube start \
  --cpus=4 \
  --memory=8192 \
  --disk-size=40g \
  --driver=docker

# Configure Docker registry mirror (optional)
minikube start --insecure-registry="10.0.0.0/24"

# Use specific Kubernetes version
minikube start --kubernetes-version=v1.28.3
```

### Minikube Addons

```bash
# List available addons
minikube addons list

# Enable metrics-server (for resource monitoring)
minikube addons enable metrics-server

# Enable dashboard (web UI)
minikube addons enable dashboard

# Enable ingress (for Ingress resources)
minikube addons enable ingress

# Access dashboard
minikube dashboard
```

## Docker Configuration

### Docker Desktop Settings

**Windows/macOS:**
1. Open Docker Desktop
2. Go to Settings → Resources
3. Set CPU: 4 cores, Memory: 8GB
4. Apply & Restart

### Docker Daemon Configuration

```bash
# Check Docker daemon status
docker info

# Configure Docker to use more resources (Linux)
sudo systemctl edit docker

# Add the following:
[Service]
ExecStart=
ExecStart=/usr/bin/dockerd -H fd:// --containerd=/run/containerd/containerd.sock --default-ulimit nofile=65536:65536

# Restart Docker
sudo systemctl daemon-reload
sudo systemctl restart docker
```

## kubectl Configuration

### Shell Completion

**Bash:**
```bash
# Add to ~/.bashrc
source <(kubectl completion bash)
alias k=kubectl
complete -F __start_kubectl k
```

**Zsh:**
```bash
# Add to ~/.zshrc
source <(kubectl completion zsh)
alias k=kubectl
```

**PowerShell:**
```powershell
# Add to $PROFILE
kubectl completion powershell | Out-String | Invoke-Expression
```

### kubectl Aliases

```bash
# Add to ~/.bashrc or ~/.zshrc
alias k='kubectl'
alias kgp='kubectl get pods'
alias kgs='kubectl get services'
alias kgd='kubectl get deployments'
alias kl='kubectl logs'
alias kd='kubectl describe'
alias ke='kubectl exec -it'
```

### Context Configuration

```bash
# View current context
kubectl config current-context

# List all contexts
kubectl config get-contexts

# Switch context
kubectl config use-context minikube

# Set default namespace
kubectl config set-context --current --namespace=default
```

## Helm Configuration

### Repository Setup

```bash
# Add common Helm repositories
helm repo add stable https://charts.helm.sh/stable
helm repo add bitnami https://charts.bitnami.com/bitnami

# Update repositories
helm repo update

# List repositories
helm repo list
```

### Helm Plugins

```bash
# Install helm-diff plugin (useful for upgrades)
helm plugin install https://github.com/databus23/helm-diff

# Install helm-secrets plugin (for secret management)
helm plugin install https://github.com/jkroepke/helm-secrets

# List installed plugins
helm plugin list
```

## Platform-Specific Setup

### Windows

**Enable Hyper-V:**
```powershell
# Run as Administrator
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
```

**Enable WSL2 (recommended):**
```powershell
# Run as Administrator
wsl --install
wsl --set-default-version 2

# Install Ubuntu from Microsoft Store
# Configure Docker Desktop to use WSL2 backend
```

**Firewall Configuration:**
```powershell
# Allow Minikube ports
New-NetFirewallRule -DisplayName "Minikube" -Direction Inbound -LocalPort 30000-32767 -Protocol TCP -Action Allow
```

### macOS

**Enable Virtualization:**
```bash
# Check if virtualization is enabled
sysctl -a | grep machdep.cpu.features | grep VMX

# If not enabled, enable in BIOS/UEFI
```

**Configure Docker Desktop:**
1. Open Docker Desktop
2. Preferences → Resources
3. Set CPU: 4, Memory: 8GB
4. Apply & Restart

### Linux

**Install Dependencies:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y \
  apt-transport-https \
  ca-certificates \
  curl \
  gnupg \
  lsb-release

# Enable and start Docker
sudo systemctl enable docker
sudo systemctl start docker
```

**Configure User Permissions:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify
docker ps
```

## Verification

### Verify All Tools

```bash
# Check Docker
docker --version
docker ps

# Check Minikube
minikube version
minikube status

# Check kubectl
kubectl version --client
kubectl cluster-info

# Check Helm
helm version
helm repo list
```

### Test Deployment

```bash
# Deploy a test application
kubectl create deployment hello-minikube --image=kicbase/echo-server:1.0
kubectl expose deployment hello-minikube --type=NodePort --port=8080

# Access the application
minikube service hello-minikube

# Cleanup
kubectl delete service hello-minikube
kubectl delete deployment hello-minikube
```

## Troubleshooting

### Minikube Won't Start

**Windows:**
- Ensure Hyper-V or WSL2 is enabled
- Run PowerShell as Administrator
- Check Docker Desktop is running

**macOS:**
- Ensure Docker Desktop is running
- Check virtualization is enabled
- Try different driver: `minikube start --driver=hyperkit`

**Linux:**
- Ensure Docker daemon is running: `sudo systemctl status docker`
- Check user is in docker group: `groups $USER`
- Try different driver: `minikube start --driver=kvm2`

### kubectl Cannot Connect

```bash
# Check Minikube status
minikube status

# Update kubectl context
kubectl config use-context minikube

# Verify connection
kubectl cluster-info
```

### Docker Issues

```bash
# Restart Docker daemon (Linux)
sudo systemctl restart docker

# Restart Docker Desktop (Windows/macOS)
# Use Docker Desktop UI

# Check Docker logs
docker system info
```

## Next Steps

- Proceed to [Quick Start Guide](./QUICKSTART.md) for deployment
- Review [Troubleshooting Guide](./TROUBLESHOOTING.md) for common issues
- Explore [kubectl AI Guide](./KUBECTL_AI.md) for AI-assisted operations

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [kubectl Documentation](https://kubernetes.io/docs/reference/kubectl/)
- [Helm Documentation](https://helm.sh/docs/)
