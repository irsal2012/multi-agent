"""
Requirement Analysis Agent for converting natural language descriptions 
into structured software requirements.
"""

import autogen
from typing import Dict, Any
from agents.base import BaseAgent, AgentMetadata, ConfigType


class RequirementAnalystAgent(BaseAgent):
    """Agent specialized in analyzing and structuring software requirements."""
    
    @classmethod
    def get_metadata(cls) -> AgentMetadata:
        """Return agent metadata for registration and discovery."""
        return AgentMetadata(
            name="Requirement Analyst",
            description="Converts natural language descriptions into structured software requirements",
            capabilities=[
                "Requirement analysis",
                "User story creation",
                "Acceptance criteria definition",
                "Edge case identification",
                "Functional requirement extraction",
                "Non-functional requirement analysis",
                "Requirement validation"
            ],
            config_type=ConfigType.STANDARD,
            dependencies=[],  # First in pipeline, no dependencies
            version="2.0.0"
        )
    
    def get_system_message(self) -> str:
        """Get the system message for this agent."""
        return """You are a Requirements Analysis Agent specialized in converting natural language descriptions into structured software requirements.

Your responsibilities:
1. Analyze user input to extract functional and non-functional requirements
2. Identify edge cases and potential issues
3. Create structured requirement documents in JSON format
4. Ask clarifying questions when requirements are ambiguous
5. Ensure requirements are testable and implementable
6. Break down complex requirements into manageable components
7. Identify dependencies between requirements

Output Format:
- Return requirements as structured JSON with sections for:
  - functional_requirements: List of specific features with IDs
  - non_functional_requirements: Performance, security, usability requirements
  - constraints: Technical or business constraints
  - assumptions: Any assumptions made
  - edge_cases: Potential edge cases to consider
  - questions: Clarifying questions if needed
  - acceptance_criteria: Testable criteria for each requirement

Standards:
- Each requirement should have a unique ID (e.g., FR-001, NFR-001)
- Requirements should be specific, measurable, and testable
- Use clear, unambiguous language
- Consider the complete software development lifecycle
- Identify potential risks and mitigation strategies

Be thorough, precise, and always consider the complete software development lifecycle."""
    
    def create_agent(self) -> autogen.AssistantAgent:
        """Create and return a configured RequirementAnalyst agent."""
        return autogen.AssistantAgent(
            name="requirement_analyst",
            system_message=self.get_system_message(),
            llm_config=self.llm_config,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=3  # Needs iteration for clarification
        )
    
    def validate_input(self, input_data: Any) -> Dict[str, Any]:
        """Validate input data for the Requirement Analyst agent."""
        issues = []
        warnings = []
        suggestions = []
        
        if not input_data:
            issues.append("No input data provided")
            return {"is_valid": False, "warnings": warnings, "suggestions": suggestions}
        
        # Check if input contains meaningful requirements
        if isinstance(input_data, str):
            if len(input_data.strip()) < 20:
                warnings.append("Input seems very short for comprehensive requirement analysis")
            
            # Check for key requirement indicators
            requirement_keywords = ["need", "want", "should", "must", "require", "feature", "function"]
            if not any(keyword in input_data.lower() for keyword in requirement_keywords):
                suggestions.append("Consider including more specific requirements using words like 'need', 'should', 'must', etc.")
            
            # Check for vague language
            vague_terms = ["good", "fast", "easy", "nice", "better", "simple"]
            if any(term in input_data.lower() for term in vague_terms):
                suggestions.append("Try to be more specific than terms like 'good', 'fast', 'easy' - provide measurable criteria")
        
        elif isinstance(input_data, dict):
            if "description" not in input_data and "requirements" not in input_data:
                suggestions.append("Consider including 'description' or 'requirements' key in input data")
        
        return {
            "is_valid": len(issues) == 0,
            "warnings": warnings,
            "suggestions": suggestions
        }
    
    def process(self, input_data: Any, context: Dict[str, Any] = None) -> Any:
        """Process user input and generate structured requirements."""
        # Validate input first
        validation = self.validate_input(input_data)
        if not validation["is_valid"]:
            return {
                "error": "Invalid input data",
                "validation_issues": validation
            }
        
        # Get the agent instance
        agent = self.get_agent()
        
        # Process the input (this would typically involve AutoGen conversation)
        # For now, return a structured response
        return {
            "agent": self.metadata.name,
            "input_processed": True,
            "validation": validation,
            "context": context,
            "agent_instance": agent.name if agent else None,
            "requirements_structure": {
                "functional_requirements": [],
                "non_functional_requirements": [],
                "constraints": [],
                "assumptions": [],
                "edge_cases": [],
                "questions": [],
                "acceptance_criteria": []
            }
        }


# Backward compatibility - keep the old class for existing code
class RequirementAnalyst:
    """Legacy wrapper for backward compatibility."""
    
    @staticmethod
    def get_config() -> Dict[str, Any]:
        """Get configuration for the Requirement Analysis Agent."""
        return {
            "name": "RequirementAnalyst",
            "system_message": RequirementAnalystAgent.get_metadata().description,
            "human_input_mode": "NEVER",
            "max_consecutive_auto_reply": 3,
        }
    
    @staticmethod
    def create_agent(llm_config: Dict[str, Any]) -> autogen.AssistantAgent:
        """Create and return a configured RequirementAnalyst agent."""
        agent_instance = RequirementAnalystAgent(llm_config)
        return agent_instance.create_agent()
