# Build stage: Next.js application
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the Next.js application
RUN npm run build

# Production stage
FROM node:20-alpine AS runner

WORKDIR /app

# Copy node modules from builder stage
COPY --from=builder /app/node_modules ./node_modules
# Copy built application from builder stage
COPY --from=builder /app/.next ./.next
# Copy public files
COPY --from=builder /app/public ./public
# Copy package.json and other necessary files
COPY --from=builder /app/package.json ./
COPY --from=builder /app/next.config.* ./
COPY --from=builder /app/CLAUDE.md ./
COPY --from=builder /app/README.md ./
COPY --from=builder /app/eslint.config.mjs ./
COPY --from=builder /app/postcss.config.* ./
COPY --from=builder /app/tailwind.config.* ./
COPY --from=builder /app/tsconfig.json ./

# Set environment variables
ENV NODE_ENV=production
ENV PORT=3000

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/api/health || exit 1

# Run the application
CMD ["npm", "start"]