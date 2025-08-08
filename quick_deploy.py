#!/usr/bin/env python3
"""
One-Click Deployment Script for Enhanced GPU Chatbot
Handles all setup and deployment steps automatically
"""

import os
import subprocess
import sys
import time
from pathlib import Path

def print_banner():
    """Print deployment banner"""
    print("🚀 Enhanced GPU Chatbot - One-Click Deployment")
    print("=" * 50)
    print("This script will deploy your chatbot to Railway.app")
    print("Cost: $0-5/month | Setup Time: 5-10 minutes")
    print("=" * 50)

def run_command(command, description, check_output=False):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        if check_output:
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
        else:
            result = subprocess.run(command, shell=True)
        
        if result.returncode == 0:
            print(f"✅ {description} completed")
            return True
        else:
            print(f"❌ {description} failed")
            if check_output and result.stderr:
                print(f"   Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return False

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("\n🔍 Checking prerequisites...")
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ required")
        return False
    
    # Check if git is installed
    if not run_command("git --version", "Checking Git", check_output=True):
        print("❌ Git is not installed. Please install Git first.")
        return False
    
    # Check if we're in a git repository
    if not Path(".git").exists():
        print("❌ Not in a git repository")
        print("   Please initialize git: git init")
        return False
    
    print("✅ All prerequisites met")
    return True

def prepare_deployment():
    """Prepare the code for deployment"""
    print("\n📦 Preparing deployment...")
    
    # Add all files to git
    if not run_command("git add .", "Adding files to git"):
        return False
    
    # Commit changes
    if not run_command('git commit -m "Prepare for Railway deployment"', "Committing changes"):
        return False
    
    # Push to remote (if exists)
    run_command("git push", "Pushing to remote repository")
    
    print("✅ Deployment preparation completed")
    return True

def install_railway_cli():
    """Install Railway CLI"""
    print("\n📦 Installing Railway CLI...")
    
    # Check if Railway CLI is already installed
    if run_command("railway --version", "Checking Railway CLI", check_output=True):
        print("✅ Railway CLI is already installed")
        return True
    
    # Try to install with npm
    if run_command("npm install -g @railway/cli", "Installing Railway CLI"):
        return True
    
    print("❌ Failed to install Railway CLI")
    print("   Please install manually:")
    print("   1. Install Node.js from https://nodejs.org")
    print("   2. Run: npm install -g @railway/cli")
    return False

def deploy_to_railway():
    """Deploy to Railway"""
    print("\n🚀 Deploying to Railway...")
    
    # Login to Railway
    print("🔐 You'll be redirected to Railway login...")
    if not run_command("railway login", "Logging in to Railway"):
        return False
    
    # Deploy
    if not run_command("railway up", "Deploying application"):
        return False
    
    print("✅ Deployment completed!")
    return True

def get_railway_url():
    """Get the Railway URL"""
    print("\n🔗 Getting your application URL...")
    
    try:
        result = subprocess.run(["railway", "status"], capture_output=True, text=True)
        if result.returncode == 0:
            # Parse the output to find the URL
            output = result.stdout
            if "https://" in output:
                url = output.split("https://")[1].split()[0]
                return f"https://{url}"
    except:
        pass
    
    return None

def main():
    """Main deployment function"""
    print_banner()
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above.")
        return
    
    # Prepare deployment
    if not prepare_deployment():
        print("\n❌ Failed to prepare deployment.")
        return
    
    # Install Railway CLI
    if not install_railway_cli():
        print("\n❌ Failed to install Railway CLI.")
        return
    
    # Deploy
    if not deploy_to_railway():
        print("\n❌ Deployment failed.")
        return
    
    # Get URL
    url = get_railway_url()
    
    print("\n🎉 Deployment Successful!")
    print("=" * 50)
    if url:
        print(f"🌐 Your chatbot is live at: {url}")
        print(f"🔍 Health check: {url}/health/enhanced")
        print(f"📚 API docs: {url}/docs")
    else:
        print("🌐 Check your Railway dashboard for the URL")
    
    print("\n📋 Next steps:")
    print("   1. Test your chatbot at the URL above")
    print("   2. Configure environment variables in Railway dashboard")
    print("   3. Share your chatbot with others!")
    print("   4. Monitor usage and performance")
    
    print("\n💰 Cost Information:")
    print("   - Free tier: $0/month (limited usage)")
    print("   - Hobby plan: $5/month (1GB RAM)")
    print("   - Pro plan: $20/month (2GB RAM)")
    
    print("\n🆘 Need help?")
    print("   - Check the LOW_COST_HOSTING_GUIDE.md file")
    print("   - Visit Railway docs: https://docs.railway.app")
    print("   - Check your Railway dashboard for logs")

if __name__ == "__main__":
    main() 