"""
Progress API routes with WebSocket support.
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, List
import asyncio
import json
import logging

from models.responses import ProgressResponse
from services.progress_service import ProgressService
from api.dependencies import get_progress_service

router = APIRouter()
logger = logging.getLogger(__name__)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, project_id: str):
        await websocket.accept()
        if project_id not in self.active_connections:
            self.active_connections[project_id] = []
        self.active_connections[project_id].append(websocket)
        logger.info(f"WebSocket connected for project {project_id}")

    def disconnect(self, websocket: WebSocket, project_id: str):
        if project_id in self.active_connections:
            if websocket in self.active_connections[project_id]:
                self.active_connections[project_id].remove(websocket)
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]
        logger.info(f"WebSocket disconnected for project {project_id}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {str(e)}")

    async def broadcast_to_project(self, message: str, project_id: str):
        if project_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[project_id]:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to WebSocket: {str(e)}")
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for connection in disconnected:
                self.disconnect(connection, project_id)

manager = ConnectionManager()

@router.get("/{project_id}", response_model=ProgressResponse)
async def get_project_progress(
    project_id: str,
    progress_service: ProgressService = Depends(get_progress_service)
):
    """
    Get current progress for a specific project.
    
    This endpoint returns the current progress information for a project
    including step details, completion status, and recent logs.
    """
    try:
        progress = progress_service.get_project_progress(project_id)
        
        if not progress:
            raise HTTPException(status_code=404, detail="Project progress not found")
        
        return progress
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get project progress: {str(e)}")

@router.get("/{project_id}/logs")
async def get_project_logs(
    project_id: str,
    limit: int = 50,
    progress_service: ProgressService = Depends(get_progress_service)
):
    """
    Get recent logs for a specific project.
    
    This endpoint returns recent log entries for a project.
    """
    try:
        logs = progress_service.get_recent_logs(project_id, limit)
        
        return {
            "project_id": project_id,
            "logs": logs,
            "count": len(logs)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get project logs: {str(e)}")

@router.get("/{project_id}/summary")
async def get_project_summary(
    project_id: str,
    progress_service: ProgressService = Depends(get_progress_service)
):
    """
    Get a summary of project progress.
    
    This endpoint returns a condensed summary of project progress.
    """
    try:
        summary = progress_service.get_project_summary(project_id)
        
        if not summary:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get project summary: {str(e)}")

@router.websocket("/ws/{project_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    project_id: str,
    progress_service: ProgressService = Depends(get_progress_service)
):
    """
    WebSocket endpoint for real-time progress updates.
    
    This WebSocket endpoint provides real-time progress updates for a specific project.
    Clients can connect to receive live updates about pipeline execution progress.
    """
    await manager.connect(websocket, project_id)
    
    try:
        # Send initial progress state
        initial_progress = progress_service.get_project_progress(project_id)
        if initial_progress:
            await manager.send_personal_message(
                json.dumps({
                    "type": "progress_update",
                    "project_id": project_id,
                    "data": initial_progress.dict()
                }),
                websocket
            )
        
        # Keep connection alive and send periodic updates
        while True:
            try:
                # Wait for any message from client (heartbeat)
                await asyncio.wait_for(websocket.receive_text(), timeout=5.0)
            except asyncio.TimeoutError:
                # Send periodic progress updates
                current_progress = progress_service.get_project_progress(project_id)
                if current_progress:
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "progress_update",
                            "project_id": project_id,
                            "data": current_progress.dict(),
                            "timestamp": current_progress.logs[-1]["timestamp"] if current_progress.logs else None
                        }),
                        websocket
                    )
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error for project {project_id}: {str(e)}")
                break
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for project {project_id}")
    except Exception as e:
        logger.error(f"WebSocket error for project {project_id}: {str(e)}")
    finally:
        manager.disconnect(websocket, project_id)

@router.get("/")
async def get_all_active_projects(
    progress_service: ProgressService = Depends(get_progress_service)
):
    """
    Get all active projects with their progress summaries.
    
    This endpoint returns a list of all currently tracked projects
    with their basic progress information.
    """
    try:
        project_ids = progress_service.get_all_project_ids()
        
        projects = []
        for project_id in project_ids:
            summary = progress_service.get_project_summary(project_id)
            if summary:
                projects.append(summary)
        
        return {
            "active_projects": projects,
            "total_count": len(projects)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get active projects: {str(e)}")

@router.get("/test/{project_id}")
async def test_progress_tracking(
    project_id: str,
    progress_service: ProgressService = Depends(get_progress_service)
):
    """
    Test endpoint to verify progress tracking is working.
    Creates fake progress data for testing.
    """
    try:
        # Create fake project metadata for testing
        from models.schemas import ProjectMetadata, ProjectStatus
        from datetime import datetime
        
        fake_metadata = ProjectMetadata(
            project_id=project_id,
            project_name=f"test_project_{project_id}",
            user_input="Test project for progress tracking",
            status=ProjectStatus.RUNNING
        )
        
        # Create progress tracking
        progress_service.create_project_progress(project_id, fake_metadata)
        
        # Update with some test progress
        test_progress = {
            'total_steps': 7,
            'completed_steps': 2,
            'failed_steps': 0,
            'progress_percentage': 28.5,
            'steps': [
                {
                    'name': 'requirements_analysis',
                    'description': 'Analyzing requirements from user input',
                    'status': 'completed',
                    'progress_percentage': 100.0,
                    'start_time': datetime.now().isoformat(),
                    'end_time': datetime.now().isoformat(),
                    'agent_name': 'requirement_analyst'
                },
                {
                    'name': 'code_generation',
                    'description': 'Generating Python code from requirements',
                    'status': 'running',
                    'progress_percentage': 45.0,
                    'start_time': datetime.now().isoformat(),
                    'agent_name': 'python_coder'
                }
            ],
            'is_running': True,
            'is_completed': False,
            'has_failures': False,
            'current_step_info': {
                'name': 'code_generation',
                'description': 'Generating Python code from requirements',
                'status': 'running',
                'progress_percentage': 45.0,
                'agent_name': 'python_coder'
            }
        }
        
        progress_service.update_project_progress(project_id, test_progress)
        
        # Get the updated progress
        updated_progress = progress_service.get_project_progress(project_id)
        
        return {
            "message": "Test progress created successfully",
            "project_id": project_id,
            "progress": updated_progress.dict() if updated_progress else None
        }
        
    except Exception as e:
        logger.error(f"Test progress tracking failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")

# Utility function to broadcast progress updates (can be called from services)
async def broadcast_progress_update(project_id: str, progress_data: dict):
    """Broadcast progress update to all connected WebSocket clients for a project."""
    message = json.dumps({
        "type": "progress_update",
        "project_id": project_id,
        "data": progress_data
    })
    await manager.broadcast_to_project(message, project_id)
