# Multi-stage Dockerfile for TodoBoard Frontend
# Uses Alpine Linux for minimal footprint and improved security

# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies based on lock file
COPY package.json package-lock.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM node:20-alpine

WORKDIR /app

# Install only production dependencies
COPY package.json package-lock.json ./
RUN npm ci --only=production && npm cache clean --force

# Copy built application from builder stage
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.js ./
COPY --from=builder /app/package.json ./

# Add non-root user for security
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

# Change ownership to non-root user
RUN chown -R appuser:appgroup /app
USER appuser

# Expose frontend port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

# Metadata
LABEL maintainer="Evolution of Todo"
LABEL description="TodoBoard Frontend - AI-Powered Todo Chatbot UI"

# Start the application
CMD ["npm", "start"]

# Health check - commented out as Next.js doesn't have a default health endpoint
# HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
#     CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1