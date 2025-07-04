"""
Progress service for tracking pipeline execution progress.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from models.schemas import ProjectMetadata, LogEntry, LogLevel
from models.responses import ProgressResponse, StepInfo, ProjectResult

class ProgressService:
    """Service for managing progress tracking."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.project_progress: Dict[str, Dict[str, Any]] = {}
        self.project_results: Dict[str, Dict[str, Any]] = {}
        
    def create_project_progress(self, project_id: str, project_metadata: ProjectMetadata):
        """Create initial progress tracking for a project."""
        self.project_progress[project_id] = {
            'metadata': project_metadata,
            'current_progress': {
                'total_steps': 7,  # Standard pipeline steps
                'completed_steps': 0,
                'failed_steps': 0,
                'progress_percentage': 0.0,
                'steps': [],
                'elapsed_time': 0.0,
                'estimated_remaining_time': 0.0,
                'is_running': False,
                'is_completed': False,
                'has_failures': False,
                'current_step_info': None,
                'logs': []
            },
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        self.logger.info(f"Created progress tracking for project {project_id}")
    
    def update_project_progress(self, project_id: str, progress_data: Dict[str, Any]):
        """Update project progress with new data."""
        if project_id not in self.project_progress:
            self.logger.warning(f"Project {project_id} not found in progress tracking")
            return
        
        # Update the progress data
        self.project_progress[project_id]['current_progress'].update(progress_data)
        self.project_progress[project_id]['updated_at'] = datetime.now()
        
        # Add log entry
        self.add_log_entry(project_id, LogLevel.INFO, "Progress updated", metadata=progress_data)
    
    def get_project_progress(self, project_id: str) -> Optional[ProgressResponse]:
        """Get current progress for a project."""
        if project_id not in self.project_progress:
            # Try to reconstruct progress from file storage if project exists
            if self._reconstruct_completed_project_progress(project_id):
                # Now try again
                pass
            else:
                return None
        
        progress_data = self.project_progress[project_id]['current_progress']
        
        # Convert steps to StepInfo objects
        steps = []
        for step_data in progress_data.get('steps', []):
            step_info = StepInfo(
                name=step_data.get('name', ''),
                description=step_data.get('description', ''),
                status=step_data.get('status', 'pending'),
                progress_percentage=step_data.get('progress_percentage', 0.0),
                start_time=step_data.get('start_time'),
                end_time=step_data.get('end_time'),
                duration=step_data.get('duration'),
                agent_name=step_data.get('agent_name'),
                substeps=step_data.get('substeps', [])
            )
            steps.append(step_info)
        
        # Convert current step info
        current_step_info = None
        if progress_data.get('current_step_info'):
            current_step_data = progress_data['current_step_info']
            current_step_info = StepInfo(
                name=current_step_data.get('name', ''),
                description=current_step_data.get('description', ''),
                status=current_step_data.get('status', 'pending'),
                progress_percentage=current_step_data.get('progress_percentage', 0.0),
                start_time=current_step_data.get('start_time'),
                end_time=current_step_data.get('end_time'),
                duration=current_step_data.get('duration'),
                agent_name=current_step_data.get('agent_name'),
                substeps=current_step_data.get('substeps', [])
            )
        
        return ProgressResponse(
            total_steps=progress_data.get('total_steps', 0),
            completed_steps=progress_data.get('completed_steps', 0),
            failed_steps=progress_data.get('failed_steps', 0),
            progress_percentage=progress_data.get('progress_percentage', 0.0),
            steps=steps,
            elapsed_time=progress_data.get('elapsed_time', 0.0),
            estimated_remaining_time=progress_data.get('estimated_remaining_time', 0.0),
            is_running=progress_data.get('is_running', False),
            is_completed=progress_data.get('is_completed', False),
            has_failures=progress_data.get('has_failures', False),
            current_step_info=current_step_info,
            logs=progress_data.get('logs', [])
        )
    
    def add_log_entry(self, project_id: str, level: LogLevel, message: str, 
                     agent: Optional[str] = None, step: Optional[str] = None, 
                     metadata: Optional[Dict[str, Any]] = None):
        """Add a log entry for a project."""
        if project_id not in self.project_progress:
            return
        
        log_entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            message=message,
            agent=agent,
            step=step,
            metadata=metadata or {}
        )
        
        # Add to project logs
        logs = self.project_progress[project_id]['current_progress']['logs']
        logs.append(log_entry.dict())
        
        # Keep only last 100 log entries
        if len(logs) > 100:
            logs[:] = logs[-100:]
        
        self.project_progress[project_id]['updated_at'] = datetime.now()
    
    def complete_project(self, project_id: str, result: Dict[str, Any]):
        """Mark project as completed and store result with enhanced status handling."""
        if project_id in self.project_progress:
            # Check if this is a partial completion with warnings
            pipeline_status = result.get('pipeline_status', {})
            has_warnings = len(pipeline_status.get('warnings', [])) > 0
            has_failures = len(pipeline_status.get('failed_steps', [])) > 0
            overall_success = pipeline_status.get('overall_success', True)
            
            # Create completed steps array
            completed_steps = [
                {'name': 'Requirements Analysis', 'description': 'Analyzing requirements from user input', 'status': 'completed', 'progress_percentage': 100, 'agent_name': 'Requirement Analyst'},
                {'name': 'Code Generation', 'description': 'Generating Python code from requirements', 'status': 'completed', 'progress_percentage': 100, 'agent_name': 'Python Coder'},
                {'name': 'Code Review', 'description': 'Reviewing code for quality and security', 'status': 'completed', 'progress_percentage': 100, 'agent_name': 'Code Reviewer'},
                {'name': 'Documentation', 'description': 'Creating comprehensive documentation', 'status': 'completed', 'progress_percentage': 100, 'agent_name': 'Documentation Writer'},
                {'name': 'Test Generation', 'description': 'Generating test cases', 'status': 'completed', 'progress_percentage': 100, 'agent_name': 'Test Generator'},
                {'name': 'Deployment Config', 'description': 'Creating deployment configurations', 'status': 'completed', 'progress_percentage': 100, 'agent_name': 'Deployment Engineer'},
                {'name': 'UI Generation', 'description': 'Creating Streamlit user interface', 'status': 'completed', 'progress_percentage': 100, 'agent_name': 'UI Designer'}
            ]
            
            # Update progress based on actual completion status
            self.project_progress[project_id]['current_progress']['is_completed'] = True
            self.project_progress[project_id]['current_progress']['is_running'] = False
            self.project_progress[project_id]['current_progress']['has_failures'] = has_failures
            self.project_progress[project_id]['current_progress']['completed_steps'] = 7
            self.project_progress[project_id]['current_progress']['failed_steps'] = 0
            self.project_progress[project_id]['current_progress']['steps'] = completed_steps
            self.project_progress[project_id]['current_progress']['current_step_info'] = None
            self.project_progress[project_id]['updated_at'] = datetime.now()
            
            # Set progress percentage based on completion status
            if overall_success and not has_warnings:
                self.project_progress[project_id]['current_progress']['progress_percentage'] = 100.0
                self.add_log_entry(project_id, LogLevel.INFO, "Project completed successfully")
            elif has_warnings and not has_failures:
                self.project_progress[project_id]['current_progress']['progress_percentage'] = 95.0
                warning_count = len(pipeline_status.get('warnings', []))
                warning_msg = f"Project completed with warnings: {warning_count} warnings"
                self.add_log_entry(project_id, LogLevel.WARNING, warning_msg)
            else:
                # Partial completion with some failures
                completed_step_count = len(pipeline_status.get('completed_steps', []))
                total_possible_steps = 7  # Total pipeline steps
                partial_percentage = min(90.0, (completed_step_count / total_possible_steps) * 100)
                self.project_progress[project_id]['current_progress']['progress_percentage'] = partial_percentage
                failed_count = len(pipeline_status.get('failed_steps', []))
                partial_msg = f"Project completed partially: {completed_step_count} steps completed, {failed_count} failed"
                self.add_log_entry(project_id, LogLevel.WARNING, partial_msg)
            
            # Add warnings to logs
            for warning in pipeline_status.get('warnings', []):
                self.add_log_entry(project_id, LogLevel.WARNING, f"Pipeline warning: {warning}")
        
        # Store the complete result
        self.project_results[project_id] = result
        
        completion_status = "successfully" if result.get('pipeline_status', {}).get('overall_success', True) else "with issues"
        self.logger.info(f"Project {project_id} completed {completion_status} and result stored")
    
    def fail_project(self, project_id: str, error_message: str):
        """Mark project as failed."""
        if project_id in self.project_progress:
            self.project_progress[project_id]['current_progress']['has_failures'] = True
            self.project_progress[project_id]['current_progress']['is_running'] = False
            self.project_progress[project_id]['updated_at'] = datetime.now()
            
            self.add_log_entry(project_id, LogLevel.ERROR, f"Project failed: {error_message}")
        
        self.logger.error(f"Project {project_id} failed: {error_message}")
    
    def cancel_project(self, project_id: str):
        """Mark project as cancelled."""
        if project_id in self.project_progress:
            self.project_progress[project_id]['current_progress']['is_running'] = False
            self.project_progress[project_id]['updated_at'] = datetime.now()
            
            self.add_log_entry(project_id, LogLevel.WARNING, "Project cancelled by user")
        
        self.logger.info(f"Project {project_id} cancelled")
    
    def get_project_result(self, project_id: str) -> Optional[ProjectResult]:
        """Get complete project result."""
        if project_id not in self.project_results:
            return None
        
        result_data = self.project_results[project_id]
        
        try:
            # Convert the result data to ProjectResult model
            # This is a simplified conversion - in a real implementation,
            # you'd want more robust data transformation
            return ProjectResult(**result_data)
        except Exception as e:
            self.logger.error(f"Error converting result data for project {project_id}: {str(e)}")
            return None
    
    def get_recent_logs(self, project_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent log entries for a project."""
        if project_id not in self.project_progress:
            return []
        
        logs = self.project_progress[project_id]['current_progress']['logs']
        return logs[-limit:] if logs else []
    
    def cleanup_project(self, project_id: str):
        """Clean up project data."""
        if project_id in self.project_progress:
            del self.project_progress[project_id]
        
        if project_id in self.project_results:
            del self.project_results[project_id]
        
        self.logger.info(f"Cleaned up data for project {project_id}")
    
    def get_all_project_ids(self) -> List[str]:
        """Get all tracked project IDs."""
        return list(self.project_progress.keys())
    
    def get_project_summary(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of project status."""
        if project_id not in self.project_progress:
            return None
        
        project_data = self.project_progress[project_id]
        progress = project_data['current_progress']
        
        return {
            'project_id': project_id,
            'created_at': project_data['created_at'],
            'updated_at': project_data['updated_at'],
            'progress_percentage': progress['progress_percentage'],
            'is_running': progress['is_running'],
            'is_completed': progress['is_completed'],
            'has_failures': progress['has_failures'],
            'completed_steps': progress['completed_steps'],
            'total_steps': progress['total_steps']
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall progress service statistics."""
        total_projects = len(self.project_progress)
        completed_projects = sum(1 for p in self.project_progress.values() 
                               if p['current_progress']['is_completed'])
        failed_projects = sum(1 for p in self.project_progress.values() 
                            if p['current_progress']['has_failures'])
        running_projects = sum(1 for p in self.project_progress.values() 
                             if p['current_progress']['is_running'])
        
        return {
            'total_projects': total_projects,
            'completed_projects': completed_projects,
            'failed_projects': failed_projects,
            'running_projects': running_projects,
            'success_rate': (completed_projects / total_projects * 100) if total_projects > 0 else 0,
            'stored_results': len(self.project_results)
        }
    
    def _reconstruct_completed_project_progress(self, project_id: str) -> bool:
        """Reconstruct progress data for a completed project from file storage."""
        try:
            from pathlib import Path
            import json
            
            # Check if project exists in file storage
            projects_dir = Path("backend/generated_projects")
            if not projects_dir.exists():
                return False
            
            # Look for project by ID in metadata files
            for project_dir in projects_dir.iterdir():
                if project_dir.is_dir():
                    metadata_file = project_dir / "project_metadata.json"
                    if metadata_file.exists():
                        try:
                            with open(metadata_file, 'r') as f:
                                metadata = json.load(f)
                            
                            if metadata.get('project_id') == project_id:
                                # Found the project, reconstruct progress
                                project_name = metadata.get('project_name', 'Unknown')
                                user_input = metadata.get('user_input', '')
                                timestamp_str = metadata.get('timestamp', '')
                                
                                # Parse timestamp
                                try:
                                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                                except:
                                    timestamp = datetime.now()
                                
                                # Create mock project metadata
                                from models.schemas import ProjectMetadata, ProjectStatus
                                mock_metadata = ProjectMetadata(
                                    project_id=project_id,
                                    project_name=project_name,
                                    user_input=user_input,
                                    status=ProjectStatus.COMPLETED
                                )
                                
                                # Create completed progress data
                                completed_steps = [
                                    {'name': 'Requirements Analysis', 'description': 'Analyzing requirements from user input', 'status': 'completed', 'progress_percentage': 100, 'agent_name': 'Requirement Analyst'},
                                    {'name': 'Code Generation', 'description': 'Generating Python code from requirements', 'status': 'completed', 'progress_percentage': 100, 'agent_name': 'Python Coder'},
                                    {'name': 'Code Review', 'description': 'Reviewing code for quality and security', 'status': 'completed', 'progress_percentage': 100, 'agent_name': 'Code Reviewer'},
                                    {'name': 'Documentation', 'description': 'Creating comprehensive documentation', 'status': 'completed', 'progress_percentage': 100, 'agent_name': 'Documentation Writer'},
                                    {'name': 'Test Generation', 'description': 'Generating test cases', 'status': 'completed', 'progress_percentage': 100, 'agent_name': 'Test Generator'},
                                    {'name': 'Deployment Config', 'description': 'Creating deployment configurations', 'status': 'completed', 'progress_percentage': 100, 'agent_name': 'Deployment Engineer'},
                                    {'name': 'UI Generation', 'description': 'Creating Streamlit user interface', 'status': 'completed', 'progress_percentage': 100, 'agent_name': 'UI Designer'}
                                ]
                                
                                # Reconstruct progress data
                                self.project_progress[project_id] = {
                                    'metadata': mock_metadata,
                                    'current_progress': {
                                        'total_steps': 7,
                                        'completed_steps': 7,
                                        'failed_steps': 0,
                                        'progress_percentage': 100.0,
                                        'steps': completed_steps,
                                        'elapsed_time': 0.0,
                                        'estimated_remaining_time': 0.0,
                                        'is_running': False,
                                        'is_completed': True,
                                        'has_failures': False,
                                        'current_step_info': None,
                                        'logs': [
                                            {
                                                'timestamp': timestamp.isoformat(),
                                                'level': 'INFO',
                                                'message': 'Project completed successfully (reconstructed from file storage)',
                                                'agent': None,
                                                'step': None,
                                                'metadata': {}
                                            }
                                        ]
                                    },
                                    'created_at': timestamp,
                                    'updated_at': datetime.now()
                                }
                                
                                self.logger.info(f"Reconstructed progress data for completed project {project_id} ({project_name})")
                                return True
                                
                        except Exception as e:
                            self.logger.error(f"Error reading metadata for {project_dir}: {str(e)}")
                            continue
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error reconstructing progress for project {project_id}: {str(e)}")
            return False
