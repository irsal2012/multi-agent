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
    """Track progress of multi-agent pipeline."""
    
    def __init__(self):
        self.steps = []
        self.current_step = 0
        self.start_time = datetime.now()
    
    def add_step(self, step_name: str, description: str = "") -> None:
        """Add a step to track."""
        self.steps.append({
            'name': step_name,
            'description': description,
            'status': 'pending',
            'start_time': None,
            'end_time': None,
            'duration': None
        })
    
    def start_step(self, step_index: int) -> None:
        """Mark step as started."""
        if 0 <= step_index < len(self.steps):
            self.steps[step_index]['status'] = 'running'
            self.steps[step_index]['start_time'] = datetime.now()
            self.current_step = step_index
    
    def complete_step(self, step_index: int, success: bool = True) -> None:
        """Mark step as completed."""
        if 0 <= step_index < len(self.steps):
            self.steps[step_index]['status'] = 'completed' if success else 'failed'
            self.steps[step_index]['end_time'] = datetime.now()
            if self.steps[step_index]['start_time']:
                duration = self.steps[step_index]['end_time'] - self.steps[step_index]['start_time']
                self.steps[step_index]['duration'] = duration.total_seconds()
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress status."""
        completed = sum(1 for step in self.steps if step['status'] == 'completed')
        failed = sum(1 for step in self.steps if step['status'] == 'failed')
        total = len(self.steps)
        
        return {
            'total_steps': total,
            'completed_steps': completed,
            'failed_steps': failed,
            'current_step': self.current_step,
            'progress_percentage': (completed / total * 100) if total > 0 else 0,
            'steps': self.steps,
            'elapsed_time': (datetime.now() - self.start_time).total_seconds()
        }
