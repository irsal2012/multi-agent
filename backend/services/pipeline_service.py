"""
Pipeline service for managing multi-agent pipeline execution.
"""

import asyncio
import logging
import uuid
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from core.pipeline import MultiAgentPipeline
from models.schemas import ProjectMetadata, ProjectStatus, ProgressUpdate
from models.responses import GenerationResponse, ProjectResult, ValidationResponse
from .progress_service import ProgressService

class PipelineService:
    """Service for managing pipeline execution."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pipeline = MultiAgentPipeline()
        self.progress_service = ProgressService()
        self.active_projects: Dict[str, ProjectMetadata] = {}
        self.executor = ThreadPoolExecutor(max_workers=2)  # Limit concurrent pipelines
        
    async def start_generation(
        self, 
        user_input: str, 
        project_name: Optional[str] = None,
        progress_callback: Optional[Callable[[ProgressUpdate], None]] = None
    ) -> GenerationResponse:
        """Start code generation pipeline asynchronously."""
        
        # Generate unique project ID
        project_id = str(uuid.uuid4())
        
        # Create project metadata
        project_metadata = ProjectMetadata(
            project_id=project_id,
            project_name=project_name or f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            user_input=user_input,
            status=ProjectStatus.CREATED
        )
        
        # Store project metadata
        self.active_projects[project_id] = project_metadata
        self.progress_service.create_project_progress(project_id, project_metadata)
        
        # Start pipeline execution in background
        asyncio.create_task(self._execute_pipeline(project_id, user_input, project_name, progress_callback))
        
        return GenerationResponse(
            project_id=project_id,
            project_name=project_metadata.project_name,
            status="running",
            message="Pipeline execution started",
            progress_url=f"/api/v1/progress/{project_id}"
        )
    
    async def _execute_pipeline(
        self, 
        project_id: str, 
        user_input: str, 
        project_name: Optional[str],
        progress_callback: Optional[Callable[[ProgressUpdate], None]] = None
    ):
        """Execute the pipeline in a separate thread."""
        
        try:
            # Update project status
            self.active_projects[project_id].status = ProjectStatus.RUNNING
            self.active_projects[project_id].started_at = datetime.now()
            
            # Create progress update callback
            def update_progress():
                try:
                    progress = self.progress_service.get_project_progress(project_id)
                    if progress and progress_callback:
                        progress_update = ProgressUpdate(
                            project_id=project_id,
                            progress_percentage=progress.progress_percentage,
                            status=progress.current_step_info.status.value if progress.current_step_info else "running",
                            message=progress.current_step_info.description if progress.current_step_info else "Processing...",
                            logs=[]
                        )
                        progress_callback(progress_update)
                except Exception as e:
                    self.logger.error(f"Error in progress callback: {str(e)}")
            
            # Execute pipeline in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                self._run_pipeline_sync,
                project_id,
                user_input,
                project_name,
                update_progress
            )
            
            # Update project status on success
            self.active_projects[project_id].status = ProjectStatus.COMPLETED
            self.active_projects[project_id].completed_at = datetime.now()
            
            # Store final result
            self.progress_service.complete_project(project_id, result)
            
            self.logger.info(f"Pipeline {project_id} completed successfully")
            
        except Exception as e:
            # Update project status on failure
            self.active_projects[project_id].status = ProjectStatus.FAILED
            self.active_projects[project_id].completed_at = datetime.now()
            self.active_projects[project_id].error = str(e)
            
            # Store error
            self.progress_service.fail_project(project_id, str(e))
            
            self.logger.error(f"Pipeline {project_id} failed: {str(e)}")
    
    def _run_pipeline_sync(
        self, 
        project_id: str, 
        user_input: str, 
        project_name: Optional[str],
        progress_callback: Callable
    ) -> Dict[str, Any]:
        """Run the pipeline synchronously in a thread."""
        
        # Set up progress monitoring
        original_get_progress = self.pipeline.agent_manager.get_progress
        
        def monitored_get_progress():
            progress = original_get_progress()
            # Update our progress service
            self.progress_service.update_project_progress(project_id, progress)
            # Call the callback
            progress_callback()
            return progress
        
        # Replace the get_progress method temporarily
        self.pipeline.agent_manager.get_progress = monitored_get_progress
        
        try:
            # Run the actual pipeline
            result = self.pipeline.run_pipeline(user_input, project_name)
            return result
        finally:
            # Restore original method
            self.pipeline.agent_manager.get_progress = original_get_progress
    
    async def get_project_status(self, project_id: str) -> Optional[ProjectMetadata]:
        """Get project status by ID."""
        return self.active_projects.get(project_id)
    
    async def get_project_result(self, project_id: str) -> Optional[ProjectResult]:
        """Get complete project result by ID."""
        return self.progress_service.get_project_result(project_id)
    
    async def cancel_project(self, project_id: str) -> bool:
        """Cancel a running project."""
        if project_id in self.active_projects:
            project = self.active_projects[project_id]
            if project.status == ProjectStatus.RUNNING:
                project.status = ProjectStatus.CANCELLED
                project.completed_at = datetime.now()
                self.progress_service.cancel_project(project_id)
                return True
        return False
    
    async def validate_input(self, user_input: str) -> ValidationResponse:
        """Validate user input."""
        validation_result = self.pipeline.validate_input(user_input)
        
        return ValidationResponse(
            is_valid=validation_result['is_valid'],
            warnings=validation_result['warnings'],
            suggestions=validation_result['suggestions']
        )
    
    async def get_pipeline_status(self) -> Dict[str, Any]:
        """Get overall pipeline status."""
        return self.pipeline.get_pipeline_status()
    
    async def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information."""
        return self.pipeline.get_agent_info()
    
    def cleanup_completed_projects(self, max_age_hours: int = 24):
        """Clean up old completed projects."""
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        
        projects_to_remove = []
        for project_id, project in self.active_projects.items():
            if (project.status in [ProjectStatus.COMPLETED, ProjectStatus.FAILED, ProjectStatus.CANCELLED] and
                project.completed_at and project.completed_at.timestamp() < cutoff_time):
                projects_to_remove.append(project_id)
        
        for project_id in projects_to_remove:
            del self.active_projects[project_id]
            self.progress_service.cleanup_project(project_id)
        
        self.logger.info(f"Cleaned up {len(projects_to_remove)} old projects")
