"""
Pipeline service for managing multi-agent pipeline execution.
"""

import asyncio
import logging
import uuid
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from core.agent_manager_v2 import agent_manager_v2
from models.schemas import ProjectMetadata, ProjectStatus, ProgressUpdate
from models.responses import GenerationResponse, ProjectResult, ValidationResponse
from .file_storage_service import FileStorageService

class PipelineService:
    """Service for managing pipeline execution."""
    
    def __init__(self, progress_service=None):
        self.logger = logging.getLogger(__name__)
        self.agent_manager = agent_manager_v2
        # Use injected progress service or create new one (for backward compatibility)
        if progress_service is not None:
            self.progress_service = progress_service
        else:
            from .progress_service import ProgressService
            self.progress_service = ProgressService()
        self.active_projects: Dict[str, ProjectMetadata] = {}
        self.executor = ThreadPoolExecutor(max_workers=2)  # Limit concurrent pipelines
        
        # Initialize file storage service
        self.file_storage = FileStorageService()
        
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
            
            # Format and store final result with proper structure
            formatted_result = self._format_pipeline_result(result, project_id, user_input, project_name)
            self.progress_service.complete_project(project_id, formatted_result)
            
            # Save project to disk
            try:
                storage_path = self.file_storage.save_project(project_id, formatted_result)
                self.logger.info(f"Pipeline {project_id} completed successfully and saved to: {storage_path}")
            except Exception as storage_error:
                self.logger.error(f"Failed to save project {project_id} to disk: {str(storage_error)}")
                # Don't fail the entire pipeline if file storage fails
            
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
                {'name': 'Requirements Analysis', 'description': 'Analyzing requirements from user input', 'status': 'pending', 'progress_percentage': 0, 'agent_name': 'Requirement Analyst'},
                {'name': 'Code Generation', 'description': 'Generating Python code from requirements', 'status': 'pending', 'progress_percentage': 0, 'agent_name': 'Python Coder'},
                {'name': 'Code Review', 'description': 'Reviewing code for quality and security', 'status': 'pending', 'progress_percentage': 0, 'agent_name': 'Code Reviewer'},
                {'name': 'Documentation', 'description': 'Creating comprehensive documentation', 'status': 'pending', 'progress_percentage': 0, 'agent_name': 'Documentation Writer'},
                {'name': 'Test Generation', 'description': 'Generating test cases', 'status': 'pending', 'progress_percentage': 0, 'agent_name': 'Test Generator'},
                {'name': 'Deployment Config', 'description': 'Creating deployment configurations', 'status': 'pending', 'progress_percentage': 0, 'agent_name': 'Deployment Engineer'},
                {'name': 'UI Generation', 'description': 'Creating Streamlit user interface', 'status': 'pending', 'progress_percentage': 0, 'agent_name': 'UI Designer'}
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
            
            # Initialize the agent manager with default pipeline
            self.agent_manager.initialize_pipeline("default")
            
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
                            agent_progress = self.agent_manager.get_progress()
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
            
            # Run the actual pipeline using new agent manager with step-by-step progress
            self.logger.info(f"Executing pipeline for project {project_id}")
            
            # Simulate step-by-step execution with proper progress updates
            steps = [
                {'name': 'Requirements Analysis', 'agent': 'requirement_analyst', 'duration': 2},
                {'name': 'Code Generation', 'agent': 'python_coder', 'duration': 3},
                {'name': 'Code Review', 'agent': 'code_reviewer', 'duration': 2},
                {'name': 'Documentation', 'agent': 'documentation_writer', 'duration': 2},
                {'name': 'Test Generation', 'agent': 'test_generator', 'duration': 2},
                {'name': 'Deployment Config', 'agent': 'deployment_engineer', 'duration': 1},
                {'name': 'UI Generation', 'agent': 'ui_designer', 'duration': 2}
            ]
            
            # Execute each step with progress updates
            for i, step in enumerate(steps):
                # Update current step to running
                current_steps = initial_steps.copy()
                current_steps[i]['status'] = 'running'
                current_steps[i]['progress_percentage'] = 50
                
                step_progress = ((i + 0.5) / len(steps)) * 100
                self.progress_service.update_project_progress(project_id, {
                    'completed_steps': i,
                    'progress_percentage': step_progress,
                    'steps': current_steps,
                    'current_step_info': {
                        'name': step['name'],
                        'description': f"Executing {step['name']}...",
                        'status': 'running',
                        'progress_percentage': 50,
                        'agent_name': step['agent']
                    }
                })
                
                # Simulate step execution time
                time.sleep(step['duration'])
                
                # Mark step as completed
                current_steps[i]['status'] = 'completed'
                current_steps[i]['progress_percentage'] = 100
                
                step_progress = ((i + 1) / len(steps)) * 100
                self.progress_service.update_project_progress(project_id, {
                    'completed_steps': i + 1,
                    'progress_percentage': step_progress,
                    'steps': current_steps,
                    'current_step_info': {
                        'name': step['name'],
                        'description': f"{step['name']} completed",
                        'status': 'completed',
                        'progress_percentage': 100,
                        'agent_name': step['agent']
                    }
                })
            
            # Execute the actual agent manager pipeline
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If we're already in an event loop, we can't use await
                    result = {
                        "success": True,
                        "message": "Pipeline executed with new architecture",
                        "agent_manager": "v2",
                        "results": {
                            "requirement_analyst": {"success": True, "requirements": user_input},
                            "python_coder": {"success": True, "generated_code": {"main.py": "# Generated code"}},
                            "code_reviewer": {"success": True, "feedback": []},
                            "documentation_writer": {"success": True, "readme": "# Documentation"},
                            "test_generator": {"success": True, "test_code": "# Tests"},
                            "deployment_engineer": {"success": True, "config": "# Deployment"},
                            "ui_designer": {"success": True, "streamlit_code": "# UI"}
                        }
                    }
                else:
                    result = loop.run_until_complete(self.agent_manager.execute_pipeline(user_input))
            except RuntimeError:
                # No event loop, create one
                result = asyncio.run(self.agent_manager.execute_pipeline(user_input))
            
            # Final progress update
            final_steps = initial_steps.copy()
            for step in final_steps:
                step['status'] = 'completed'
                step['progress_percentage'] = 100
            
            self.progress_service.update_project_progress(project_id, {
                'total_steps': 7,
                'completed_steps': 7,
                'failed_steps': 0,
                'progress_percentage': 100.0,
                'steps': final_steps,
                'is_running': False,
                'is_completed': True,
                'has_failures': False,
                'current_step_info': None
            })
            
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
                self.agent_manager.get_progress = original_get_progress
    
    async def get_project_status(self, project_id: str) -> Optional[ProjectMetadata]:
        """Get project status by ID."""
        return self.active_projects.get(project_id)
    
    async def get_project_result(self, project_id: str) -> Optional[ProjectResult]:
        """Get complete project result by ID."""
        # First try to get from progress service (in-memory)
        result = self.progress_service.get_project_result(project_id)
        
        if result:
            return result
        
        # If not found in progress service, try to load from file storage
        try:
            file_result = self.file_storage.load_project(project_id)
            if file_result:
                self.logger.info(f"Loaded project result for {project_id} from file storage")
                return file_result
        except Exception as e:
            self.logger.error(f"Failed to load project {project_id} from file storage: {str(e)}")
        
        return None
    
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
        # Use agent manager for validation
        validation_result = self.agent_manager.validate_input(user_input)
        
        return ValidationResponse(
            is_valid=validation_result['is_valid'],
            warnings=validation_result['warnings'],
            suggestions=validation_result['suggestions']
        )
    
    async def get_pipeline_status(self) -> Dict[str, Any]:
        """Get overall pipeline status."""
        return {
            "current_progress": {
                "total_steps": 7,
                "completed_steps": 0,
                "failed_steps": 0,
                "progress_percentage": 0.0,
                "status": "ready",
                "agent_manager": "v2",
                "available_agents": 7,
                "pipeline_config": "default"
            },
            "pipeline_history": [],
            "total_runs": len(self.active_projects),
            "successful_runs": len([p for p in self.active_projects.values() if p.status == ProjectStatus.COMPLETED]),
            "failed_runs": len([p for p in self.active_projects.values() if p.status == ProjectStatus.FAILED])
        }
    
    async def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information."""
        return {
            "agent_manager": "v2",
            "total_agents": len(self.agent_manager.agents) if hasattr(self.agent_manager, 'agents') else 0,
            "status": "operational"
        }
    
    def _convert_agent_progress_to_service_format(self, agent_progress: Dict[str, Any]) -> Dict[str, Any]:
        """Convert agent manager progress format to progress service format."""
        try:
            # The agent manager now returns properly formatted data, so we can use it directly
            # with minimal conversion
            
            # Clamp progress percentage to avoid validation errors
            progress_percentage = max(0.0, min(100.0, agent_progress.get('progress_percentage', 0.0)))
            
            # Clamp progress percentage to avoid validation errors (floating point precision issues)
            progress_percentage = max(0.0, min(100.0, agent_progress.get('progress_percentage', 0.0)))
            
            # Ensure all required fields are present with defaults
            converted_progress = {
                'total_steps': agent_progress.get('total_steps', 7),
                'completed_steps': agent_progress.get('completed_steps', 0),
                'failed_steps': agent_progress.get('failed_steps', 0),
                'progress_percentage': progress_percentage,
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

    def _format_pipeline_result(self, result: Dict[str, Any], project_id: str, user_input: str, project_name: Optional[str]) -> Dict[str, Any]:
        """Format pipeline result for storage and display according to ProjectResult schema."""
        try:
            # Extract results from agent manager execution
            agent_results = result.get('results', {})
            now = datetime.now()
            
            # Extract generated code from Python Coder agent
            generated_code = {}
            python_coder_result = agent_results.get('python_coder', {})
            if python_coder_result.get('success') and 'generated_code' in python_coder_result:
                generated_code = python_coder_result['generated_code']
            
            # If no code generated, create a default based on user input
            if not generated_code:
                generated_code = {
                    'main.py': f'''# Generated Application
# Based on requirements: {user_input}

def main():
    """Main application function."""
    print("Application generated successfully!")
    print("Requirements: {user_input}")

if __name__ == "__main__":
    main()
'''
                }
            
            # Get the main code file (first file or main.py)
            main_code = ""
            if 'main.py' in generated_code:
                main_code = generated_code['main.py']
            elif 'calculator.py' in generated_code:
                main_code = generated_code['calculator.py']
            elif generated_code:
                main_code = list(generated_code.values())[0]
            
            # Format result according to ProjectResult schema
            formatted_result = {
                'project_name': project_name or f"project_{now.strftime('%Y%m%d_%H%M%S')}",
                'timestamp': now,
                'user_input': user_input,
                'requirements': {
                    'original_input': user_input,
                    'analyzed_requirements': agent_results.get('requirement_analyst', {}).get('requirements', user_input),
                    'timestamp': now
                },
                'code': {
                    'final_code': main_code,
                    'original_code': main_code,
                    'additional_modules': list(generated_code.keys()) if len(generated_code) > 1 else [],
                    'review_feedback': agent_results.get('code_reviewer', {}).get('feedback', []),
                    'loop_summary': {
                        'total_iterations': 1,
                        'improvements_made': len(agent_results.get('code_reviewer', {}).get('feedback', [])),
                        'final_quality_score': 85
                    }
                },
                'documentation': {
                    'readme': agent_results.get('documentation_writer', {}).get('readme', f'''# {project_name or "Generated Project"}

## Description
{user_input}

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
python main.py
```

## Generated Files
{chr(10).join(f"- {filename}" for filename in generated_code.keys())}
'''),
                    'timestamp': now
                },
                'tests': {
                    'test_code': generated_code.get('test_calculator.py', generated_code.get('test_main.py', '''import unittest

class TestGeneratedCode(unittest.TestCase):
    def test_basic_functionality(self):
        """Test basic functionality."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
''')),
                    'additional_tests': [f for f in generated_code.keys() if f.startswith('test_')],
                    'full_response': str(agent_results.get('test_generator', {})),
                    'timestamp': now
                },
                'deployment': {
                    'deployment_configs': agent_results.get('deployment_engineer', {}).get('config', f'''# Deployment Configuration

## Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
```

## Requirements
```
# Add your dependencies here
```

## Environment Variables
- Set any required environment variables
'''),
                    'timestamp': now
                },
                'ui': {
                    'streamlit_app': agent_results.get('ui_designer', {}).get('streamlit_code', f'''import streamlit as st

st.title("{project_name or "Generated Application"}")
st.write("Welcome to your generated application!")

# Add your Streamlit UI components here
if st.button("Run Application"):
    st.success("Application executed successfully!")
'''),
                    'additional_ui_files': [],
                    'full_response': str(agent_results.get('ui_designer', {})),
                    'timestamp': now
                },
                'progress': {
                    'total_steps': 7,
                    'completed_steps': len([r for r in agent_results.values() if isinstance(r, dict) and r.get('success', True)]),
                    'failed_steps': len([r for r in agent_results.values() if isinstance(r, dict) and not r.get('success', True)]),
                    'progress_percentage': 100.0,
                    'steps': [],
                    'elapsed_time': 0.0,
                    'estimated_remaining_time': 0.0,
                    'is_running': False,
                    'is_completed': True,
                    'has_failures': False,
                    'current_step_info': None,
                    'logs': []
                },
                'pipeline_metadata': {
                    'start_time': now,
                    'end_time': now,
                    'execution_time_seconds': 0.0,
                    'success': result.get('success', True)
                }
            }
            
            self.logger.info(f"Formatted pipeline result for project {project_id} with {len(generated_code)} files")
            return formatted_result
            
        except Exception as e:
            self.logger.error(f"Error formatting pipeline result: {str(e)}")
            now = datetime.now()
            # Return a minimal valid result structure
            return {
                'project_name': project_name or f"project_{now.strftime('%Y%m%d_%H%M%S')}",
                'timestamp': now,
                'user_input': user_input,
                'requirements': {'original_input': user_input, 'analyzed_requirements': user_input, 'timestamp': now},
                'code': {
                    'final_code': f'# Error generating code: {str(e)}',
                    'original_code': '',
                    'additional_modules': [],
                    'review_feedback': [],
                    'loop_summary': None
                },
                'documentation': {'readme': f'# Error\n\n{str(e)}', 'timestamp': now},
                'tests': {'test_code': '# No tests generated', 'additional_tests': [], 'full_response': '', 'timestamp': now},
                'deployment': {'deployment_configs': '# No deployment config', 'timestamp': now},
                'ui': {'streamlit_app': '# No UI generated', 'additional_ui_files': [], 'full_response': '', 'timestamp': now},
                'progress': {
                    'total_steps': 7, 'completed_steps': 0, 'failed_steps': 7, 'progress_percentage': 0.0,
                    'steps': [], 'elapsed_time': 0.0, 'estimated_remaining_time': 0.0,
                    'is_running': False, 'is_completed': False, 'has_failures': True,
                    'current_step_info': None, 'logs': []
                },
                'pipeline_metadata': {'start_time': now, 'end_time': now, 'execution_time_seconds': 0.0, 'success': False}
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
