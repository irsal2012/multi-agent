"""
FastAPI backend server for the Multi-Agent Framework.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from datetime import datetime
from contextlib import asynccontextmanager

from api.routes import pipeline, agents, progress, projects
from core.utils import setup_logging

# Setup logging
logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Multi-Agent Framework Backend")
    yield
    logger.info("Shutting down Multi-Agent Framework Backend")

# Create FastAPI app
app = FastAPI(
    title="Multi-Agent Framework API",
    description="Backend API for the Multi-Agent Code Generation Framework",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501", 
        "http://127.0.0.1:8501",
        "http://localhost:3000",  # React dev server
        "http://127.0.0.1:3000",
        "http://0.0.0.0:8501",    # Docker/container access
        "*"  # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
    ],
    expose_headers=["*"],
)

# Include routers
app.include_router(pipeline.router, prefix="/api/v1/pipeline", tags=["pipeline"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(progress.router, prefix="/api/v1/progress", tags=["progress"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Multi-Agent Framework Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Enhanced health check endpoint with service validation."""
    try:
        from api.dependencies import get_pipeline_service, get_progress_service, get_agent_service, get_project_service
        
        # Test service initialization
        services_status = {}
        overall_healthy = True
        
        # Check pipeline service
        try:
            pipeline_service = get_pipeline_service()
            # Test basic functionality
            test_validation = await pipeline_service.validate_input("test input")
            services_status["pipeline_service"] = "healthy"
        except Exception as e:
            services_status["pipeline_service"] = f"error: {str(e)}"
            overall_healthy = False
        
        # Check progress service
        try:
            progress_service = get_progress_service()
            # Test basic functionality
            test_stats = progress_service.get_statistics()
            services_status["progress_service"] = "healthy"
        except Exception as e:
            services_status["progress_service"] = f"error: {str(e)}"
            overall_healthy = False
        
        # Check agent service
        try:
            agent_service = get_agent_service()
            # Test basic functionality
            agent_info = await agent_service.get_agents_info()
            services_status["agent_service"] = "healthy"
        except Exception as e:
            services_status["agent_service"] = f"error: {str(e)}"
            overall_healthy = False
        
        # Check project service
        try:
            project_service = get_project_service()
            # Test basic functionality
            stats = await project_service.get_statistics()
            services_status["project_service"] = "healthy"
        except Exception as e:
            services_status["project_service"] = f"error: {str(e)}"
            overall_healthy = False
        
        return {
            "status": "healthy" if overall_healthy else "degraded",
            "service": "multi-agent-framework-backend",
            "services": services_status,
            "timestamp": datetime.now().isoformat(),
            "ready": overall_healthy
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "multi-agent-framework-backend",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "ready": False
        }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
