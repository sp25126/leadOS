FROM nginx:alpine

# Remove default configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create directory for SSL certs and html
RUN mkdir -p /etc/nginx/ssl /usr/share/nginx/html

# Expose ports
EXPOSE 80 443
