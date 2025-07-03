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
        
        try:
            # Initialize progress tracking with proper step structure
            initial_steps = [
                {'name': 'Requirements Analysis', 'description': 'Analyzing requirements from user input', 'status': 'pending', 'progress_percentage': 0},
                {'name': 'Code Generation', 'description': 'Generating Python code from requirements', 'status': 'pending', 'progress_percentage': 0},
                {'name': 'Code Review', 'description': 'Reviewing code for quality and security', 'status': 'pending', 'progress_percentage': 0},
                {'name': 'Documentation', 'description': 'Creating comprehensive documentation', 'status': 'pending', 'progress_percentage': 0},
                {'name': 'Test Generation', 'description': 'Generating test cases', 'status': 'pending', 'progress_percentage': 0},
                {'name': 'Deployment Config', 'description': 'Creating deployment configurations', 'status': 'pending', 'progress_percentage': 0},
                {'name': 'UI Generation', 'description': 'Creating Streamlit user interface', 'status': 'pending', 'progress_percentage': 0}
            ]
            
            self.progress_service.update_project_progress(project_id, {
                'total_steps': 7,
                'completed_steps': 0,
                'failed_steps': 0,
                'progress_percentage': 0.0,
                'steps': initial_steps,
                'is_running': True,
                'is_completed': False,
                'has_failures': False,
                'current_step_info': initial_steps[0]
            })
            
            self.logger.info(f"Starting pipeline execution for project {project_id}")
            
            # Set up progress monitoring with proper integration
            original_get_progress = self.pipeline.agent_manager.get_progress
            
            def monitored_get_progress():
                try:
                    # Get progress from agent manager
                    agent_progress = original_get_progress()
                    
                    # Convert agent manager progress to progress service format
                    progress_data = self._convert_agent_progress_to_service_format(agent_progress)
                    
                    # Update our progress service
                    self.progress_service.update_project_progress(project_id, progress_data)
                    
                    # Call the callback
                    progress_callback()
                    
                    return agent_progress
                except Exception as e:
                    self.logger.error(f"Error in progress monitoring: {str(e)}")
                    return original_get_progress()
            
            # Replace the get_progress method temporarily
            self.pipeline.agent_manager.get_progress = monitored_get_progress
            
            # Set up periodic progress updates
            import threading
            import time
            
            def periodic_progress_update():
                """Periodically update progress even if get_progress isn't called."""
                update_count = 0
                last_progress_percentage = 0
                consecutive_errors = 0
                
                while (project_id in self.active_projects and 
                       self.active_projects[project_id].status == ProjectStatus.RUNNING):
                    try:
                        update_count += 1
                        self.logger.debug(f"Periodic progress update #{update_count} for project {project_id}")
                        
                        # Try to get progress from agent manager
                        progress_updated = False
                        try:
                            agent_progress = self.pipeline.agent_manager.get_progress()
                            progress_data = self._convert_agent_progress_to_service_format(agent_progress)
                            
                            # Only update if we have meaningful progress data
                            if progress_data.get('progress_percentage', 0) > 0 or progress_data.get('is_running'):
                                self.progress_service.update_project_progress(project_id, progress_data)
                                last_progress_percentage = progress_data.get('progress_percentage', 0)
                                progress_updated = True
                                consecutive_errors = 0  # Reset error counter
                                self.logger.debug(f"Progress updated: {last_progress_percentage:.1f}%")
                            
                        except Exception as progress_error:
                            consecutive_errors += 1
                            self.logger.debug(f"Agent progress error #{consecutive_errors}: {str(progress_error)}")
                            
                            # If we haven't had progress for a while, provide fallback updates
                            if consecutive_errors > 3:
                                fallback_progress = min(last_progress_percentage + (update_count * 0.5), 95)
                                fallback_data = {
                                    'is_running': True,
                                    'progress_percentage': fallback_progress,
                                    'current_step_info': {
                                        'name': 'Processing',
                                        'description': 'Pipeline is running...',
                                        'status': 'running',
                                        'progress_percentage': fallback_progress
                                    }
                                }
                                self.progress_service.update_project_progress(project_id, fallback_data)
                                progress_updated = True
                                self.logger.debug(f"Fallback progress: {fallback_progress:.1f}%")
                        
                        # Call progress callback if we updated anything
                        if progress_updated:
                            try:
                                progress_callback()
                            except Exception as callback_error:
                                self.logger.debug(f"Progress callback error: {str(callback_error)}")
                        
                        # Sleep between updates
                        time.sleep(1.5)  # Update every 1.5 seconds for more responsive UI
                        
                    except Exception as e:
                        self.logger.error(f"Periodic progress update failed: {str(e)}")
                        consecutive_errors += 1
                        if consecutive_errors > 10:
                            self.logger.error("Too many consecutive errors, stopping periodic updates")
                            break
                        time.sleep(2)  # Wait longer on error
                
                self.logger.info(f"Periodic progress updates stopped for project {project_id} after {update_count} updates")
            
            # Start periodic updates in background
            progress_thread = threading.Thread(target=periodic_progress_update, daemon=True)
            progress_thread.start()
            
            # Give the progress thread a moment to start
            time.sleep(0.5)
            
            # Run the actual pipeline
            self.logger.info(f"Executing pipeline for project {project_id}")
            result = self.pipeline.run_pipeline(user_input, project_name)
            
            # Final progress update
            final_progress = self.pipeline.agent_manager.get_progress()
            final_progress_data = self._convert_agent_progress_to_service_format(final_progress)
            final_progress_data.update({
                'is_running': False,
                'is_completed': True,
                'progress_percentage': 100.0
            })
            self.progress_service.update_project_progress(project_id, final_progress_data)
            
            self.logger.info(f"Pipeline execution completed for project {project_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Pipeline execution failed for project {project_id}: {str(e)}")
            # Update progress to show failure
            self.progress_service.update_project_progress(project_id, {
                'is_running': False,
                'is_completed': False,
                'has_failures': True,
                'progress_percentage': 0.0
            })
            raise
        finally:
            # Restore original method
            if 'original_get_progress' in locals():
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
    
    def _convert_agent_progress_to_service_format(self, agent_progress: Dict[str, Any]) -> Dict[str, Any]:
        """Convert agent manager progress format to progress service format."""
        try:
            # The agent manager now returns properly formatted data, so we can use it directly
            # with minimal conversion
            
            # Ensure all required fields are present with defaults
            converted_progress = {
                'total_steps': agent_progress.get('total_steps', 7),
                'completed_steps': agent_progress.get('completed_steps', 0),
                'failed_steps': agent_progress.get('failed_steps', 0),
                'progress_percentage': agent_progress.get('progress_percentage', 0.0),
                'steps': agent_progress.get('steps', []),
                'elapsed_time': agent_progress.get('elapsed_time', 0.0),
                'estimated_remaining_time': agent_progress.get('estimated_remaining_time', 0.0),
                'is_running': agent_progress.get('is_running', False),
                'is_completed': agent_progress.get('is_completed', False),
                'has_failures': agent_progress.get('has_failures', False),
                'current_step_info': agent_progress.get('current_step_info'),
                'logs': agent_progress.get('logs', [])
            }
            
            self.logger.debug(f"Converted progress: {converted_progress['progress_percentage']:.1f}% complete, "
                            f"{converted_progress['completed_steps']}/{converted_progress['total_steps']} steps")
            
            return converted_progress
            
        except Exception as e:
            self.logger.error(f"Error converting agent progress: {str(e)}")
            # Return minimal progress data with running status
            return {
                'total_steps': 7,
                'completed_steps': 0,
                'failed_steps': 0,
                'progress_percentage': 0.0,
                'steps': [],
                'elapsed_time': 0.0,
                'estimated_remaining_time': 0.0,
                'is_running': True,
                'is_completed': False,
                'has_failures': False,
                'current_step_info': None,
                'logs': []
            }

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
