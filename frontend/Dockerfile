FROM nginx:alpine

# Install openssl
RUN apk add --no-cache openssl

# Create directory for certs
RUN mkdir -p /etc/nginx/certs

# Generate self-signed certificate
RUN openssl req -x509 -nodes -days 365 \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost" \
  -newkey rsa:2048 \
  -keyout /etc/nginx/certs/server.key \
  -out /etc/nginx/certs/server.crt

# COPY ONLY STATIC FILES, NOT THE ENTIRE FOLDER
COPY ./css /usr/share/nginx/html/css
COPY ./images /usr/share/nginx/html/images
COPY ./index.html /usr/share/nginx/html/index.html
COPY ./about.html /usr/share/nginx/html/about.html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80 443
