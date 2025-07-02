"""
FastAPI backend server for the Multi-Agent Framework.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
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
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],  # Streamlit default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "multi-agent-framework-backend"
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
