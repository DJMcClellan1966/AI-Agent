from pydantic import field_validator
from pydantic_settings import BaseSettings
from typing import List, Union
import os


def _parse_list_str(v: Union[str, List[str], None]) -> List[str]:
    """Accept comma-separated string from .env or list from JSON."""
    if v is None:
        return []
    if isinstance(v, list):
        return [x.strip() for x in v if isinstance(x, str) and x.strip()]
    if isinstance(v, str):
        return [x.strip() for x in v.split(",") if x.strip()]
    return []


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Agentic AI Life Assistant"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # Database (use SQLite for simplified local run: sqlite:///./agentic_ai.db)
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/agentic_ai"
    
    # Redis (required only when USE_CELERY=true)
    REDIS_URL: str = "redis://localhost:6379"
    # Set False to run without Celery/Redis: task execution runs in-process
    USE_CELERY: bool = False
    
    # CORS (env: comma-separated, e.g. http://localhost:3000,http://localhost:8000)
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://localhost:8000"
    
    # AI APIs
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    ANTHROPIC_MODEL: str = "claude-3-opus-20240229"
    
    # Local LLM Settings (default True so app runs without API keys when Ollama is used)
    USE_LOCAL_LLM: bool = True
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
    
    # Build: Synthesis-style single index file (open in browser with no server)
    BUILD_SINGLE_FILE: bool = True  # One index.html with inline CSS/JS; False = multi-file (index + styles.css + app.js)

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    RATE_LIMIT_AGENT_CHAT_PER_MINUTE: int = 30
    RATE_LIMIT_BUILD_GENERATE_PER_MINUTE: int = 10

    # Request limits
    REQUEST_BODY_MAX_BYTES: int = 1_048_576  # 1MB

    # LLM
    LLM_REQUEST_TIMEOUT_SECONDS: int = 120

    # Security: workspace allowlist (empty = no restriction; else workspace_root must be under one of these)
    # Env: comma-separated paths or leave empty
    WORKSPACE_ALLOWED_ROOTS: Union[str, List[str]] = ""

    @field_validator("CORS_ORIGINS", "WORKSPACE_ALLOWED_ROOTS", mode="after")
    @classmethod
    def _normalize_list(cls, v: Union[str, List[str]]) -> List[str]:
        """Normalize to List[str] so app code always gets a list."""
        return _parse_list_str(v)

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # ignore extra keys from .env (e.g. NEXT_PUBLIC_* for frontend)


settings = Settings()
