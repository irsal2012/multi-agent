"""
Agent factory for dynamic agent registration and creation.
"""

import logging
import importlib
import pkgutil
from typing import Dict, Type, Optional, List
from agents.base import BaseAgent, AgentMetadata, ConfigType
from config.model_config import model_config

class AgentFactory:
    """Factory for creating and managing agent instances."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._agents: Dict[str, Type[BaseAgent]] = {}
        self._metadata_cache: Dict[str, AgentMetadata] = {}
        self._instances: Dict[str, BaseAgent] = {}
        
    def register_agent(self, agent_class: Type[BaseAgent]) -> str:
        """
        Register an agent class with the factory.
        Returns the agent key for future reference.
        """
        try:
            metadata = agent_class.get_metadata()
            agent_key = self._generate_agent_key(metadata.name)
            
            self._agents[agent_key] = agent_class
            self._metadata_cache[agent_key] = metadata
            
            self.logger.info(f"Registered agent: {metadata.name} (key: {agent_key})")
            return agent_key
            
        except Exception as e:
            self.logger.error(f"Failed to register agent {agent_class.__name__}: {str(e)}")
            raise
    
    def create_agent(self, agent_key: str, config_override: Optional[Dict] = None) -> BaseAgent:
        """
        Create an agent instance by key.
        Optionally override the default LLM configuration.
        """
        if agent_key not in self._agents:
            raise ValueError(f"Unknown agent key: {agent_key}. Available: {list(self._agents.keys())}")
        
        # Check if we already have an instance (singleton pattern)
        if agent_key in self._instances:
            return self._instances[agent_key]
        
        try:
            agent_class = self._agents[agent_key]
            metadata = self._metadata_cache[agent_key]
            
            # Get appropriate LLM configuration
            if config_override:
                llm_config = config_override
            else:
                llm_config = self._get_llm_config_for_type(metadata.config_type)
            
            # Create agent instance
            agent_instance = agent_class(llm_config)
            
            # Cache the instance
            self._instances[agent_key] = agent_instance
            
            self.logger.info(f"Created agent instance: {metadata.name}")
            return agent_instance
            
        except Exception as e:
            self.logger.error(f"Failed to create agent {agent_key}: {str(e)}")
            raise
    
    def get_agent(self, agent_key: str) -> Optional[BaseAgent]:
        """Get an existing agent instance if it exists."""
        return self._instances.get(agent_key)
    
    def get_available_agents(self) -> Dict[str, AgentMetadata]:
        """Get metadata for all registered agents."""
        return self._metadata_cache.copy()
    
    def get_agent_metadata(self, agent_key: str) -> Optional[AgentMetadata]:
        """Get metadata for a specific agent."""
        return self._metadata_cache.get(agent_key)
    
    def get_agents_by_config_type(self, config_type: ConfigType) -> List[str]:
        """Get all agent keys that use a specific configuration type."""
        return [
            key for key, metadata in self._metadata_cache.items()
            if metadata.config_type == config_type
        ]
    
    def auto_discover_agents(self) -> int:
        """
        Automatically discover and register all agent classes.
        Returns the number of agents discovered.
        """
        discovered_count = 0
        
        try:
            import agents
            
            # Iterate through all modules in the agents package
            for importer, modname, ispkg in pkgutil.iter_modules(agents.__path__):
                if modname == 'base' or modname.startswith('__'):
                    continue
                
                try:
                    # Import the module
                    module = importlib.import_module(f'agents.{modname}')
                    
                    # Look for agent classes
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        
                        # Check if it's a BaseAgent subclass (but not BaseAgent itself)
                        if (isinstance(attr, type) and 
                            issubclass(attr, BaseAgent) and 
                            attr != BaseAgent):
                            
                            try:
                                self.register_agent(attr)
                                discovered_count += 1
                            except Exception as e:
                                self.logger.warning(f"Failed to register {attr.__name__}: {str(e)}")
                
                except Exception as e:
                    self.logger.warning(f"Failed to import agents.{modname}: {str(e)}")
            
            self.logger.info(f"Auto-discovered {discovered_count} agents")
            return discovered_count
            
        except Exception as e:
            self.logger.error(f"Auto-discovery failed: {str(e)}")
            return 0
    
    def validate_dependencies(self) -> Dict[str, List[str]]:
        """
        Validate agent dependencies and return any issues.
        Returns a dict of agent_key -> list of missing dependencies.
        """
        issues = {}
        
        for agent_key, metadata in self._metadata_cache.items():
            if metadata.dependencies:
                missing_deps = []
                for dep in metadata.dependencies:
                    dep_key = self._generate_agent_key(dep)
                    if dep_key not in self._agents:
                        missing_deps.append(dep)
                
                if missing_deps:
                    issues[agent_key] = missing_deps
        
        return issues
    
    def get_dependency_order(self) -> List[str]:
        """
        Get agents in dependency order (dependencies first).
        Raises ValueError if circular dependencies are detected.
        """
        # Simple topological sort
        visited = set()
        temp_visited = set()
        result = []
        
        def visit(agent_key: str):
            if agent_key in temp_visited:
                raise ValueError(f"Circular dependency detected involving {agent_key}")
            
            if agent_key not in visited:
                temp_visited.add(agent_key)
                
                metadata = self._metadata_cache.get(agent_key)
                if metadata and metadata.dependencies:
                    for dep in metadata.dependencies:
                        dep_key = self._generate_agent_key(dep)
                        if dep_key in self._agents:
                            visit(dep_key)
                
                temp_visited.remove(agent_key)
                visited.add(agent_key)
                result.append(agent_key)
        
        for agent_key in self._agents.keys():
            if agent_key not in visited:
                visit(agent_key)
        
        return result
    
    def clear_instances(self):
        """Clear all cached agent instances."""
        self._instances.clear()
        self.logger.info("Cleared all agent instances")
    
    def get_factory_stats(self) -> Dict[str, int]:
        """Get factory statistics."""
        return {
            "registered_agents": len(self._agents),
            "cached_instances": len(self._instances),
            "config_types": len(set(m.config_type for m in self._metadata_cache.values()))
        }
    
    def _generate_agent_key(self, agent_name: str) -> str:
        """Generate a consistent key from agent name."""
        return agent_name.lower().replace(' ', '_').replace('-', '_')
    
    def _get_llm_config_for_type(self, config_type: ConfigType) -> Dict:
        """Get appropriate LLM configuration for the given type."""
        config_methods = {
            ConfigType.STANDARD: model_config.get_llm_config,
            ConfigType.CODING: model_config.get_coding_config,
            ConfigType.REVIEW: model_config.get_review_config,
            ConfigType.CREATIVE: model_config.get_creative_config
        }
        
        method = config_methods.get(config_type, model_config.get_llm_config)
        return method()

# Global factory instance
agent_factory = AgentFactory()
