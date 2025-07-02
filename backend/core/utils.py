"""
Utility functions for the Multi-Agent Framework.
"""

import json
import os
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('multi_agent_framework.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def ensure_directory(path: str) -> None:
    """Ensure directory exists, create if it doesn't."""
    Path(path).mkdir(parents=True, exist_ok=True)

def save_json(data: Dict[Any, Any], filepath: str) -> None:
    """Save data as JSON file."""
    ensure_directory(os.path.dirname(filepath))
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_json(filepath: str) -> Dict[Any, Any]:
    """Load data from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_text(content: str, filepath: str) -> None:
    """Save text content to file."""
    ensure_directory(os.path.dirname(filepath))
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def load_text(filepath: str) -> str:
    """Load text content from file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def generate_timestamp() -> str:
    """Generate timestamp string for file naming."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def validate_requirements(requirements: Dict[str, Any]) -> bool:
    """Validate requirements structure."""
    required_keys = [
        'functional_requirements',
        'non_functional_requirements',
        'constraints',
        'assumptions'
    ]
    return all(key in requirements for key in required_keys)

def extract_code_blocks(text: str, language: str = "python") -> List[str]:
    """Extract code blocks from markdown text."""
    import re
    pattern = f"```{language}\\n(.*?)\\n```"
    matches = re.findall(pattern, text, re.DOTALL)
    return matches

def format_agent_response(agent_name: str, content: str) -> str:
    """Format agent response with timestamp and agent name."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"[{timestamp}] {agent_name}: {content}"

def create_project_structure(base_path: str, project_name: str) -> Dict[str, str]:
    """Create project directory structure."""
    project_path = os.path.join(base_path, project_name)
    
    directories = {
        'root': project_path,
        'src': os.path.join(project_path, 'src'),
        'tests': os.path.join(project_path, 'tests'),
        'docs': os.path.join(project_path, 'docs'),
        'config': os.path.join(project_path, 'config'),
        'scripts': os.path.join(project_path, 'scripts'),
    }
    
    for dir_path in directories.values():
        ensure_directory(dir_path)
    
    return directories

def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters."""
    import re
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove multiple underscores
    filename = re.sub(r'_+', '_', filename)
    # Remove leading/trailing underscores
    filename = filename.strip('_')
    return filename

class ProgressTracker:
    """Enhanced progress tracker with real-time updates and detailed monitoring."""
    
    def __init__(self):
        self.steps = []
        self.current_step = 0
        self.start_time = datetime.now()
        self.logs = []
        self.agent_activities = {}
        self.substeps = {}
        self.estimated_times = {}
        self.callbacks = []
    
    def add_step(self, step_name: str, description: str = "", estimated_duration: float = 30.0) -> None:
        """Add a step to track with estimated duration."""
        self.steps.append({
            'name': step_name,
            'description': description,
            'status': 'pending',
            'start_time': None,
            'end_time': None,
            'duration': None,
            'estimated_duration': estimated_duration,
            'substeps': [],
            'agent_name': None,
            'progress_percentage': 0
        })
        self.estimated_times[step_name] = estimated_duration
    
    def add_substep(self, step_index: int, substep_name: str, description: str = "") -> None:
        """Add a substep to a main step."""
        if 0 <= step_index < len(self.steps):
            self.steps[step_index]['substeps'].append({
                'name': substep_name,
                'description': description,
                'status': 'pending',
                'timestamp': datetime.now().isoformat()
            })
            self._notify_callbacks()
    
    def update_substep(self, step_index: int, substep_name: str, status: str) -> None:
        """Update substep status."""
        if 0 <= step_index < len(self.steps):
            for substep in self.steps[step_index]['substeps']:
                if substep['name'] == substep_name:
                    substep['status'] = status
                    substep['timestamp'] = datetime.now().isoformat()
                    break
            self._notify_callbacks()
    
    def start_step(self, step_index: int, agent_name: str = None) -> None:
        """Mark step as started with optional agent name."""
        if 0 <= step_index < len(self.steps):
            self.steps[step_index]['status'] = 'running'
            self.steps[step_index]['start_time'] = datetime.now().isoformat()
            self.steps[step_index]['agent_name'] = agent_name
            self.current_step = step_index
            
            # Log the step start
            self.add_log(f"Started: {self.steps[step_index]['description']}", "info", agent_name)
            
            # Track agent activity
            if agent_name:
                self.agent_activities[agent_name] = {
                    'status': 'active',
                    'current_task': self.steps[step_index]['description'],
                    'start_time': datetime.now().isoformat()
                }
            
            self._notify_callbacks()
    
    def update_step_progress(self, step_index: int, percentage: float, message: str = None) -> None:
        """Update progress percentage for a specific step."""
        if 0 <= step_index < len(self.steps):
            self.steps[step_index]['progress_percentage'] = min(100, max(0, percentage))
            if message:
                self.add_log(f"Progress: {message} ({percentage:.1f}%)", "info")
            self._notify_callbacks()
    
    def complete_step(self, step_index: int, success: bool = True, message: str = None) -> None:
        """Mark step as completed with optional message."""
        if 0 <= step_index < len(self.steps):
            self.steps[step_index]['status'] = 'completed' if success else 'failed'
            self.steps[step_index]['progress_percentage'] = 100 if success else 0
            end_time = datetime.now()
            self.steps[step_index]['end_time'] = end_time.isoformat()
            
            if self.steps[step_index]['start_time']:
                start_time = datetime.fromisoformat(self.steps[step_index]['start_time'])
                duration = end_time - start_time
                self.steps[step_index]['duration'] = duration.total_seconds()
            
            # Log completion
            status_msg = "Completed" if success else "Failed"
            log_message = message or f"{status_msg}: {self.steps[step_index]['description']}"
            log_level = "success" if success else "error"
            self.add_log(log_message, log_level, self.steps[step_index]['agent_name'])
            
            # Update agent activity
            agent_name = self.steps[step_index]['agent_name']
            if agent_name and agent_name in self.agent_activities:
                self.agent_activities[agent_name]['status'] = 'completed' if success else 'failed'
                self.agent_activities[agent_name]['end_time'] = end_time.isoformat()
            
            self._notify_callbacks()
    
    def add_log(self, message: str, level: str = "info", agent_name: str = None) -> None:
        """Add a log entry with timestamp."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'level': level,  # info, success, warning, error
            'agent_name': agent_name
        }
        self.logs.append(log_entry)
        
        # Keep only last 100 logs to prevent memory issues
        if len(self.logs) > 100:
            self.logs = self.logs[-100:]
        
        self._notify_callbacks()
    
    def get_progress(self) -> Dict[str, Any]:
        """Get comprehensive progress status."""
        completed = sum(1 for step in self.steps if step['status'] == 'completed')
        failed = sum(1 for step in self.steps if step['status'] == 'failed')
        running = sum(1 for step in self.steps if step['status'] == 'running')
        total = len(self.steps)
        
        # Calculate overall progress percentage
        overall_progress = 0
        if total > 0:
            for i, step in enumerate(self.steps):
                if step['status'] == 'completed':
                    overall_progress += 100 / total
                elif step['status'] == 'running':
                    step_progress = step.get('progress_percentage', 0)
                    overall_progress += (step_progress / total)
        
        # Calculate estimated time remaining
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        estimated_total_time = sum(self.estimated_times.values())
        estimated_remaining = max(0, estimated_total_time - elapsed_time)
        
        # Get current step info
        current_step_info = None
        if 0 <= self.current_step < len(self.steps):
            current_step_info = self.steps[self.current_step].copy()
        
        return {
            'total_steps': total,
            'completed_steps': completed,
            'failed_steps': failed,
            'running_steps': running,
            'current_step': self.current_step,
            'current_step_info': current_step_info,
            'progress_percentage': overall_progress,
            'steps': self.steps,
            'elapsed_time': elapsed_time,
            'estimated_remaining_time': estimated_remaining,
            'estimated_total_time': estimated_total_time,
            'logs': self.logs[-20:],  # Last 20 logs
            'agent_activities': self.agent_activities,
            'is_running': running > 0,
            'is_completed': completed == total and total > 0,
            'has_failures': failed > 0
        }
    
    def get_recent_logs(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent log entries."""
        return self.logs[-count:] if self.logs else []
    
    def add_progress_callback(self, callback) -> None:
        """Add a callback function to be called on progress updates."""
        self.callbacks.append(callback)
    
    def _notify_callbacks(self) -> None:
        """Notify all registered callbacks of progress updates."""
        for callback in self.callbacks:
            try:
                callback(self.get_progress())
            except Exception as e:
                # Don't let callback errors break the progress tracking
                pass
    
    def reset(self) -> None:
        """Reset the progress tracker for a new run."""
        self.steps = []
        self.current_step = 0
        self.start_time = datetime.now()
        self.logs = []
        self.agent_activities = {}
        self.substeps = {}
        self.callbacks = []


class RealTimeProgressManager:
    """Manages real-time progress updates for Streamlit."""
    
    def __init__(self):
        self.progress_tracker = None
        self.update_containers = {}
        self.is_active = False
    
    def initialize(self, progress_tracker: ProgressTracker):
        """Initialize with a progress tracker."""
        self.progress_tracker = progress_tracker
        self.is_active = True
        
        # Add callback to progress tracker
        progress_tracker.add_progress_callback(self._on_progress_update)
    
    def _on_progress_update(self, progress_data: Dict[str, Any]):
        """Handle progress updates from the tracker."""
        if not self.is_active:
            return
        
        # Update containers if they exist
        for container_name, container in self.update_containers.items():
            try:
                if container_name == 'progress_bar' and 'progress_bar' in container:
                    container['progress_bar'].progress(progress_data['progress_percentage'] / 100)
                elif container_name == 'status_text' and 'status_text' in container:
                    current_step = progress_data.get('current_step_info')
                    if current_step:
                        status_icon = self._get_status_icon(current_step['status'])
                        container['status_text'].write(f"{status_icon} {current_step['description']}")
            except Exception:
                pass
    
    def _get_status_icon(self, status: str) -> str:
        """Get icon for status."""
        icons = {
            'pending': '⏳',
            'running': '🔄',
            'completed': '✅',
            'failed': '❌'
        }
        return icons.get(status, '❓')
    
    def register_container(self, name: str, container_dict: Dict):
        """Register a container for updates."""
        self.update_containers[name] = container_dict
    
    def stop(self):
        """Stop the progress manager."""
        self.is_active = False
        self.update_containers.clear()
