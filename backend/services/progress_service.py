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
        """Mark project as completed and store result."""
        if project_id in self.project_progress:
            self.project_progress[project_id]['current_progress']['is_completed'] = True
            self.project_progress[project_id]['current_progress']['is_running'] = False
            self.project_progress[project_id]['current_progress']['progress_percentage'] = 100.0
            self.project_progress[project_id]['updated_at'] = datetime.now()
            
            self.add_log_entry(project_id, LogLevel.INFO, "Project completed successfully")
        
        # Store the complete result
        self.project_results[project_id] = result
        
        self.logger.info(f"Project {project_id} completed and result stored")
    
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
