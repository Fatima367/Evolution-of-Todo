# Multi-stage Dockerfile for TodoBoard Frontend
# Uses Alpine Linux for minimal footprint and improved security

# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Set npm registry and network settings for resilience
RUN npm config set fetch-retries 5 && \
    npm config set fetch-retry-mintimeout 20000 && \
    npm config set fetch-retry-maxtimeout 120000

# Install dependencies based on lock file
# We need all dependencies (including devDeps) to build the Next.js app
COPY package.json package-lock.json ./
RUN npm ci

# Copy source code
COPY . .

# Build the application with standalone output for optimized production deployment
ENV NEXT_PRIVATE_STANDALONE_OUTPUT=true
RUN npm run build

# Production stage
FROM node:20-alpine

WORKDIR /app

# Copy standalone output and static assets from builder
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

# Add non-root user for security
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -D -S -G appgroup appuser

# Change ownership to non-root user
RUN chown -R appuser:appgroup /app
USER appuser

# Expose frontend port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

# Metadata
LABEL maintainer="Evolution of Todo"
LABEL description="TodoBoard Frontend - AI-Powered Todo Chatbot UI"

# Start the application using the standalone server
CMD ["node", "server.js"]

# Health check - commented out as Next.js doesn't have a default health endpoint
# HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
#     CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1