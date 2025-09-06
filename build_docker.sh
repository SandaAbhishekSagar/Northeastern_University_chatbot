#!/bin/bash

# Northeastern University Chatbot - Docker Build Script
# This script builds the Docker image for the fixed chatbot system

echo "🐳 Building Northeastern University Chatbot Docker Image"
echo "=================================================="

# Set image name and tag
IMAGE_NAME="northeastern-chatbot"
TAG="latest"
FULL_IMAGE_NAME="${IMAGE_NAME}:${TAG}"

echo "📦 Image: ${FULL_IMAGE_NAME}"
echo ""

# Build the Docker image
echo "🔨 Building Docker image..."
docker build -t "${FULL_IMAGE_NAME}" .

# Check if build was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Docker image built successfully!"
    echo "📋 Image details:"
    docker images "${IMAGE_NAME}"
    echo ""
    echo "🚀 To run the container:"
    echo "   docker run -p 8001:8001 ${FULL_IMAGE_NAME}"
    echo ""
    echo "🔧 To run with environment variables:"
    echo "   docker run -p 8001:8001 -e OPENAI_API_KEY=your_key_here ${FULL_IMAGE_NAME}"
    echo ""
    echo "📚 To access the application:"
    echo "   - Chat Interface: http://localhost:8001"
    echo "   - API Docs: http://localhost:8001/docs"
    echo "   - Health Check: http://localhost:8001/health"
else
    echo ""
    echo "❌ Docker build failed!"
    echo "Please check the error messages above and try again."
    exit 1
fi
