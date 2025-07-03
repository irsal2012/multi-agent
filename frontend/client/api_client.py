"""
HTTP API client for communicating with the FastAPI backend.
"""

import httpx
import logging
from typing import Dict, Any, Optional, List
import streamlit as st

class APIClient:
    """HTTP client for backend API communication."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)
        
    def _get_client(self) -> httpx.Client:
        """Get HTTP client with timeout configuration."""
        return httpx.Client(
            base_url=self.base_url,
            timeout=httpx.Timeout(30.0, connect=5.0)
        )
    
    async def _get_async_client(self) -> httpx.AsyncClient:
        """Get async HTTP client with timeout configuration."""
        return httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(30.0, connect=5.0)
        )
    
    def health_check(self) -> bool:
        """Check if the backend is healthy."""
        try:
            with self._get_client() as client:
                response = client.get("/health")
                return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return False
    
    def generate_code(self, user_input: str, project_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Start code generation."""
        try:
            with self._get_client() as client:
                payload = {
                    "user_input": user_input,
                    "project_name": project_name
                }
                response = client.post("/api/v1/pipeline/generate", json=payload)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            self.logger.error(f"Code generation request failed: {str(e)}")
            st.error(f"Failed to start code generation: {str(e)}")
            return None
    
    def validate_input(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Validate user input."""
        try:
            with self._get_client() as client:
                payload = {"user_input": user_input}
                response = client.post("/api/v1/pipeline/validate", json=payload)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            self.logger.error(f"Input validation failed: {str(e)}")
            return None
    
    def get_pipeline_status(self) -> Optional[Dict[str, Any]]:
        """Get overall pipeline status."""
        try:
            with self._get_client() as client:
                response = client.get("/api/v1/pipeline/status")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            self.logger.error(f"Failed to get pipeline status: {str(e)}")
            return None
    
    def get_project_status(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get status for a specific project."""
        try:
            with self._get_client() as client:
                response = client.get(f"/api/v1/pipeline/status/{project_id}")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            self.logger.error(f"Failed to get project status: {str(e)}")
            return None
    
    def get_project_result(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get complete project result."""
        try:
            with self._get_client() as client:
                response = client.get(f"/api/v1/pipeline/result/{project_id}")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            self.logger.error(f"Failed to get project result: {str(e)}")
            return None
    
    def cancel_project(self, project_id: str) -> bool:
        """Cancel a running project."""
        try:
            with self._get_client() as client:
                response = client.post(f"/api/v1/pipeline/cancel/{project_id}")
                response.raise_for_status()
                return True
        except Exception as e:
            self.logger.error(f"Failed to cancel project: {str(e)}")
            return False
    
    def get_agents_info(self) -> Optional[Dict[str, Any]]:
        """Get information about all agents."""
        try:
            with self._get_client() as client:
                response = client.get("/api/v1/agents/info")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            self.logger.error(f"Failed to get agents info: {str(e)}")
            return None
    
    def get_agent_details(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific agent."""
        try:
            with self._get_client() as client:
                response = client.get(f"/api/v1/agents/{agent_name}")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            self.logger.error(f"Failed to get agent details: {str(e)}")
            return None
    
    def get_project_progress(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get current progress for a project."""
        try:
            with self._get_client() as client:
                response = client.get(f"/api/v1/progress/{project_id}")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            self.logger.error(f"Failed to get project progress: {str(e)}")
            return None
    
    def get_project_logs(self, project_id: str, limit: int = 50) -> Optional[Dict[str, Any]]:
        """Get logs for a project."""
        try:
            with self._get_client() as client:
                response = client.get(f"/api/v1/progress/{project_id}/logs?limit={limit}")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            self.logger.error(f"Failed to get project logs: {str(e)}")
            return None
    
    def get_project_history(self, limit: int = 10, offset: int = 0, filter_success: Optional[bool] = None) -> Optional[Dict[str, Any]]:
        """Get project history."""
        try:
            with self._get_client() as client:
                params = {"limit": limit, "offset": offset}
                if filter_success is not None:
                    params["filter_success"] = filter_success
                
                response = client.get("/api/v1/projects/history", params=params)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            self.logger.error(f"Failed to get project history: {str(e)}")
            return None
    
    def get_project_statistics(self) -> Optional[Dict[str, Any]]:
        """Get project statistics."""
        try:
            with self._get_client() as client:
                response = client.get("/api/v1/projects/statistics")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            self.logger.error(f"Failed to get project statistics: {str(e)}")
            return None
    
    def search_projects(self, query: str) -> Optional[Dict[str, Any]]:
        """Search projects."""
        try:
            with self._get_client() as client:
                response = client.get(f"/api/v1/projects/search?q={query}")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            self.logger.error(f"Failed to search projects: {str(e)}")
            return None
    
    def get_recent_projects(self, limit: int = 10) -> Optional[Dict[str, Any]]:
        """Get recent projects."""
        try:
            with self._get_client() as client:
                response = client.get(f"/api/v1/projects/recent?limit={limit}")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            self.logger.error(f"Failed to get recent projects: {str(e)}")
            return None
    
    def test_progress_tracking(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Test progress tracking with fake data."""
        try:
            with self._get_client() as client:
                response = client.get(f"/api/v1/progress/test/{project_id}")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            self.logger.error(f"Failed to test progress tracking: {str(e)}")
            st.error(f"Progress tracking test failed: {str(e)}")
            return None
