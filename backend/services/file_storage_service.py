"""
File storage service for persisting generated projects to disk.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

class FileStorageService:
    """Service for managing persistent file storage of generated projects."""
    
    def __init__(self, base_storage_path: str = "generated_projects"):
        self.logger = logging.getLogger(__name__)
        self.base_storage_path = Path(base_storage_path)
        
        # Create base storage directory if it doesn't exist
        self.base_storage_path.mkdir(exist_ok=True)
        
        self.logger.info(f"File storage initialized at: {self.base_storage_path.absolute()}")
    
    def save_project(self, project_id: str, project_data: Dict[str, Any]) -> str:
        """Save a complete project to disk with organized folder structure."""
        try:
            # Create project directory
            project_name = project_data.get('project_name', f'project_{project_id[:8]}')
            # Sanitize project name for filesystem
            safe_project_name = self._sanitize_filename(project_name)
            
            project_dir = self.base_storage_path / safe_project_name
            project_dir.mkdir(exist_ok=True)
            
            # Save project metadata
            metadata = {
                'project_id': project_id,
                'project_name': project_data.get('project_name'),
                'user_input': project_data.get('user_input'),
                'timestamp': project_data.get('timestamp', datetime.now()).isoformat(),
                'generated_at': datetime.now().isoformat()
            }
            
            with open(project_dir / 'project_metadata.json', 'w') as f:
                json.dump(metadata, f, indent=2, default=str)
            
            # Save generated code files
            code_data = project_data.get('code', {})
            if isinstance(code_data, dict):
                # Handle new format with final_code
                final_code = code_data.get('final_code', '')
                if final_code:
                    with open(project_dir / 'main.py', 'w') as f:
                        f.write(final_code)
                
                # Save additional modules if any
                additional_modules = code_data.get('additional_modules', [])
                for module_name in additional_modules:
                    # This would need to be enhanced to get actual module content
                    pass
            
            # Check if we have generated_files in the old format
            if 'generated_files' in project_data:
                generated_files = project_data['generated_files']
                if isinstance(generated_files, dict):
                    for filename, content in generated_files.items():
                        safe_filename = self._sanitize_filename(filename)
                        with open(project_dir / safe_filename, 'w') as f:
                            f.write(content)
            
            # Save documentation
            docs_data = project_data.get('documentation', {})
            if isinstance(docs_data, dict) and 'readme' in docs_data:
                with open(project_dir / 'README.md', 'w') as f:
                    f.write(docs_data['readme'])
            
            # Save tests
            tests_data = project_data.get('tests', {})
            if isinstance(tests_data, dict) and 'test_code' in tests_data:
                with open(project_dir / 'test_main.py', 'w') as f:
                    f.write(tests_data['test_code'])
            
            # Save deployment configuration
            deployment_data = project_data.get('deployment', {})
            if isinstance(deployment_data, dict) and 'deployment_configs' in deployment_data:
                with open(project_dir / 'DEPLOYMENT.md', 'w') as f:
                    f.write(deployment_data['deployment_configs'])
            
            # Save UI code
            ui_data = project_data.get('ui', {})
            if isinstance(ui_data, dict) and 'streamlit_app' in ui_data:
                with open(project_dir / 'streamlit_app.py', 'w') as f:
                    f.write(ui_data['streamlit_app'])
            
            # Save requirements.txt if we can infer dependencies
            self._generate_requirements_file(project_dir, project_data)
            
            # Save complete project data as JSON for backup
            with open(project_dir / 'complete_project_data.json', 'w') as f:
                json.dump(project_data, f, indent=2, default=str)
            
            self.logger.info(f"Project {project_id} saved to: {project_dir.absolute()}")
            return str(project_dir.absolute())
            
        except Exception as e:
            self.logger.error(f"Failed to save project {project_id}: {str(e)}")
            raise
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem compatibility."""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip(' .')
        
        # Ensure it's not empty
        if not filename:
            filename = 'unnamed_file'
        
        return filename
    
    def _generate_requirements_file(self, project_dir: Path, project_data: Dict[str, Any]):
        """Generate a requirements.txt file based on project content."""
        requirements = set()
        
        # Check code content for common imports
        code_content = ""
        
        # Get code from various sources
        code_data = project_data.get('code', {})
        if isinstance(code_data, dict):
            code_content += code_data.get('final_code', '')
        
        if 'generated_files' in project_data:
            generated_files = project_data['generated_files']
            if isinstance(generated_files, dict):
                for content in generated_files.values():
                    code_content += content
        
        # Check for common imports and add corresponding packages
        import_mappings = {
            'import requests': 'requests',
            'from requests': 'requests',
            'import pandas': 'pandas',
            'from pandas': 'pandas',
            'import numpy': 'numpy',
            'from numpy': 'numpy',
            'import flask': 'flask',
            'from flask': 'flask',
            'import fastapi': 'fastapi',
            'from fastapi': 'fastapi',
            'import streamlit': 'streamlit',
            'from streamlit': 'streamlit',
            'import sqlalchemy': 'sqlalchemy',
            'from sqlalchemy': 'sqlalchemy',
            'import pytest': 'pytest',
            'from pytest': 'pytest',
        }
        
        for import_pattern, package in import_mappings.items():
            if import_pattern in code_content.lower():
                requirements.add(package)
        
        # Always add some basic packages for generated projects
        basic_requirements = []
        
        # Add streamlit if UI was generated
        ui_data = project_data.get('ui', {})
        if isinstance(ui_data, dict) and ui_data.get('streamlit_app'):
            basic_requirements.append('streamlit')
        
        requirements.update(basic_requirements)
        
        # Write requirements.txt
        if requirements:
            with open(project_dir / 'requirements.txt', 'w') as f:
                for req in sorted(requirements):
                    f.write(f"{req}\n")
        else:
            # Create empty requirements.txt with comment
            with open(project_dir / 'requirements.txt', 'w') as f:
                f.write("# Add your project dependencies here\n")
                f.write("# Example:\n")
                f.write("# requests>=2.25.1\n")
                f.write("# pandas>=1.3.0\n")
    
    def load_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Load complete project data from disk."""
        try:
            project_path = self.get_project_path(project_id)
            if not project_path:
                return None
            
            project_dir = Path(project_path)
            complete_data_file = project_dir / 'complete_project_data.json'
            
            if complete_data_file.exists():
                with open(complete_data_file, 'r') as f:
                    project_data = json.load(f)
                    self.logger.info(f"Loaded complete project data for {project_id} from {complete_data_file}")
                    return project_data
            else:
                # Fallback: reconstruct from individual files
                self.logger.info(f"Reconstructing project data for {project_id} from individual files")
                return self._reconstruct_project_from_files(project_dir, project_id)
                
        except Exception as e:
            self.logger.error(f"Failed to load project {project_id}: {str(e)}")
            return None
    
    def _reconstruct_project_from_files(self, project_dir: Path, project_id: str) -> Dict[str, Any]:
        """Reconstruct project data from individual files when complete JSON is not available."""
        try:
            # Load metadata
            metadata = {}
            metadata_file = project_dir / 'project_metadata.json'
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            
            # Load code files
            main_code = ""
            main_py = project_dir / 'main.py'
            if main_py.exists():
                with open(main_py, 'r') as f:
                    main_code = f.read()
            
            # Load documentation
            readme = ""
            readme_file = project_dir / 'README.md'
            if readme_file.exists():
                with open(readme_file, 'r') as f:
                    readme = f.read()
            
            # Load tests
            test_code = ""
            test_file = project_dir / 'test_main.py'
            if test_file.exists():
                with open(test_file, 'r') as f:
                    test_code = f.read()
            
            # Load deployment config
            deployment_config = ""
            deployment_file = project_dir / 'DEPLOYMENT.md'
            if deployment_file.exists():
                with open(deployment_file, 'r') as f:
                    deployment_config = f.read()
            
            # Load UI code
            ui_code = ""
            ui_file = project_dir / 'streamlit_app.py'
            if ui_file.exists():
                with open(ui_file, 'r') as f:
                    ui_code = f.read()
            
            # Reconstruct project data structure
            now = datetime.now()
            project_data = {
                'project_name': metadata.get('project_name', f'project_{project_id[:8]}'),
                'timestamp': metadata.get('timestamp', now.isoformat()),
                'user_input': metadata.get('user_input', 'Reconstructed from files'),
                'requirements': {
                    'original_input': metadata.get('user_input', 'Reconstructed from files'),
                    'analyzed_requirements': metadata.get('user_input', 'Reconstructed from files'),
                    'timestamp': now
                },
                'code': {
                    'final_code': main_code,
                    'original_code': main_code,
                    'additional_modules': [],
                    'review_feedback': [],
                    'loop_summary': {
                        'total_iterations': 1,
                        'improvements_made': 0,
                        'final_quality_score': 85
                    }
                },
                'documentation': {
                    'readme': readme,
                    'timestamp': now
                },
                'tests': {
                    'test_code': test_code,
                    'additional_tests': [],
                    'full_response': '',
                    'timestamp': now
                },
                'deployment': {
                    'deployment_configs': deployment_config,
                    'timestamp': now
                },
                'ui': {
                    'streamlit_app': ui_code,
                    'additional_ui_files': [],
                    'full_response': '',
                    'timestamp': now
                },
                'progress': {
                    'total_steps': 7,
                    'completed_steps': 7,
                    'failed_steps': 0,
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
                    'success': True
                }
            }
            
            self.logger.info(f"Reconstructed project data for {project_id}")
            return project_data
            
        except Exception as e:
            self.logger.error(f"Failed to reconstruct project {project_id}: {str(e)}")
            raise
    
    def get_project_path(self, project_id: str, project_name: Optional[str] = None) -> Optional[str]:
        """Get the file system path for a project."""
        if project_name:
            safe_project_name = self._sanitize_filename(project_name)
            project_dir = self.base_storage_path / safe_project_name
            if project_dir.exists():
                return str(project_dir.absolute())
        
        # Fallback: search for project by ID in metadata files
        for project_dir in self.base_storage_path.iterdir():
            if project_dir.is_dir():
                metadata_file = project_dir / 'project_metadata.json'
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                            if metadata.get('project_id') == project_id:
                                return str(project_dir.absolute())
                    except:
                        continue
        
        return None
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all stored projects."""
        projects = []
        
        for project_dir in self.base_storage_path.iterdir():
            if project_dir.is_dir():
                metadata_file = project_dir / 'project_metadata.json'
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                            metadata['storage_path'] = str(project_dir.absolute())
                            projects.append(metadata)
                    except Exception as e:
                        self.logger.warning(f"Failed to read metadata for {project_dir}: {str(e)}")
        
        # Sort by timestamp (newest first)
        projects.sort(key=lambda x: x.get('generated_at', ''), reverse=True)
        return projects
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project from disk."""
        project_path = self.get_project_path(project_id)
        if project_path:
            try:
                import shutil
                shutil.rmtree(project_path)
                self.logger.info(f"Deleted project {project_id} from {project_path}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to delete project {project_id}: {str(e)}")
        return False
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        try:
            projects = self.list_projects()
            total_size = 0
            
            for project_dir in self.base_storage_path.iterdir():
                if project_dir.is_dir():
                    for file_path in project_dir.rglob('*'):
                        if file_path.is_file():
                            total_size += file_path.stat().st_size
            
            return {
                'base_path': str(self.base_storage_path.absolute()),
                'total_projects': len(projects),
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'projects': projects
            }
        except Exception as e:
            self.logger.error(f"Failed to get storage stats: {str(e)}")
            return {
                'base_path': str(self.base_storage_path.absolute()),
                'total_projects': 0,
                'total_size_bytes': 0,
                'total_size_mb': 0,
                'projects': [],
                'error': str(e)
            }
