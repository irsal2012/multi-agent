"""
Base agent interface and metadata definitions for the Multi-Agent Framework.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ConfigType(Enum):
    """Configuration types for different agent roles."""
    STANDARD = "standard"
    CODING = "coding"
    REVIEW = "review"
    CREATIVE = "creative"

@dataclass
class AgentMetadata:
    """Metadata for agent registration and discovery."""
    name: str
    description: str
    capabilities: List[str]
    config_type: ConfigType
    dependencies: Optional[List[str]] = None
    version: str = "1.0.0"
    author: str = "Multi-Agent Framework"

class BaseAgent(ABC):
    """Abstract base class for all agents in the framework."""
    
    def __init__(self, llm_config: Dict[str, Any]):
        self.llm_config = llm_config
        self.metadata = self.get_metadata()
        self._agent_instance = None
        self._initialized = False
    
    @classmethod
    @abstractmethod
    def get_metadata(cls) -> AgentMetadata:
        """Return agent metadata for registration and discovery."""
        pass
    
    @abstractmethod
    def create_agent(self) -> Any:
        """Create and return the actual AutoGen agent instance."""
        pass
    
    def get_agent(self) -> Any:
        """Get the agent instance, creating it if necessary."""
        if not self._initialized:
            self._agent_instance = self.create_agent()
            self._initialized = True
        return self._agent_instance
    
    def process(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Process input data and return output.
        Default implementation delegates to the agent instance.
        Override for custom processing logic.
        """
        agent = self.get_agent()
        # Default processing - subclasses should override for specific behavior
        return {"agent": self.metadata.name, "input": input_data, "context": context}
    
    def validate_input(self, input_data: Any) -> Dict[str, Any]:
        """
        Validate input data for this agent.
        Returns validation result with is_valid, warnings, and suggestions.
        """
        return {
            "is_valid": True,
            "warnings": [],
            "suggestions": []
        }
    
    def get_system_message(self) -> str:
        """Get the system message for this agent. Override in subclasses."""
        return f"You are {self.metadata.name}. {self.metadata.description}"
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities."""
        return self.metadata.capabilities.copy()
    
    def get_dependencies(self) -> List[str]:
        """Get agent dependencies."""
        return self.metadata.dependencies.copy() if self.metadata.dependencies else []
    
    def __str__(self) -> str:
        return f"{self.metadata.name} (v{self.metadata.version})"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.metadata.name}>"
