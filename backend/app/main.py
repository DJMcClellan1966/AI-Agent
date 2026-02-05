from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging

from sqlalchemy import text

from app.core.config import settings
from app.core.middleware import RateLimitMiddleware, RequestBodySizeLimitMiddleware, RequestIDMiddleware
from app.api.v1 import auth, users, build, agent_chat, workspace
from app.db.database import engine, Base
from app.core.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("Starting Agentic AI Life Assistant API")
    # Production checks
    if getattr(settings, "ENVIRONMENT", "").lower() == "production":
        if getattr(settings, "SECRET_KEY", "") in ("", "your-secret-key-change-in-production"):
            logger.warning("SECRET_KEY is default or empty in production; set a strong value in .env")
        cors = getattr(settings, "CORS_ORIGINS", [])
        if "*" in cors or (isinstance(cors, str) and cors == "*"):
            logger.warning("CORS_ORIGINS includes '*' in production; set explicit origins for credentials")
    # Create database tables and verify connectivity
    try:
        Base.metadata.create_all(bind=engine)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        logger.error("Database connectivity check failed: %s", e)
        raise
    yield
    logger.info("Shutting down Agentic AI Life Assistant API")


app = FastAPI(
    title="Agentic AI Life Assistant",
    description="Proactive AI agent system for autonomous task management",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Robustness middleware (first added = outermost; request sees: CORS -> RequestID -> BodySize -> RateLimit -> route)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestBodySizeLimitMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint (liveness: process is running)
@app.get("/health")
async def health_check():
    """Health check endpoint (no dependencies)."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "agentic-ai-api"
    }


# Readiness: can we serve traffic? (DB ping)
@app.get("/health/ready")
async def health_ready():
    """Readiness probe: DB connectivity. Returns 503 if DB is unreachable."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        logger.warning("Readiness check failed: %s", e)
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "detail": "Database unreachable"},
        )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Agentic AI Life Assistant API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }


# Include routers (simplified: local agent IDE – auth, users, workspace, agent chat, build)
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(workspace.router, prefix="/api/v1/workspace", tags=["Workspace"])
app.include_router(build.router, prefix="/api/v1/build", tags=["Build"])
app.include_router(agent_chat.router, prefix="/api/v1/agent", tags=["Agent"])


# Validation error handler (consistent JSON shape)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "type": "validation_error",
        },
    )


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred",
            "type": "internal_server_error"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
