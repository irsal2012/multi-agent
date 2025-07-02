"""
Agent service for managing agent information and capabilities.
"""

import logging
from typing import Dict, Any, List

from models.responses import AgentsResponse, AgentInfo

class AgentService:
    """Service for managing agent information."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Agent information and capabilities
        self.agent_info = {
            'requirement_analyst': {
                'name': 'Requirement Analyst',
                'description': 'Analyzes natural language input and creates structured requirements',
                'capabilities': [
                    'Natural language processing',
                    'Requirement extraction and structuring',
                    'Ambiguity detection and clarification',
                    'JSON output formatting'
                ]
            },
            'python_coder': {
                'name': 'Python Coder',
                'description': 'Generates high-quality Python code from requirements',
                'capabilities': [
                    'Python code generation',
                    'Best practices implementation',
                    'Type hints and documentation',
                    'Error handling and logging'
                ]
            },
            'code_reviewer': {
                'name': 'Code Reviewer',
                'description': 'Reviews code for quality, security, and best practices',
                'capabilities': [
                    'Code quality analysis',
                    'Security vulnerability detection',
                    'Performance optimization',
                    'Best practices validation'
                ]
            },
            'documentation_writer': {
                'name': 'Documentation Writer',
                'description': 'Creates comprehensive documentation',
                'capabilities': [
                    'README generation',
                    'API documentation',
                    'Architecture documentation',
                    'User guides and tutorials'
                ]
            },
            'test_generator': {
                'name': 'Test Generator',
                'description': 'Generates comprehensive test suites',
                'capabilities': [
                    'Unit test generation',
                    'Integration test creation',
                    'Test fixture setup',
                    'Mock object creation'
                ]
            },
            'deployment_engineer': {
                'name': 'Deployment Engineer',
                'description': 'Creates deployment configurations and scripts',
                'capabilities': [
                    'Docker containerization',
                    'CI/CD pipeline setup',
                    'Cloud deployment configs',
                    'Environment management'
                ]
            },
            'ui_designer': {
                'name': 'UI Designer',
                'description': 'Creates Streamlit user interfaces',
                'capabilities': [
                    'Streamlit app generation',
                    'Interactive component design',
                    'Data visualization',
                    'User experience optimization'
                ]
            }
        }
        
        self.pipeline_steps = [
            'Requirements Analysis',
            'Code Generation', 
            'Code Review & Iteration',
            'Documentation Generation',
            'Test Case Generation',
            'Deployment Configuration',
            'UI Generation'
        ]
    
    async def get_agents_info(self) -> AgentsResponse:
        """Get comprehensive agent information."""
        
        # Create detailed agent info list
        agents_info = []
        for agent_key, info in self.agent_info.items():
            agent_info = AgentInfo(
                name=info['name'],
                description=info['description'],
                capabilities=info['capabilities']
            )
            agents_info.append(agent_info)
        
        # Create agent descriptions dict
        agent_descriptions = {
            key: info['description'] 
            for key, info in self.agent_info.items()
        }
        
        return AgentsResponse(
            available_agents=list(self.agent_info.keys()),
            agent_descriptions=agent_descriptions,
            pipeline_steps=self.pipeline_steps,
            agents_info=agents_info
        )
    
    async def get_agent_capabilities(self, agent_name: str) -> List[str]:
        """Get capabilities for a specific agent."""
        if agent_name in self.agent_info:
            return self.agent_info[agent_name]['capabilities']
        return []
    
    async def get_pipeline_steps(self) -> List[str]:
        """Get the list of pipeline steps."""
        return self.pipeline_steps
    
    async def validate_agent_exists(self, agent_name: str) -> bool:
        """Check if an agent exists."""
        return agent_name in self.agent_info
    
    async def get_agent_description(self, agent_name: str) -> str:
        """Get description for a specific agent."""
        if agent_name in self.agent_info:
            return self.agent_info[agent_name]['description']
        return ""
    
    async def get_agents_summary(self) -> Dict[str, Any]:
        """Get a summary of all agents."""
        return {
            'total_agents': len(self.agent_info),
            'agent_names': list(self.agent_info.keys()),
            'pipeline_steps_count': len(self.pipeline_steps),
            'capabilities_count': sum(len(info['capabilities']) for info in self.agent_info.values())
        }
