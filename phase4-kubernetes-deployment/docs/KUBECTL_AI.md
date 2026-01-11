# kubectl-ai: AI-Powered Kubernetes Operations

kubectl-ai is a natural language interface for Kubernetes that allows you to interact with your cluster using plain English commands instead of complex kubectl syntax.

## Installation

### Prerequisites
- kubectl installed and configured
- OpenAI API key or compatible LLM API

### Install kubectl-ai

```bash
# Using kubectl plugin manager (krew)
kubectl krew install ai

# Or download binary from GitHub
# https://github.com/GoogleCloudPlatform/kubectl-ai
```

### Configuration

```bash
# Set OpenAI API key
export OPENAI_API_KEY=your-api-key-here

# Or configure in ~/.kube/config
kubectl config set-credentials kubectl-ai --token=$OPENAI_API_KEY
```

## Basic Usage

### Syntax

```bash
kubectl ai "your natural language query"
```

### Common Examples

#### Deployment Status

```bash
# Check if all pods are running
kubectl ai "show me all pods that are not running"

# Get deployment status
kubectl ai "what is the status of todoboard deployment?"

# Check resource usage
kubectl ai "show me pods using more than 500MB memory"
```

#### Scaling Operations

```bash
# Scale deployment
kubectl ai "scale the backend to 3 replicas"

# Scale down
kubectl ai "reduce frontend replicas to 1"

# Auto-scale
kubectl ai "enable autoscaling for backend with min 2 max 5 replicas"
```

#### Troubleshooting

```bash
# Diagnose pod failures
kubectl ai "why is the frontend pod failing?"

# Check logs
kubectl ai "show me the last 50 lines of backend logs"

# Investigate errors
kubectl ai "find all pods with errors in the last hour"
```

#### Resource Management

```bash
# View resource usage
kubectl ai "show me resource usage for all pods"

# Check limits
kubectl ai "which pods are hitting their memory limits?"

# Optimize resources
kubectl ai "suggest resource optimizations for my cluster"
```

## TodoBoard-Specific Examples

### Deployment Operations

```bash
# Check TodoBoard deployment
kubectl ai "is todoboard fully deployed and healthy?"

# Verify all services
kubectl ai "show me all todoboard services and their endpoints"

# Check database connection
kubectl ai "is the backend connected to the database?"
```

### Debugging

```bash
# Backend issues
kubectl ai "why can't the backend connect to postgres?"

# Frontend issues
kubectl ai "why is the frontend returning 502 errors?"

# Database issues
kubectl ai "is the postgres pod running and accepting connections?"
```

### Configuration

```bash
# View configuration
kubectl ai "show me all environment variables for the backend"

# Check secrets
kubectl ai "list all secrets used by todoboard"

# Verify ConfigMaps
kubectl ai "what configuration is the frontend using?"
```

### Monitoring

```bash
# Check health
kubectl ai "are all todoboard health checks passing?"

# View metrics
kubectl ai "show me CPU and memory usage for todoboard pods"

# Check logs
kubectl ai "show me errors in backend logs from the last 10 minutes"
```

## Advanced Usage

### Complex Queries

```bash
# Multi-condition queries
kubectl ai "show me pods that are not ready and have been restarting"

# Aggregated information
kubectl ai "summarize the health of all todoboard components"

# Comparative analysis
kubectl ai "compare resource usage between backend and frontend"
```

### Automation

```bash
# Create deployment
kubectl ai "create a deployment for nginx with 3 replicas"

# Update configuration
kubectl ai "update backend deployment to use image version 0.2.0"

# Rollback
kubectl ai "rollback the last deployment change"
```

### Best Practices

```bash
# Security audit
kubectl ai "check for security issues in my deployments"

# Resource optimization
kubectl ai "suggest ways to reduce resource usage"

# High availability
kubectl ai "check if my deployments are highly available"
```

## Tips and Tricks

### Be Specific

❌ Bad: "show me pods"
✅ Good: "show me all todoboard pods that are not running"

### Use Context

❌ Bad: "scale it"
✅ Good: "scale the todoboard-backend deployment to 3 replicas"

### Ask for Explanations

```bash
# Understand errors
kubectl ai "explain why this pod is in CrashLoopBackOff"

# Learn best practices
kubectl ai "what are best practices for resource limits?"

# Get recommendations
kubectl ai "how can I improve the reliability of my deployment?"
```

## Common Workflows

### Initial Deployment Check

```bash
kubectl ai "show me the status of all todoboard resources"
kubectl ai "are there any errors or warnings?"
kubectl ai "is the application accessible?"
```

### Troubleshooting Workflow

```bash
kubectl ai "what pods are failing?"
kubectl ai "show me logs for the failing pod"
kubectl ai "what events are associated with this pod?"
kubectl ai "suggest fixes for this issue"
```

### Scaling Workflow

```bash
kubectl ai "what is the current load on backend pods?"
kubectl ai "scale backend to handle more traffic"
kubectl ai "verify the scaling completed successfully"
```

## Limitations

- Requires internet connection for API calls
- May not understand very complex or ambiguous queries
- Cannot perform destructive operations without confirmation
- Limited to kubectl capabilities (cannot modify cluster infrastructure)

## Troubleshooting kubectl-ai

### API Key Issues

```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Test connection
kubectl ai "test connection"
```

### Command Not Found

```bash
# Verify installation
kubectl plugin list | grep ai

# Reinstall if needed
kubectl krew install ai
```

### Unexpected Results

```bash
# Be more specific in your query
# Add context about namespace, labels, etc.
# Use kubectl directly for critical operations
```

## Comparison with Standard kubectl

| Task | kubectl | kubectl-ai |
|------|---------|------------|
| List pods | `kubectl get pods -l app=todoboard-backend` | `kubectl ai "show me backend pods"` |
| Scale deployment | `kubectl scale deployment todoboard-backend --replicas=3` | `kubectl ai "scale backend to 3 replicas"` |
| View logs | `kubectl logs -l app=todoboard-backend --tail=50` | `kubectl ai "show me last 50 lines of backend logs"` |
| Troubleshoot | `kubectl describe pod <name>` + manual analysis | `kubectl ai "why is this pod failing?"` |

## Resources

- [kubectl-ai GitHub](https://github.com/GoogleCloudPlatform/kubectl-ai)
- [kubectl-ai Documentation](https://kubectl-ai.readthedocs.io/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)

## Next Steps

- Try [kagent](./KAGENT.md) for cluster-wide analysis
- Explore [Gordon](./GORDON.md) for Docker AI assistance
- Review [AI Deployment Workflow](./AI_DEPLOYMENT.md) for integrated approach
