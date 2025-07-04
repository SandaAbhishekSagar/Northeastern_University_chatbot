#!/usr/bin/env python3
"""
Main runner for the University Chatbot System
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and handle output"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True
        )
        if result.returncode != 0:
            print(f"Error running command: {command}")
            print(f"Error output: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"Exception running command {command}: {e}")
        return False

def setup_database():
    """Initialize the database"""
    print("Setting up database...")
    return run_command("python services/shared/database.py")

def start_celery_worker():
    """Start Celery worker"""
    print("Starting Celery worker...")
    return run_command("celery -A services.processing_service.tasks worker --loglevel=info", cwd=".")

def start_celery_beat():
    """Start Celery beat scheduler"""
    print("Starting Celery beat scheduler...")
    return run_command("celery -A services.processing_service.tasks beat --loglevel=info", cwd=".")

def start_api_server():
    """Start the FastAPI server"""
    print("Starting API server...")
    return run_command("python -m uvicorn services.chat_service.api:app --host 0.0.0.0 --port 8001", cwd=".")

def run_scraper(university_urls=None):
    """Run the web scraper"""
    print("Running web scraper...")
    
    if university_urls:
        scrapy_cmd = f"scrapy crawl university -a university_urls='{university_urls}'"
        print(f"Scraping URLs: {university_urls}")
    else:
        scrapy_cmd = "scrapy crawl university"
        print("Using default URLs from spider configuration")
    
    return run_command(scrapy_cmd, cwd="services/scraping_service")

def main():
    if len(sys.argv) < 2:
        print("Usage: python run.py [setup|scrape|worker|beat|api|all] [--university_urls=url1,url2,...]")
        print("\nCommands:")
        print("  setup  - Initialize database")
        print("  scrape - Run web scraper once")
        print("  worker - Start Celery worker")
        print("  beat   - Start Celery beat scheduler")
        print("  api    - Start API server")
        print("  all    - Start all services")
        print("\nOptions:")
        print("  --university_urls=url1,url2,... - Specify URLs to scrape")
        return
    
    command = sys.argv[1].lower()
    
    # Parse university URLs from command line arguments
    university_urls = None
    for arg in sys.argv[2:]:
        if arg.startswith('--university_urls='):
            university_urls = arg.split('=', 1)[1]
            break
    
    if command == "setup":
        setup_database()
    
    elif command == "scrape":
        run_scraper(university_urls)
    
    elif command == "worker":
        start_celery_worker()
    
    elif command == "beat":
        start_celery_beat()
    
    elif command == "api":
        start_api_server()
    
    elif command == "all":
        print("Starting all services...")
        setup_database()
        print("Database setup complete!")
        
        print("\nTo run all services, open separate terminals and run:")
        print("1. python run.py worker")
        print("2. python run.py beat")
        print("3. python run.py api")
        print("4. python run.py scrape  # (optional, to run scraper manually)")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()