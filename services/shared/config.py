import os
from pathlib import Path

# Try to load environment variables
try:
    from dotenv import load_dotenv
    
    # Find .env file
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent
    env_file = project_root / '.env'
    
    if env_file.exists():
        load_dotenv(env_file)
        print(f"[OK] Loaded .env from: {env_file}")
    else:
        print(f"[WARNING] No .env file found at: {env_file}")
        print("Using default values")
        
except ImportError:
    print("[WARNING] python-dotenv not installed. Using environment variables only.")

class Config:
    # ChromaDB settings
    CHROMADB_HOST = os.getenv("CHROMADB_HOST", "localhost")
    CHROMADB_HTTP_PORT = int(os.getenv("CHROMADB_HTTP_PORT", 8000))
    CHROMADB_PORT = int(os.getenv("CHROMADB_PORT", 8000))
    
    # Redis URL
    REDIS_URL = os.getenv(
        "REDIS_URL", 
        "redis://localhost:6379/0"
    )
    
    # Local LLM settings (Ollama - no API key needed!)
    LOCAL_LLM_MODEL = os.getenv("LOCAL_LLM_MODEL", "llama2:7b")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # OpenAI settings (for OpenAI-powered chatbot)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # Options: gpt-4o-mini (recommended), gpt-4o, gpt-4, o4-mini-2025-04-16
    
    # Scraping settings
    SCRAPING_DELAY = int(os.getenv("SCRAPING_DELAY", 3))
    MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", 2))
    USER_AGENT = os.getenv("USER_AGENT", "UniversityResearchBot/1.0")
    
    # University URLs
    urls_string = os.getenv("UNIVERSITY_URLS", "https://www.northeastern.edu,https://catalog.northeastern.edu")
    UNIVERSITY_URLS = [url.strip() for url in urls_string.split(",") if url.strip()]

# Create global config instance
config = Config()

# Debug info when run directly
if __name__ == "__main__":
    print("Configuration")
    print("=" * 30)
    print(f"CHROMADB_HOST: {config.CHROMADB_HOST}")
    print(f"CHROMADB_HTTP_PORT: {config.CHROMADB_HTTP_PORT}")
    print(f"CHROMADB_PORT: {config.CHROMADB_PORT}")
    print(f"REDIS_URL: {config.REDIS_URL}")
    print(f"LOCAL_LLM_MODEL: {config.LOCAL_LLM_MODEL}")
    print(f"EMBEDDING_MODEL: {config.EMBEDDING_MODEL}")
    print(f"OPENAI_API_KEY: {'***' + config.OPENAI_API_KEY[-4:] if len(config.OPENAI_API_KEY) > 4 else 'Not set'}")
    print(f"OPENAI_MODEL: {config.OPENAI_MODEL}")
    print(f"UNIVERSITY_URLS: {config.UNIVERSITY_URLS}")
    print(f"SCRAPING_DELAY: {config.SCRAPING_DELAY}")