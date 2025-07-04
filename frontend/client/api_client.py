"""
HTTP API client for communicating with the FastAPI backend.
"""

import httpx
import logging
import time
from typing import Dict, Any, Optional, List
import streamlit as st

class APIClient:
    """HTTP client for backend API communication."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)
        self._connection_status = None
        self._last_health_check = 0
        
    def _get_client(self, extended_timeout: bool = False) -> httpx.Client:
        """Get HTTP client with timeout configuration."""
        if extended_timeout:
            # Extended timeout for long-running operations like UI generation
            timeout = httpx.Timeout(120.0, connect=15.0, read=120.0, write=30.0)
        else:
            # Standard timeout for regular operations
            timeout = httpx.Timeout(30.0, connect=10.0, read=30.0, write=10.0)
        
        return httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            follow_redirects=True
        )
    
    async def _get_async_client(self) -> httpx.AsyncClient:
        """Get async HTTP client with timeout configuration."""
        return httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(30.0, connect=5.0)
        )
    
    def health_check(self, max_retries: int = 3, retry_delay: float = 1.0) -> bool:
        """Check if the backend is healthy with retry logic."""
        current_time = time.time()
        
        # Use cached result if recent (within 5 seconds)
        if (self._connection_status is not None and 
            current_time - self._last_health_check < 5.0):
            return self._connection_status
        
        for attempt in range(max_retries):
            try:
                with self._get_client() as client:
                    response = client.get("/health")
                    if response.status_code == 200:
                        # Check if response indicates services are ready
                        try:
                            health_data = response.json()
                            is_ready = health_data.get('ready', True)  # Default to True for backward compatibility
                            self._connection_status = is_ready
                            self._last_health_check = current_time
                            
                            if not is_ready:
                                self.logger.warning(f"Backend services not ready: {health_data}")
                            
                            return is_ready
                        except Exception:
                            # If we can't parse JSON, assume healthy if status is 200
                            self._connection_status = True
                            self._last_health_check = current_time
                            return True
                    else:
                        self.logger.warning(f"Health check returned status {response.status_code}")
                        
            except httpx.ConnectError as e:
                self.logger.warning(f"Connection failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                    
            except httpx.TimeoutException as e:
                self.logger.warning(f"Health check timeout (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    
            except Exception as e:
                self.logger.error(f"Health check failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
        
        # All attempts failed
        self._connection_status = False
        self._last_health_check = current_time
        return False
    
    def get_detailed_health_status(self) -> Dict[str, Any]:
        """Get detailed health status from backend."""
        try:
            with self._get_client() as client:
                response = client.get("/health")
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "status": "unhealthy",
                        "error": f"HTTP {response.status_code}",
                        "ready": False
                    }
        except Exception as e:
            return {
                "status": "unreachable",
                "error": str(e),
                "ready": False
            }
    
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
    
    def get_project_progress(self, project_id: str, extended_timeout: bool = False) -> Optional[Dict[str, Any]]:
        """Get current progress for a project with enhanced error handling."""
        max_retries = 3 if extended_timeout else 2
        retry_delay = 2.0 if extended_timeout else 1.0
        
        for attempt in range(max_retries):
            try:
                with self._get_client(extended_timeout=extended_timeout) as client:
                    response = client.get(f"/api/v1/progress/{project_id}")
                    response.raise_for_status()
                    return response.json()
                    
            except httpx.TimeoutException as e:
                self.logger.warning(f"Progress request timeout (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    self.logger.error(f"Progress request timed out after {max_retries} attempts")
                    return None
                    
            except httpx.ConnectError as e:
                self.logger.warning(f"Progress request connection failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    self.logger.error(f"Progress request connection failed after {max_retries} attempts")
                    return None
                    
            except Exception as e:
                self.logger.error(f"Failed to get project progress (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    return None
        
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
    
    def check_project_completion_fallback(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Check if project is completed by looking for results when progress is unavailable."""
        try:
            with self._get_client() as client:
                # Try to get project result
                response = client.get(f"/api/v1/pipeline/result/{project_id}")
                if response.status_code == 200:
                    result = response.json()
                    self.logger.info(f"Found completed project result for {project_id}")
                    return {
                        'is_completed': True,
                        'has_result': True,
                        'result': result
                    }
                elif response.status_code == 404:
                    # No result found, project might not exist or failed
                    return {
                        'is_completed': False,
                        'has_result': False,
                        'result': None
                    }
                else:
                    # Other error
                    return None
        except Exception as e:
            self.logger.error(f"Failed to check project completion fallback: {str(e)}")
            return None
