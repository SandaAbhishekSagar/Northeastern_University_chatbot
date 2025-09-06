# 🐳 Docker Deployment Guide - Northeastern University Chatbot

This guide will help you deploy the fixed Northeastern University Chatbot using Docker.

## 🚀 Quick Start

### 1. Build the Docker Image

```bash
# Make the build script executable (Linux/Mac)
chmod +x build_docker.sh

# Run the build script
./build_docker.sh
```

Or build manually:
```bash
docker build -t northeastern-chatbot:latest .
```

### 2. Run the Container

```bash
# Basic run
docker run -p 8001:8001 northeastern-chatbot:latest

# With OpenAI API key
docker run -p 8001:8001 -e OPENAI_API_KEY=your_api_key_here northeastern-chatbot:latest

# With custom environment file
docker run -p 8001:8001 --env-file .env northeastern-chatbot:latest
```

### 3. Access the Application

- **Chat Interface**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Required for ChatGPT integration
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Pinecone configuration
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment

# Optional: Custom settings
CHROMADB_HOST=localhost
CHROMADB_PORT=8000
UNIVERSITY_NAME=Northeastern University
UNIVERSITY_URL=https://www.northeastern.edu
EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_MODEL=gpt-3.5-turbo
```

### Docker Compose (Recommended)

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  northeastern-chatbot:
    build: .
    ports:
      - "8001:8001"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - PINECONE_API_KEY=${PINECONE_API_KEY}
      - PINECONE_ENVIRONMENT=${PINECONE_ENVIRONMENT}
    volumes:
      - ./chroma_data:/app/chroma_data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Run with Docker Compose:
```bash
docker-compose up -d
```

## 🏗️ Production Deployment

### 1. Cloud Deployment (Railway, Heroku, etc.)

The Dockerfile is optimized for cloud deployment. Key features:
- ✅ No Ollama dependency (removed network issues)
- ✅ ChatGPT integration for better reliability
- ✅ Health checks for monitoring
- ✅ Proper error handling and fallbacks

### 2. Environment Setup

For production deployment, ensure you have:
- OpenAI API key configured
- Proper environment variables set
- Health check endpoint accessible
- Logging configured

### 3. Monitoring

The application includes:
- Health check endpoint at `/health`
- Structured logging
- Error handling with fallbacks
- Database connection monitoring

## 🔍 Troubleshooting

### Common Issues

1. **Build Fails with Network Error**
   - ✅ **Fixed**: Removed Ollama installation that was causing network issues
   - The new Dockerfile only installs Python dependencies

2. **API Key Not Working**
   - Ensure `OPENAI_API_KEY` is set correctly
   - Check the API key has sufficient credits
   - Verify the key is valid

3. **Database Connection Issues**
   - The system automatically falls back to ChromaDB if Pinecone fails
   - Check logs for specific error messages

4. **Port Already in Use**
   - Change the port mapping: `docker run -p 8002:8001 northeastern-chatbot:latest`
   - Or stop the existing container: `docker stop $(docker ps -q)`

### Logs and Debugging

```bash
# View container logs
docker logs <container_id>

# Follow logs in real-time
docker logs -f <container_id>

# Access container shell
docker exec -it <container_id> /bin/bash
```

## 📊 Performance Optimization

### Resource Limits

```bash
# Run with resource limits
docker run -p 8001:8001 \
  --memory=2g \
  --cpus=2 \
  northeastern-chatbot:latest
```

### Scaling

For high-traffic scenarios:
- Use a load balancer (nginx, traefik)
- Deploy multiple container instances
- Use a managed database service
- Implement caching strategies

## 🔒 Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **Environment Variables**: Use Docker secrets or environment files
3. **Network**: Use Docker networks for service isolation
4. **Updates**: Regularly update base images and dependencies

## 📈 Monitoring and Maintenance

### Health Checks

The application provides health check endpoints:
- `/health` - Basic health check
- `/docs` - API documentation
- Container health checks via Docker

### Updates

To update the application:
1. Pull the latest code
2. Rebuild the Docker image
3. Restart the container
4. Verify health checks pass

## 🆘 Support

If you encounter issues:
1. Check the logs: `docker logs <container_id>`
2. Verify environment variables
3. Test the health endpoint
4. Check the API documentation at `/docs`

## 🎯 Key Features of the Fixed System

- ✅ **ChatGPT Integration**: Uses OpenAI's ChatGPT API instead of Ollama
- ✅ **URL Handling**: Properly displays actual website URLs from scraped content
- ✅ **Fallback Support**: Automatically falls back to ChromaDB if Pinecone fails
- ✅ **Error Handling**: Comprehensive error handling and recovery
- ✅ **Health Monitoring**: Built-in health checks and monitoring
- ✅ **Production Ready**: Optimized for production deployment

The system is now ready for reliable production deployment! 🚀
