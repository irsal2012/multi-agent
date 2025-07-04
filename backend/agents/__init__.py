"""
Agents package for the Multi-Agent Framework.
Contains all specialized agents for different tasks using the new modular architecture.
"""

from .base import BaseAgent, AgentMetadata, ConfigType
from .requirement_analyst_agent import RequirementAnalystAgent, RequirementAnalyst
from .python_coder_agent import PythonCoderAgent, PythonCoder
from .code_reviewer_agent import CodeReviewerAgent, CodeReviewer
from .test_generator_agent import TestGeneratorAgent, TestGenerator
from .documentation_writer_agent import DocumentationWriterAgent, DocumentationWriter
from .deployment_engineer_agent import DeploymentEngineerAgent, DeploymentEngineer
from .ui_designer_agent import UIDesignerAgent, UIDesigner

__all__ = [
    # Base classes
    'BaseAgent',
    'AgentMetadata', 
    'ConfigType',
    
    # New modular agents
    'RequirementAnalystAgent',
    'PythonCoderAgent',
    'CodeReviewerAgent',
    'TestGeneratorAgent',
    'DocumentationWriterAgent',
    'DeploymentEngineerAgent',
    'UIDesignerAgent',
    
    # Legacy compatibility
    'RequirementAnalyst',
    'PythonCoder',
    'CodeReviewer',
    'TestGenerator',
    'DocumentationWriter',
    'DeploymentEngineer',
    'UIDesigner'
]
