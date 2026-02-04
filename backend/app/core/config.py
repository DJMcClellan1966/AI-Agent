from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Agentic AI Life Assistant"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/agentic_ai"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # AI APIs
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    ANTHROPIC_MODEL: str = "claude-3-opus-20240229"
    
    # Local LLM Settings
    USE_LOCAL_LLM: bool = False  # Set to True to use local models
    LOCAL_LLM_BACKEND: str = "ollama"  # Options: ollama, gpt4all, llama-cpp
    LOCAL_MODEL_NAME: str = "mistral:7b"  # Model to use
    OLLAMA_HOST: str = "http://localhost:11434"
    LOCAL_MODEL_MAX_TOKENS: int = 500
    LOCAL_MODEL_TEMPERATURE: float = 0.7
    LOCAL_MODEL_THREADS: int = 4  # CPU threads
    
    # Authentication
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # Email Service
    EMAIL_SERVICE_API_KEY: str = ""
    IMAP_HOST: str = "imap.gmail.com"
    IMAP_PORT: int = 993
    
    # Google Calendar
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/integrations/google/callback"
    
    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_ID_PRO: str = ""
    STRIPE_PRICE_ID_PREMIUM: str = ""
    
    # Agent Settings
    MAX_AGENT_RETRIES: int = 3
    AGENT_TIMEOUT_SECONDS: int = 120
    MAX_PENDING_TASKS: int = 100
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
