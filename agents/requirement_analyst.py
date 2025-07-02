"""
Requirement Analysis Agent for converting natural language descriptions 
into structured software requirements.
"""

import autogen
from typing import Dict, Any


class RequirementAnalyst:
    """Agent specialized in analyzing and structuring software requirements."""
    
    @staticmethod
    def get_config() -> Dict[str, Any]:
        """Get configuration for the Requirement Analysis Agent."""
        return {
            "name": "RequirementAnalyst",
            "system_message": """You are a Requirements Analysis Agent specialized in converting natural language descriptions into structured software requirements.

Your responsibilities:
1. Analyze user input to extract functional and non-functional requirements
2. Identify edge cases and potential issues
3. Create structured requirement documents in JSON format
4. Ask clarifying questions when requirements are ambiguous
5. Ensure requirements are testable and implementable

Output Format:
- Return requirements as structured JSON with sections for:
  - functional_requirements: List of specific features
  - non_functional_requirements: Performance, security, usability requirements
  - constraints: Technical or business constraints
  - assumptions: Any assumptions made
  - questions: Clarifying questions if needed

Be thorough, precise, and always consider the complete software development lifecycle.""",
            "human_input_mode": "NEVER",
            "max_consecutive_auto_reply": 3,
        }
    
    @staticmethod
    def create_agent(llm_config: Dict[str, Any]) -> autogen.AssistantAgent:
        """Create and return a configured RequirementAnalyst agent."""
        config = RequirementAnalyst.get_config()
        return autogen.AssistantAgent(
            llm_config=llm_config,
            **config
        )
