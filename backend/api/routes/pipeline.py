"""
Pipeline API routes.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import Dict, Any

from models.requests import GenerateCodeRequest, ValidateInputRequest
from models.responses import GenerationResponse, ValidationResponse, PipelineStatusResponse
from services.pipeline_service import PipelineService
from api.dependencies import get_pipeline_service

router = APIRouter()

@router.post("/generate", response_model=GenerationResponse)
async def generate_code(
    request: GenerateCodeRequest,
    background_tasks: BackgroundTasks,
    pipeline_service: PipelineService = Depends(get_pipeline_service)
):
    """
    Start code generation pipeline.
    
    This endpoint starts the multi-agent pipeline to generate code based on the user input.
    The pipeline runs asynchronously in the background.
    """
    try:
        response = await pipeline_service.start_generation(
            user_input=request.user_input,
            project_name=request.project_name
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start generation: {str(e)}")

@router.post("/validate", response_model=ValidationResponse)
async def validate_input(
    request: ValidateInputRequest,
    pipeline_service: PipelineService = Depends(get_pipeline_service)
):
    """
    Validate user input before starting generation.
    
    This endpoint validates the user input and provides suggestions for improvement.
    """
    try:
        validation_result = await pipeline_service.validate_input(request.user_input)
        return validation_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate input: {str(e)}")

@router.get("/status", response_model=PipelineStatusResponse)
async def get_pipeline_status(
    pipeline_service: PipelineService = Depends(get_pipeline_service)
):
    """
    Get overall pipeline status and statistics.
    
    This endpoint returns the current status of the pipeline system including
    statistics about runs, success rates, and current progress.
    """
    try:
        status = await pipeline_service.get_pipeline_status()
        
        # Convert to response model
        return PipelineStatusResponse(
            current_progress=status['current_progress'],
            pipeline_history=status['pipeline_history'],
            total_runs=status['total_runs'],
            successful_runs=status['successful_runs'],
            failed_runs=status['failed_runs']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pipeline status: {str(e)}")

@router.get("/status/{project_id}")
async def get_project_status(
    project_id: str,
    pipeline_service: PipelineService = Depends(get_pipeline_service)
):
    """
    Get status for a specific project.
    
    This endpoint returns the current status of a specific project by its ID.
    """
    try:
        project_status = await pipeline_service.get_project_status(project_id)
        
        if not project_status:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return project_status
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get project status: {str(e)}")

@router.post("/cancel/{project_id}")
async def cancel_project(
    project_id: str,
    pipeline_service: PipelineService = Depends(get_pipeline_service)
):
    """
    Cancel a running project.
    
    This endpoint cancels a running project by its ID.
    """
    try:
        success = await pipeline_service.cancel_project(project_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Project not found or not running")
        
        return {"message": "Project cancelled successfully", "project_id": project_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel project: {str(e)}")

@router.get("/result/{project_id}")
async def get_project_result(
    project_id: str,
    pipeline_service: PipelineService = Depends(get_pipeline_service)
):
    """
    Get complete project result by ID.
    
    This endpoint returns the complete result of a finished project.
    """
    try:
        result = await pipeline_service.get_project_result(project_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Project result not found")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get project result: {str(e)}")
