# GitHub Secrets Configuration Guide

This document describes all GitHub Secrets required for the CI/CD pipeline to function properly.

## Overview

The CI/CD pipeline uses GitHub Secrets to securely store sensitive credentials and configuration values. These secrets are used across three workflows:
- `build-and-test.yml` - Build, test, and security scanning
- `deploy-staging.yml` - Automated staging deployment
- `deploy-production.yml` - Manual production deployment

## Required Secrets

### 1. Container Registry Authentication

#### `GITHUB_TOKEN`
- **Type**: Automatically provided by GitHub Actions
- **Purpose**: Authenticate to GitHub Container Registry (ghcr.io)
- **Used in**: `build-and-test.yml` (Docker image push)
- **Configuration**: No action required - automatically available
- **Scope**: Read/write packages

### 2. Kubernetes Cluster Access

#### `KUBECONFIG_STAGING`
- **Type**: Base64-encoded kubeconfig file
- **Purpose**: Authenticate to staging Kubernetes cluster
- **Used in**: `deploy-staging.yml`
- **Configuration**:
  ```bash
  # Generate from your kubeconfig
  cat ~/.kube/config-staging | base64 -w 0
  ```
- **Required fields in kubeconfig**:
  - Cluster endpoint URL
  - Certificate authority data
  - Client certificate or token
  - Context named "staging"

#### `KUBECONFIG_PRODUCTION`
- **Type**: Base64-encoded kubeconfig file
- **Purpose**: Authenticate to production Kubernetes cluster
- **Used in**: `deploy-production.yml`
- **Configuration**:
  ```bash
  # Generate from your kubeconfig
  cat ~/.kube/config-production | base64 -w 0
  ```
- **Required fields in kubeconfig**:
  - Cluster endpoint URL
  - Certificate authority data
  - Client certificate or token
  - Context named "production"

### 3. Notification Services (Optional)

#### `SLACK_WEBHOOK_URL`
- **Type**: HTTPS webhook URL
- **Purpose**: Send deployment notifications to Slack
- **Used in**: `deploy-staging.yml`, `deploy-production.yml`
- **Configuration**:
  1. Create a Slack App at https://api.slack.com/apps
  2. Enable Incoming Webhooks
  3. Create a webhook for your channel
  4. Copy the webhook URL (format: `https://hooks.slack.com/services/...`)
- **Optional**: If not configured, deployment will succeed but notifications will be skipped

#### `DISCORD_WEBHOOK_URL` (Alternative)
- **Type**: HTTPS webhook URL
- **Purpose**: Send deployment notifications to Discord (alternative to Slack)
- **Used in**: Custom notification steps (if implemented)
- **Configuration**:
  1. Go to Discord Server Settings → Integrations → Webhooks
  2. Create a new webhook
  3. Copy the webhook URL

### 4. Cloud Provider Credentials (Optional - for cluster setup)

These are only needed if using automated cluster provisioning scripts.

#### Oracle Cloud (OKE)
- `OCI_TENANCY_OCID` - Oracle Cloud tenancy identifier
- `OCI_USER_OCID` - Oracle Cloud user identifier
- `OCI_FINGERPRINT` - API key fingerprint
- `OCI_PRIVATE_KEY` - Base64-encoded private key
- `OCI_REGION` - Oracle Cloud region (e.g., `us-ashburn-1`)

#### Google Cloud (GKE)
- `GCP_PROJECT_ID` - Google Cloud project ID
- `GCP_SERVICE_ACCOUNT_KEY` - Base64-encoded service account JSON key
- `GCP_REGION` - Google Cloud region (e.g., `us-central1`)

#### Azure (AKS)
- `AZURE_SUBSCRIPTION_ID` - Azure subscription ID
- `AZURE_CLIENT_ID` - Service principal client ID
- `AZURE_CLIENT_SECRET` - Service principal secret
- `AZURE_TENANT_ID` - Azure tenant ID
- `AZURE_RESOURCE_GROUP` - Resource group name

## Setting Up Secrets

### Via GitHub Web UI

1. Navigate to your repository on GitHub
2. Go to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Enter the secret name and value
5. Click **Add secret**

### Via GitHub CLI

```bash
# Install GitHub CLI if not already installed
# https://cli.github.com/

# Authenticate
gh auth login

# Add a secret
gh secret set SECRET_NAME < secret-file.txt

# Or set directly
echo "secret-value" | gh secret set SECRET_NAME

# Example: Set kubeconfig
cat ~/.kube/config-staging | base64 -w 0 | gh secret set KUBECONFIG_STAGING

# Example: Set Slack webhook
echo "https://hooks.slack.com/services/YOUR/WEBHOOK/URL" | gh secret set SLACK_WEBHOOK_URL
```

## Environment-Specific Configuration

### Staging Environment

The staging environment is configured in GitHub Settings → Environments → staging:
- **Protection rules**: None (auto-deploy on main branch)
- **Required secrets**: `KUBECONFIG_STAGING`
- **Deployment URL**: https://staging.todoboard.app

### Production Environment

The production environment requires manual approval:

1. Create environment: **Settings** → **Environments** → **New environment** → "production"
2. Enable **Required reviewers** and add team members
3. Set **Wait timer** (optional): 5 minutes minimum wait before deployment
4. Add required secrets: `KUBECONFIG_PRODUCTION`
5. Set **Deployment URL**: https://todoboard.app

### Production Approval Environment

Create a separate approval gate:

1. Create environment: "production-approval"
2. Enable **Required reviewers** (same as production)
3. No secrets needed for this environment
4. This creates a manual checkpoint before deployment starts

## Security Best Practices

### 1. Principle of Least Privilege
- Use service accounts with minimal required permissions
- Create separate kubeconfigs for staging and production
- Limit kubeconfig to specific namespaces if possible

### 2. Secret Rotation
- Rotate kubeconfig credentials every 90 days
- Rotate webhook URLs if compromised
- Update cloud provider credentials regularly

### 3. Access Control
- Limit who can view/edit secrets (repository admins only)
- Use environment protection rules for production
- Enable audit logging for secret access

### 4. Kubeconfig Security
- Use short-lived tokens instead of certificates when possible
- Consider using OIDC authentication for Kubernetes
- Never commit kubeconfig files to the repository

### 5. Monitoring
- Monitor failed authentication attempts in workflow logs
- Set up alerts for unauthorized access attempts
- Review deployment logs regularly

## Validation

### Test Staging Deployment
```bash
# Trigger staging deployment manually
gh workflow run deploy-staging.yml

# Check workflow status
gh run list --workflow=deploy-staging.yml
```

### Test Production Deployment
```bash
# Trigger production deployment (requires approval)
gh workflow run deploy-production.yml -f version=main

# Approve the deployment in GitHub UI
# Settings → Environments → production → View deployment → Review deployments
```

## Troubleshooting

### "Error: Invalid kubeconfig"
- Verify the kubeconfig is base64-encoded correctly
- Check that the context name matches ("staging" or "production")
- Ensure cluster endpoint is accessible from GitHub Actions runners

### "Error: Authentication failed"
- Verify credentials haven't expired
- Check service account permissions
- Ensure RBAC rules allow required operations

### "Slack notification failed"
- Verify webhook URL is correct
- Check that the Slack app is still installed
- Ensure webhook has permission to post to the channel

### "Docker push failed"
- Verify `GITHUB_TOKEN` has package write permissions
- Check that GitHub Container Registry is enabled
- Ensure repository visibility settings allow package publishing

## Reference

- [GitHub Actions Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [GitHub Environments Documentation](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
- [Kubernetes Authentication](https://kubernetes.io/docs/reference/access-authn-authz/authentication/)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
