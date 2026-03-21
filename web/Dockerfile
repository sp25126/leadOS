# Stage 1: Build
FROM node:18-slim AS builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Runtime
FROM node:18-slim AS runner

WORKDIR /app

ENV NODE_ENV=production

# Create non-root user
RUN useradd -m -u 1001 leados
USER leados

# Copy necessary files from builder
COPY --from=builder --chown=leados:leados /app/next.config.js ./
COPY --from=builder --chown=leados:leados /app/public ./public
COPY --from=builder --chown=leados:leados /app/.next ./.next
COPY --from=builder --chown=leados:leados /app/node_modules ./node_modules
COPY --from=builder --chown=leados:leados /app/package.json ./package.json

# Expose port
EXPOSE 3000

# Start application
CMD ["npm", "start"]
