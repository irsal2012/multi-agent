"""
Pydantic models for API responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from enum import Enum

class StatusEnum(str, Enum):
    """Status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class ValidationResponse(BaseModel):
    """Response model for input validation."""
    is_valid: bool = Field(..., description="Whether the input is valid")
    warnings: List[str] = Field(default_factory=list, description="List of warnings")
    suggestions: List[str] = Field(default_factory=list, description="List of suggestions")

class StepInfo(BaseModel):
    """Information about a pipeline step."""
    name: str = Field(..., description="Step name")
    description: str = Field(..., description="Step description")
    status: StatusEnum = Field(..., description="Step status")
    progress_percentage: float = Field(0.0, description="Step progress percentage", ge=0, le=100)
    start_time: Optional[datetime] = Field(None, description="Step start time")
    end_time: Optional[datetime] = Field(None, description="Step end time")
    duration: Optional[float] = Field(None, description="Step duration in seconds")
    agent_name: Optional[str] = Field(None, description="Agent responsible for this step")
    substeps: List[Dict[str, Any]] = Field(default_factory=list, description="Sub-steps information")

class ProgressResponse(BaseModel):
    """Response model for progress information."""
    total_steps: int = Field(..., description="Total number of steps")
    completed_steps: int = Field(..., description="Number of completed steps")
    failed_steps: int = Field(..., description="Number of failed steps")
    progress_percentage: float = Field(..., description="Overall progress percentage", ge=0, le=100)
    steps: List[StepInfo] = Field(default_factory=list, description="Detailed step information")
    elapsed_time: float = Field(0.0, description="Elapsed time in seconds")
    estimated_remaining_time: float = Field(0.0, description="Estimated remaining time in seconds")
    is_running: bool = Field(False, description="Whether the pipeline is currently running")
    is_completed: bool = Field(False, description="Whether the pipeline is completed")
    has_failures: bool = Field(False, description="Whether there are any failures")
    current_step_info: Optional[StepInfo] = Field(None, description="Current step information")
    logs: List[Dict[str, Any]] = Field(default_factory=list, description="Recent log entries")

class PipelineMetadata(BaseModel):
    """Pipeline execution metadata."""
    start_time: datetime = Field(..., description="Pipeline start time")
    end_time: Optional[datetime] = Field(None, description="Pipeline end time")
    execution_time_seconds: float = Field(0.0, description="Total execution time in seconds")
    success: bool = Field(..., description="Whether the pipeline succeeded")

class CodeResult(BaseModel):
    """Code generation result."""
    final_code: str = Field(..., description="Final generated code")
    original_code: Optional[str] = Field(None, description="Original code before review")
    additional_modules: List[str] = Field(default_factory=list, description="Additional code modules")
    review_feedback: List[str] = Field(default_factory=list, description="Code review feedback")
    loop_summary: Optional[Dict[str, Any]] = Field(None, description="Code review loop summary")

class DocumentationResult(BaseModel):
    """Documentation generation result."""
    readme: str = Field(..., description="README documentation")
    timestamp: datetime = Field(..., description="Generation timestamp")

class TestResult(BaseModel):
    """Test generation result."""
    test_code: str = Field(..., description="Generated test code")
    additional_tests: List[str] = Field(default_factory=list, description="Additional test files")
    full_response: str = Field(..., description="Full agent response")
    timestamp: datetime = Field(..., description="Generation timestamp")

class DeploymentResult(BaseModel):
    """Deployment configuration result."""
    deployment_configs: str = Field(..., description="Deployment configurations")
    timestamp: datetime = Field(..., description="Generation timestamp")

class UIResult(BaseModel):
    """UI generation result."""
    streamlit_app: str = Field(..., description="Generated Streamlit application")
    additional_ui_files: List[str] = Field(default_factory=list, description="Additional UI files")
    full_response: str = Field(..., description="Full agent response")
    timestamp: datetime = Field(..., description="Generation timestamp")

class GenerationResponse(BaseModel):
    """Response model for code generation."""
    project_id: str = Field(..., description="Unique project identifier")
    project_name: str = Field(..., description="Project name")
    status: StatusEnum = Field(..., description="Generation status")
    message: str = Field(..., description="Status message")
    progress_url: Optional[str] = Field(None, description="URL for progress tracking")

class ProjectResult(BaseModel):
    """Complete project result."""
    project_name: str = Field(..., description="Project name")
    timestamp: datetime = Field(..., description="Project creation timestamp")
    user_input: str = Field(..., description="Original user input")
    requirements: Dict[str, Any] = Field(..., description="Analyzed requirements")
    code: CodeResult = Field(..., description="Generated code")
    documentation: DocumentationResult = Field(..., description="Generated documentation")
    tests: TestResult = Field(..., description="Generated tests")
    deployment: DeploymentResult = Field(..., description="Deployment configuration")
    ui: UIResult = Field(..., description="Generated UI")
    progress: ProgressResponse = Field(..., description="Final progress information")
    pipeline_metadata: PipelineMetadata = Field(..., description="Pipeline execution metadata")

class AgentInfo(BaseModel):
    """Agent information."""
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    capabilities: List[str] = Field(default_factory=list, description="Agent capabilities")

class AgentsResponse(BaseModel):
    """Response model for agents information."""
    available_agents: List[str] = Field(..., description="List of available agent names")
    agent_descriptions: Dict[str, str] = Field(..., description="Agent descriptions")
    pipeline_steps: List[str] = Field(..., description="Pipeline steps")
    agents_info: List[AgentInfo] = Field(default_factory=list, description="Detailed agent information")

class ProjectHistoryItem(BaseModel):
    """Project history item."""
    timestamp: datetime = Field(..., description="Project timestamp")
    project_name: str = Field(..., description="Project name")
    user_input: str = Field(..., description="User input")
    success: bool = Field(..., description="Whether the project succeeded")
    execution_time: float = Field(..., description="Execution time in seconds")
    error: Optional[str] = Field(None, description="Error message if failed")

class ProjectHistoryResponse(BaseModel):
    """Response model for project history."""
    projects: List[ProjectHistoryItem] = Field(..., description="List of projects")
    total_count: int = Field(..., description="Total number of projects")
    successful_count: int = Field(..., description="Number of successful projects")
    failed_count: int = Field(..., description="Number of failed projects")

class PipelineStatusResponse(BaseModel):
    """Response model for pipeline status."""
    current_progress: ProgressResponse = Field(..., description="Current progress information")
    pipeline_history: List[ProjectHistoryItem] = Field(..., description="Pipeline history")
    total_runs: int = Field(..., description="Total number of runs")
    successful_runs: int = Field(..., description="Number of successful runs")
    failed_runs: int = Field(..., description="Number of failed runs")

class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str = Field(..., description="Error detail message")
    error_code: Optional[str] = Field(None, description="Error code")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
