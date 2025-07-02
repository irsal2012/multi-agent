"""
Pydantic models for API requests.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class GenerateCodeRequest(BaseModel):
    """Request model for code generation."""
    user_input: str = Field(..., description="Natural language description of the software to build", min_length=10)
    project_name: Optional[str] = Field(None, description="Optional project name (auto-generated if not provided)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_input": "Create a web scraper that extracts product information from e-commerce websites, stores the data in a database, and provides a REST API to query the results.",
                "project_name": "web-scraper-api"
            }
        }

class ValidateInputRequest(BaseModel):
    """Request model for input validation."""
    user_input: str = Field(..., description="User input to validate")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_input": "Build a chatbot for customer service"
            }
        }

class ProjectQueryRequest(BaseModel):
    """Request model for project queries."""
    limit: Optional[int] = Field(10, description="Number of projects to return", ge=1, le=100)
    offset: Optional[int] = Field(0, description="Number of projects to skip", ge=0)
    filter_success: Optional[bool] = Field(None, description="Filter by success status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "limit": 10,
                "offset": 0,
                "filter_success": True
            }
        }
