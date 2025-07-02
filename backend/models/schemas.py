"""
Data schemas and utility models.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class ProjectStatus(str, Enum):
    """Project status enumeration."""
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AgentType(str, Enum):
    """Agent type enumeration."""
    REQUIREMENT_ANALYST = "requirement_analyst"
    PYTHON_CODER = "python_coder"
    CODE_REVIEWER = "code_reviewer"
    DOCUMENTATION_WRITER = "documentation_writer"
    TEST_GENERATOR = "test_generator"
    DEPLOYMENT_ENGINEER = "deployment_engineer"
    UI_DESIGNER = "ui_designer"

class LogLevel(str, Enum):
    """Log level enumeration."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class LogEntry(BaseModel):
    """Log entry model."""
    timestamp: datetime = Field(default_factory=datetime.now, description="Log timestamp")
    level: LogLevel = Field(..., description="Log level")
    message: str = Field(..., description="Log message")
    agent: Optional[str] = Field(None, description="Agent that generated the log")
    step: Optional[str] = Field(None, description="Pipeline step")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class SubStep(BaseModel):
    """Sub-step model for detailed progress tracking."""
    id: str = Field(..., description="Sub-step identifier")
    description: str = Field(..., description="Sub-step description")
    status: str = Field("pending", description="Sub-step status")
    progress_percentage: float = Field(0.0, description="Sub-step progress", ge=0, le=100)
    start_time: Optional[datetime] = Field(None, description="Sub-step start time")
    end_time: Optional[datetime] = Field(None, description="Sub-step end time")

class PipelineStep(BaseModel):
    """Pipeline step model."""
    id: str = Field(..., description="Step identifier")
    name: str = Field(..., description="Step name")
    description: str = Field(..., description="Step description")
    agent_type: AgentType = Field(..., description="Agent responsible for this step")
    status: str = Field("pending", description="Step status")
    progress_percentage: float = Field(0.0, description="Step progress", ge=0, le=100)
    start_time: Optional[datetime] = Field(None, description="Step start time")
    end_time: Optional[datetime] = Field(None, description="Step end time")
    duration: Optional[float] = Field(None, description="Step duration in seconds")
    substeps: List[SubStep] = Field(default_factory=list, description="Sub-steps")
    logs: List[LogEntry] = Field(default_factory=list, description="Step logs")
    result: Optional[Dict[str, Any]] = Field(None, description="Step result")
    error: Optional[str] = Field(None, description="Error message if failed")

class ProjectMetadata(BaseModel):
    """Project metadata model."""
    project_id: str = Field(..., description="Unique project identifier")
    project_name: str = Field(..., description="Project name")
    user_input: str = Field(..., description="Original user input")
    status: ProjectStatus = Field(..., description="Project status")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    total_duration: Optional[float] = Field(None, description="Total duration in seconds")
    steps: List[PipelineStep] = Field(default_factory=list, description="Pipeline steps")
    error: Optional[str] = Field(None, description="Error message if failed")

class WebSocketMessage(BaseModel):
    """WebSocket message model."""
    type: str = Field(..., description="Message type")
    project_id: str = Field(..., description="Project identifier")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")
    data: Dict[str, Any] = Field(..., description="Message data")

class ProgressUpdate(BaseModel):
    """Progress update model for WebSocket messages."""
    project_id: str = Field(..., description="Project identifier")
    step_id: Optional[str] = Field(None, description="Current step identifier")
    progress_percentage: float = Field(..., description="Overall progress percentage", ge=0, le=100)
    current_step: Optional[str] = Field(None, description="Current step name")
    status: str = Field(..., description="Current status")
    message: str = Field(..., description="Progress message")
    logs: List[LogEntry] = Field(default_factory=list, description="Recent logs")
