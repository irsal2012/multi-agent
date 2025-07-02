"""
Agents API routes.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List

from models.responses import AgentsResponse
from services.agent_service import AgentService
from api.dependencies import get_agent_service

router = APIRouter()

@router.get("/info", response_model=AgentsResponse)
async def get_agents_info(
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    Get comprehensive information about all available agents.
    
    This endpoint returns detailed information about all agents including
    their capabilities, descriptions, and the pipeline steps they handle.
    """
    try:
        agents_info = await agent_service.get_agents_info()
        return agents_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agents info: {str(e)}")

@router.get("/capabilities/{agent_name}")
async def get_agent_capabilities(
    agent_name: str,
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    Get capabilities for a specific agent.
    
    This endpoint returns the list of capabilities for a specific agent.
    """
    try:
        # Validate agent exists
        if not await agent_service.validate_agent_exists(agent_name):
            raise HTTPException(status_code=404, detail="Agent not found")
        
        capabilities = await agent_service.get_agent_capabilities(agent_name)
        
        return {
            "agent_name": agent_name,
            "capabilities": capabilities
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent capabilities: {str(e)}")

@router.get("/steps")
async def get_pipeline_steps(
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    Get the list of pipeline steps.
    
    This endpoint returns the ordered list of steps in the multi-agent pipeline.
    """
    try:
        steps = await agent_service.get_pipeline_steps()
        
        return {
            "pipeline_steps": steps,
            "total_steps": len(steps)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pipeline steps: {str(e)}")

@router.get("/summary")
async def get_agents_summary(
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    Get a summary of all agents.
    
    This endpoint returns summary statistics about the available agents.
    """
    try:
        summary = await agent_service.get_agents_summary()
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agents summary: {str(e)}")

@router.get("/{agent_name}")
async def get_agent_details(
    agent_name: str,
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    Get detailed information about a specific agent.
    
    This endpoint returns detailed information about a specific agent
    including its description and capabilities.
    """
    try:
        # Validate agent exists
        if not await agent_service.validate_agent_exists(agent_name):
            raise HTTPException(status_code=404, detail="Agent not found")
        
        description = await agent_service.get_agent_description(agent_name)
        capabilities = await agent_service.get_agent_capabilities(agent_name)
        
        return {
            "agent_name": agent_name,
            "description": description,
            "capabilities": capabilities
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent details: {str(e)}")
