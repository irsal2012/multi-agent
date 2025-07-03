"""
Project service for managing project data and history.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from models.responses import ProjectHistoryResponse, ProjectHistoryItem, ProjectResult
from models.requests import ProjectQueryRequest

class ProjectService:
    """Service for managing project data and history."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.project_history: List[Dict[str, Any]] = []
        self.project_results: Dict[str, Dict[str, Any]] = {}
    
    async def add_project_to_history(self, project_data: Dict[str, Any]):
        """Add a project to the history."""
        history_item = {
            'timestamp': project_data.get('timestamp', datetime.now()),
            'project_name': project_data.get('project_name', ''),
            'user_input': project_data.get('user_input', ''),
            'success': project_data.get('success', False),
            'execution_time': project_data.get('execution_time', 0.0),
            'error': project_data.get('error')
        }
        
        self.project_history.append(history_item)
        
        # Keep only last 1000 projects
        if len(self.project_history) > 1000:
            self.project_history = self.project_history[-1000:]
        
        self.logger.info(f"Added project {project_data.get('project_name')} to history")
    
    async def get_project_history(self, query: ProjectQueryRequest) -> ProjectHistoryResponse:
        """Get project history with filtering and pagination."""
        
        # Filter by success status if specified
        filtered_history = self.project_history
        if query.filter_success is not None:
            filtered_history = [
                project for project in self.project_history 
                if project['success'] == query.filter_success
            ]
        
        # Sort by timestamp (most recent first)
        filtered_history = sorted(
            filtered_history, 
            key=lambda x: x['timestamp'], 
            reverse=True
        )
        
        # Apply pagination
        start_idx = query.offset
        end_idx = start_idx + query.limit
        paginated_history = filtered_history[start_idx:end_idx]
        
        # Convert to ProjectHistoryItem objects
        history_items = []
        for item in paginated_history:
            history_item = ProjectHistoryItem(
                timestamp=item['timestamp'],
                project_name=item['project_name'],
                user_input=item['user_input'],
                success=item['success'],
                execution_time=item['execution_time'],
                error=item.get('error')
            )
            history_items.append(history_item)
        
        # Calculate counts
        total_count = len(filtered_history)
        successful_count = sum(1 for item in filtered_history if item['success'])
        failed_count = total_count - successful_count
        
        return ProjectHistoryResponse(
            projects=history_items,
            total_count=total_count,
            successful_count=successful_count,
            failed_count=failed_count
        )
    
    async def get_project_by_name(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Get a project by name from history."""
        for project in reversed(self.project_history):  # Search from most recent
            if project['project_name'] == project_name:
                return project
        return None
    
    async def store_project_result(self, project_id: str, result: Dict[str, Any]):
        """Store complete project result."""
        self.project_results[project_id] = result
        
        # Also add to history
        await self.add_project_to_history({
            'timestamp': result.get('timestamp', datetime.now()),
            'project_name': result.get('project_name', ''),
            'user_input': result.get('user_input', ''),
            'success': result.get('pipeline_metadata', {}).get('success', False),
            'execution_time': result.get('pipeline_metadata', {}).get('execution_time_seconds', 0.0),
            'error': None
        })
        
        self.logger.info(f"Stored result for project {project_id}")
    
    async def get_project_result(self, project_id: str) -> Optional[ProjectResult]:
        """Get complete project result by ID."""
        if project_id not in self.project_results:
            return None
        
        result_data = self.project_results[project_id]
        
        try:
            return ProjectResult(**result_data)
        except Exception as e:
            self.logger.error(f"Error converting result data for project {project_id}: {str(e)}")
            return None
    
    async def delete_project_result(self, project_id: str) -> bool:
        """Delete a project result."""
        if project_id in self.project_results:
            del self.project_results[project_id]
            self.logger.info(f"Deleted result for project {project_id}")
            return True
        return False
    
    async def get_project_statistics(self) -> Dict[str, Any]:
        """Get project statistics."""
        if not self.project_history:
            return {
                'total_projects': 0,
                'successful_projects': 0,
                'failed_projects': 0,
                'success_rate': 0.0,
                'average_execution_time': 0.0,
                'projects_last_24h': 0,
                'projects_last_7d': 0
            }
        
        total_projects = len(self.project_history)
        successful_projects = sum(1 for p in self.project_history if p['success'])
        failed_projects = total_projects - successful_projects
        success_rate = (successful_projects / total_projects) * 100 if total_projects > 0 else 0.0
        
        # Calculate average execution time
        execution_times = [p['execution_time'] for p in self.project_history if p['execution_time'] > 0]
        average_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0.0
        
        # Calculate recent project counts
        now = datetime.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        
        projects_last_24h = sum(
            1 for p in self.project_history 
            if isinstance(p['timestamp'], datetime) and p['timestamp'] >= last_24h
        )
        
        projects_last_7d = sum(
            1 for p in self.project_history 
            if isinstance(p['timestamp'], datetime) and p['timestamp'] >= last_7d
        )
        
        return {
            'total_projects': total_projects,
            'successful_projects': successful_projects,
            'failed_projects': failed_projects,
            'success_rate': success_rate,
            'average_execution_time': average_execution_time,
            'projects_last_24h': projects_last_24h,
            'projects_last_7d': projects_last_7d
        }
    
    async def get_recent_projects(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent projects."""
        sorted_history = sorted(
            self.project_history, 
            key=lambda x: x['timestamp'], 
            reverse=True
        )
        return sorted_history[:limit]
    
    async def search_projects(self, query: str) -> List[Dict[str, Any]]:
        """Search projects by user input or project name."""
        query_lower = query.lower()
        
        matching_projects = []
        for project in self.project_history:
            if (query_lower in project['project_name'].lower() or 
                query_lower in project['user_input'].lower()):
                matching_projects.append(project)
        
        # Sort by timestamp (most recent first)
        return sorted(matching_projects, key=lambda x: x['timestamp'], reverse=True)
    
    async def cleanup_old_results(self, max_age_days: int = 30):
        """Clean up old project results."""
        cutoff_time = datetime.now() - timedelta(days=max_age_days)
        
        # Clean up project results
        results_to_remove = []
        for project_id, result in self.project_results.items():
            result_time = result.get('timestamp')
            if isinstance(result_time, str):
                try:
                    result_time = datetime.fromisoformat(result_time.replace('Z', '+00:00'))
                except:
                    continue
            
            if isinstance(result_time, datetime) and result_time < cutoff_time:
                results_to_remove.append(project_id)
        
        for project_id in results_to_remove:
            del self.project_results[project_id]
        
        # Clean up history
        self.project_history = [
            project for project in self.project_history
            if isinstance(project['timestamp'], datetime) and project['timestamp'] >= cutoff_time
        ]
        
        self.logger.info(f"Cleaned up {len(results_to_remove)} old project results and history entries")
    
    def get_all_project_ids(self) -> List[str]:
        """Get all stored project IDs."""
        return list(self.project_results.keys())
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get project statistics (alias for get_project_statistics for health check)."""
        return await self.get_project_statistics()
