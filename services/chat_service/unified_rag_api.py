"""
Unified RAG API - Common Interface for Ollama and OpenAI
Provides a unified interface for both RAG implementations
"""

import os
import time
from typing import List, Dict, Any, Optional, Literal
from enum import Enum

# Import both RAG implementations
from .enhanced_gpu_chatbot import EnhancedGPUUniversityRAGChatbot, create_enhanced_gpu_chatbot
from .openai_rag_chatbot import OpenAIUniversityRAGChatbot, create_openai_chatbot

class RAGProvider(Enum):
    """Available RAG providers"""
    OLLAMA = "ollama"
    OPENAI = "openai"

class UnifiedRAGAPI:
    """Unified API for both Ollama and OpenAI RAG systems"""
    
    def __init__(self, provider: RAGProvider = RAGProvider.OLLAMA, 
                 model_name: str = None, openai_api_key: str = None):
        """
        Initialize the unified RAG API
        
        Args:
            provider: RAG provider to use (OLLAMA or OPENAI)
            model_name: Model name for the provider
            openai_api_key: OpenAI API key (required for OpenAI provider)
        """
        self.provider = provider
        self.model_name = model_name
        self.openai_api_key = openai_api_key
        
        # Set default model names
        if not model_name:
            if provider == RAGProvider.OLLAMA:
                self.model_name = "llama2:7b"
            elif provider == RAGProvider.OPENAI:
                self.model_name = "o4-mini-2025-04-16-2024-07-18"
        
        # Initialize the appropriate chatbot
        self.chatbot = self._initialize_chatbot()
        
        print(f"[Unified RAG] Initialized with provider: {provider.value}")
        print(f"[Unified RAG] Model: {self.model_name}")
    
    def _initialize_chatbot(self):
        """Initialize the appropriate chatbot based on provider"""
        try:
            if self.provider == RAGProvider.OLLAMA:
                print("[Unified RAG] Initializing Ollama RAG system...")
                return create_enhanced_gpu_chatbot(self.model_name)
            
            elif self.provider == RAGProvider.OPENAI:
                print("[Unified RAG] Initializing OpenAI RAG system...")
                if not self.openai_api_key and not os.getenv('OPENAI_API_KEY'):
                    raise ValueError("OpenAI API key is required for OpenAI provider")
                return create_openai_chatbot(self.model_name, self.openai_api_key)
            
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
                
        except Exception as e:
            print(f"[Unified RAG] Error initializing chatbot: {e}")
            raise
    
    def switch_provider(self, new_provider: RAGProvider, model_name: str = None, openai_api_key: str = None):
        """Switch to a different RAG provider"""
        print(f"[Unified RAG] Switching from {self.provider.value} to {new_provider.value}")
        
        self.provider = new_provider
        if model_name:
            self.model_name = model_name
        if openai_api_key:
            self.openai_api_key = openai_api_key
        
        # Reinitialize chatbot
        self.chatbot = self._initialize_chatbot()
    
    def generate_response(self, question: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a response using the current RAG provider
        
        Args:
            question: The question to answer
            session_id: Optional session ID for conversation history
            
        Returns:
            Dictionary containing response data
        """
        try:
            start_time = time.time()
            
            # Call the appropriate method based on provider
            if self.provider == RAGProvider.OLLAMA:
                response = self.chatbot.generate_enhanced_gpu_response(question, session_id)
            elif self.provider == RAGProvider.OPENAI:
                response = self.chatbot.generate_openai_response(question, session_id)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
            
            # Add provider information to response
            response['provider'] = self.provider.value
            response['model'] = self.model_name
            
            total_time = time.time() - start_time
            print(f"[Unified RAG] {self.provider.value.upper()} response generated in {total_time:.2f}s")
            
            return response
            
        except Exception as e:
            print(f"[Unified RAG] Error generating response: {e}")
            return {
                'answer': f"I'm sorry, I encountered an error with the {self.provider.value} provider. Please try again.",
                'sources': [],
                'confidence': 0.0,
                'response_time': time.time() - start_time if 'start_time' in locals() else 0,
                'provider': self.provider.value,
                'model': self.model_name,
                'error': str(e)
            }
    
    def compare_providers(self, question: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Compare responses from both providers for the same question
        
        Args:
            question: The question to compare
            session_id: Optional session ID for conversation history
            
        Returns:
            Dictionary containing comparison data
        """
        print(f"[Unified RAG] Comparing providers for question: {question[:50]}...")
        
        comparison = {
            'question': question,
            'ollama_response': None,
            'openai_response': None,
            'comparison': {}
        }
        
        # Get Ollama response
        try:
            original_provider = self.provider
            self.switch_provider(RAGProvider.OLLAMA)
            ollama_response = self.generate_response(question, session_id)
            comparison['ollama_response'] = ollama_response
        except Exception as e:
            print(f"[Unified RAG] Ollama comparison error: {e}")
            comparison['ollama_response'] = {'error': str(e)}
        
        # Get OpenAI response
        try:
            self.switch_provider(RAGProvider.OPENAI)
            openai_response = self.generate_response(question, session_id)
            comparison['openai_response'] = openai_response
        except Exception as e:
            print(f"[Unified RAG] OpenAI comparison error: {e}")
            comparison['openai_response'] = {'error': str(e)}
        
        # Restore original provider
        self.switch_provider(original_provider)
        
        # Generate comparison metrics
        if comparison['ollama_response'] and comparison['openai_response']:
            if 'error' not in comparison['ollama_response'] and 'error' not in comparison['openai_response']:
                comparison['comparison'] = {
                    'ollama_faster': comparison['ollama_response']['response_time'] < comparison['openai_response']['response_time'],
                    'openai_faster': comparison['openai_response']['response_time'] < comparison['ollama_response']['response_time'],
                    'ollama_higher_confidence': comparison['ollama_response']['confidence'] > comparison['openai_response']['confidence'],
                    'openai_higher_confidence': comparison['openai_response']['confidence'] > comparison['ollama_response']['confidence'],
                    'time_difference': abs(comparison['ollama_response']['response_time'] - comparison['openai_response']['response_time']),
                    'confidence_difference': abs(comparison['ollama_response']['confidence'] - comparison['openai_response']['confidence'])
                }
        
        return comparison
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the current provider"""
        return {
            'provider': self.provider.value,
            'model': self.model_name,
            'available_providers': [p.value for p in RAGProvider],
            'supports_conversation_history': True,
            'supports_confidence_scoring': True,
            'supports_source_attribution': True
        }
    
    def save_cache(self):
        """Save embedding cache for the current provider"""
        try:
            self.chatbot.save_cache()
            print(f"[Unified RAG] Cache saved for {self.provider.value}")
        except Exception as e:
            print(f"[Unified RAG] Error saving cache: {e}")

def create_unified_rag_api(provider: str = "ollama", model_name: str = None, openai_api_key: str = None):
    """
    Factory function to create a unified RAG API
    
    Args:
        provider: Provider name ("ollama" or "openai")
        model_name: Model name for the provider
        openai_api_key: OpenAI API key (required for OpenAI provider)
    
    Returns:
        UnifiedRAGAPI instance
    """
    provider_enum = RAGProvider(provider.lower())
    return UnifiedRAGAPI(provider_enum, model_name, openai_api_key)

# Convenience functions for quick access
def create_ollama_rag_api(model_name: str = "llama2:7b"):
    """Create an Ollama RAG API instance"""
    return UnifiedRAGAPI(RAGProvider.OLLAMA, model_name)

def create_openai_rag_api(model_name: str = "o4-mini-2025-04-16", openai_api_key: str = None):
    """Create an OpenAI RAG API instance"""
    return UnifiedRAGAPI(RAGProvider.OPENAI, model_name, openai_api_key)

if __name__ == "__main__":
    # Test the unified API
    print("Testing Unified RAG API...")
    
    # Test with Ollama
    print("\n=== Testing Ollama Provider ===")
    ollama_api = create_ollama_rag_api()
    ollama_response = ollama_api.generate_response("What are the admission requirements for Northeastern University?")
    print(f"Ollama Answer: {ollama_response['answer'][:100]}...")
    print(f"Ollama Confidence: {ollama_response['confidence']:.2f}")
    print(f"Ollama Response Time: {ollama_response['response_time']:.2f}s")
    
    # Test with OpenAI (if API key is available)
    if os.getenv('OPENAI_API_KEY'):
        print("\n=== Testing OpenAI Provider ===")
        openai_api = create_openai_rag_api()
        openai_response = openai_api.generate_response("What are the admission requirements for Northeastern University?")
        print(f"OpenAI Answer: {openai_response['answer'][:100]}...")
        print(f"OpenAI Confidence: {openai_response['confidence']:.2f}")
        print(f"OpenAI Response Time: {openai_response['response_time']:.2f}s")
        
        # Test comparison
        print("\n=== Testing Provider Comparison ===")
        comparison = openai_api.compare_providers("What is the computer science program like?")
        print(f"Comparison completed: {comparison['comparison']}")
    else:
        print("\nOpenAI API key not found, skipping OpenAI tests")
    
    print("\nUnified RAG API test completed!") 