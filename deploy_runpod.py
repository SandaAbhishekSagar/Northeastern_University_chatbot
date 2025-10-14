#!/usr/bin/env python3
"""
Automated RunPod Deployment Script
Deploys the enhanced GPU chatbot to RunPod.io
"""

import os
import sys
import json
import requests
from pathlib import Path

class RunPodDeployer:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('RUNPOD_API_KEY')
        self.base_url = "https://api.runpod.io/graphql"
        self.headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
    
    def check_api_key(self):
        """Check if API key is configured"""
        if not self.api_key:
            print("❌ RunPod API key not found!")
            print("")
            print("To get your API key:")
            print("1. Go to https://runpod.io")
            print("2. Sign up or log in")
            print("3. Go to Settings → API Keys")
            print("4. Create a new API key")
            print("")
            print("Then set it as environment variable:")
            print("  export RUNPOD_API_KEY='your-api-key'")
            print("")
            return False
        return True
    
    def list_gpu_types(self):
        """List available GPU types"""
        query = """
        query {
            gpuTypes {
                id
                displayName
                memoryInGb
                securePrice
                communityPrice
            }
        }
        """
        
        response = requests.post(
            self.base_url,
            headers=self.headers,
            json={"query": query}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('data', {}).get('gpuTypes', [])
        return []
    
    def create_pod(self, config):
        """Create a new pod on RunPod"""
        mutation = """
        mutation {
            podFindAndDeployOnDemand(
                input: {
                    cloudType: SECURE
                    gpuTypeId: "%s"
                    name: "%s"
                    imageName: "%s"
                    dockerArgs: "%s"
                    ports: "%s"
                    volumeInGb: %d
                    containerDiskInGb: %d
                    env: [
                        {key: "PORT", value: "8001"},
                        {key: "HOST", value: "0.0.0.0"},
                        {key: "CUDA_VISIBLE_DEVICES", value: "0"}
                    ]
                }
            ) {
                id
                desiredStatus
                imageName
                gpuTypeId
                ports
            }
        }
        """ % (
            config['gpu_type_id'],
            config['pod_name'],
            config['image_name'],
            config.get('docker_args', ''),
            config.get('ports', '8001/http,3000/http'),
            config.get('volume_gb', 50),
            config.get('container_disk_gb', 50)
        )
        
        response = requests.post(
            self.base_url,
            headers=self.headers,
            json={"query": mutation}
        )
        
        return response.json()
    
    def list_pods(self):
        """List all pods"""
        query = """
        query {
            myself {
                pods {
                    id
                    name
                    desiredStatus
                    runtime {
                        uptimeInSeconds
                        ports {
                            ip
                            isIpPublic
                            privatePort
                            publicPort
                        }
                    }
                    machine {
                        gpuDisplayName
                    }
                }
            }
        }
        """
        
        response = requests.post(
            self.base_url,
            headers=self.headers,
            json={"query": query}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('data', {}).get('myself', {}).get('pods', [])
        return []
    
    def display_gpu_options(self, gpu_types):
        """Display available GPU options"""
        print("📊 Available GPU Types:")
        print("=" * 80)
        print(f"{'#':<4} {'GPU Name':<20} {'VRAM':<10} {'Price/hr':<12} {'Monthly*':<12}")
        print("=" * 80)
        
        recommended_gpus = ['RTX 3060', 'RTX A4000', 'RTX 3070', 'RTX 3080', 'A10']
        
        for idx, gpu in enumerate(gpu_types, 1):
            name = gpu['displayName']
            vram = f"{gpu['memoryInGb']}GB"
            price = f"${gpu.get('securePrice', 0):.2f}"
            monthly = f"${gpu.get('securePrice', 0) * 730:.0f}"
            
            # Highlight recommended GPUs
            marker = "⭐" if any(rec in name for rec in recommended_gpus) else "  "
            
            print(f"{marker} {idx:<2} {name:<20} {vram:<10} {price:<12} {monthly:<12}")
        
        print("=" * 80)
        print("* Monthly cost = hourly price × 730 hours (assumes 24/7 usage)")
        print("⭐ = Recommended for this chatbot")
        print("")

def main():
    """Main deployment flow"""
    print("=" * 80)
    print("🚀 RunPod Automated Deployment")
    print("Enhanced GPU Chatbot for Northeastern University")
    print("=" * 80)
    print("")
    
    # Initialize deployer
    deployer = RunPodDeployer()
    
    # Check API key
    if not deployer.check_api_key():
        sys.exit(1)
    
    print("✅ RunPod API key found")
    print("")
    
    # Get GPU types
    print("📡 Fetching available GPU types...")
    gpu_types = deployer.list_gpu_types()
    
    if not gpu_types:
        print("❌ Failed to fetch GPU types. Please check your API key.")
        sys.exit(1)
    
    print(f"✅ Found {len(gpu_types)} GPU types")
    print("")
    
    # Display options
    deployer.display_gpu_options(gpu_types)
    
    # Get user input
    print("🔧 Configuration:")
    print("")
    
    # Docker image
    default_image = "yourusername/university-chatbot-gpu:latest"
    image_name = input(f"Docker image [{default_image}]: ").strip()
    if not image_name:
        image_name = default_image
    
    # Pod name
    default_name = "northeastern-chatbot-gpu"
    pod_name = input(f"Pod name [{default_name}]: ").strip()
    if not pod_name:
        pod_name = default_name
    
    # GPU selection
    print("")
    print("Recommended GPUs for your chatbot:")
    print("  • RTX 3060 (12GB) - ~$0.24/hr (~$175/month) - Best value")
    print("  • RTX A4000 (16GB) - ~$0.34/hr (~$250/month) - More VRAM")
    print("  • RTX 3070 (8GB) - ~$0.30/hr (~$220/month) - Good performance")
    print("")
    
    gpu_choice = input("Select GPU number from the list above: ").strip()
    
    try:
        gpu_idx = int(gpu_choice) - 1
        if gpu_idx < 0 or gpu_idx >= len(gpu_types):
            print("❌ Invalid GPU selection")
            sys.exit(1)
        
        selected_gpu = gpu_types[gpu_idx]
        print(f"✅ Selected: {selected_gpu['displayName']} ({selected_gpu['memoryInGb']}GB)")
        print(f"   Price: ${selected_gpu['securePrice']:.2f}/hour (~${selected_gpu['securePrice'] * 730:.0f}/month)")
    except ValueError:
        print("❌ Invalid input")
        sys.exit(1)
    
    print("")
    
    # Confirm deployment
    print("=" * 80)
    print("📋 Deployment Summary:")
    print("=" * 80)
    print(f"  • Docker Image: {image_name}")
    print(f"  • Pod Name: {pod_name}")
    print(f"  • GPU: {selected_gpu['displayName']} ({selected_gpu['memoryInGb']}GB)")
    print(f"  • Price: ${selected_gpu['securePrice']:.2f}/hour")
    print(f"  • Estimated Monthly: ${selected_gpu['securePrice'] * 730:.0f}")
    print(f"  • Storage: 50GB")
    print(f"  • Ports: 8001 (API), 3000 (Frontend)")
    print("=" * 80)
    print("")
    
    confirm = input("Deploy now? (yes/no): ").strip().lower()
    
    if confirm not in ['yes', 'y']:
        print("❌ Deployment cancelled")
        sys.exit(0)
    
    # Create pod
    print("")
    print("🚀 Creating pod on RunPod...")
    
    config = {
        'gpu_type_id': selected_gpu['id'],
        'pod_name': pod_name,
        'image_name': image_name,
        'ports': '8001/http,3000/http',
        'volume_gb': 50,
        'container_disk_gb': 50
    }
    
    result = deployer.create_pod(config)
    
    # Check result
    if 'errors' in result:
        print("❌ Deployment failed!")
        print(json.dumps(result['errors'], indent=2))
        sys.exit(1)
    
    pod_data = result.get('data', {}).get('podFindAndDeployOnDemand')
    
    if pod_data:
        print("=" * 80)
        print("✅ Pod deployed successfully!")
        print("=" * 80)
        print(f"  • Pod ID: {pod_data['id']}")
        print(f"  • Name: {pod_name}")
        print(f"  • Status: {pod_data['desiredStatus']}")
        print(f"  • GPU: {selected_gpu['displayName']}")
        print("=" * 80)
        print("")
        print("🔗 Next Steps:")
        print("  1. Go to https://runpod.io/console/pods")
        print("  2. Find your pod: " + pod_name)
        print("  3. Wait for it to start (may take 2-5 minutes)")
        print("  4. Click 'Connect' to get the public URL")
        print("  5. Access your chatbot:")
        print("     - API: https://[pod-id]-8001.proxy.runpod.net")
        print("     - Frontend: https://[pod-id]-3000.proxy.runpod.net")
        print("")
        print("🎉 Your enhanced GPU chatbot is now running in the cloud!")
        print("=" * 80)
    else:
        print("❌ Failed to create pod. Please check the response:")
        print(json.dumps(result, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Deployment cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

