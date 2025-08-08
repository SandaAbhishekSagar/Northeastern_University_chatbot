#!/bin/bash

# 🚀 Elastic Beanstalk Setup Script for Northeastern University Chatbot
# This script prepares your application for AWS Elastic Beanstalk deployment

set -e  # Exit on any error

echo "🚀 Setting up Northeastern University Chatbot for Elastic Beanstalk"
echo "=================================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "requirements.txt" ] || [ ! -d "services" ]; then
    print_error "Please run this script from the university_chatbot root directory"
    exit 1
fi

# Create Elastic Beanstalk directory
print_status "Creating Elastic Beanstalk deployment directory..."
EB_DIR="northeastern-chatbot-eb"
rm -rf $EB_DIR
mkdir -p $EB_DIR
cd $EB_DIR

# Copy application files
print_status "Copying application files..."
cp -r ../services .
cp -r ../frontend .
cp ../requirements.txt .
cp ../start_enhanced_gpu_system.py .
cp ../start_production.py .

# Create .ebextensions directory
print_status "Creating Elastic Beanstalk configuration..."
mkdir -p .ebextensions

# Create 01_packages.config
print_status "Creating packages configuration..."
cat > .ebextensions/01_packages.config << 'EOF'
packages:
  yum:
    python3.9: []
    python3.9-pip: []
    git: []
    nginx: []
    docker: []
    htop: []
    wget: []
    curl: []
    unzip: []
    build-essential: []
    python3.9-dev: []
    python3.9-venv: []
EOF

# Create 02_commands.config
print_status "Creating container commands configuration..."
cat > .ebextensions/02_commands.config << 'EOF'
container_commands:
  01_install_nodejs:
    command: |
      curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
      export NVM_DIR="$HOME/.nvm"
      [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
      nvm install 16
      nvm use 16
      nvm alias default 16
  02_install_pm2:
    command: |
      export NVM_DIR="$HOME/.nvm"
      [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
      npm install -g pm2
  03_setup_python:
    command: |
      python3.9 -m venv /opt/python/run/venv
      source /opt/python/run/venv/bin/activate
      pip install --upgrade pip
      pip install -r requirements.txt
      pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
      pip install sentence-transformers transformers
  04_create_startup_script:
    command: |
      cat > /opt/python/run/start_production_gpu.py << 'EOF'
      #!/usr/bin/env python3
      import os
      import subprocess
      import sys
      import torch
      import gc
      from pathlib import Path

      def main():
          # Set environment variables
          os.environ['PORT'] = '8001'
          os.environ['HOST'] = '0.0.0.0'
          os.environ['CUDA_VISIBLE_DEVICES'] = '0'
          
          # GPU optimization
          if torch.cuda.is_available():
              torch.cuda.empty_cache()
              gc.collect()
              print(f"🚀 GPU detected: {torch.cuda.get_device_name(0)}")
          else:
              print("⚠️  No GPU detected, using CPU")
          
          # Change to project directory
          project_dir = Path('/var/app/current')
          os.chdir(project_dir)
          
          print("🚀 Starting Northeastern University Chatbot with GPU support...")
          print(f"📍 Project directory: {project_dir}")
          print(f"🔧 CUDA device: {os.environ.get('CUDA_VISIBLE_DEVICES', 'Not set')}")
          
          # Start API server
          api_process = subprocess.Popen([
              sys.executable, '-m', 'uvicorn',
              'services.chat_service.enhanced_gpu_api:app',
              '--host', '0.0.0.0',
              '--port', '8001',
              '--reload'
          ])
          
          # Start frontend server
          frontend_process = subprocess.Popen([
              'python3', '-m', 'http.server', '3000'
          ], cwd='frontend')
          
          try:
              print("✅ Both API and frontend servers started successfully!")
              print("🌐 Frontend: http://localhost:3000")
              print("🔌 API: http://localhost:8001")
              print("📊 Health check: http://localhost:8001/health")
              
              # Wait for processes
              api_process.wait()
              frontend_process.wait()
          except KeyboardInterrupt:
              print("\n🛑 Shutting down servers...")
              api_process.terminate()
              frontend_process.terminate()
              print("✅ Servers stopped successfully!")

      if __name__ == "__main__":
          main()
      EOF
      chmod +x /opt/python/run/start_production_gpu.py
  05_create_pm2_config:
    command: |
      cat > /opt/python/run/ecosystem.config.js << 'EOF'
      module.exports = {
        apps: [
          {
            name: 'northeastern-chatbot-api',
            script: '/opt/python/run/start_production_gpu.py',
            interpreter: '/opt/python/run/venv/bin/python',
            cwd: '/var/app/current',
            env: {
              PORT: '8001',
              HOST: '0.0.0.0',
              CUDA_VISIBLE_DEVICES: '0',
              NODE_ENV: 'production'
            },
            instances: 1,
            autorestart: true,
            watch: false,
            max_memory_restart: '2G',
            log_file: '/var/log/eb-python-app/api.log',
            error_file: '/var/log/eb-python-app/api-error.log',
            out_file: '/var/log/eb-python-app/api-out.log',
            log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
          }
        ]
      };
      EOF
EOF

# Create 03_nginx.config
print_status "Creating Nginx configuration..."
cat > .ebextensions/03_nginx.config << 'EOF'
files:
  "/etc/nginx/conf.d/proxy.conf":
    mode: "000644"
    owner: root
    group: root
    content: |
      upstream backend {
          server 127.0.0.1:8001;
      }
      
      server {
          listen 80;
          server_name _;
          
          # Frontend
          location / {
              proxy_pass http://127.0.0.1:3000;
              proxy_http_version 1.1;
              proxy_set_header Upgrade $http_upgrade;
              proxy_set_header Connection 'upgrade';
              proxy_set_header Host $host;
              proxy_set_header X-Real-IP $remote_addr;
              proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
              proxy_set_header X-Forwarded-Proto $scheme;
              proxy_cache_bypass $http_upgrade;
              proxy_read_timeout 300s;
              proxy_connect_timeout 75s;
          }
          
          # API
          location /api/ {
              proxy_pass http://backend/;
              proxy_http_version 1.1;
              proxy_set_header Upgrade $http_upgrade;
              proxy_set_header Connection 'upgrade';
              proxy_set_header Host $host;
              proxy_set_header X-Real-IP $remote_addr;
              proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
              proxy_set_header X-Forwarded-Proto $scheme;
              proxy_cache_bypass $http_upgrade;
              proxy_read_timeout 300s;
              proxy_connect_timeout 75s;
          }
          
          # Health check
          location /health {
              proxy_pass http://backend/health;
              proxy_set_header Host $host;
              proxy_set_header X-Real-IP $remote_addr;
              proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
              proxy_set_header X-Forwarded-Proto $scheme;
          }
      }

container_commands:
  01_reload_nginx:
    command: "service nginx reload"
EOF

# Create 04_application.config
print_status "Creating application configuration..."
cat > .ebextensions/04_application.config << 'EOF'
option_settings:
  aws:elasticbeanstalk:application:environment:
    PYTHONPATH: "/var/app/current"
    CUDA_VISIBLE_DEVICES: "0"
    PYTORCH_CUDA_ALLOC_CONF: "max_split_size_mb:512"
    TOKENIZERS_PARALLELISM: "false"
  
  aws:elasticbeanstalk:container:python:
    WSGIPath: "start_production_gpu.py"
    NumProcesses: 1
    NumThreads: 1
  
  aws:elasticbeanstalk:environment:proxy:staticfiles:
    /static: frontend/
  
  aws:autoscaling:launchconfiguration:
    InstanceType: g4dn.xlarge
    IamInstanceProfile: aws-elasticbeanstalk-ec2-role
  
  aws:autoscaling:asg:
    MinSize: 1
    MaxSize: 3
  
  aws:elasticbeanstalk:environment:
    EnvironmentType: LoadBalanced
    LoadBalancerType: application
EOF

# Create Procfile
print_status "Creating Procfile..."
cat > Procfile << 'EOF'
web: pm2 start ecosystem.config.js && pm2 logs northeastern-chatbot-api
EOF

# Create application.py for Elastic Beanstalk
print_status "Creating application.py entry point..."
cat > application.py << 'EOF'
#!/usr/bin/env python3
"""
Elastic Beanstalk entry point for Northeastern University Chatbot
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    # Set environment variables
    os.environ['PORT'] = '8001'
    os.environ['HOST'] = '0.0.0.0'
    os.environ['CUDA_VISIBLE_DEVICES'] = '0'
    
    # Change to project directory
    project_dir = Path('/var/app/current')
    os.chdir(project_dir)
    
    print("🚀 Starting Northeastern University Chatbot on Elastic Beanstalk...")
    print(f"📍 Project directory: {project_dir}")
    
    # Start the API server
    api_process = subprocess.Popen([
        sys.executable, '-m', 'uvicorn',
        'services.chat_service.enhanced_gpu_api:app',
        '--host', '0.0.0.0',
        '--port', '8001',
        '--reload'
    ])
    
    # Start frontend server
    frontend_process = subprocess.Popen([
        'python3', '-m', 'http.server', '3000'
    ], cwd='frontend')
    
    try:
        print("✅ Both API and frontend servers started successfully!")
        print("🌐 Frontend: http://localhost:3000")
        print("🔌 API: http://localhost:8001")
        print("📊 Health check: http://localhost:8001/health")
        
        # Wait for processes
        api_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        api_process.terminate()
        frontend_process.terminate()
        print("✅ Servers stopped successfully!")

if __name__ == "__main__":
    main()
EOF

# Create deployment package
print_status "Creating deployment package..."
zip -r northeastern-chatbot-eb.zip . -x "*.git*" "*.pyc" "__pycache__/*" "*.log" "*.pkl" "chroma_data/*" "env_py3.9/*"

# Create deployment instructions
print_status "Creating deployment instructions..."
cat > DEPLOYMENT_INSTRUCTIONS.md << 'EOF'
# 🚀 Elastic Beanstalk Deployment Instructions

## Quick Deployment Steps:

### 1. Go to AWS Elastic Beanstalk Console
- Visit: https://console.aws.amazon.com/elasticbeanstalk/
- Click "Create Application"

### 2. Create Application
```
Application name: northeastern-chatbot
Platform: Python
Platform branch: Python 3.9
Platform version: 3.9.18
```

### 3. Upload Code
- Choose "Upload your code"
- Upload: `northeastern-chatbot-eb.zip`
- Click "Configure more options"

### 4. Configure Environment
- **Software**: Add environment variables
- **Instances**: Set instance type to g4dn.xlarge
- **Capacity**: Set Min=1, Max=3
- **Load Balancer**: Application Load Balancer

### 5. Deploy
- Click "Create environment"
- Wait 10-15 minutes for deployment

## Your Application URL:
- Will be: `http://northeastern-chatbot.region.elasticbeanstalk.com`
- Test: `http://your-url/health`

## Cost:
- ~$396/month (g4dn.xlarge + Load Balancer)
- Use spot instances for 70% savings
EOF

print_success "Elastic Beanstalk setup completed!"
echo ""
echo "📦 Files created:"
echo "  - northeastern-chatbot-eb.zip (deployment package)"
echo "  - DEPLOYMENT_INSTRUCTIONS.md (deployment guide)"
echo ""
echo "🚀 Next steps:"
echo "  1. Go to AWS Elastic Beanstalk Console"
echo "  2. Create new application"
echo "  3. Upload northeastern-chatbot-eb.zip"
echo "  4. Configure for g4dn.xlarge instance"
echo "  5. Deploy!"
echo ""
echo "💰 Expected cost: ~$396/month (or $118/month with spot instances)"
echo "" 