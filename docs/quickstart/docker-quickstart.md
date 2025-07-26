# 🐳 Docker Quick Start

Run Canopy in a container with zero setup! Perfect for deployment, testing, or isolated environments.

## 🚀 Quick Run

### Using Docker Hub (Fastest)

```bash
# Pull and run with your API keys
docker run -d \
  --name canopy \
  -p 8000:8000 \
  -e OPENROUTER_API_KEY=your_key_here \
  canopy/canopy:latest

# Check it's running
curl http://localhost:8000/health
```

### Build from Source

```bash
# Clone the repo
git clone https://github.com/yourusername/canopy.git
cd canopy

# Build the image
docker build -t canopy:local .

# Run with environment variables
docker run -d \
  --name canopy \
  -p 8000:8000 \
  -e OPENROUTER_API_KEY=your_key_here \
  canopy:local
```

## 🔧 Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  canopy:
    image: canopy/canopy:latest
    container_name: canopy-server
    ports:
      - "8000:8000"
    environment:
      # API Keys (use .env file in production)
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      
      # Server Configuration
      - CANOPY_PORT=8000
      - CANOPY_HOST=0.0.0.0
      - CANOPY_WORKERS=4
      
      # Default Models
      - CANOPY_DEFAULT_MODELS=gpt-4o,claude-3-sonnet,gemini-pro
      
    volumes:
      # Persist logs
      - ./logs:/app/logs
      # Custom config
      - ./config:/app/config
      
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
      
    restart: unless-stopped
```

Run with Docker Compose:

```bash
# Create .env file
cat > .env << EOF
OPENROUTER_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
EOF

# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

## 💻 Using the Docker Container

### API Access

```python
from openai import OpenAI

# Connect to containerized Canopy
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed"
)

response = client.chat.completions.create(
    model="canopy-multi",
    messages=[{"role": "user", "content": "Hello from Docker!"}]
)
```

### CLI Access

```bash
# Run CLI commands inside container
docker exec -it canopy python -m canopy "What is Docker?" \
  --models gpt-4o claude-3-haiku

# Interactive mode
docker exec -it canopy python -m canopy \
  --models gpt-4o claude-3-haiku --interactive

# Access container shell
docker exec -it canopy /bin/bash
```

## 🎯 Production Deployment

### Dockerfile (Custom Build)

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install Canopy
RUN pip install --no-cache-dir -e .

# Create non-root user
RUN useradd -m -u 1000 canopy && chown -R canopy:canopy /app
USER canopy

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "-m", "canopy", "--serve", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: canopy
  labels:
    app: canopy
spec:
  replicas: 3
  selector:
    matchLabels:
      app: canopy
  template:
    metadata:
      labels:
        app: canopy
    spec:
      containers:
      - name: canopy
        image: canopy/canopy:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENROUTER_API_KEY
          valueFrom:
            secretKeyRef:
              name: canopy-secrets
              key: openrouter-api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: canopy-service
spec:
  selector:
    app: canopy
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

## 🔐 Security Best Practices

### 1. Use Secrets for API Keys

```bash
# Create Docker secret
echo "your_api_key" | docker secret create openrouter_key -

# Use in docker-compose.yml
services:
  canopy:
    image: canopy/canopy:latest
    secrets:
      - openrouter_key
    environment:
      - OPENROUTER_API_KEY_FILE=/run/secrets/openrouter_key

secrets:
  openrouter_key:
    external: true
```

### 2. Use .env File

```bash
# .env file (don't commit!)
OPENROUTER_API_KEY=sk-...
OPENAI_API_KEY=sk-...

# docker-compose.yml
env_file:
  - .env
```

### 3. Network Isolation

```yaml
services:
  canopy:
    networks:
      - canopy-network
      
networks:
  canopy-network:
    driver: bridge
```

## 🚀 Quick Commands

```bash
# Build and run
docker build -t canopy . && docker run -p 8000:8000 canopy

# Run with all environment variables
docker run -d \
  --name canopy \
  -p 8000:8000 \
  -e OPENROUTER_API_KEY=$OPENROUTER_API_KEY \
  -e CANOPY_DEFAULT_MODELS="gpt-4o,claude-3-sonnet" \
  -e CANOPY_WORKERS=4 \
  -v $(pwd)/logs:/app/logs \
  canopy/canopy:latest

# Quick test
docker run --rm canopy/canopy:latest \
  python -m canopy "Hello Docker!" --models gpt-4o-mini

# Development mode with live reload
docker run -it --rm \
  -v $(pwd):/app \
  -p 8000:8000 \
  canopy/canopy:dev

# Clean up
docker stop canopy && docker rm canopy
```

## 📊 Monitoring

### View Logs

```bash
# Follow logs
docker logs -f canopy

# Last 100 lines
docker logs --tail 100 canopy

# With timestamps
docker logs -t canopy
```

### Container Stats

```bash
# Resource usage
docker stats canopy

# Detailed inspection
docker inspect canopy
```

## 🐛 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs canopy

# Common issues:
# - Missing API keys: Ensure environment variables are set
# - Port conflict: Change -p 8000:8000 to -p 3000:8000
# - Memory issues: Increase Docker memory allocation
```

### Can't Connect to API

```bash
# Verify container is running
docker ps

# Test from inside container
docker exec canopy curl http://localhost:8000/health

# Check port mapping
docker port canopy
```

### Performance Issues

```bash
# Increase resources in docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
```

## 🎯 Next Steps

- Set up [monitoring](../monitoring.md) for production
- Configure [load balancing](../scaling.md) for high availability
- Implement [CI/CD pipeline](../ci-cd.md) for automated deployment
- Explore [Kubernetes deployment](../kubernetes.md) for scale

---

**Need help?** Check our [Docker FAQ](../docker-faq.md) or [open an issue](https://github.com/yourusername/canopy/issues)!