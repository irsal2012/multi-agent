"""
FastAPI dependencies for dependency injection.
"""

from functools import lru_cache
from services.pipeline_service import PipelineService
from services.agent_service import AgentService
from services.progress_service import ProgressService
from services.project_service import ProjectService

# Global service instances (singleton pattern)
_pipeline_service = None
_agent_service = None
_progress_service = None
_project_service = None

def get_pipeline_service() -> PipelineService:
    """Get pipeline service instance."""
    global _pipeline_service
    if _pipeline_service is None:
        # Inject the shared progress service into pipeline service
        progress_service = get_progress_service()
        _pipeline_service = PipelineService(progress_service=progress_service)
    return _pipeline_service

def get_agent_service() -> AgentService:
    """Get agent service instance."""
    global _agent_service
    if _agent_service is None:
        _agent_service = AgentService()
    return _agent_service

def get_progress_service() -> ProgressService:
    """Get progress service instance."""
    global _progress_service
    if _progress_service is None:
        _progress_service = ProgressService()
    return _progress_service

def get_project_service() -> ProjectService:
    """Get project service instance."""
    global _project_service
    if _project_service is None:
        _project_service = ProjectService()
    return _project_service
