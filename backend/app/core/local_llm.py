"""
Local LLM Service - Support for running models locally
Supports: Ollama, GPT4All, Llama.cpp
"""
import logging
from typing import Optional, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)


class LocalLLMService:
    """Service for interacting with local LLMs"""
    
    def __init__(self):
        self.backend = settings.LOCAL_LLM_BACKEND
        self.model = settings.LOCAL_MODEL_NAME
        self.client = None
        self._initialize_backend()
    
    def _initialize_backend(self):
        """Initialize the appropriate local LLM backend"""
        if self.backend == "ollama":
            self._initialize_ollama()
        elif self.backend == "gpt4all":
            self._initialize_gpt4all()
        elif self.backend == "llama-cpp":
            self._initialize_llama_cpp()
        else:
            logger.warning(f"Unknown backend: {self.backend}, falling back to Ollama")
            self._initialize_ollama()
    
    def _initialize_ollama(self):
        """Initialize Ollama client"""
        try:
            import ollama
            self.client = ollama
            logger.info(f"Initialized Ollama with model: {self.model}")
        except ImportError:
            logger.error("Ollama not installed. Install with: pip install ollama")
            self.client = None
    
    def _initialize_gpt4all(self):
        """Initialize GPT4All"""
        try:
            from gpt4all import GPT4All
            # Model will be downloaded automatically if not present
            self.client = GPT4All(self.model)
            logger.info(f"Initialized GPT4All with model: {self.model}")
        except ImportError:
            logger.error("GPT4All not installed. Install with: pip install gpt4all")
            self.client = None
    
    def _initialize_llama_cpp(self):
        """Initialize Llama.cpp"""
        try:
            from llama_cpp import Llama
            # Expecting model path in LOCAL_MODEL_NAME
            self.client = Llama(
                model_path=self.model,
                n_ctx=2048,
                n_threads=settings.LOCAL_MODEL_THREADS,
                n_gpu_layers=0  # Set > 0 for GPU support
            )
            logger.info(f"Initialized Llama.cpp with model: {self.model}")
        except ImportError:
            logger.error("llama-cpp-python not installed. Install with: pip install llama-cpp-python")
            self.client = None
    
    def generate(self, prompt: str, max_tokens: Optional[int] = None, **kwargs) -> str:
        """Generate text using the local LLM"""
        if not self.client:
            logger.error("No LLM client initialized")
            return ""
        
        max_tokens = max_tokens or settings.LOCAL_MODEL_MAX_TOKENS
        temperature = kwargs.get("temperature", settings.LOCAL_MODEL_TEMPERATURE)
        
        try:
            if self.backend == "ollama":
                return self._generate_ollama(prompt, max_tokens, temperature)
            elif self.backend == "gpt4all":
                return self._generate_gpt4all(prompt, max_tokens, temperature)
            elif self.backend == "llama-cpp":
                return self._generate_llama_cpp(prompt, max_tokens, temperature)
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return ""
    
    def _generate_ollama(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate using Ollama"""
        response = self.client.generate(
            model=self.model,
            prompt=prompt,
            options={
                "num_predict": max_tokens,
                "temperature": temperature,
            }
        )
        return response.get("response", "")
    
    def _generate_gpt4all(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate using GPT4All"""
        response = self.client.generate(
            prompt,
            max_tokens=max_tokens,
            temp=temperature,
            top_k=40,
            top_p=0.9,
            repeat_penalty=1.1
        )
        return response
    
    def _generate_llama_cpp(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate using Llama.cpp"""
        response = self.client(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=["</s>", "\n\n"],
            echo=False
        )
        return response["choices"][0]["text"]
    
    def is_available(self) -> bool:
        """Check if local LLM is available"""
        return self.client is not None
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about the local LLM"""
        return {
            "backend": self.backend,
            "model": self.model,
            "available": self.is_available(),
            "host": settings.OLLAMA_HOST if self.backend == "ollama" else "local"
        }


# Singleton instance
_local_llm_service: Optional[LocalLLMService] = None


def get_local_llm() -> LocalLLMService:
    """Get or create the local LLM service singleton"""
    global _local_llm_service
    if _local_llm_service is None:
        _local_llm_service = LocalLLMService()
    return _local_llm_service
