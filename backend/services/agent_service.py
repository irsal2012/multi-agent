"""
Agent service for managing agent information and capabilities using the new factory system.
"""

import logging
from typing import Dict, Any, List

from models.responses import AgentsResponse, AgentInfo
from core.agent_factory import agent_factory
from config.pipeline_config import pipeline_config_manager

class AgentService:
    """Service for managing agent information using the factory system."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Ensure agents are discovered
        self._ensure_agents_discovered()
        
        # Legacy pipeline steps for backward compatibility
        self.pipeline_steps = [
            'Requirements Analysis',
            'Code Generation', 
            'Code Review & Iteration',
            'Documentation Generation',
            'Test Case Generation',
            'Deployment Configuration',
            'UI Generation'
        ]
    
    def _ensure_agents_discovered(self):
        """Ensure agents are discovered and registered."""
        try:
            if not agent_factory.get_available_agents():
                discovered_count = agent_factory.auto_discover_agents()
                self.logger.info(f"Auto-discovered {discovered_count} agents")
        except Exception as e:
            self.logger.error(f"Failed to discover agents: {str(e)}")
    
    def _get_agent_info_from_factory(self) -> Dict[str, Dict[str, Any]]:
        """Get agent information from the factory system."""
        agent_info = {}
        available_agents = agent_factory.get_available_agents()
        
        for agent_key, metadata in available_agents.items():
            agent_info[agent_key] = {
                'name': metadata.name,
                'description': metadata.description,
                'capabilities': metadata.capabilities,
                'config_type': metadata.config_type.value,
                'dependencies': metadata.dependencies or [],
                'version': metadata.version,
                'author': metadata.author
            }
        
        return agent_info
    
    async def get_agents_info(self) -> AgentsResponse:
        """Get comprehensive agent information from the factory system."""
        
        # Get agent info from factory
        agent_info = self._get_agent_info_from_factory()
        
        # Create detailed agent info list
        agents_info = []
        for agent_key, info in agent_info.items():
            agent_info_obj = AgentInfo(
                name=info['name'],
                description=info['description'],
                capabilities=info['capabilities']
            )
            agents_info.append(agent_info_obj)
        
        # Create agent descriptions dict
        agent_descriptions = {
            key: info['description'] 
            for key, info in agent_info.items()
        }
        
        # Get pipeline steps from configuration
        pipeline_steps = self._get_pipeline_steps_from_config()
        
        return AgentsResponse(
            available_agents=list(agent_info.keys()),
            agent_descriptions=agent_descriptions,
            pipeline_steps=pipeline_steps,
            agents_info=agents_info
        )
    
    async def get_agent_capabilities(self, agent_name: str) -> List[str]:
        """Get capabilities for a specific agent."""
        agent_info = self._get_agent_info_from_factory()
        if agent_name in agent_info:
            return agent_info[agent_name]['capabilities']
        return []
    
    async def get_pipeline_steps(self) -> List[str]:
        """Get the list of pipeline steps."""
        return self._get_pipeline_steps_from_config()
    
    async def validate_agent_exists(self, agent_name: str) -> bool:
        """Check if an agent exists."""
        agent_info = self._get_agent_info_from_factory()
        return agent_name in agent_info
    
    async def get_agent_description(self, agent_name: str) -> str:
        """Get description for a specific agent."""
        agent_info = self._get_agent_info_from_factory()
        if agent_name in agent_info:
            return agent_info[agent_name]['description']
        return ""
    
    async def get_agents_summary(self) -> Dict[str, Any]:
        """Get a summary of all agents."""
        agent_info = self._get_agent_info_from_factory()
        factory_stats = agent_factory.get_factory_stats()
        
        return {
            'total_agents': len(agent_info),
            'agent_names': list(agent_info.keys()),
            'pipeline_steps_count': len(self._get_pipeline_steps_from_config()),
            'capabilities_count': sum(len(info['capabilities']) for info in agent_info.values()),
            'factory_stats': factory_stats,
            'available_pipelines': pipeline_config_manager.get_available_pipelines()
        }
    
    def _get_pipeline_steps_from_config(self) -> List[str]:
        """Get pipeline steps from the current configuration."""
        try:
            # Get default pipeline configuration
            pipeline_config = pipeline_config_manager.get_pipeline_config("default")
            
            # Extract step names from configuration
            steps = []
            for step in pipeline_config.steps:
                # Try to get agent metadata for better step names
                agent_metadata = agent_factory.get_agent_metadata(step.agent_type)
                if agent_metadata:
                    steps.append(agent_metadata.name)
                else:
                    # Fallback to agent type
                    steps.append(step.agent_type.replace('_', ' ').title())
            
            return steps
            
        except Exception as e:
            self.logger.warning(f"Failed to get pipeline steps from config: {str(e)}")
            # Return legacy pipeline steps as fallback
            return self.pipeline_steps
    
    async def get_pipeline_configurations(self) -> Dict[str, Any]:
        """Get available pipeline configurations."""
        try:
            available_pipelines = pipeline_config_manager.get_available_pipelines()
            pipeline_info = {}
            
            for pipeline_name in available_pipelines:
                config = pipeline_config_manager.get_pipeline_config(pipeline_name)
                pipeline_info[pipeline_name] = {
                    'name': config.name,
                    'description': config.description,
                    'version': config.version,
                    'total_steps': len(config.steps),
                    'step_names': [step.agent_type for step in config.steps]
                }
            
            return {
                'available_pipelines': available_pipelines,
                'pipeline_details': pipeline_info
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get pipeline configurations: {str(e)}")
            return {
                'available_pipelines': ['default'],
                'pipeline_details': {}
            }
    
    async def get_agent_dependencies(self, agent_name: str) -> Dict[str, Any]:
        """Get dependency information for a specific agent."""
        try:
            agent_metadata = agent_factory.get_agent_metadata(agent_name)
            if not agent_metadata:
                return {'error': f'Agent {agent_name} not found'}
            
            dependencies = agent_metadata.dependencies or []
            dependency_info = []
            
            for dep in dependencies:
                dep_metadata = agent_factory.get_agent_metadata(dep.lower().replace(' ', '_'))
                if dep_metadata:
                    dependency_info.append({
                        'name': dep_metadata.name,
                        'description': dep_metadata.description,
                        'available': True
                    })
                else:
                    dependency_info.append({
                        'name': dep,
                        'description': 'Dependency not found',
                        'available': False
                    })
            
            return {
                'agent_name': agent_metadata.name,
                'dependencies': dependency_info,
                'dependency_count': len(dependencies)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get agent dependencies: {str(e)}")
            return {'error': str(e)}
