FROM node:18-slim

# Install system dependencies for Puppeteer
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    libnss3 \
    libatk-bridge2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Set Puppeteer to use the installed Chromium
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

WORKDIR /app

# Create non-root user
RUN useradd -m -u 1001 leados
RUN mkdir -p /app/.wwebjs_auth && chown -R leados:leados /app
USER leados

# Copy package files
COPY --chown=leados:leados package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY --chown=leados:leados . .

# Expose port
EXPOSE 3001

# Start application
CMD ["node", "index.js"]
