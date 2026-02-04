"""
Local LLM Agent using GPT4All
Optimized for local execution without API costs
"""
from typing import Dict, Any, List
import logging
from gpt4all import GPT4All

from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class LocalBaseAgent(BaseAgent):
    """Base agent using local LLM via GPT4All"""
    
    def _initialize_llm(self):
        """Initialize local LLM instead of API-based one"""
        model_name = self.config.get("model_name", "mistral-7b-openorca.Q4_0.gguf")
        
        # Download and load model (cached after first run)
        logger.info(f"Loading local model: {model_name}")
        return GPT4All(model_name)
    
    async def _generate_response(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate response using local model"""
        try:
            response = self.llm.generate(
                prompt,
                max_tokens=max_tokens,
                temp=0.7,
                top_k=40,
                top_p=0.9,
                repeat_penalty=1.1
            )
            return response
        except Exception as e:
            logger.error(f"Local LLM generation failed: {e}")
            return ""


# Alternative: Ollama integration
class OllamaBaseAgent(BaseAgent):
    """Base agent using Ollama for local LLM"""
    
    def _initialize_llm(self):
        """Initialize Ollama client"""
        import ollama
        return ollama
    
    async def _generate_response(self, prompt: str) -> str:
        """Generate response using Ollama"""
        try:
            response = self.llm.generate(
                model='mistral:7b',  # or llama2, codellama, etc.
                prompt=prompt
            )
            return response['response']
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return ""
