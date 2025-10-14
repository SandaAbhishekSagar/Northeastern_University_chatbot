#!/bin/bash

# Cloud GPU Deployment Script
# Supports: RunPod, Vast.ai, Lambda Labs, and other cloud GPU providers

set -e

echo "======================================"
echo "🚀 Cloud GPU Deployment Helper"
echo "======================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DOCKER_USERNAME="${DOCKER_USERNAME:-yourusername}"
IMAGE_NAME="university-chatbot-gpu"
IMAGE_TAG="${IMAGE_TAG:-latest}"
FULL_IMAGE_NAME="$DOCKER_USERNAME/$IMAGE_NAME:$IMAGE_TAG"

# Functions
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Step 1: Check prerequisites
echo "📋 Step 1: Checking prerequisites..."
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi
print_success "Docker is installed"

# Check if docker-compose is installed (optional)
if command -v docker-compose &> /dev/null; then
    print_success "Docker Compose is installed"
else
    print_info "Docker Compose is not installed (optional)"
fi

echo ""

# Step 2: Build Docker image
echo "🔨 Step 2: Building Docker image..."
echo ""

read -p "Do you want to build the Docker image? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Building Docker image: $FULL_IMAGE_NAME"
    
    # Build with production Dockerfile
    if [ -f "Dockerfile.production" ]; then
        docker build -f Dockerfile.production -t $FULL_IMAGE_NAME .
    else
        docker build -t $FULL_IMAGE_NAME .
    fi
    
    if [ $? -eq 0 ]; then
        print_success "Docker image built successfully"
    else
        print_error "Failed to build Docker image"
        exit 1
    fi
else
    print_info "Skipping Docker build"
fi

echo ""

# Step 3: Test Docker image locally
echo "🧪 Step 3: Test Docker image locally (optional)..."
echo ""

read -p "Do you want to test the image locally? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Running Docker container locally..."
    print_info "This will start the container on ports 8001 (API) and 3000 (Frontend)"
    print_info "Press Ctrl+C to stop the test"
    
    docker run --rm -it \
        --gpus all \
        -p 8001:8001 \
        -p 3000:3000 \
        -e PORT=8001 \
        -e HOST=0.0.0.0 \
        $FULL_IMAGE_NAME
    
    print_success "Local test completed"
else
    print_info "Skipping local test"
fi

echo ""

# Step 4: Push to Docker Hub
echo "📤 Step 4: Push to Docker Hub..."
echo ""

read -p "Do you want to push the image to Docker Hub? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Logging into Docker Hub..."
    docker login
    
    if [ $? -eq 0 ]; then
        print_success "Logged into Docker Hub"
        
        print_info "Pushing image: $FULL_IMAGE_NAME"
        docker push $FULL_IMAGE_NAME
        
        if [ $? -eq 0 ]; then
            print_success "Image pushed successfully"
            print_info "Image URL: $FULL_IMAGE_NAME"
        else
            print_error "Failed to push image"
            exit 1
        fi
    else
        print_error "Failed to login to Docker Hub"
        exit 1
    fi
else
    print_info "Skipping Docker Hub push"
fi

echo ""

# Step 5: Deployment instructions
echo "======================================"
echo "🎉 Build Complete!"
echo "======================================"
echo ""
echo "Your Docker image is ready: $FULL_IMAGE_NAME"
echo ""
echo "📝 Next Steps:"
echo ""
echo "🔹 RunPod Deployment:"
echo "   1. Go to https://runpod.io"
echo "   2. Click 'Deploy' → 'New Pod'"
echo "   3. Select GPU: RTX 3060 (12GB) or better"
echo "   4. Choose 'Docker' deployment"
echo "   5. Image: $FULL_IMAGE_NAME"
echo "   6. Ports: 8001, 3000"
echo "   7. GPU: 1x GPU"
echo "   8. RAM: 16GB+"
echo "   9. Storage: 50GB+"
echo "   10. Click 'Deploy'"
echo ""
echo "🔹 Vast.ai Deployment:"
echo "   1. Install CLI: pip install vastai"
echo "   2. Login: vastai set api-key YOUR_API_KEY"
echo "   3. Search: vastai search offers 'gpu_name=RTX 3060 reliability > 0.99'"
echo "   4. Create: vastai create instance OFFER_ID --image $FULL_IMAGE_NAME"
echo ""
echo "🔹 Lambda Labs Deployment:"
echo "   1. Sign up at https://lambdalabs.com"
echo "   2. Launch instance (A10 or RTX 6000)"
echo "   3. SSH into instance"
echo "   4. Run: docker run -d -p 8001:8001 -p 3000:3000 --gpus all $FULL_IMAGE_NAME"
echo ""
echo "🔹 Manual SSH Deployment:"
echo "   1. SSH into your GPU instance"
echo "   2. Run: docker pull $FULL_IMAGE_NAME"
echo "   3. Run: docker run -d -p 8001:8001 -p 3000:3000 --gpus all $FULL_IMAGE_NAME"
echo ""
echo "======================================"
echo "📊 Estimated Monthly Costs:"
echo "======================================"
echo "• Vast.ai:       \$85-110   (RTX 3060, Budget)"
echo "• TensorDock:    \$145-180  (RTX 3060)"
echo "• RunPod:        \$180-200  (RTX 3060, Recommended)"
echo "• Lambda Labs:   \$599      (A10, Enterprise)"
echo ""
echo "✨ For detailed instructions, see: CLOUD_GPU_DEPLOYMENT_GUIDE.md"
echo ""

