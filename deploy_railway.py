#!/usr/bin/env python3
"""
Railway.app Deployment Script
Automates the deployment process for the Enhanced GPU Chatbot
"""

import os
import subprocess
import sys
from pathlib import Path

def check_requirements():
    """Check if all required files exist"""
    required_files = [
        "start_production.py",
        "Procfile", 
        "railway.json",
        "requirements.txt",
        "services/chat_service/enhanced_gpu_api.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files found")
    return True

def check_git_status():
    """Check if git repository is ready for deployment"""
    try:
        # Check if we're in a git repository
        result = subprocess.run(["git", "status"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Not in a git repository")
            return False
        
        # Check if there are uncommitted changes
        result = subprocess.run(["git", "diff", "--quiet"], capture_output=True)
        if result.returncode != 0:
            print("⚠️  You have uncommitted changes")
            print("   Please commit your changes before deploying:")
            print("   git add .")
            print("   git commit -m 'Prepare for deployment'")
            return False
        
        print("✅ Git repository is ready")
        return True
        
    except FileNotFoundError:
        print("❌ Git is not installed")
        return False

def install_railway_cli():
    """Install Railway CLI if not already installed"""
    try:
        # Check if Railway CLI is installed
        result = subprocess.run(["railway", "--version"], capture_output=True)
        if result.returncode == 0:
            print("✅ Railway CLI is already installed")
            return True
    except FileNotFoundError:
        pass
    
    print("📦 Installing Railway CLI...")
    try:
        # Try to install with npm
        result = subprocess.run(["npm", "install", "-g", "@railway/cli"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Railway CLI installed successfully")
            return True
        else:
            print("❌ Failed to install Railway CLI with npm")
            print("   Please install manually: npm install -g @railway/cli")
            return False
    except FileNotFoundError:
        print("❌ npm is not installed")
        print("   Please install Node.js and npm first")
        return False

def deploy_to_railway():
    """Deploy the application to Railway"""
    print("\n🚀 Deploying to Railway...")
    
    try:
        # Login to Railway
        print("🔐 Logging in to Railway...")
        result = subprocess.run(["railway", "login"], input="y\n", text=True)
        if result.returncode != 0:
            print("❌ Failed to login to Railway")
            return False
        
        # Deploy the application
        print("📤 Deploying application...")
        result = subprocess.run(["railway", "up"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Deployment successful!")
            print("\n🎉 Your Enhanced GPU Chatbot is now live!")
            print("   Check your Railway dashboard for the URL")
            return True
        else:
            print("❌ Deployment failed")
            print("   Error:", result.stderr)
            return False
            
    except FileNotFoundError:
        print("❌ Railway CLI not found")
        return False

def main():
    """Main deployment function"""
    print("🚀 Railway.app Deployment Script")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Please fix the missing files before deploying")
        return
    
    # Check git status
    if not check_git_status():
        print("\n❌ Please fix git issues before deploying")
        return
    
    # Install Railway CLI
    if not install_railway_cli():
        print("\n❌ Please install Railway CLI before deploying")
        return
    
    # Deploy
    if deploy_to_railway():
        print("\n🎉 Deployment completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Check your Railway dashboard")
        print("   2. Configure environment variables")
        print("   3. Test your application")
        print("   4. Share your public URL")
    else:
        print("\n❌ Deployment failed")
        print("   Please check the error messages above")

if __name__ == "__main__":
    main() 