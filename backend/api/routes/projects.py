"""
Projects API routes.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional

from models.requests import ProjectQueryRequest
from models.responses import ProjectHistoryResponse, ProjectResult
from services.project_service import ProjectService
from api.dependencies import get_project_service

router = APIRouter()

@router.get("/history", response_model=ProjectHistoryResponse)
async def get_project_history(
    limit: int = Query(10, ge=1, le=100, description="Number of projects to return"),
    offset: int = Query(0, ge=0, description="Number of projects to skip"),
    filter_success: Optional[bool] = Query(None, description="Filter by success status"),
    project_service: ProjectService = Depends(get_project_service)
):
    """
    Get project history with filtering and pagination.
    
    This endpoint returns the history of all projects with optional filtering
    by success status and pagination support.
    """
    try:
        query = ProjectQueryRequest(
            limit=limit,
            offset=offset,
            filter_success=filter_success
        )
        
        history = await project_service.get_project_history(query)
        return history
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get project history: {str(e)}")

@router.get("/statistics")
async def get_project_statistics(
    project_service: ProjectService = Depends(get_project_service)
):
    """
    Get project statistics.
    
    This endpoint returns comprehensive statistics about all projects
    including success rates, execution times, and recent activity.
    """
    try:
        stats = await project_service.get_project_statistics()
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get project statistics: {str(e)}")

@router.get("/recent")
async def get_recent_projects(
    limit: int = Query(10, ge=1, le=50, description="Number of recent projects to return"),
    project_service: ProjectService = Depends(get_project_service)
):
    """
    Get recent projects.
    
    This endpoint returns the most recently created projects.
    """
    try:
        recent_projects = await project_service.get_recent_projects(limit)
        
        return {
            "recent_projects": recent_projects,
            "count": len(recent_projects)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recent projects: {str(e)}")

@router.get("/search")
async def search_projects(
    q: str = Query(..., min_length=1, description="Search query"),
    project_service: ProjectService = Depends(get_project_service)
):
    """
    Search projects by name or description.
    
    This endpoint searches through project names and user inputs
    to find matching projects.
    """
    try:
        matching_projects = await project_service.search_projects(q)
        
        return {
            "query": q,
            "matching_projects": matching_projects,
            "count": len(matching_projects)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search projects: {str(e)}")

@router.get("/{project_id}", response_model=ProjectResult)
async def get_project_result(
    project_id: str,
    project_service: ProjectService = Depends(get_project_service)
):
    """
    Get complete project result by ID.
    
    This endpoint returns the complete result of a project including
    all generated code, documentation, tests, and metadata.
    """
    try:
        result = await project_service.get_project_result(project_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get project result: {str(e)}")

@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    project_service: ProjectService = Depends(get_project_service)
):
    """
    Delete a project result.
    
    This endpoint deletes a project result and removes it from history.
    """
    try:
        success = await project_service.delete_project_result(project_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return {
            "message": "Project deleted successfully",
            "project_id": project_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete project: {str(e)}")

@router.get("/name/{project_name}")
async def get_project_by_name(
    project_name: str,
    project_service: ProjectService = Depends(get_project_service)
):
    """
    Get project by name.
    
    This endpoint finds a project by its name and returns its information.
    If multiple projects have the same name, returns the most recent one.
    """
    try:
        project = await project_service.get_project_by_name(project_name)
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return project
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get project by name: {str(e)}")

@router.post("/cleanup")
async def cleanup_old_projects(
    max_age_days: int = Query(30, ge=1, le=365, description="Maximum age in days for projects to keep"),
    project_service: ProjectService = Depends(get_project_service)
):
    """
    Clean up old project results.
    
    This endpoint removes old project results and history entries
    that are older than the specified number of days.
    """
    try:
        await project_service.cleanup_old_results(max_age_days)
        
        return {
            "message": f"Cleaned up projects older than {max_age_days} days",
            "max_age_days": max_age_days
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup projects: {str(e)}")

@router.get("/")
async def list_all_projects(
    project_service: ProjectService = Depends(get_project_service)
):
    """
    List all project IDs.
    
    This endpoint returns a list of all stored project IDs.
    """
    try:
        project_ids = project_service.get_all_project_ids()
        
        return {
            "project_ids": project_ids,
            "total_count": len(project_ids)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list projects: {str(e)}")
