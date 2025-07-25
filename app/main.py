# app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import time
import uuid
import logging
from contextlib import asynccontextmanager

from app.api.endpoints import search, health
from app.config.settings import settings
from app.core.exceptions import CustomHTTPException
from app.database.connection import init_database, close_database

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events"""
    # Startup
    try:
        logging.info("🚀 Starting LLM Search Backend...")
        
        # Initialize database
        await init_database()
        logging.info("✅ Database initialized")
        
        # Add any other startup tasks here
        # await initialize_cache()
        # await warm_up_services()
        
        logging.info("🎉 Application startup completed")
        
    except Exception as e:
        logging.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    try:
        logging.info("🔄 Shutting down LLM Search Backend...")
        
        # Close database connections
        await close_database()
        logging.info("✅ Database connections closed")
        
        # Add any other cleanup tasks here
        # await close_cache()
        # await shutdown_services()
        
        logging.info("👋 Application shutdown completed")
        
    except Exception as e:
        logging.error(f"❌ Shutdown error: {e}")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="LLM Search Backend",
    description="AI-powered search with intelligent content analysis and database logging",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(search.router, prefix="/api/v1", tags=["search"])
app.include_router(health.router, prefix="/health", tags=["health"])

# Global exception handler
@app.exception_handler(CustomHTTPException)
async def custom_exception_handler(request: Request, exc: CustomHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "error_code": exc.error_code,
            "request_id": getattr(request.state, "request_id", None)
        }
    )

# Add request ID and timing to all requests
@app.middleware("http")
async def add_request_metadata(request: Request, call_next):
    request.state.request_id = str(uuid.uuid4())
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Request-ID"] = request.state.request_id
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

@app.get("/")
async def root():
    return {
        "message": "LLM Search Backend API", 
        "version": "1.0.0",
        "features": ["AI Search", "Content Analysis", "Cost Tracking", "Database Logging"],
        "docs": "/docs" if settings.DEBUG else "disabled"
    }

@app.get("/api/v1/info")
async def api_info():
    """Get API information and capabilities"""
    return {
        "name": "LLM Search Backend",
        "version": "1.0.0",
        "description": "AI-powered search with intelligent content analysis",
        "features": {
            "query_enhancement": "Multi-strategy query expansion",
            "multi_search": "Brave Search + Bing Search integration",
            "content_fetching": "ZenRows web scraping with fallbacks",
            "llm_analysis": "Local Ollama model processing",
            "caching": "Redis + memory caching",
            "cost_tracking": "Real-time budget monitoring",
            "database_logging": "Comprehensive request logging and analytics"
        },
        "endpoints": {
            "search": "/api/v1/search",
            "suggestions": "/api/v1/search/suggestions",
            "stats": "/api/v1/search/stats",
            "health": "/health",
            "docs": "/docs" if settings.DEBUG else None
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
